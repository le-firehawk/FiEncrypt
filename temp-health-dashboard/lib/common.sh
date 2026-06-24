#!/usr/bin/env bash

CACHE_DIR=""

usage() {
  cat <<'USAGE'
Usage: ./main.sh [options]

Options:
  --config FILE       Hosts configuration file (default: ./hosts.conf)
  --interval SECONDS  Refresh interval for live mode (default: 5)
  --once              Render one dashboard frame and exit
  --demo              Use deterministic simulated health data instead of pinging
  -h, --help          Show this help
USAGE
}

init_cache() {
  CACHE_DIR="${TMPDIR:-/tmp}/healthcheck.$$"
  mkdir -p "$CACHE_DIR"
  trap 'rm -rf "$CACHE_DIR"' EXIT
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --config) CONFIG_FILE="${2:?--config requires a file}"; shift 2 ;;
      --interval) REFRESH_INTERVAL="${2:?--interval requires seconds}"; shift 2 ;;
      --once) RUN_ONCE=1; shift ;;
      --demo) DEMO_MODE=1; shift ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
    esac
  done
}

safe_key() {
  printf '%s' "$1" | tr -c '[:alnum:]_.-' '_'
}
