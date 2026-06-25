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
REFRESH_NOW=0
SUPPRESS_STDERR_LOGS=0

parse_args "$@"
load_config "$CONFIG_FILE"
init_cache
require_tui_or_once
[[ "$RUN_ONCE" -eq 0 ]] && SUPPRESS_STDERR_LOGS=1
trap 'printf "\nExiting health dashboard.\n" >&2; exit 130' INT TERM
log_event INFO "starting health dashboard config=$CONFIG_FILE interval=${REFRESH_INTERVAL}s once=$RUN_ONCE"

while true; do
  log_event INFO "starting collection cycle"
  collect_dashboard_cycle
  REFRESH_NOW=0
  render_dashboard
  log_event INFO "finished collection cycle"
  [[ "$RUN_ONCE" -eq 1 ]] && break
  [[ "$REFRESH_NOW" -eq 1 ]] && continue
  sleep "$REFRESH_INTERVAL"
done
