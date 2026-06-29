#!/usr/bin/env bash

cache_file() { printf '%s/%s.%s' "$CACHE_DIR" "$(safe_key "$1_$2")" "$3"; }
get_ping_result() { cat "$(cache_file "$1" "$2" ping)" 2>/dev/null || echo "FAIL|missing"; }
get_ssh_result() { cat "$(cache_file "$1" "$2" ssh)" 2>/dev/null || echo "FAIL|missing"; }
get_systemd_statuses() { cat "$(cache_file "$1" "$2" systemd)" 2>/dev/null || true; }
get_systemd_logs() { cat "$(cache_file "$1" "$2" systemd_logs)" 2>/dev/null || true; }
get_docker_statuses() { cat "$(cache_file "$1" "$2" docker)" 2>/dev/null || true; }
get_docker_logs() { cat "$(cache_file "$1" "$2" docker_logs)" 2>/dev/null || true; }
get_timesync_statuses() { cat "$(cache_file "$1" "$2" timesync)" 2>/dev/null || true; }
get_timesync_status() { get_timesync_statuses "$1" "$2" | awk -F'=' '$1 == "TIMESYNC" {print; found=1; exit} END {if (!found) print "TIMESYNC=missing|no result"}'; }

summarize_status_lines() {
  local type="$1"
  awk -F'[=|]' -v type="$type" '$1 == type { total++; if ($3 == "active" || $3 == "running" || $4 == "healthy" || $4 == "no-healthcheck") ok++ } END { if (!total) print "none"; else printf "%d/%d ok", ok, total }'
}
