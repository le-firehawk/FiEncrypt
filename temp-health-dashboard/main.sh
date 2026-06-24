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

parse_args "$@"
load_config "$CONFIG_FILE"
init_cache
require_tui_or_once
log_event INFO "starting health dashboard config=$CONFIG_FILE interval=${REFRESH_INTERVAL}s once=$RUN_ONCE"

while true; do
  log_event INFO "starting collection cycle"
  clear_cycle_cache
  collect_ping_parallel
  collect_ssh_parallel
  collect_systemd_parallel
  collect_docker_parallel
  render_dashboard
  log_event INFO "finished collection cycle"
  [[ "$RUN_ONCE" -eq 1 ]] && break
  sleep "$REFRESH_INTERVAL"
done
