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
trap 'cleanup_stream_tunnels; printf "\nExiting health dashboard.\n" >&2; exit 130' INT TERM
trap 'cleanup_stream_tunnels' EXIT

run_checks() {
  clear_cycle_cache
  render_loading "Loading - running health checks..." 50
  if is_check_skipped icmp; then mark_check_skipped icmp; else collect_ping_parallel; fi
  if is_check_skipped ssh; then mark_check_skipped ssh; else collect_ssh_parallel; fi
  maybe_prompt_for_ssh_password
  run_tests
}

run_tests() {
  render_loading "Loading - completing health checks..." 75
  if is_check_skipped systemd; then mark_check_skipped systemd; else collect_systemd_parallel; fi
  if is_check_skipped docker; then mark_check_skipped docker; else collect_docker_parallel; fi
  if is_check_skipped timesync; then mark_check_skipped timesync; else collect_timesync_parallel; fi
}

run_checks
if [[ "$RUN_ONCE" -eq 1 || ! -t 1 ]]; then
  render_dashboard
  exit 0
fi
while true; do
  render_dashboard
  action="$DASHBOARD_ACTION"
  case "$action" in
    quit) break ;;
    refresh) run_tests ;;
    recheck) run_checks ;;
    display|*) : ;;
  esac
done
