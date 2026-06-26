#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"
# shellcheck source=lib/config.sh
source "$SCRIPT_DIR/lib/config.sh"
# shellcheck source=lib/tests.sh
source "$SCRIPT_DIR/lib/tests.sh"
# shellcheck source=lib/collectors.sh
source "$SCRIPT_DIR/lib/collectors.sh"
# shellcheck source=lib/tui.sh
source "$SCRIPT_DIR/lib/tui.sh"

CONFIG_FILE="$SCRIPT_DIR/hosts.conf"
REFRESH_INTERVAL=5
RUN_ONCE=0
SUPPRESS_STDERR_LOGS=0

parse_args "$@"
load_config "$CONFIG_FILE"
init_cache
[[ "$RUN_ONCE" -eq 0 ]] && SUPPRESS_STDERR_LOGS=1
trap 'printf "\nExiting health dashboard.\n" >&2; exit 130' INT TERM

while true; do
  clear_cycle_cache
  loading_begin
  render_loading "Running ICMP checks..." 15
  collect_ping_parallel
  render_loading "Running SSH checks..." 35
  collect_ssh_parallel
  loading_end
  maybe_prompt_for_ssh_password
  loading_begin
  render_loading "Running systemd checks..." 55
  collect_systemd_parallel
  render_loading "Running Docker checks..." 75
  collect_docker_parallel
  render_loading "Running NTP/time-sync checks..." 90
  collect_timesync_parallel
  render_loading "Rendering dashboard..." 98
  loading_end
  render_dashboard
  [[ "$RUN_ONCE" -eq 1 ]] && break
  sleep "$REFRESH_INTERVAL" || true
done
