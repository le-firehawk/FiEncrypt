# Temporary Health Dashboard TUI

This directory expands the provided shell sketch into a real-results-only Bash dashboard for host health checks. Interactive mode uses an external TUI program (`dialog` preferred, `whiptail` fallback) so terminal drawing does not fight with stderr logs.

## What it checks

- ICMP reachability with `ping` for every configured host/IP.
- SSH connectivity for every host/IP; host-level SSH overrides are intentionally not supported so every address is tested independently.
- Systemd unit status and recent journal logs over SSH with `systemctl is-active`, `systemctl is-enabled`, and `journalctl`, rendered one unit per row with qualified states such as `running/enabled`, `stopped/disabled`, or `failed/enabled`. For hosts with multiple IPs, generic SSH-backed checks run on the first SSH-successful IP and later IPs are marked `SKIPPED`; if an earlier IP does not yield an SSH result, the next IP is tried.
- Docker container status and recent logs over SSH with `docker ps`, `docker inspect`, and `docker logs`, rendered one container per row. If SSH fails for every IP, Docker rows are marked `SSH_FAILED` with the SSH failure reason.
- Time synchronization health over SSH, including a per-host NTP summary in the dashboard and a separate NTP Sources submenu for every source reported by `chronyc`, `ntpq`, or `timedatectl`.
- Docker logs over SSH with `docker logs --tail`, wrapped to the current screen width.

All collection activity is logged to stderr. Use `--log-file path` to also append those logs to a file. When SSH checks fail, interactive mode offers a password-auth popup per host; if `sshpass` is installed and a password is entered, that same host password is reused for every configured IP and SSH-backed check for the host during the run. SSH commands explicitly disable OpenSSH askpass helpers; password retries use `sshpass -e` with public-key auth disabled so GUI askpass tools such as `ksshaskpass` cannot steal the prompt.

## Run

```bash
./main.sh --config hosts.conf
```

For CI or non-interactive checks:

```bash
./main.sh --config hosts.conf --once
```

Interactive mode opens a dark-themed external TUI viewer (`dialog` with color by default, `whiptail` fallback). If neither package is installed, the tool warns and falls back to CLI stdin/stdout controls (`r` refresh, `q` quit). The first run and every manual refresh show a running-checks screen with the active collection stage before the updated dashboard is rendered. The main menu shows a summary preview above simple menu choices and includes a scrollable Summary view for the full result output, `Refresh` to re-run host tests, `Recheck` to re-run checks and tests, an NTP Sources browser, structured Systemd/Docker submenus (`service -> host -> unit/container -> operation`) for row actions such as realtime logs, start, stop, and restart, and optional Host Streams (`host -> stream URL`) entries. Missing, skipped, or SSH-failed Docker containers/systemd units are shown in the summary but omitted from operation submenus.

## Config

`hosts.conf` is a Bash config file. Define `HOST_IPS`; optionally define `HOST_SERVICES`, `HOST_CONTAINERS`, `HOST_TIMESYNC`, `HOSTS_VIA`, `HOST_STREAMS`, `SSH_USER`, `SUDO_USER`, `SSH_OPTS`, `SSH_CHECK_RETRIES`, and `DOCKER_LOG_LINES`. Use `--interval SECONDS` to configure operation timeouts; ICMP performs one-second ping attempts using a count of `interval - 1` attempts, while SSH, systemd, Docker, and time-sync operations use a timeout one second shorter than the interval, with a minimum of one second. `HOST_TIMESYNC[host]="1"` enables the NTP/time-sync check for that host and `0`, `no`, `false`, or `disabled` skips it. `SSH_CHECK_RETRIES` defaults to `1` and only retries transient SSH transport failures such as blank-stderr exits and timeouts; authentication failures are not retried unless the interactive password retry path is used.

Define each host once in `HOST_IPS` and put multiple addresses in a comma-separated value, for example `[edge-a]="10.0.0.10,10.0.1.10"`. Repeating the same Bash associative-array key overwrites the earlier value, so only the last assignment survives.

If `HOST_CONTAINERS[host]` is empty or unset, the dashboard discovers containers on that host with `docker ps --format '{{.Names}}'` over SSH.

`HOSTS_VIA[host]="jump-a,jump-b"` adds OpenSSH `ProxyJump` routing for that host. Jump hosts must also exist in `HOST_IPS`, and nested routes are expanded, so if `jump-b` itself has `HOSTS_VIA[jump-b]="bastion"`, connections to `host` go through `jump-a,bastion,jump-b`.

Docker actions run `docker` directly as the SSH user. Systemd start/stop/restart actions run through `sudo systemctl`; `SUDO_USER` defaults to `SSH_USER` and is fixed by `hosts.conf`. The TUI prompts once per host for the sudo password before the first systemd action or systemd realtime log stream and stores it separately from SSH passwords for the current run; canceling the prompt attempts `sudo -n` without a password. Action failures and successes are shown in popups, successful Docker/Systemd actions immediately refresh that host's cached rows, and authentication failures clear cached passwords so the next attempt can prompt again.

`HOST_STREAMS[host]="url1,url2"` adds media streams to the Host Streams menu. Selecting a stream launches `ffplay`; for HTTP(S)/RTSP URLs the tool opens an SSH local-forward through the host's configured `HOSTS_VIA` chain before rewriting the URL to the local tunnel, then reports if `ffplay` exits immediately.

## Tests

Run the included smoke/unit test suite:

```bash
./tests/run.sh
```
