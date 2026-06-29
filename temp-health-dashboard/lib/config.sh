#!/usr/bin/env bash

declare -Ag HOST_IPS=()
declare -Ag HOST_SERVICES=()
declare -Ag HOST_CONTAINERS=()
declare -Ag HOST_TIMESYNC=()
declare -Ag HOSTS_VIA=()
declare -Ag CHECK_SCOPES=([icmp]=per-ip [ssh]=per-ip [systemd]=per-host [docker]=per-host [timesync]=per-host)
SSH_USER="${SSH_USER:-}"
SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new}"
SSH_CHECK_RETRIES="${SSH_CHECK_RETRIES:-1}"
DOCKER_LOG_LINES="${DOCKER_LOG_LINES:-40}"

load_config() {
  local file="$1"
  [[ -f "$file" ]] || { echo "Missing config file: $file" >&2; exit 1; }
  # shellcheck source=/dev/null
  source "$file"
  [[ ${#HOST_IPS[@]} -gt 0 ]] || { echo "Config must define HOST_IPS" >&2; exit 1; }
  [[ "$SSH_CHECK_RETRIES" =~ ^[0-9]+$ ]] || { echo "SSH_CHECK_RETRIES must be a non-negative integer" >&2; exit 1; }
  validate_hosts_via
}

ssh_target_for_ip() {
  [[ -n "$SSH_USER" && "$1" != *@* ]] && printf '%s@%s' "$SSH_USER" "$1" || printf '%s' "$1"
}

validate_hosts_via() {
  local host via
  for host in "${!HOSTS_VIA[@]}"; do
    [[ -n "${HOST_IPS[$host]:-}" ]] || { echo "HOSTS_VIA references unknown host: $host" >&2; exit 1; }
    IFS=',' read -ra vias <<< "${HOSTS_VIA[$host]}"
    for via in "${vias[@]}"; do
      via="${via//[[:space:]]/}"
      [[ -z "$via" ]] && continue
      [[ -n "${HOST_IPS[$via]:-}" ]] || { echo "HOSTS_VIA[$host] references unknown host: $via" >&2; exit 1; }
    done
    ssh_jump_hosts_for_host "$host" >/dev/null || exit 1
  done
}

first_host_ip() { host_ips "$1" | head -1; }

ssh_jump_hosts_for_host() {
  local host="$1" seen="${2:-}" via
  [[ ",$seen," == *",$host,"* ]] && { echo "HOSTS_VIA cycle at $host" >&2; return 1; }
  seen="${seen:+$seen,}$host"
  IFS=',' read -ra vias <<< "${HOSTS_VIA[$host]:-}"
  for via in "${vias[@]}"; do
    via="${via//[[:space:]]/}"
    [[ -z "$via" ]] && continue
    ssh_jump_hosts_for_host "$via" "$seen"
    printf '%s\n' "$via"
  done
}

ssh_proxy_jump_for_host() {
  local host="$1" via ip target out=()
  while IFS= read -r via; do
    [[ -z "$via" ]] && continue
    ip="$(first_host_ip "$via")"
    target="$(ssh_target_for_ip "$ip")"
    out+=("$target")
  done < <(ssh_jump_hosts_for_host "$host")
  ((${#out[@]})) && local IFS=, && printf '%s' "${out[*]}"
}
