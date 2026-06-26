#!/usr/bin/env bash

CACHE_DIR=""
LOG_FILE="${LOG_FILE:-}"

usage() {
  cat <<'USAGE'
Usage: ./main.sh [--config FILE] [--interval SECONDS] [--once] [--log-file FILE]
USAGE
}

init_cache() {
  CACHE_DIR="${TMPDIR:-/tmp}/healthcheck.$$"
  mkdir -p "$CACHE_DIR"
  trap 'rm -rf "$CACHE_DIR"' EXIT
}

log_event() {
  local level="$1"; shift
  local line
  line="$(date '+%Y-%m-%dT%H:%M:%S%z') [$level] $*"
  [[ "${SUPPRESS_STDERR_LOGS:-0}" -eq 1 ]] || printf '%s\n' "$line" >&2
  [[ -n "$LOG_FILE" ]] && printf '%s\n' "$line" >> "$LOG_FILE"
  return 0
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --config) CONFIG_FILE="${2:?--config requires a file}"; shift 2 ;;
      --interval) REFRESH_INTERVAL="${2:?--interval requires seconds}"; validate_positive_int "$REFRESH_INTERVAL" "--interval"; shift 2 ;;
      --once) RUN_ONCE=1; shift ;;
      --log-file) LOG_FILE="${2:?--log-file requires a file}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
    esac
  done
}

safe_key() { printf '%s' "$1" | tr -c '[:alnum:]_.-' '_'; }

validate_positive_int() {
  [[ "$1" =~ ^[0-9]+$ && "$1" -gt 0 ]] || { echo "$2 requires a positive integer" >&2; exit 2; }
}

operation_timeout() {
  local interval="${REFRESH_INTERVAL:-5}"
  [[ "$interval" =~ ^[0-9]+$ && "$interval" -gt 1 ]] && printf '%s' "$((interval - 1))" || printf '1'
}
