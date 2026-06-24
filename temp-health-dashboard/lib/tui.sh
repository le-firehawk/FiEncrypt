#!/usr/bin/env bash

require_tui_or_once() {
  if [[ "$RUN_ONCE" -eq 0 && ! -t 1 ]]; then
    echo "Interactive TUI mode requires a TTY. Use --once for non-interactive output." >&2
    exit 2
  fi
}

render_dashboard() {
  if [[ "$RUN_ONCE" -eq 1 || ! -t 1 ]]; then
    render_plain_dashboard
  else
    render_tui_dashboard
  fi
}

render_tui_dashboard() {
  local reset bold dim width now key=""
  reset="$(tput sgr0)"; bold="$(tput bold)"; dim="$(tput dim || true)"
  width="$(tput cols 2>/dev/null || echo 120)"
  now="$(date '+%Y-%m-%d %H:%M:%S')"
  tput smcup
  trap 'tput rmcup; tput cnorm' EXIT INT TERM
  tput civis
  clear
  printf '%s%*s%s\n' "$bold" $(((width + 28) / 2)) 'Health Dashboard' "$reset"
  printf '%sUpdated %s | interval %ss | q quits | l toggles Docker logs%s\n\n' "$dim" "$now" "$REFRESH_INTERVAL" "$reset"
  render_table 1
  if [[ "${SHOW_LOGS:-0}" -eq 1 ]]; then
    printf '\n%sDocker logs%s\n' "$bold" "$reset"
    render_logs
  fi
  printf '\n%sLegend: green=healthy yellow=transitional red=failing%s\n' "$dim" "$reset"
  read -r -s -t 0.2 -n 1 key || true
  case "${key:-}" in
    q) tput rmcup; tput cnorm; exit 0 ;;
    l) SHOW_LOGS=$((1 - ${SHOW_LOGS:-0})) ;;
  esac
}

render_plain_dashboard() {
  echo "Health Dashboard"
  echo "Updated $(date '+%Y-%m-%d %H:%M:%S')"
  render_table 0
  echo
  echo "Docker logs"
  render_logs
}

render_table() {
  local colorize="$1"
  printf '%-18s %-15s %-12s %-12s %-18s %-18s\n' 'HOST' 'IP' 'ICMP' 'SSH' 'SYSTEMD' 'DOCKER'
  printf '%-18s %-15s %-12s %-12s %-18s %-18s\n' '------------------' '---------------' '------------' '------------' '------------------' '------------------'
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      render_row "$host" "$ip" "$colorize"
    done < <(host_ips "$host")
  done
}

render_row() {
  local host="$1" ip="$2" colorize="$3" ping ssh_status systemd docker
  ping="$(get_ping_result "$host" "$ip")"
  ssh_status="$(get_ssh_result "$host" "$ip")"
  systemd="$(get_systemd_statuses "$host" "$ip" | summarize_status_lines SYSTEMD)"
  docker="$(get_docker_statuses "$host" "$ip" | summarize_status_lines DOCKER)"
  printf '%-18s %-15s ' "$host" "$ip"
  print_cell "${ping%%|*}" "$(status_icon "${ping%%|*}") ${ping#*|}" "$colorize"
  print_cell "${ssh_status%%|*}" "$(status_icon "${ssh_status%%|*}") $(truncate_cell "${ssh_status#*|}" 10)" "$colorize"
  printf '%-18s %-18s\n' "$systemd" "$docker"
}

truncate_cell() {
  local text="$1" max="$2"
  text="${text//$'\r'/}"
  if (( ${#text} > max )); then
    printf '%s…' "${text:0:max}"
  else
    printf '%s' "$text"
  fi
}

print_cell() {
  local state="$1" text="$2" colorize="$3" reset=''
  if [[ "$colorize" -eq 1 ]]; then
    reset="$(tput sgr0)"
    printf '%b%-12s%b ' "$(status_color "$state")" "$text" "$reset"
  else
    printf '%-12s ' "$text"
  fi
}

render_logs() {
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      local logs
      logs="$(get_docker_logs "$host" "$ip")"
      [[ -z "$logs" ]] && continue
      printf '%s %s\n' "$host" "$ip"
      printf '%s\n' "$logs" | sed 's/^/  /'
    done < <(host_ips "$host")
  done
}
