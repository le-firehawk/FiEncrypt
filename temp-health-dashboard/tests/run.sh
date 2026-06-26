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
SSH_PASSWORDS[localhost]="host-secret"
assert_eq "$(ssh_password_for_host localhost)" "host-secret"

# ICMP ping test parsing: localhost should be reachable in normal Linux CI.
ping_one localhost 127.0.0.1 > "$(cache_file localhost 127.0.0.1 ping)"
[[ "$(get_ping_result localhost 127.0.0.1)" == PASS\|* ]] || fail "ICMP ping to 127.0.0.1 did not pass"
fake_bin="$CACHE_DIR/fakebin"
mkdir -p "$fake_bin"
cat > "$fake_bin/ping" <<'FAKEPING'
#!/usr/bin/env bash
count_file="${FAKE_PING_COUNT:?}"
count=0
[[ -f "$count_file" ]] && count="$(cat "$count_file")"
count=$((count + 1))
printf '%s' "$count" > "$count_file"
exit 1
FAKEPING
chmod +x "$fake_bin/ping"
fake_count="$CACHE_DIR/fake-ping-count"
REFRESH_INTERVAL=3 FAKE_PING_COUNT="$fake_count" PATH="$fake_bin:$PATH" ping_one timeout-host 192.0.2.1 > "$(cache_file timeout-host 192.0.2.1 ping)"
assert_eq "$(get_ping_result timeout-host 192.0.2.1)" "FAIL|unreachable after 2 attempts"
assert_eq "$(cat "$fake_count")" "2"
REFRESH_INTERVAL=5

# SSH result accessor and xtrace-safe reason parsing tests.
printf 'PASS|connected\n' > "$(cache_file localhost 127.0.0.1 ssh)"
assert_eq "$(get_ssh_result localhost 127.0.0.1)" "PASS|connected"
printf '+ local target=host command=true\nPermission denied (publickey,password).\n' > "$(cache_file localhost 127.0.0.1 ssh.err)"
assert_eq "$(ssh_error_reason "$(cache_file localhost 127.0.0.1 ssh.err)")" "Permission denied (publickey,password)."
assert_eq "$(ssh_error_reason_text $'+ local target=host command=true\nPermission denied (publickey,password).')" "Permission denied (publickey,password)."
assert_eq "$(ssh_error_reason_text "" 124)" "timeout after 4s"
assert_eq "$(ssh_error_reason_text "" 255)" "connection_failed (ssh exited 255 without stderr)"
ssh_retryable_reason "connection_failed (ssh exited 255 without stderr)" || fail "blank-stderr ssh failure should be retryable"

# Systemd unit status summary test.
cat > "$(cache_file localhost 127.0.0.1 systemd)" <<'DATA'
SYSTEMD=ssh|active|ssh is active and running
SYSTEMD=nginx|failed|nginx is failed; inspect journalctl -u nginx for the failure log
DATA
assert_eq "$(get_systemd_statuses localhost 127.0.0.1 | summarize_status_lines SYSTEMD)" "1/2 ok"
assert_eq "$(systemd_result_message nginx failed)" "nginx is failed; inspect journalctl -u nginx for the failure log"

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
printf 'TIMESYNC=PASS|source=192.0.2.1 synchronized=yes\n' > "$(cache_file localhost 127.0.0.1 timesync)"
printf 'TIMESYNC=SKIPPED|checked via 127.0.0.1\n' > "$(cache_file localhost 127.0.0.2 timesync)"
dashboard="$(build_dashboard_text 96)"
grep -q '127.0.0.2' <<< "$dashboard" || fail "second IP was not rendered"
grep -q 'SSH_FAILED' <<< "$dashboard" || fail "SSH failure did not skip downstream checks"
grep -q 'auth denied' <<< "$dashboard" || fail "SSH failure reason was not rendered"
grep -q 'TIME SYNC / NTP' <<< "$dashboard" || fail "time sync table was not rendered"
grep -q 'source=192.0.2.1' <<< "$dashboard" || fail "NTP source was not rendered"
! grep -q 'DOCKER LOGS' <<< "$dashboard" || fail "docker logs should not render on the main dashboard"
grep -qE 'localhost[[:space:]]+127\.0\.0\.1[[:space:]]+ssh[[:space:]]+active' <<< "$dashboard" || fail "systemd unit row was not rendered"
grep -qE 'localhost[[:space:]]+127\.0\.0\.1[[:space:]]+nginx[[:space:]]+failed' <<< "$dashboard" || fail "second systemd unit row was not rendered"
grep -q 'journalctl' <<< "$dashboard" || fail "systemd templated failure guidance was not rendered"

HOST_TIMESYNC[localhost]=0
collect_timesync_parallel
grep -q 'disabled in HOST_TIMESYNC' "$(cache_file localhost 127.0.0.1 timesync)" || fail "HOST_TIMESYNC disable setting was not honored"
HOST_TIMESYNC[localhost]=1

mark_ssh_password_prompt_cancelled localhost "password prompt cancelled; SSH-dependent checks skipped"
grep -q 'SSH-dependent checks skipped' "$(cache_file localhost 127.0.0.2 ssh)" || fail "SSH cancellation reason was not cached"

echo "all tests passed"
