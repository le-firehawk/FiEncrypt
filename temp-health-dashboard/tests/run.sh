#!/usr/bin/env bash
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/lib/common.sh"
source "$ROOT/lib/config.sh"
source "$ROOT/lib/tests.sh"
source "$ROOT/lib/collectors.sh"
source "$ROOT/lib/tui.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }
assert_eq() { [[ "$1" == "$2" ]] || fail "expected '$2' got '$1'"; }

REFRESH_INTERVAL=5
RUN_ONCE=1
init_cache
declare -Ag HOST_IPS=([localhost]="127.0.0.1,127.0.0.2")
assert_eq "$(operation_timeout)" "4"
ntp_source_command | grep -q 'print $2' || fail "NTP source command lost awk field quoting"

ping_one localhost 127.0.0.1 > "$(cache_file localhost 127.0.0.1 ping)"
[[ "$(get_ping_result localhost 127.0.0.1)" == PASS\|* ]] || fail "localhost ping failed"

printf 'PASS|connected\n' > "$(cache_file localhost 127.0.0.1 ssh)"
printf 'FAIL|auth denied\n' > "$(cache_file localhost 127.0.0.2 ssh)"
assert_eq "$(ssh_ok_ip localhost)" "127.0.0.1"

cat > "$(cache_file localhost 127.0.0.1 systemd)" <<'DATA'
SYSTEMD=ssh|active|ssh is active and running
SYSTEMD=nginx|failed|nginx is failed; inspect journalctl -u nginx
DATA
assert_eq "$(get_systemd_statuses localhost 127.0.0.1 | summarize_status_lines SYSTEMD)" "1/2 ok"

cat > "$(cache_file localhost 127.0.0.1 docker)" <<'DATA'
DOCKER=api|running|healthy
DOCKER=worker|exited|unknown
DATA
assert_eq "$(get_docker_statuses localhost 127.0.0.1 | summarize_status_lines DOCKER)" "1/2 ok"
printf '===== api =====\nready\n' > "$(cache_file localhost 127.0.0.1 docker_logs)"
get_docker_logs localhost 127.0.0.1 | grep -q ready || fail "docker logs unreadable"

cat > "$(cache_file localhost 127.0.0.1 timesync)" <<'DATA'
TIMESYNC=PASS|synchronized=yes primary=192.0.2.1
TIMESYNC_SOURCE=192.0.2.1|chrony *
TIMESYNC_SOURCE=192.0.2.2|chrony +
DATA
printf 'TIMESYNC=SKIPPED|checked via 127.0.0.1\n' > "$(cache_file localhost 127.0.0.2 timesync)"
printf 'PASS|1ms\n' > "$(cache_file localhost 127.0.0.2 ping)"
printf 'DOCKER=discovery|SSH_FAILED|auth denied\n' > "$(cache_file localhost 127.0.0.2 docker)"
printf 'SYSTEMD=docker|SSH_FAILED|auth denied\n' > "$(cache_file localhost 127.0.0.2 systemd)"

dashboard="$(build_dashboard_text 100)"
grep -q '127.0.0.2' <<< "$dashboard" || fail "second IP missing"
grep -q 'TIME SYNC / NTP' <<< "$dashboard" || fail "timesync table missing"
grep -q 'primary=192.0.2.1' <<< "$dashboard" || fail "timesync primary missing"
grep -q '192.0.2.2' <<< "$dashboard" || fail "secondary timesync source missing"
grep -q 'journalctl' <<< "$dashboard" || fail "systemd guidance missing"

echo "all tests passed"
