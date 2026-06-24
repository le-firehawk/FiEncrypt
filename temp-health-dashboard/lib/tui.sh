#!/usr/bin/env bash

require_tui_or_once() {
  if [[ "$RUN_ONCE" -eq 0 && ! -t 1 ]]; then
    echo "Interactive TUI mode requires a TTY. Use --once for non-interactive output." >&2
    exit 2
  fi
  if [[ "$RUN_ONCE" -eq 0 ]] && ! command -v dialog >/dev/null 2>&1 && ! command -v whiptail >/dev/null 2>&1; then
    echo "Interactive TUI mode requires external tool 'dialog' or 'whiptail'. Use --once for plain output." >&2
    exit 2
  fi
}

render_dashboard() {
  if [[ "$RUN_ONCE" -eq 1 || ! -t 1 ]]; then
    render_plain_dashboard
  else
    render_external_tui
  fi
}

screen_cols() { tput cols 2>/dev/null || echo 120; }
screen_lines() { tput lines 2>/dev/null || echo 40; }

render_external_tui() {
  local tmp width height status=0 colorize=0
  width="$(screen_cols)"; height="$(screen_lines)"
  tmp="$(mktemp "${TMPDIR:-/tmp}/health-dashboard.XXXXXX")"
  if command -v dialog >/dev/null 2>&1; then
    colorize=1
  fi
  build_dashboard_text "$width" "$colorize" > "$tmp"
  if command -v dialog >/dev/null 2>&1; then
    local dialogrc
    dialogrc="$(write_dark_dialogrc)"
    DIALOGRC="$dialogrc" dialog --colors --clear --backtitle "Health Dashboard" --title "Dark Health Dashboard" --ok-label "Refresh" --extra-button --extra-label "Quit" --textbox "$tmp" "$height" "$width" 2>/dev/tty || status=$?
    rm -f "$dialogrc"
    rm -f "$tmp"
    [[ "$status" -eq 3 || "$status" -eq 1 || "$status" -eq 255 ]] && exit 0
  else
    whiptail --title "Health Dashboard" --scrolltext --msgbox "$(cat "$tmp")" "$height" "$width" 2>/dev/tty || status=$?
    rm -f "$tmp"
    [[ "$status" -ne 0 ]] && exit 0
  fi
}

render_plain_dashboard() {
  build_dashboard_text "$(screen_cols)" 0
}

build_dashboard_text() {
  local width="$1" colorize="${2:-0}"
  echo "Health Dashboard"
  echo "Updated $(date '+%Y-%m-%d %H:%M:%S') | interval ${REFRESH_INTERVAL}s"
  echo
  render_endpoint_table "$width" "$colorize"
  echo
  render_systemd_table "$width" "$colorize"
  echo
  render_docker_table "$width" "$colorize"
  echo
  render_logs_section "$width"
}

separator() {
  local width="$1"
  printf '%*s\n' "$width" '' | tr ' ' '-'
}

print_subtitle() {
  local title="$1" width="$2" colorize="$3"
  separator "$width"
  if [[ "$colorize" -eq 1 ]]; then
    printf '\Zb\Z6%s\Zn\n' "$title"
  else
    printf '%s\n' "$title"
  fi
  separator "$width"
}

color_status() {
  local status="$1" colorize="$2" width="${3:-0}"
  if [[ "$colorize" -ne 1 ]]; then
    if [[ "$width" -gt 0 ]]; then printf '%-*s' "$width" "$status"; else printf '%s' "$status"; fi
    return 0
  fi
  case "$status" in
    PASS|active|running|healthy|no-healthcheck) printf '\Z2%-*s\Zn' "$width" "$status" ;;
    SSH_FAILED|FAIL|failed|missing|exited|unhealthy|unknown) printf '\Z1%-*s\Zn' "$width" "$status" ;;
    n/a|activating|degraded) printf '\Z3%-*s\Zn' "$width" "$status" ;;
    *) printf '\Z7%-*s\Zn' "$width" "$status" ;;
  esac
}

write_dark_dialogrc() {
  local file
  file="$(mktemp "${TMPDIR:-/tmp}/health-dashboard-dialogrc.XXXXXX")"
  cat > "$file" <<'DIALOGRC'
use_colors = ON
use_shadow = OFF
screen_color = (WHITE,BLACK,ON)
dialog_color = (WHITE,BLACK,OFF)
title_color = (CYAN,BLACK,ON)
border_color = (CYAN,BLACK,ON)
button_active_color = (BLACK,GREEN,ON)
button_inactive_color = (WHITE,BLACK,OFF)
button_key_active_color = (BLACK,GREEN,ON)
button_key_inactive_color = (GREEN,BLACK,ON)
DIALOGRC
  printf '%s' "$file"
}

render_endpoint_table() {
  local width="$1" colorize="${2:-0}" host_w=18 ip_w=15 check_w=8 status_w=12 detail_w
  detail_w=$((width - host_w - ip_w - check_w - status_w - 8))
  (( detail_w < 20 )) && detail_w=20
  print_subtitle "ENDPOINT CHECKS" "$width" "$colorize"
  printf '%-*s %-*s %-*s %-*s %s\n' "$host_w" HOST "$ip_w" IP "$check_w" CHECK "$status_w" STATUS DETAIL
  separator "$width"
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      emit_endpoint_row "$width" "$host_w" "$ip_w" "$check_w" "$status_w" "$detail_w" "$colorize" "$host" "$ip" ICMP "$(get_ping_result "$host" "$ip")"
      emit_endpoint_row "$width" "$host_w" "$ip_w" "$check_w" "$status_w" "$detail_w" "$colorize" "$host" "$ip" SSH "$(get_ssh_result "$host" "$ip")"
    done < <(host_ips "$host")
  done
  return 0
}

emit_endpoint_row() {
  local width="$1" host_w="$2" ip_w="$3" check_w="$4" status_w="$5" detail_w="$6" colorize="$7" host="$8" ip="$9" check="${10}" result="${11}"
  local state="${result%%|*}" detail="${result#*|}"
  emit_wrapped_row "$host_w" "$ip_w" "$check_w" "$status_w" "$detail_w" "$colorize" "$host" "$ip" "$check" "$state" "$detail"
}

render_systemd_table() {
  local width="$1" colorize="${2:-0}" host_w=18 ip_w=15 unit_w=28 status_w=12 detail_w
  detail_w=$((width - host_w - ip_w - unit_w - status_w - 8))
  (( detail_w < 16 )) && detail_w=16
  print_subtitle "SYSTEMD UNITS" "$width" "$colorize"
  printf '%-*s %-*s %-*s %-*s %s\n' "$host_w" HOST "$ip_w" IP "$unit_w" UNIT "$status_w" STATUS DETAIL
  separator "$width"
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      local emitted=0
      while IFS='=|' read -r kind unit state detail; do
        [[ "$kind" != SYSTEMD ]] && continue
        emitted=1
        [[ -z "${detail:-}" ]] && detail="systemctl is-active $unit"
        emit_wrapped_row "$host_w" "$ip_w" "$unit_w" "$status_w" "$detail_w" "$colorize" "$host" "$ip" "$unit" "$state" "$detail"
      done < <(get_systemd_statuses "$host" "$ip")
      [[ "$emitted" -eq 0 ]] && emit_wrapped_row "$host_w" "$ip_w" "$unit_w" "$status_w" "$detail_w" "$colorize" "$host" "$ip" "none configured" "n/a" "No HOST_SERVICES entries"
    done < <(host_ips "$host")
  done
  return 0
}

render_docker_table() {
  local width="$1" colorize="${2:-0}" host_w=18 ip_w=15 container_w=28 status_w=12 detail_w
  detail_w=$((width - host_w - ip_w - container_w - status_w - 8))
  (( detail_w < 16 )) && detail_w=16
  print_subtitle "DOCKER CONTAINERS" "$width" "$colorize"
  printf '%-*s %-*s %-*s %-*s %s\n' "$host_w" HOST "$ip_w" IP "$container_w" CONTAINER "$status_w" STATE HEALTH
  separator "$width"
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      local emitted=0
      while IFS='=|' read -r kind container state health; do
        [[ "$kind" != DOCKER ]] && continue
        emitted=1
        emit_wrapped_row "$host_w" "$ip_w" "$container_w" "$status_w" "$detail_w" "$colorize" "$host" "$ip" "$container" "$state" "$health"
      done < <(get_docker_statuses "$host" "$ip")
      [[ "$emitted" -eq 0 ]] && emit_wrapped_row "$host_w" "$ip_w" "$container_w" "$status_w" "$detail_w" "$colorize" "$host" "$ip" "none discovered" "n/a" "No containers returned by docker ps or config"
    done < <(host_ips "$host")
  done
  return 0
}

emit_wrapped_row() {
  local w1="$1" w2="$2" w3="$3" w4="$4" w5="$5" colorize="$6" c1="$7" c2="$8" c3="$9" c4="${10}" c5="${11}"
  mapfile -t parts < <(wrap_text "$c5" "$w5")
  [[ ${#parts[@]} -eq 0 ]] && parts=("")
  printf '%-*.*s %-*.*s %-*.*s %s %s\n' "$w1" "$w1" "$c1" "$w2" "$w2" "$c2" "$w3" "$w3" "$c3" "$(color_status "$c4" "$colorize" "$w4")" "${parts[0]}"
  local i
  for ((i=1; i<${#parts[@]}; i++)); do
    printf '%-*s %-*s %-*s %-*s %s\n' "$w1" '' "$w2" '' "$w3" '' "$w4" '' "${parts[$i]}"
  done
}

wrap_text() {
  local text="$1" width="$2"
  text="${text//$'\r'/}"
  if command -v fold >/dev/null 2>&1; then
    printf '%s\n' "$text" | fold -s -w "$width"
  else
    printf '%s\n' "$text"
  fi
}

render_logs_section() {
  local width="$1" body_width=$((width - 4))
  (( body_width < 20 )) && body_width=20
  printf 'DOCKER LOGS\n'
  separator "$width"
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      local logs
      logs="$(get_docker_logs "$host" "$ip")"
      [[ -z "$logs" ]] && continue
      printf '%s %s\n' "$host" "$ip"
      printf '%s\n' "$logs" | while IFS= read -r line; do
        wrap_text "$line" "$body_width" | sed 's/^/  /'
      done
    done < <(host_ips "$host")
  done
  return 0
}
