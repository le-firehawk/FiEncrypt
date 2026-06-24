#!/usr/bin/env bash

render_dashboard() {
  if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
    render_ansi_dashboard
  else
    render_plain_dashboard
  fi
}

render_ansi_dashboard() {
  local reset bold dim width now
  reset="$(tput sgr0)"; bold="$(tput bold)"; dim="$(tput dim || true)"
  width="$(tput cols 2>/dev/null || echo 100)"
  now="$(date '+%Y-%m-%d %H:%M:%S')"
  clear
  printf '%s%*s%s\n' "$bold" $(((width + 28) / 2)) 'Health Dashboard' "$reset"
  printf '%sUpdated %s | interval %ss | q/Ctrl-C to quit%s\n\n' "$dim" "$now" "$REFRESH_INTERVAL" "$reset"
  render_table 1
  printf '\n%sLegend: green=healthy yellow=warning red=failing%s\n' "$dim" "$reset"
  if [[ "$RUN_ONCE" -eq 0 ]]; then
    read -r -s -t 0.2 -n 1 key || true
    [[ "${key:-}" == q ]] && exit 0
  fi
}

render_plain_dashboard() {
  echo "Health Dashboard"
  echo "Updated $(date '+%Y-%m-%d %H:%M:%S')"
  render_table 0
}

render_table() {
  local colorize="$1"
  printf '%-18s %-15s %-12s %-12s %-28s %-24s\n' 'HOST' 'IP' 'PING' 'BOOTSTRAP' 'CONTAINERS' 'SERVICES'
  printf '%-18s %-15s %-12s %-12s %-28s %-24s\n' '------------------' '---------------' '------------' '------------' '----------------------------' '------------------------'
  for host in "${!HOST_IPS[@]}"; do
    IFS=',' read -ra ips <<< "${HOST_IPS[$host]}"
    for ip in "${ips[@]}"; do
      ip="${ip//[[:space:]]/}"
      [[ -z "$ip" ]] && continue
      render_row "$host" "$ip" "$colorize"
    done
  done
}

render_row() {
  local host="$1" ip="$2" colorize="$3" ping ping_state ping_detail bootstrap containers services reset=''
  [[ "$colorize" -eq 1 ]] && reset="$(tput sgr0)"
  ping="$(get_ping_result "$host" "$ip")"
  ping_state="${ping%%|*}"; ping_detail="${ping#*|}"
  bootstrap="$(get_snapshot "$host" "$ip" | awk -F= '/^BOOTSTRAP=/{print $2; exit}')"
  containers="$(summarize_snapshot "$host" "$ip" DOCKER)"
  services="$(summarize_snapshot "$host" "$ip" SYSTEMD)"
  printf '%-18s %-15s ' "$host" "$ip"
  print_cell "$ping_state" "$(status_icon "$ping_state") $ping_detail" "$colorize"
  print_cell "${bootstrap:-FAIL}" "$(status_icon "${bootstrap:-FAIL}") ${bootstrap:-FAIL}" "$colorize"
  printf '%-28s %-24s\n' "$containers" "$services"
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

summarize_snapshot() {
  local host="$1" ip="$2" type="$3"
  get_snapshot "$host" "$ip" | awk -F'[=|]' -v type="$type" '
    $1 == type { total++; if ($3 == "active" || $3 == "healthy" || $4 == "healthy") ok++ }
    END { if (total == 0) print "none"; else printf "%d/%d ok", ok, total }
  '
}
