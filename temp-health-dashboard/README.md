# Temporary Health Dashboard TUI

This directory expands the provided shell sketch into a real-results-only Bash TUI for host health checks.

## What it checks

- ICMP reachability with `ping` for every configured host/IP.
- SSH connectivity for every host/IP.
- Systemd unit status over SSH with `systemctl is-active`.
- Docker container status over SSH with `docker ps` discovery or configured container names.
- Docker logs over SSH with `docker logs --tail`, visible in the TUI with `l` or always printed in `--once` mode.

All collection activity is logged to stderr. Use `--log-file path` to also append those logs to a file.

## Run

```bash
./main.sh --config hosts.conf
```

For CI or non-interactive checks:

```bash
./main.sh --config hosts.conf --once
```

Interactive keys:

- `q`: quit.
- `l`: toggle Docker log display.

## Config

`hosts.conf` is a Bash config file. Define `HOST_IPS`; optionally define `HOST_SSH_TARGETS`, `HOST_SERVICES`, `HOST_CONTAINERS`, `SSH_USER`, `SSH_OPTS`, and `DOCKER_LOG_LINES`.

If `HOST_CONTAINERS[host]` is empty or unset, the dashboard discovers containers on that host with `docker ps --format '{{.Names}}'` over SSH.

## Tests

Run the included smoke/unit test suite:

```bash
./tests/run.sh
```
