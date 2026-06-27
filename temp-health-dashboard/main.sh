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
  if is_check_skipped icmp; then mark_check_skipped icmp; else run_with_loading 5 20 "Running ICMP checks" collect_ping_parallel; fi
  if is_check_skipped ssh; then mark_check_skipped ssh; else run_with_loading 20 40 "Running SSH checks" collect_ssh_parallel; maybe_prompt_for_ssh_password; fi
  if is_check_skipped systemd; then mark_check_skipped systemd; else run_with_loading 40 60 "Running systemd checks" collect_systemd_parallel; fi
  if is_check_skipped docker; then mark_check_skipped docker; else run_with_loading 60 80 "Running Docker checks" collect_docker_parallel; fi
  if is_check_skipped timesync; then mark_check_skipped timesync; else run_with_loading 80 95 "Running NTP/time-sync checks" collect_timesync_parallel; fi
  render_loading "Rendering dashboard..." 98
  render_dashboard
  [[ "$RUN_ONCE" -eq 1 ]] && break
  sleep "$REFRESH_INTERVAL" || true
done
