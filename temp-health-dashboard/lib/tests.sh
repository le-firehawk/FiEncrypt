#!/usr/bin/env bash

cache_file() {
  local host="$1" ip="$2" suffix="$3"
  printf '%s/%s.%s' "$CACHE_DIR" "$(safe_key "${host}_${ip}")" "$suffix"
}

get_ping_result() { cat "$(cache_file "$1" "$2" ping)" 2>/dev/null || echo "FAIL|missing"; }
get_ssh_result() { cat "$(cache_file "$1" "$2" ssh)" 2>/dev/null || echo "FAIL|missing"; }
get_systemd_statuses() { cat "$(cache_file "$1" "$2" systemd)" 2>/dev/null || true; }
get_docker_statuses() { cat "$(cache_file "$1" "$2" docker)" 2>/dev/null || true; }
get_docker_logs() { cat "$(cache_file "$1" "$2" docker_logs)" 2>/dev/null || true; }

status_icon() {
  case "$1" in
    PASS|active|healthy|running|no-healthcheck) printf '✓' ;;
    activating|degraded) printf '!' ;;
    *) printf '✗' ;;
  esac
}

status_color() {
  case "$1" in
    PASS|active|healthy|running|no-healthcheck) printf '\033[32m' ;;
    activating|degraded) printf '\033[33m' ;;
    *) printf '\033[31m' ;;
  esac
}

summarize_status_lines() {
  local type="$1"
  awk -F'[=|]' -v type="$type" '
    $1 == type {
      total++
      if ($3 == "active" || $3 == "running" || $4 == "healthy" || $4 == "no-healthcheck") ok++
    }
    END { if (total == 0) print "none"; else printf "%d/%d ok", ok, total }
  '
}
