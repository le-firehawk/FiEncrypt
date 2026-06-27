#!/usr/bin/env bash

declare -Ag HOST_IPS=()
declare -Ag HOST_SERVICES=()
declare -Ag HOST_CONTAINERS=()
declare -Ag HOST_TIMESYNC=()
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
}

ssh_target_for_ip() {
  [[ -n "$SSH_USER" && "$1" != *@* ]] && printf '%s@%s' "$SSH_USER" "$1" || printf '%s' "$1"
}
