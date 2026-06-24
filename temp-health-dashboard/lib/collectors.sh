#!/usr/bin/env bash

clear_cycle_cache() {
  mkdir -p "$CACHE_DIR"
  rm -f "$CACHE_DIR"/*
}

collect_ping_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      IFS=',' read -ra ips <<< "${HOST_IPS[$host]}"
      for ip in "${ips[@]}"; do
        ip="${ip//[[:space:]]/}"
        [[ -z "$ip" ]] && continue
        local_key="$(safe_key "${host}_${ip}")"
        if [[ "$DEMO_MODE" -eq 1 ]]; then
          simulate_ping "$host" "$ip" > "$CACHE_DIR/${local_key}.ping"
        else
          ping_one "$host" "$ip" > "$CACHE_DIR/${local_key}.ping"
        fi
      done
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

simulate_ping() {
  local host="$1" ip="$2" seed latency
  seed=$(cksum <<< "${host}${ip}" | awk '{print $1}')
  if (( seed % 11 == 0 )); then
    printf 'FAIL|timeout\n'
  else
    latency=$(( (seed % 90) + 8 ))
    printf 'PASS|%sms\n' "$latency"
  fi
}

collect_snapshots_parallel() {
  for host in "${!HOST_IPS[@]}"; do
    (
      IFS=',' read -ra ips <<< "${HOST_IPS[$host]}"
      for ip in "${ips[@]}"; do
        ip="${ip//[[:space:]]/}"
        [[ -z "$ip" ]] && continue
        local_key="$(safe_key "${host}_${ip}")"
        if [[ "$DEMO_MODE" -eq 1 ]]; then
          simulate_snapshot "$host" "$ip" > "$CACHE_DIR/${local_key}.snapshot"
        else
          local_snapshot "$host" "$ip" > "$CACHE_DIR/${local_key}.snapshot"
        fi
      done
    ) &
  done
  wait
}

local_snapshot() {
  local host="$1"
  printf 'BOOTSTRAP=PASS\n'
  emit_containers "$host"
  emit_services "$host"
}

simulate_snapshot() {
  local host="$1" ip="$2" seed
  seed=$(cksum <<< "${host}${ip}" | awk '{print $1}')
  (( seed % 7 == 0 )) && printf 'BOOTSTRAP=WARN\n' || printf 'BOOTSTRAP=PASS\n'
  emit_containers "$host" "$seed"
  emit_services "$host" "$seed"
}

emit_containers() {
  local host="$1" seed="${2:-1}" list="${HOST_CONTAINERS[$host]:-api,worker,db}"
  IFS=',' read -ra containers <<< "$list"
  for container in "${containers[@]}"; do
    container="${container//[[:space:]]/}"
    [[ -z "$container" ]] && continue
    if (( seed % 13 == 0 )); then
      printf 'DOCKER=%s|running|unhealthy\n' "$container"
    else
      printf 'DOCKER=%s|running|healthy\n' "$container"
    fi
  done
}

emit_services() {
  local host="$1" seed="${2:-1}" list="${HOST_SERVICES[$host]:-ssh,cron}"
  IFS=',' read -ra services <<< "$list"
  for service in "${services[@]}"; do
    service="${service//[[:space:]]/}"
    [[ -z "$service" ]] && continue
    if (( seed % 17 == 0 )); then
      printf 'SYSTEMD=%s|failed\n' "$service"
    else
      printf 'SYSTEMD=%s|active\n' "$service"
    fi
  done
}
