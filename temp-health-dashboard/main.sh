#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"
# shellcheck source=lib/config.sh
source "$SCRIPT_DIR/lib/config.sh"
# shellcheck source=lib/collectors.sh
source "$SCRIPT_DIR/lib/collectors.sh"
# shellcheck source=lib/tests.sh
source "$SCRIPT_DIR/lib/tests.sh"
# shellcheck source=lib/tui.sh
source "$SCRIPT_DIR/lib/tui.sh"

CONFIG_FILE="$SCRIPT_DIR/hosts.conf"
REFRESH_INTERVAL=5
RUN_ONCE=0
DEMO_MODE=0

parse_args "$@"
load_config "$CONFIG_FILE"
init_cache

while true; do
  clear_cycle_cache
  collect_ping_parallel
  collect_snapshots_parallel
  render_dashboard
  [[ "$RUN_ONCE" -eq 1 ]] && break
  sleep "$REFRESH_INTERVAL"
done
