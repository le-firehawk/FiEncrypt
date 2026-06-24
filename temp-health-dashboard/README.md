# Temporary Health Dashboard TUI

This directory expands the provided shell sketch into a real-results-only Bash dashboard for host health checks. Interactive mode uses an external TUI program (`dialog` preferred, `whiptail` fallback) so terminal drawing does not fight with stderr logs.

## What it checks

- ICMP reachability with `ping` for every configured host/IP.
- SSH connectivity for every host/IP; host-level SSH overrides are intentionally not supported so every address is tested independently.
- Systemd unit status over SSH with `systemctl is-active`, rendered one unit per row.
- Docker container status over SSH with `docker ps` discovery or configured container names, rendered one container per row.
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

Interactive mode opens the external TUI viewer; close it to refresh or quit from the viewer controls.

## Config

`hosts.conf` is a Bash config file. Define `HOST_IPS`; optionally define `HOST_SERVICES`, `HOST_CONTAINERS`, `SSH_USER`, `SSH_OPTS`, and `DOCKER_LOG_LINES`.

If `HOST_CONTAINERS[host]` is empty or unset, the dashboard discovers containers on that host with `docker ps --format '{{.Names}}'` over SSH.

## Tests

Run the included smoke/unit test suite:

```bash
./tests/run.sh
```
