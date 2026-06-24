#!/usr/bin/env bash

declare -Ag HOST_IPS=()
declare -Ag HOST_SERVICES=()
declare -Ag HOST_CONTAINERS=()

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
