# Temporary Health Dashboard TUI

This directory expands the provided shell sketch into a runnable Bash health dashboard with:

- argument parsing and config validation;
- parallel ping and snapshot collection;
- deterministic `--demo` data for systems without network reachability;
- ANSI TUI rendering when attached to a terminal;
- plain text rendering for CI, logs, and `--once` captures.

Run it from this directory:

```bash
./main.sh --demo --once
```

Use a custom config with `--config path/to/hosts.conf`. The config should define `HOST_IPS` and may define `HOST_SERVICES` and `HOST_CONTAINERS` associative arrays.
