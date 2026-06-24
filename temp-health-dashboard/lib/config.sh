#!/usr/bin/env bash

declare -Ag HOST_IPS=()
declare -Ag HOST_SSH_TARGETS=()
declare -Ag HOST_SERVICES=()
declare -Ag HOST_CONTAINERS=()
SSH_USER="${SSH_USER:-}"
SSH_OPTS="${SSH_OPTS:--o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new}"
DOCKER_LOG_LINES="${DOCKER_LOG_LINES:-40}"

load_config() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "Missing config file: $file" >&2
    exit 1
  fi
  # shellcheck source=/dev/null
  source "$file"
  if [[ ${#HOST_IPS[@]} -eq 0 ]]; then
    echo "Config must define HOST_IPS associative array" >&2
    exit 1
  fi
}

ssh_target_for() {
  local host="$1" ip="$2" target
  target="${HOST_SSH_TARGETS[$host]:-$ip}"
  if [[ -n "$SSH_USER" && "$target" != *@* ]]; then
    printf '%s@%s' "$SSH_USER" "$target"
  else
    printf '%s' "$target"
  fi
}
