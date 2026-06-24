#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/lib/common.sh"
source "$ROOT/lib/config.sh"
source "$ROOT/lib/collectors.sh"
source "$ROOT/lib/tests.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }
assert_eq() { [[ "$1" == "$2" ]] || fail "expected '$2' got '$1'"; }

CONFIG_FILE="$ROOT/hosts.conf"
REFRESH_INTERVAL=5
RUN_ONCE=1
init_cache

# ICMP ping test parsing: localhost should be reachable in normal Linux CI.
ping_one localhost 127.0.0.1 > "$(cache_file localhost 127.0.0.1 ping)"
[[ "$(get_ping_result localhost 127.0.0.1)" == PASS\|* ]] || fail "ICMP ping to 127.0.0.1 did not pass"

# SSH result accessor test.
printf 'PASS|connected\n' > "$(cache_file localhost 127.0.0.1 ssh)"
assert_eq "$(get_ssh_result localhost 127.0.0.1)" "PASS|connected"

# Systemd unit status summary test.
cat > "$(cache_file localhost 127.0.0.1 systemd)" <<'DATA'
SYSTEMD=ssh|active
SYSTEMD=nginx|failed
DATA
assert_eq "$(get_systemd_statuses localhost 127.0.0.1 | summarize_status_lines SYSTEMD)" "1/2 ok"

# Docker container status summary and log viewing test.
cat > "$(cache_file localhost 127.0.0.1 docker)" <<'DATA'
DOCKER=api|running|healthy
DOCKER=worker|exited|unknown
DOCKER=db|running|no-healthcheck
DATA
assert_eq "$(get_docker_statuses localhost 127.0.0.1 | summarize_status_lines DOCKER)" "2/3 ok"
cat > "$(cache_file localhost 127.0.0.1 docker_logs)" <<'DATA'
===== api =====
ready
===== worker =====
crashed
DATA
get_docker_logs localhost 127.0.0.1 | grep -q 'ready' || fail "docker logs were not readable"

echo "all tests passed"
