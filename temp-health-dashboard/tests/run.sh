#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/lib/common.sh"
source "$ROOT/lib/config.sh"
source "$ROOT/lib/collectors.sh"
source "$ROOT/lib/tests.sh"
source "$ROOT/lib/tui.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }
assert_eq() { [[ "$1" == "$2" ]] || fail "expected '$2' got '$1'"; }

CONFIG_FILE="$ROOT/hosts.conf"
REFRESH_INTERVAL=5
RUN_ONCE=1
assert_eq "$(operation_timeout)" "4"
init_cache
declare -Ag HOST_IPS=([localhost]="127.0.0.1,127.0.0.2")

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

# Rendering test: every IP is displayed independently and each systemd unit has its own row.
printf 'PASS|1ms\n' > "$(cache_file localhost 127.0.0.2 ping)"
printf 'FAIL|auth denied\n' > "$(cache_file localhost 127.0.0.2 ssh)"
printf 'SYSTEMD=docker|SSH_FAILED|auth denied\n' > "$(cache_file localhost 127.0.0.2 systemd)"
printf 'DOCKER=discovery|SSH_FAILED|auth denied\n' > "$(cache_file localhost 127.0.0.2 docker)"
dashboard="$(build_dashboard_text 96)"
grep -q '127.0.0.2' <<< "$dashboard" || fail "second IP was not rendered"
grep -q 'SSH_FAILED' <<< "$dashboard" || fail "SSH failure did not skip downstream checks"
grep -q 'auth denied' <<< "$dashboard" || fail "SSH failure reason was not rendered"
! grep -q 'DOCKER LOGS' <<< "$dashboard" || fail "docker logs should not render on the main dashboard"
grep -qE 'localhost[[:space:]]+127\.0\.0\.1[[:space:]]+ssh[[:space:]]+active' <<< "$dashboard" || fail "systemd unit row was not rendered"
grep -qE 'localhost[[:space:]]+127\.0\.0\.1[[:space:]]+nginx[[:space:]]+failed' <<< "$dashboard" || fail "second systemd unit row was not rendered"

mark_ssh_password_prompt_cancelled "password prompt cancelled; SSH-dependent checks skipped"
grep -q 'SSH-dependent checks skipped' "$(cache_file localhost 127.0.0.2 ssh)" || fail "SSH cancellation reason was not cached"

echo "all tests passed"
