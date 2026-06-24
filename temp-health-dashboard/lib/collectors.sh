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
  ssh $SSH_OPTS "$target" "$command"
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
  if ping -c1 -W2 "$ip" > "$tmp" 2>/dev/null; then
    local lat
    lat="$(sed -n 's/.*time=\([0-9.]*\).*/\1/p' "$tmp" | head -1)"
    printf 'PASS|%sms\n' "${lat:-unknown}"
  else
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
          printf 'FAIL|%s\n' "$(head -1 "$CACHE_DIR/${local_key}.ssh.err" 2>/dev/null || echo connection_failed)" > "$CACHE_DIR/${local_key}.ssh"
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
        IFS=',' read -ra services <<< "${HOST_SERVICES[$host]:-}"
        for service in "${services[@]}"; do
          service="${service//[[:space:]]/}"
          [[ -z "$service" ]] && continue
          log_event INFO "systemd check host=$host service=$service"
          if state="$(run_ssh "$target" "systemctl is-active '$service'" 2>/dev/null)"; then
            printf 'SYSTEMD=%s|%s\n' "$service" "$state" >> "$CACHE_DIR/${local_key}.systemd"
          else
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
    printf 'DOCKER=%s|%s|%s\n' "$container" "$state" "$health" >> "$status_file"
    logs="$(run_ssh "$target" "docker logs --tail '$DOCKER_LOG_LINES' '$container' 2>&1" 2>/dev/null || true)"
    {
      printf '===== %s =====\n' "$container"
      printf '%s\n' "$logs"
    } >> "$logs_file"
  done
}
