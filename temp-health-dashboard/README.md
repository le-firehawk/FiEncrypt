# Temporary Health Dashboard TUI

This directory expands the provided shell sketch into a real-results-only Bash dashboard for host health checks. Interactive mode uses an external TUI program (`dialog` preferred, `whiptail` fallback) so terminal drawing does not fight with stderr logs.

## What it checks

- ICMP reachability with `ping` for every configured host/IP.
- SSH connectivity for every host/IP; host-level SSH overrides are intentionally not supported so every address is tested independently.
- Systemd unit status over SSH with `systemctl is-active`, rendered one unit per row with state-specific guidance such as active, inactive, failed, activating, or unknown. For hosts with multiple IPs, generic SSH-backed checks run on the first SSH-successful IP and later IPs are marked `SKIPPED`; if an earlier IP does not yield an SSH result, the next IP is tried.
- Docker container status over SSH with `docker ps` discovery or configured container names, rendered one container per row. If SSH fails for every IP, Docker rows are marked `SSH_FAILED` with the SSH failure reason.
- Time synchronization health over SSH, including NTP synchronization status and the best available NTP source from `chronyc` or `ntpq`.
- Docker logs over SSH with `docker logs --tail`, wrapped to the current screen width.

All collection activity is logged to stderr. Use `--log-file path` to also append those logs to a file. When SSH checks fail, interactive mode offers a password-auth popup per host; if `sshpass` is installed and a password is entered, that same host password is reused for every configured IP and SSH-backed check for the host during the run. A persistent loading gauge stays visible while SSH checks are retried for the current cycle using `sshpass -d` so the password is provided directly to sshpass; the password retry path leaves stdin available for sshpass and disables OpenSSH askpass helpers so GUI key-passphrase prompts cannot steal control before sshpass handles the password prompt. If the prompt is cancelled or `sshpass` is unavailable, SSH-dependent checks are skipped with that reason instead of repeatedly prompting.

## Run

```bash
./main.sh --config hosts.conf
```

For CI or non-interactive checks:

```bash
./main.sh --config hosts.conf --once
```

Interactive mode opens a dark-themed external TUI viewer (`dialog` with color by default, `whiptail` fallback). If neither package is installed, the tool warns and falls back to CLI stdin/stdout controls (`r` refresh, `l` logs, `q` quit). The first run and every manual refresh show a running-checks screen with the active collection stage before the updated dashboard is rendered. The main screen uses a navigable action menu; choose `Refresh now`, `Docker logs`, or `q Quit`. In `dialog`, use the Docker Logs button to open a separate container-log picker/screen; logs are not shown on the main dashboard.

## Config

`hosts.conf` is a Bash config file. Define `HOST_IPS`; optionally define `HOST_SERVICES`, `HOST_CONTAINERS`, `HOST_TIMESYNC`, `SSH_USER`, `SSH_OPTS`, `SSH_CHECK_RETRIES`, and `DOCKER_LOG_LINES`. Use `--interval SECONDS` to configure operation timeouts; ICMP, SSH, systemd, Docker, and time-sync operations use a timeout one second shorter than the interval, with a minimum of one second. `HOST_TIMESYNC[host]="1"` enables the NTP/time-sync check for that host and `0`, `no`, `false`, or `disabled` skips it. `SSH_CHECK_RETRIES` defaults to `1` and only retries transient SSH transport failures such as blank-stderr exits and timeouts; authentication failures are not retried unless the interactive password retry path is used.

Define each host once in `HOST_IPS` and put multiple addresses in a comma-separated value, for example `[edge-a]="10.0.0.10,10.0.1.10"`. Repeating the same Bash associative-array key overwrites the earlier value, so only the last assignment survives.

If `HOST_CONTAINERS[host]` is empty or unset, the dashboard discovers containers on that host with `docker ps --format '{{.Names}}'` over SSH.

## Tests

Run the included smoke/unit test suite:

```bash
./tests/run.sh
```
