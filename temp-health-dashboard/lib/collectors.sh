#!/usr/bin/env bash

clear_cycle_cache() {
  mkdir -p "$CACHE_DIR"
  rm -f "$CACHE_DIR"/*
}

host_ips() {
  local host="$1"
  IFS=',' read -ra ips <<< "${HOST_IPS[$host]}"
  printf '%s\n' "${ips[@]}" | sed 's/[[:space:]]//g' | sed '/^$/d'
}

run_ssh() (
  { set +x; } 2>/dev/null
  local target="$1" command="$2"
  # Intentionally split SSH_OPTS so config authors can provide ordinary ssh flags.
  local timeout_s
  timeout_s="$(operation_timeout)"
  if [[ -n "${SSH_PASSWORD:-}" ]] && command -v sshpass >/dev/null 2>&1; then
    if command -v timeout >/dev/null 2>&1; then
      timeout "${timeout_s}s" env SSH_ASKPASS_REQUIRE=never sshpass -d 3 ssh -T $SSH_OPTS -o LogLevel=ERROR -o NumberOfPasswordPrompts=1 -o BatchMode=no -o ConnectTimeout="$timeout_s" "$target" "$command" 3<<<"$SSH_PASSWORD"
    else
      env SSH_ASKPASS_REQUIRE=never sshpass -d 3 ssh -T $SSH_OPTS -o LogLevel=ERROR -o NumberOfPasswordPrompts=1 -o BatchMode=no -o ConnectTimeout="$timeout_s" "$target" "$command" 3<<<"$SSH_PASSWORD"
    fi
  elif command -v timeout >/dev/null 2>&1; then
    timeout "${timeout_s}s" ssh -n -T -o LogLevel=ERROR -o BatchMode=yes -o ConnectTimeout="$timeout_s" $SSH_OPTS "$target" "$command"
  else
    ssh -n -T -o LogLevel=ERROR -o BatchMode=yes -o ConnectTimeout="$timeout_s" $SSH_OPTS "$target" "$command"
  fi
)

ssh_password_for_host() {
  local host="$1"
  if declare -p SSH_PASSWORDS >/dev/null 2>&1 && [[ -n "${SSH_PASSWORDS[$host]:-}" ]]; then
    printf '%s' "${SSH_PASSWORDS[$host]}"
  else
    printf '%s' "${SSH_PASSWORD:-}"
  fi
}

run_host_ssh() {
  local host="$1" target="$2" command="$3" password
  password="$(ssh_password_for_host "$host")"
  SSH_PASSWORD="$password" run_ssh "$target" "$command"
}

ssh_error_reason_text() {
  local output="$1" status="${2:-}" reason
  reason="$(awk '!/^\+{1,} / && NF { print; exit }' <<< "$output")"
  if [[ -n "$reason" ]]; then
    printf '%s' "$reason"
  elif [[ "$status" == 124 ]]; then
    printf 'timeout after %ss' "$(operation_timeout)"
  elif [[ -n "$status" ]]; then
    printf 'connection_failed (ssh exited %s without stderr)' "$status"
  else
    printf 'connection_failed'
  fi
}

ssh_error_reason() {
  local file="$1"
  ssh_error_reason_text "$(cat "$file" 2>/dev/null || true)"
}

ssh_retryable_reason() {
  case "$1" in
    connection_failed*|timeout\ after*|Connection\ reset*|kex_exchange_identification*|Connection\ timed\ out*|No\ route\ to\ host*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

collect_ping_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      while IFS= read -r ip; do
        local_key="$(safe_key "${host}_${ip}")"
        log_event INFO "icmp ping host=$host ip=$ip"
        if declare -F collection_loading_update >/dev/null 2>&1; then
          collection_loading_update 15 "ICMP checks: $host $ip" "Pinging $ip for host $host with timeout $(operation_timeout)s."
        fi
        ping_one "$host" "$ip" > "$CACHE_DIR/${local_key}.ping"
      done < <(host_ips "$host")
    ) &
  done
  wait
}

ping_one() {
  local host="$1" ip="$2" tmp timeout_s status=0
  tmp="$CACHE_DIR/$(safe_key "${host}_${ip}").ping.raw"
  timeout_s="$(operation_timeout)"
  if command -v timeout >/dev/null 2>&1; then
    timeout -k 1s "${timeout_s}s" ping -c1 -W"$timeout_s" "$ip" > "$tmp" 2>/dev/null || status=$?
  else
    ping -c1 -W"$timeout_s" "$ip" > "$tmp" 2>/dev/null || status=$?
  fi
  if [[ "$status" -eq 0 ]]; then
    local lat
    lat="$(sed -n 's/.*time=\([0-9.]*\).*/\1/p' "$tmp" | head -1)"
    printf 'PASS|%sms\n' "${lat:-unknown}"
  else
    if [[ "$status" -eq 124 || "$status" -eq 137 ]]; then
      log_event WARN "icmp ping timed out host=$host ip=$ip timeout=${timeout_s}s"
      printf 'FAIL|timeout after %ss\n' "$timeout_s"
    else
      log_event WARN "icmp ping failed host=$host ip=$ip status=$status"
      printf 'FAIL|unreachable\n'
    fi
  fi
  rm -f "$tmp"
}

collect_ssh_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    collect_ssh_for_host "$host" &
  done
  wait
}

collect_ssh_for_host() {
  local host="$1" ip local_key target attempts max_attempts status output reason
  while IFS= read -r ip; do
    local_key="$(safe_key "${host}_${ip}")"
    target="$(ssh_target_for_ip "$ip")"
    attempts=1
    max_attempts=$((SSH_CHECK_RETRIES + 1))
    while :; do
      log_event INFO "ssh check host=$host ip=$ip target=$target attempt=$attempts/$max_attempts"
      if output="$(run_host_ssh "$host" "$target" 'true' 2>&1)"; then
        : > "$CACHE_DIR/${local_key}.ssh.err"
        printf 'PASS|connected\n' > "$CACHE_DIR/${local_key}.ssh"
        break
      fi
      status=$?
      reason="$(ssh_error_reason_text "$output" "$status")"
      printf '%s\n' "$output" > "$CACHE_DIR/${local_key}.ssh.err"
      if (( attempts < max_attempts )) && ssh_retryable_reason "$reason"; then
        log_event WARN "ssh check transient failure host=$host ip=$ip target=$target attempt=$attempts/$max_attempts reason=$reason; retrying"
        attempts=$((attempts + 1))
        sleep 0.2
        continue
      fi
      log_event WARN "ssh check failed host=$host ip=$ip target=$target attempts=$attempts reason=$reason"
      printf 'FAIL|%s\n' "$reason" > "$CACHE_DIR/${local_key}.ssh"
      break
    done
  done < <(host_ips "$host")
}

generic_ip_for_host() {
  local host="$1" ip result
  while IFS= read -r ip; do
    result="$(get_ssh_result "$host" "$ip")"
    if [[ "${result%%|*}" == PASS ]]; then
      printf '%s' "$ip"
      return 0
    fi
  done < <(host_ips "$host")
  return 1
}

collect_timesync_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      selected_ip="$(generic_ip_for_host "$host" || true)"
      while IFS= read -r ip; do
        local_key="$(safe_key "${host}_${ip}")"
        target="$(ssh_target_for_ip "$ip")"
        : > "$CACHE_DIR/${local_key}.timesync"
        if [[ "${HOST_TIMESYNC[$host]:-1}" =~ ^(0|no|false|disabled)$ ]]; then
          printf 'TIMESYNC=SKIPPED|disabled in HOST_TIMESYNC\n' > "$CACHE_DIR/${local_key}.timesync"
          continue
        fi
        if [[ -n "$selected_ip" && "$ip" != "$selected_ip" && "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" == PASS ]]; then
          printf 'TIMESYNC=SKIPPED|checked via %s\n' "$selected_ip" > "$CACHE_DIR/${local_key}.timesync"
          continue
        fi
        if [[ -z "$selected_ip" || "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" != PASS ]]; then
          reason="$(ssh_failure_reason "$host" "$ip")"
          printf 'TIMESYNC=SSH_FAILED|%s\n' "$reason" > "$CACHE_DIR/${local_key}.timesync"
          continue
        fi
        collect_timesync_for_target "$host" "$target" > "$CACHE_DIR/${local_key}.timesync"
      done < <(host_ips "$host")
    ) &
  done
  wait
}

collect_timesync_for_target() {
  local host="$1" target="$2" sync source detail
  sync="$(run_host_ssh "$host" "$target" "timedatectl show -p NTPSynchronized --value 2>/dev/null || true" 2>/dev/null || true)"
  source="$(run_host_ssh "$host" "$target" "(chronyc -n sources 2>/dev/null | awk '/^[\\^=][*+]/ {print \\\$2; exit}') || (ntpq -pn 2>/dev/null | awk '/^\\*/ {print \\\$1; exit}') || true" 2>/dev/null || true)"
  [[ -z "$source" ]] && source="unknown"
  if [[ "$sync" == yes ]]; then
    printf 'TIMESYNC=PASS|source=%s synchronized=yes\n' "$source"
  else
    detail="source=${source} synchronized=${sync:-unknown}"
    log_event WARN "time sync check failed target=$target $detail"
    printf 'TIMESYNC=FAIL|%s\n' "$detail"
  fi
}

collect_systemd_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      selected_ip="$(generic_ip_for_host "$host" || true)"
      while IFS= read -r ip; do
        local_key="$(safe_key "${host}_${ip}")"
        target="$(ssh_target_for_ip "$ip")"
        : > "$CACHE_DIR/${local_key}.systemd"
        if [[ -n "$selected_ip" && "$ip" != "$selected_ip" && "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" == PASS ]]; then
          IFS=',' read -ra services <<< "${HOST_SERVICES[$host]:-}"
          for service in "${services[@]}"; do
            service="${service//[[:space:]]/}"; [[ -z "$service" ]] && continue
            printf 'SYSTEMD=%s|SKIPPED|checked via %s\n' "$service" "$selected_ip" >> "$CACHE_DIR/${local_key}.systemd"
          done
          continue
        fi
        if ssh_failed "$host" "$ip"; then
          reason="$(ssh_failure_reason "$host" "$ip")"
          log_event WARN "skipping systemd host=$host ip=$ip reason=$reason"
          IFS=',' read -ra services <<< "${HOST_SERVICES[$host]:-}"
          for service in "${services[@]}"; do
            service="${service//[[:space:]]/}"
            [[ -z "$service" ]] && continue
            printf 'SYSTEMD=%s|SSH_FAILED|%s\n' "$service" "$reason" >> "$CACHE_DIR/${local_key}.systemd"
          done
          continue
        fi
        IFS=',' read -ra services <<< "${HOST_SERVICES[$host]:-}"
        for service in "${services[@]}"; do
          service="${service//[[:space:]]/}"
          [[ -z "$service" ]] && continue
          log_event INFO "systemd check host=$host service=$service"
          if state="$(run_host_ssh "$host" "$target" "systemctl is-active '$service' 2>/dev/null || true" 2>/dev/null)"; then
            [[ -z "$state" ]] && state="unknown"
            if [[ "$state" != active ]]; then
              log_event WARN "systemd check failed host=$host ip=$ip service=$service state=$state"
            fi
            printf 'SYSTEMD=%s|%s|%s\n' "$service" "$state" "$(systemd_result_message "$service" "$state")" >> "$CACHE_DIR/${local_key}.systemd"
          else
            log_event WARN "systemd check failed host=$host ip=$ip service=$service"
            printf 'SYSTEMD=%s|unknown|%s\n' "$service" "$(systemd_result_message "$service" unknown)" >> "$CACHE_DIR/${local_key}.systemd"
          fi
        done
      done < <(host_ips "$host")
    ) &
  done
  wait
}

systemd_result_message() {
  local unit="$1" state="$2"
  case "$state" in
    active) printf '%s is active and running' "$unit" ;;
    inactive) printf '%s is installed but inactive; start or enable it if this service should be running' "$unit" ;;
    failed) printf '%s is failed; inspect journalctl -u %s for the failure log' "$unit" "$unit" ;;
    activating) printf '%s is still activating; check for slow startup dependencies' "$unit" ;;
    deactivating) printf '%s is deactivating; confirm this is expected during maintenance' "$unit" ;;
    unknown) printf '%s status is unknown; systemctl did not return a usable state' "$unit" ;;
    *) printf '%s returned systemd state %s' "$unit" "$state" ;;
  esac
}

collect_docker_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      selected_ip="$(generic_ip_for_host "$host" || true)"
      while IFS= read -r ip; do
        local_key="$(safe_key "${host}_${ip}")"
        target="$(ssh_target_for_ip "$ip")"
        log_event INFO "docker check host=$host ip=$ip"
        if [[ -n "$selected_ip" && "$ip" != "$selected_ip" && "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" == PASS ]]; then
          printf 'DOCKER=%s|SKIPPED|checked via %s\n' "generic" "$selected_ip" > "$CACHE_DIR/${local_key}.docker"
          : > "$CACHE_DIR/${local_key}.docker_logs"
          continue
        fi
        if ssh_failed "$host" "$ip"; then
          reason="$(ssh_failure_reason "$host" "$ip")"
          log_event WARN "skipping docker host=$host ip=$ip reason=$reason"
          collect_docker_ssh_failed "$host" "$reason" "$CACHE_DIR/${local_key}.docker" "$CACHE_DIR/${local_key}.docker_logs"
          continue
        fi
        collect_docker_for_host "$host" "$target" "$CACHE_DIR/${local_key}.docker" "$CACHE_DIR/${local_key}.docker_logs"
      done < <(host_ips "$host")
    ) &
  done
  wait
}

collect_docker_for_host() {
  local host="$1" target="$2" status_file="$3" logs_file="$4" configured="${HOST_CONTAINERS[$host]:-}"
  : > "$status_file"
  : > "$logs_file"
  if [[ -n "$configured" ]]; then
    IFS=',' read -ra containers <<< "$configured"
  else
    mapfile -t containers < <(run_host_ssh "$host" "$target" "docker ps --format '{{.Names}}'" 2>/dev/null || true)
  fi
  for container in "${containers[@]}"; do
    container="${container//[[:space:]]/}"
    [[ -z "$container" ]] && continue
    local inspect state health logs
    inspect="$(run_host_ssh "$host" "$target" "docker inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' '$container'" 2>/dev/null || true)"
    state="${inspect%%|*}"
    health="${inspect#*|}"
    [[ -z "$inspect" || "$state" == "$inspect" ]] && { state="missing"; health="unknown"; }
    if [[ "$state" != running || !( "$health" == healthy || "$health" == no-healthcheck ) ]]; then
      log_event WARN "docker check failed host=$host target=$target container=$container state=$state health=$health"
    fi
    printf 'DOCKER=%s|%s|%s\n' "$container" "$state" "$health" >> "$status_file"
    logs="$(run_host_ssh "$host" "$target" "docker logs --tail '$DOCKER_LOG_LINES' '$container' 2>&1" 2>/dev/null || true)"
    {
      printf '===== %s =====\n' "$container"
      printf '%s\n' "$logs"
    } >> "$logs_file"
  done
}


ssh_failed() {
  local result
  result="$(get_ssh_result "$1" "$2")"
  [[ "${result%%|*}" != PASS ]]
}

ssh_failure_reason() {
  local result
  result="$(get_ssh_result "$1" "$2")"
  printf '%s' "${result#*|}"
}

collect_docker_ssh_failed() {
  local host="$1" reason="$2" status_file="$3" logs_file="$4" configured="${HOST_CONTAINERS[$host]:-}"
  : > "$status_file"
  : > "$logs_file"
  if [[ -n "$configured" ]]; then
    IFS=',' read -ra containers <<< "$configured"
    for container in "${containers[@]}"; do
      container="${container//[[:space:]]/}"
      [[ -z "$container" ]] && continue
      printf 'DOCKER=%s|SSH_FAILED|%s\n' "$container" "$reason" >> "$status_file"
    done
  else
    printf 'DOCKER=%s|SSH_FAILED|%s\n' "discovery" "$reason" >> "$status_file"
  fi
}
