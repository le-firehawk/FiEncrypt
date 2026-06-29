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
HOST_IPS[myserver]="192.0.2.50"
HOST_IPS[myhost1]="192.0.2.10"
HOST_IPS[myhost2]="192.0.2.20"
HOST_IPS[myhost]="192.0.2.5"
HOST_CONTAINERS[localhost]="api,worker"
HOST_STREAMS[localhost]="rtsp://camera.local/live,http://media.local/live.m3u8"
HOSTS_VIA[myserver]="myhost1,myhost2"
HOSTS_VIA[myhost2]="myhost"
assert_eq "$(operation_timeout)" "4"
assert_eq "$(ssh_proxy_jump_for_host myserver)" "192.0.2.10,192.0.2.5,192.0.2.20"
validate_hosts_via
SSH_USER=ops
SUDO_USER=admin
assert_eq "$(sudo_target_for_ip 192.0.2.99)" "admin@192.0.2.99"
SUDO_USER="$SSH_USER"
assert_eq "$(sudo_systemctl_command localhost restart ssh)" "sudo -n systemctl 'restart' 'ssh'"
assert_eq "$(sudo_journalctl_command localhost ssh)" "sudo -n journalctl -u 'ssh' -n '40' -f --no-pager"
SUDO_PASSWORDS[localhost]="secret"
[[ "$(sudo_systemctl_command localhost restart ssh)" == *"sudo -S -p '' systemctl 'restart' 'ssh'" ]] || fail "sudo password command not generated"
[[ "$(sudo_journalctl_command localhost ssh)" == *"sudo -S -p '' journalctl -u 'ssh'"* ]] || fail "sudo journal command not generated"
SUDO_USER=admin
captured_target=""
captured_password=""
run_ssh_with_password() { captured_target="$2"; captured_password="$4"; return 0; }
run_systemd_action localhost 127.0.0.1 ssh restart
assert_eq "$captured_target" "admin@127.0.0.1"
assert_eq "$captured_password" "secret"
unset -f run_ssh_with_password
SUDO_USER="$SSH_USER"
unset 'SUDO_PASSWORDS[localhost]'
SKIP_CHECKS="ssh,ntp"
is_check_skipped ssh || fail "ssh skip not detected"
is_check_skipped timesync || fail "ntp skip alias not detected"
! is_check_skipped docker || fail "docker unexpectedly skipped"
SKIP_CHECKS=""
has_configured_docker_containers || fail "configured docker containers not detected"
docker_menu="$(configured_docker_menu_args)"
grep -q "log|localhost|127.0.0.1|api" <<< "$docker_menu" || fail "docker log submenu entries missing"
grep -q "localhost (127.0.0.1) api" <<< "$docker_menu" || fail "docker log submenu label missing"
has_host_streams || fail "host streams not detected"
stream_host_menu_args | grep -q '^localhost$' || fail "stream host menu missing localhost"
stream_url_menu_args localhost | grep -q '^rtsp://camera.local/live$' || fail "stream URL menu missing stream"
fakebin="$(mktemp -d)"
ssh_log="$(mktemp)"
cat > "$fakebin/ssh" <<'FAKE'
#!/usr/bin/env bash
printf '%s\n' "$*" > "$SSH_LOG"
sleep 5
FAKE
ffplay_log="$(mktemp)"
cat > "$fakebin/ffplay" <<'FAKE'
#!/usr/bin/env bash
printf '%s\n' "$*" > "$FFPLAY_LOG"
sleep 2
FAKE
chmod +x "$fakebin"/*
SSH_LOG="$ssh_log" PATH="$fakebin:$PATH" start_stream_tunnel myserver 192.0.2.50 23456 camera.local 554 test_stream
grep -q -- '-J ops@192.0.2.10,ops@192.0.2.5,ops@192.0.2.20' "$ssh_log" || fail "stream tunnel did not include expanded ProxyJump"
grep -q -- 'ExitOnForwardFailure=yes' "$ssh_log" || fail "stream tunnel does not require forward success"
grep -q -- 'BatchMode=yes' "$ssh_log" || fail "stream tunnel can still prompt interactively"
SSH_LOG="$ssh_log" FFPLAY_LOG="$ffplay_log" PATH="$fakebin:$PATH" open_host_stream myserver rtsp://camera.local/live
grep -q 'rtsp://127.0.0.1:' "$ffplay_log" || fail "stream URL was not rewritten to forwarded localhost port"
first_stream_url="$(cat "$ffplay_log")"
SSH_LOG="$ssh_log" FFPLAY_LOG="$ffplay_log" PATH="$fakebin:$PATH" open_host_stream myserver rtsp://camera.local/live
assert_eq "$(cat "$ffplay_log")" "$first_stream_url"
cleanup_stream_tunnels
rm -rf "$fakebin" "$ssh_log" "$ffplay_log"
SKIP_CHECKS="icmp,ssh,systemd,docker,ntp"
skipped_dashboard="$(build_dashboard_text 80)"
! grep -q "ENDPOINTS" <<< "$skipped_dashboard" || fail "skipped endpoint section rendered"
! grep -q "TIME SYNC / NTP" <<< "$skipped_dashboard" || fail "skipped ntp section rendered"
SKIP_CHECKS=""
ntp_source_command | grep -q 'print $2' || fail "NTP source command lost awk field quoting"
fakebin="$(mktemp -d)"
cat > "$fakebin/chronyc" <<'FAKE'
#!/usr/bin/env bash
exit 1
FAKE
cat > "$fakebin/timedatectl" <<'FAKE'
#!/usr/bin/env bash
exit 1
FAKE
cat > "$fakebin/ip" <<'FAKE'
#!/usr/bin/env bash
case "$3" in
  192.0.2.10|192.0.2.11) echo "$3 dev eth0 src 127.0.0.1" ;;
  192.0.2.12) echo "$3 dev eth1 src 127.0.0.2" ;;
  *) exit 1 ;;
esac
FAKE
cat > "$fakebin/ntpq" <<'FAKE'
#!/usr/bin/env bash
cat <<'NTPQ'
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*192.0.2.10      .GPS.            1 u   10   64  377    0.123   -0.010   0.002
+192.0.2.11      192.0.2.10       2 u   12   64  377    0.456    0.020   0.003
 192.0.2.12      192.0.2.10       2 u   14   64  377    0.789    0.030   0.004
NTPQ
FAKE
chmod +x "$fakebin"/*
ntp_parsed="$(PATH="$fakebin:$PATH" bash -c "$(ntp_sources_command)")"
grep -q '^192.0.2.10|ntpq|\*|selected peer' <<< "$ntp_parsed" || fail "ntpq selected peer not parsed"
grep -q '^192.0.2.11|ntpq|+|candidate peer' <<< "$ntp_parsed" || fail "ntpq candidate peer not parsed"
grep -q '^192.0.2.12|ntpq| |reachable peer' <<< "$ntp_parsed" || fail "ntpq unselected peer not parsed"
! grep -q '^remote|' <<< "$ntp_parsed" || fail "ntpq header parsed as source"
rm -rf "$fakebin"

ping_one localhost 127.0.0.1 > "$(cache_file localhost 127.0.0.1 ping)"
[[ "$(get_ping_result localhost 127.0.0.1)" == PASS\|* ]] || fail "localhost ping failed"

printf 'PASS|connected\n' > "$(cache_file localhost 127.0.0.1 ssh)"
printf 'FAIL|auth denied\n' > "$(cache_file localhost 127.0.0.2 ssh)"
assert_eq "$(ssh_ok_ip localhost)" "127.0.0.1"
HOST_IPS[noroute]="203.0.113.10"
printf 'NO_ROUTE|no route to host\n' > "$(cache_file noroute 203.0.113.10 ping)"
run_ssh() { fail "SSH should not run after ICMP no route"; }
collect_ssh_for_host noroute
unset -f run_ssh
assert_eq "$(get_ssh_result noroute 203.0.113.10)" "SKIPPED|ICMP no route to host"

cat > "$(cache_file localhost 127.0.0.1 systemd)" <<'DATA'
SYSTEMD=ssh|running/enabled|ssh is running/enabled
SYSTEMD=nginx|failed/disabled|nginx is failed/disabled; inspect journalctl -u nginx
DATA
assert_eq "$(systemd_state_label active enabled)" "running/enabled"
assert_eq "$(systemd_state_label inactive disabled)" "stopped/disabled"
assert_eq "$(get_systemd_statuses localhost 127.0.0.1 | summarize_status_lines SYSTEMD)" "1/2 ok"
printf 'SYSTEMD=missing-unit|missing|missing\n' >> "$(cache_file localhost 127.0.0.1 systemd)"
systemd_menu="$(systemd_unit_menu_args localhost)"
grep -q '^ssh$' <<< "$systemd_menu" || fail "systemd submenu missing active unit"
! grep -q 'missing-unit' <<< "$systemd_menu" || fail "missing systemd unit should not be actionable"

cat > "$(cache_file localhost 127.0.0.1 docker)" <<'DATA'
DOCKER=api|running|healthy
DOCKER=worker|exited|unknown
DATA
assert_eq "$(get_docker_statuses localhost 127.0.0.1 | summarize_status_lines DOCKER)" "1/2 ok"
printf 'DOCKER=missing-container|missing|unknown\n' >> "$(cache_file localhost 127.0.0.1 docker)"
docker_items="$(docker_container_menu_args localhost)"
grep -q '^api$' <<< "$docker_items" || fail "docker submenu missing running container"
! grep -q 'missing-container' <<< "$docker_items" || fail "missing docker container should not be actionable"
printf '===== api =====\nready\n' > "$(cache_file localhost 127.0.0.1 docker_logs)"
get_docker_logs localhost 127.0.0.1 | grep -q ready || fail "docker logs unreadable"

cat > "$(cache_file localhost 127.0.0.1 timesync)" <<'DATA'
TIMESYNC=PASS|synchronized=yes primary=192.0.2.1
TIMESYNC_SOURCE=192.0.2.1|chrony|*|selected source currently disciplining the clock
TIMESYNC_SOURCE=192.0.2.2|chrony|+|acceptable source combined with the selected source
DATA
cat > "$(cache_file myserver 192.0.2.50 timesync)" <<'DATA'
TIMESYNC=FAIL|synchronized=no primary=unknown; no NTP sources reported
DATA
: > "$(cache_file localhost 127.0.0.2 timesync)"
printf 'PASS|1ms\n' > "$(cache_file localhost 127.0.0.2 ping)"
printf 'DOCKER=discovery|SSH_FAILED|auth denied\n' > "$(cache_file localhost 127.0.0.2 docker)"
printf 'SYSTEMD=docker|SSH_FAILED|auth denied\n' > "$(cache_file localhost 127.0.0.2 systemd)"

dashboard="$(build_dashboard_text 100)"
ntp_detail="$(ntp_sources_text localhost)"
grep -q '127.0.0.2' <<< "$dashboard" || fail "second IP missing"
grep -q 'TIME SYNC / NTP' <<< "$dashboard" || fail "timesync table missing"
grep -q 'primary=192.0.2.1' <<< "$dashboard" || fail "timesync primary missing"
grep -q 'myserver.*synchronized=no' <<< "$dashboard" || fail "second host NTP summary missing"
! grep -q 'acceptable source combined' <<< "$dashboard" || fail "NTP source details should be hidden from summary"
ntp_host_menu_args | grep -q '^myserver$' || fail "NTP sources menu missing second host"
grep -q '192.0.2.2' <<< "$ntp_detail" || fail "secondary timesync source missing from NTP detail"
grep -q 'acceptable source combined' <<< "$ntp_detail" || fail "timesync source detail missing from NTP detail"
grep -q 'journalctl' <<< "$dashboard" || fail "systemd guidance missing"
grep -q 'STATUS       ENABLED' <<< "$dashboard" || fail "systemd enabled column missing"
grep -q 'ssh.*running.*yes' <<< "$dashboard" || fail "systemd enabled value not rendered separately"

echo "all tests passed"
