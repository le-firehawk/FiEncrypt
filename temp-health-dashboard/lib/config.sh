#!/usr/bin/env bash

declare -Ag HOST_IPS=()
declare -Ag HOST_SERVICES=()
declare -Ag HOST_CONTAINERS=()
SSH_USER="${SSH_USER:-}"
SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new}"
DOCKER_LOG_LINES="${DOCKER_LOG_LINES:-40}"
SSH_CHECK_RETRIES="${SSH_CHECK_RETRIES:-1}"

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
  if [[ ! "$SSH_CHECK_RETRIES" =~ ^[0-9]+$ ]]; then
    echo "SSH_CHECK_RETRIES must be a non-negative integer" >&2
    exit 1
  fi
}

ssh_target_for_ip() {
  local ip="$1"
  if [[ -n "$SSH_USER" && "$ip" != *@* ]]; then
    printf '%s@%s' "$SSH_USER" "$ip"
  else
    printf '%s' "$ip"
  fi
}
