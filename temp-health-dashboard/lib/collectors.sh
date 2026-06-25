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

run_ssh() {
  local target="$1" command="$2"
  # Intentionally split SSH_OPTS so config authors can provide ordinary ssh flags.
  local timeout_s
  timeout_s="$(operation_timeout)"
  if [[ -n "${SSH_PASSWORD:-}" ]] && command -v sshpass >/dev/null 2>&1; then
    if command -v timeout >/dev/null 2>&1; then
      timeout "${timeout_s}s" sshpass -p "$SSH_PASSWORD" ssh $SSH_OPTS -o NumberOfPasswordPrompts=1 -o BatchMode=no -o PreferredAuthentications=password,keyboard-interactive -o ConnectTimeout="$timeout_s" "$target" "$command"
    else
      sshpass -p "$SSH_PASSWORD" ssh $SSH_OPTS -o NumberOfPasswordPrompts=1 -o BatchMode=no -o PreferredAuthentications=password,keyboard-interactive -o ConnectTimeout="$timeout_s" "$target" "$command"
    fi
  elif command -v timeout >/dev/null 2>&1; then
    timeout "${timeout_s}s" ssh -o BatchMode=yes -o ConnectTimeout="$timeout_s" $SSH_OPTS "$target" "$command"
  else
    ssh -o BatchMode=yes -o ConnectTimeout="$timeout_s" $SSH_OPTS "$target" "$command"
  fi
}

collect_ping_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      while IFS= read -r ip; do
        local_key="$(safe_key "${host}_${ip}")"
        log_event INFO "icmp ping host=$host ip=$ip"
        ping_one "$host" "$ip" > "$CACHE_DIR/${local_key}.ping"
      done < <(host_ips "$host")
    ) &
  done
  wait
}

ping_one() {
  local host="$1" ip="$2" tmp
  tmp="$CACHE_DIR/$(safe_key "${host}_${ip}").ping.raw"
  if ping -c1 -W"$(operation_timeout)" "$ip" > "$tmp" 2>/dev/null; then
    local lat
    lat="$(sed -n 's/.*time=\([0-9.]*\).*/\1/p' "$tmp" | head -1)"
    printf 'PASS|%sms\n' "${lat:-unknown}"
  else
    log_event WARN "icmp ping failed host=$host ip=$ip"
    printf 'FAIL|unreachable\n'
  fi
  rm -f "$tmp"
}

collect_ssh_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      while IFS= read -r ip; do
        local_key="$(safe_key "${host}_${ip}")"
        target="$(ssh_target_for_ip "$ip")"
        log_event INFO "ssh check host=$host ip=$ip target=$target"
        if run_ssh "$target" 'printf ok' >/dev/null 2>"$CACHE_DIR/${local_key}.ssh.err"; then
          printf 'PASS|connected\n' > "$CACHE_DIR/${local_key}.ssh"
        else
          reason="$(head -1 "$CACHE_DIR/${local_key}.ssh.err" 2>/dev/null || echo connection_failed)"
          log_event WARN "ssh check failed host=$host ip=$ip target=$target reason=$reason"
          printf 'FAIL|%s\n' "$reason" > "$CACHE_DIR/${local_key}.ssh"
        fi
      done < <(host_ips "$host")
    ) &
  done
  wait
}

collect_systemd_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      while IFS= read -r ip; do
        local_key="$(safe_key "${host}_${ip}")"
        target="$(ssh_target_for_ip "$ip")"
        : > "$CACHE_DIR/${local_key}.systemd"
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
          if state="$(run_ssh "$target" "systemctl is-active '$service'" 2>/dev/null)"; then
            printf 'SYSTEMD=%s|%s\n' "$service" "$state" >> "$CACHE_DIR/${local_key}.systemd"
          else
            log_event WARN "systemd check failed host=$host ip=$ip service=$service"
            printf 'SYSTEMD=%s|failed\n' "$service" >> "$CACHE_DIR/${local_key}.systemd"
          fi
        done
      done < <(host_ips "$host")
    ) &
  done
  wait
}

collect_docker_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      while IFS= read -r ip; do
        local_key="$(safe_key "${host}_${ip}")"
        target="$(ssh_target_for_ip "$ip")"
        log_event INFO "docker check host=$host ip=$ip"
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
    mapfile -t containers < <(run_ssh "$target" "docker ps --format '{{.Names}}'" 2>/dev/null || true)
  fi
  for container in "${containers[@]}"; do
    container="${container//[[:space:]]/}"
    [[ -z "$container" ]] && continue
    local inspect state health logs
    inspect="$(run_ssh "$target" "docker inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' '$container'" 2>/dev/null || true)"
    state="${inspect%%|*}"
    health="${inspect#*|}"
    [[ -z "$inspect" || "$state" == "$inspect" ]] && { state="missing"; health="unknown"; }
    if [[ "$state" != running || !( "$health" == healthy || "$health" == no-healthcheck ) ]]; then
      log_event WARN "docker check failed host=$host target=$target container=$container state=$state health=$health"
    fi
    printf 'DOCKER=%s|%s|%s\n' "$container" "$state" "$health" >> "$status_file"
    logs="$(run_ssh "$target" "docker logs --tail '$DOCKER_LOG_LINES' '$container' 2>&1" 2>/dev/null || true)"
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
