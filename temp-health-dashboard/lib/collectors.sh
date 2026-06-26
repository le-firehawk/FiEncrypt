#!/usr/bin/env bash

host_ips() {
  local host="$1"
  IFS=',' read -ra ips <<< "${HOST_IPS[$host]}"
  printf '%s\n' "${ips[@]}" | sed 's/[[:space:]]//g' | sed '/^$/d'
}

clear_cycle_cache() { mkdir -p "$CACHE_DIR"; rm -f "$CACHE_DIR"/*; }

collect_all() {
  clear_cycle_cache
  collect_ping_parallel
  collect_ssh_parallel
  collect_systemd_parallel
  collect_docker_parallel
  collect_timesync_parallel
}

ping_one() {
  local host="$1" ip="$2" tmp timeout_s lat
  tmp="$(cache_file "$host" "$ip" ping.raw)"
  timeout_s="$(operation_timeout)"
  if ping -n -c1 -W"$timeout_s" "$ip" > "$tmp" 2>/dev/null; then
    lat="$(sed -n 's/.*time=\([0-9.]*\).*/\1/p' "$tmp" | head -1)"
    printf 'PASS|%sms\n' "${lat:-unknown}"
  else
    log_event WARN "icmp ping failed host=$host ip=$ip timeout=${timeout_s}s"
    printf 'FAIL|unreachable\n'
  fi
  rm -f "$tmp"
}

collect_ping_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do
    (
      local ip
      while IFS= read -r ip; do
        log_event INFO "icmp ping host=$host ip=$ip"
        render_loading "ICMP $host $ip"
        ping_one "$host" "$ip" > "$(cache_file "$host" "$ip" ping)"
      done < <(host_ips "$host")
    ) &
  done
  wait
}

ssh_password_for_host() {
  local host="$1"
  [[ -n "${SSH_PASSWORDS[$host]:-}" ]] && printf '%s' "${SSH_PASSWORDS[$host]}" || printf '%s' "${SSH_PASSWORD:-}"
}

run_ssh() {
  local host="$1" target="$2" command="$3" password timeout_s
  password="$(ssh_password_for_host "$host")"
  timeout_s="$(operation_timeout)"
  if [[ -n "$password" ]] && command -v sshpass >/dev/null 2>&1; then
    SSHPASS="$password" timeout "${timeout_s}s" sshpass -e ssh -T $SSH_OPTS -o BatchMode=no -o NumberOfPasswordPrompts=1 -o ConnectTimeout="$timeout_s" "$target" "$command"
  else
    timeout "${timeout_s}s" ssh -n -T $SSH_OPTS -o BatchMode=yes -o ConnectTimeout="$timeout_s" "$target" "$command"
  fi
}

ssh_error_reason_text() {
  local output="$1" status="${2:-}"
  awk 'NF && $0 !~ /^\+/ { print; found=1; exit } END { if (!found) printf "%s", "connection_failed" }' <<< "$output"
  [[ -n "$status" && -z "$output" && "$status" == 124 ]] && printf 'timeout after %ss' "$(operation_timeout)"
  return 0
}

collect_ssh_for_host() {
  local host="$1" ip key target output status reason attempt max_attempts
  while IFS= read -r ip; do
    key="$(cache_file "$host" "$ip" ssh)"
    target="$(ssh_target_for_ip "$ip")"
    max_attempts=$((SSH_CHECK_RETRIES + 1))
    for ((attempt=1; attempt<=max_attempts; attempt++)); do
      if output="$(run_ssh "$host" "$target" true 2>&1)"; then
        : > "$(cache_file "$host" "$ip" ssh.err)"
        printf 'PASS|connected\n' > "$key"
        break
      fi
      status=$?
      reason="$(ssh_error_reason_text "$output" "$status")"
      printf '%s\n' "$output" > "$(cache_file "$host" "$ip" ssh.err)"
      printf 'FAIL|%s\n' "$reason" > "$key"
    done
  done < <(host_ips "$host")
}

collect_ssh_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do collect_ssh_for_host "$host" & done
  wait
}

ssh_ok_ip() {
  local host="$1" ip result
  while IFS= read -r ip; do
    result="$(get_ssh_result "$host" "$ip")"
    [[ "${result%%|*}" == PASS ]] && { printf '%s' "$ip"; return 0; }
  done < <(host_ips "$host")
  return 1
}

ssh_failed_reason() { local r; r="$(get_ssh_result "$1" "$2")"; printf '%s' "${r#*|}"; }

systemd_result_message() {
  case "$2" in
    active) printf '%s is active and running' "$1" ;;
    failed) printf '%s is failed; inspect journalctl -u %s' "$1" "$1" ;;
    inactive) printf '%s is inactive' "$1" ;;
    *) printf '%s returned systemd state %s' "$1" "$2" ;;
  esac
}

collect_systemd_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do
    (
      local selected ip service state reason target
      selected="$(ssh_ok_ip "$host" || true)"
      while IFS= read -r ip; do
        : > "$(cache_file "$host" "$ip" systemd)"
        IFS=',' read -ra services <<< "${HOST_SERVICES[$host]:-}"
        for service in "${services[@]}"; do
          service="${service//[[:space:]]/}"; [[ -z "$service" ]] && continue
          if [[ -z "$selected" || "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" != PASS ]]; then
            reason="$(ssh_failed_reason "$host" "$ip")"
            printf 'SYSTEMD=%s|SSH_FAILED|%s\n' "$service" "$reason" >> "$(cache_file "$host" "$ip" systemd)"
          elif [[ "$ip" != "$selected" ]]; then
            printf 'SYSTEMD=%s|SKIPPED|checked via %s\n' "$service" "$selected" >> "$(cache_file "$host" "$ip" systemd)"
          else
            target="$(ssh_target_for_ip "$ip")"
            state="$(run_ssh "$host" "$target" "systemctl is-active '$service' 2>/dev/null || true" 2>/dev/null || true)"
            [[ -z "$state" ]] && state=unknown
            printf 'SYSTEMD=%s|%s|%s\n' "$service" "$state" "$(systemd_result_message "$service" "$state")" >> "$(cache_file "$host" "$ip" systemd)"
          fi
        done
      done < <(host_ips "$host")
    ) &
  done
  wait
}

collect_docker_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do
    (
      local selected ip reason target names container inspect state health logs_file status_file
      selected="$(ssh_ok_ip "$host" || true)"
      while IFS= read -r ip; do
        status_file="$(cache_file "$host" "$ip" docker)"; logs_file="$(cache_file "$host" "$ip" docker_logs)"
        : > "$status_file"; : > "$logs_file"
        if [[ -z "$selected" || "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" != PASS ]]; then
          reason="$(ssh_failed_reason "$host" "$ip")"
          printf 'DOCKER=discovery|SSH_FAILED|%s\n' "$reason" > "$status_file"
          continue
        fi
        [[ "$ip" != "$selected" ]] && { printf 'DOCKER=generic|SKIPPED|checked via %s\n' "$selected" > "$status_file"; continue; }
        target="$(ssh_target_for_ip "$ip")"
        if [[ -n "${HOST_CONTAINERS[$host]:-}" ]]; then IFS=',' read -ra names <<< "${HOST_CONTAINERS[$host]}"; else mapfile -t names < <(run_ssh "$host" "$target" "docker ps --format '{{.Names}}'" 2>/dev/null || true); fi
        for container in "${names[@]}"; do
          container="${container//[[:space:]]/}"; [[ -z "$container" ]] && continue
          inspect="$(run_ssh "$host" "$target" "docker inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' '$container'" 2>/dev/null || true)"
          state="${inspect%%|*}"; health="${inspect#*|}"; [[ -z "$inspect" || "$state" == "$inspect" ]] && { state=missing; health=unknown; }
          printf 'DOCKER=%s|%s|%s\n' "$container" "$state" "$health" >> "$status_file"
          { printf '===== %s =====\n' "$container"; run_ssh "$host" "$target" "docker logs --tail '$DOCKER_LOG_LINES' '$container' 2>&1" 2>/dev/null || true; } >> "$logs_file"
        done
      done < <(host_ips "$host")
    ) &
  done
  wait
}

collect_timesync_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do
    (
      local selected ip target sync source reason
      selected="$(ssh_ok_ip "$host" || true)"
      while IFS= read -r ip; do
        if [[ "${HOST_TIMESYNC[$host]:-1}" =~ ^(0|no|false|disabled)$ ]]; then printf 'TIMESYNC=SKIPPED|disabled in HOST_TIMESYNC\n' > "$(cache_file "$host" "$ip" timesync)"; continue; fi
        if [[ -z "$selected" || "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" != PASS ]]; then reason="$(ssh_failed_reason "$host" "$ip")"; printf 'TIMESYNC=SSH_FAILED|%s\n' "$reason" > "$(cache_file "$host" "$ip" timesync)"; continue; fi
        [[ "$ip" != "$selected" ]] && { printf 'TIMESYNC=SKIPPED|checked via %s\n' "$selected" > "$(cache_file "$host" "$ip" timesync)"; continue; }
        target="$(ssh_target_for_ip "$ip")"
        sync="$(run_ssh "$host" "$target" "timedatectl show -p NTPSynchronized --value 2>/dev/null || true" 2>/dev/null || true)"
        source="$(run_ssh "$host" "$target" "chronyc -n sources 2>/dev/null | awk '/^[\\^=][*+]/ {print \\$2; exit}'" 2>/dev/null || true)"
        [[ -z "$source" ]] && source=unknown
        [[ "$sync" == yes ]] && printf 'TIMESYNC=PASS|source=%s synchronized=yes\n' "$source" > "$(cache_file "$host" "$ip" timesync)" || printf 'TIMESYNC=FAIL|source=%s synchronized=%s\n' "$source" "${sync:-unknown}" > "$(cache_file "$host" "$ip" timesync)"
      done < <(host_ips "$host")
    ) &
  done
  wait
}
