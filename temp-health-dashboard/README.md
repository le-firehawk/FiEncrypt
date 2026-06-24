# Temporary Health Dashboard TUI

This directory expands the provided shell sketch into a real-results-only Bash dashboard for host health checks. Interactive mode uses an external TUI program (`dialog` preferred, `whiptail` fallback) so terminal drawing does not fight with stderr logs.

## What it checks

- ICMP reachability with `ping` for every configured host/IP.
- SSH connectivity for every host/IP; host-level SSH overrides are intentionally not supported so every address is tested independently.
- Systemd unit status over SSH with `systemctl is-active`, rendered one unit per row. If SSH fails for an IP, systemd rows are marked `SSH_FAILED` with the SSH failure reason instead of attempting remote commands.
- Docker container status over SSH with `docker ps` discovery or configured container names, rendered one container per row. If SSH fails for an IP, Docker rows are marked `SSH_FAILED` with the SSH failure reason.
- Docker logs over SSH with `docker logs --tail`, wrapped to the current screen width.

All collection activity is logged to stderr. Use `--log-file path` to also append those logs to a file.

## Run

```bash
./main.sh --config hosts.conf
```

For CI or non-interactive checks:

```bash
./main.sh --config hosts.conf --once
```

Interactive mode opens a dark-themed external TUI viewer (`dialog` with color by default, `whiptail` fallback). The main screen auto-refreshes on the configured interval; use the Refresh button to refresh immediately. In `dialog`, use the Docker Logs button to open a separate container-log picker/screen; logs are not shown on the main dashboard.

## Config

`hosts.conf` is a Bash config file. Define `HOST_IPS`; optionally define `HOST_SERVICES`, `HOST_CONTAINERS`, `SSH_USER`, `SSH_OPTS`, and `DOCKER_LOG_LINES`. Use `--interval SECONDS` to configure the refresh cycle; ICMP, SSH, systemd, and Docker operations use a timeout one second shorter than the cycle interval, with a minimum of one second.

Define each host once in `HOST_IPS` and put multiple addresses in a comma-separated value, for example `[edge-a]="10.0.0.10,10.0.1.10"`. Repeating the same Bash associative-array key overwrites the earlier value, so only the last assignment survives.

If `HOST_CONTAINERS[host]` is empty or unset, the dashboard discovers containers on that host with `docker ps --format '{{.Names}}'` over SSH.

## Tests

Run the included smoke/unit test suite:

```bash
./tests/run.sh
```
