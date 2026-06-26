#!/usr/bin/env bash

declare -Ag SSH_PASSWORDS=()
declare -Ag SSH_PASSWORD_DECLINED=()
LOADING_FD=""
LOADING_PID=""

screen_cols() { tput cols 2>/dev/null || echo 120; }
screen_lines() { tput lines 2>/dev/null || echo 40; }
text_width() { local w; w="$(screen_cols)"; ((w > 4)) && echo $((w - 4)) || echo 80; }

loading_begin() {
  [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]] && return 0
  if command -v dialog >/dev/null 2>&1; then
    coproc HEALTH_LOADING { dialog --title "Running health checks" --gauge "Starting checks..." 8 72 0 >/dev/tty 2>/dev/tty; }
    LOADING_FD="${HEALTH_LOADING[1]}"; LOADING_PID="$HEALTH_LOADING_PID"
  elif command -v whiptail >/dev/null 2>&1; then
    coproc HEALTH_LOADING { whiptail --title "Running health checks" --gauge "Starting checks..." 8 72 0 >/dev/tty 2>/dev/tty; }
    LOADING_FD="${HEALTH_LOADING[1]}"; LOADING_PID="$HEALTH_LOADING_PID"
  else
    clear 2>/dev/null || true
    printf 'Running health checks...\n'
  fi
}

loading_step() {
  [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]] && return 0
  local percent="$1" message="$2"
  if [[ -n "$LOADING_FD" ]]; then
    printf 'XXX\n%s\n%s\nXXX\n' "$percent" "$message" >&"$LOADING_FD" 2>/dev/null || true
  else
    printf '\r%-80s' "$message"
  fi
}

loading_end() {
  [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]] && return 0
  if [[ -n "$LOADING_FD" ]]; then
    printf '100\n' >&"$LOADING_FD" 2>/dev/null || true
    eval "exec ${LOADING_FD}>&-" 2>/dev/null || true
    [[ -n "$LOADING_PID" ]] && wait "$LOADING_PID" 2>/dev/null || true
    LOADING_FD=""; LOADING_PID=""
  else
    printf '\n'
  fi
}

render_loading() {
  loading_step "${2:-10}" "$1"
}

maybe_prompt_for_ssh_password() {
  [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]] && return 0
  command -v sshpass >/dev/null 2>&1 || return 0
  local host ip result password status
  for host in "${!HOST_IPS[@]}"; do
    [[ -n "${SSH_PASSWORDS[$host]:-}" || -n "${SSH_PASSWORD_DECLINED[$host]:-}" ]] && continue
    while IFS= read -r ip; do
      result="$(get_ssh_result "$host" "$ip")"
      [[ "$result" == FAIL\|* ]] || continue
      status=0
      if command -v dialog >/dev/null 2>&1; then
        password="$(dialog --insecure --title "SSH password for host: $host" --passwordbox "SSH failed for one or more addresses assigned to host '$host'. Enter the SSH password once; it will be reused for every IP in this host definition during this run. Cancel leaves SSH-dependent checks skipped for this host." 12 78 2>&1 >/dev/tty)" || status=$?
      elif command -v whiptail >/dev/null 2>&1; then
        password="$(whiptail --title "SSH password for host: $host" --passwordbox "SSH failed for one or more addresses assigned to host '$host'. Enter the SSH password once; it will be reused for every IP in this host definition during this run. Cancel leaves SSH-dependent checks skipped for this host." 12 78 2>&1 >/dev/tty)" || status=$?
      else
        return 0
      fi
      if [[ "$status" -eq 0 && -n "$password" ]]; then
        SSH_PASSWORDS[$host]="$password"
        loading_begin
        render_loading "Retrying SSH for $host with the provided host password..." 45
        collect_ssh_for_host "$host"
        loading_end
      else
        SSH_PASSWORD_DECLINED[$host]=1
      fi
      break
    done < <(host_ips "$host")
  done
}

render_dashboard() {
  local body tmp choice status=0
  body="$(build_dashboard_text "$(text_width)")"
  if [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]]; then
    printf '%s\n' "$body"
    return 0
  fi
  if command -v dialog >/dev/null 2>&1; then
    tmp="$(mktemp)"; printf '%s\n' "$body" > "$tmp"
    choice="$(dialog --title "Health Dashboard" --menu "$(cat "$tmp")" "$(screen_lines)" "$(screen_cols)" 4 refresh "Refresh now" logs "Docker logs" quit "Quit" 2>&1 >/dev/tty)" || status=$?
    rm -f "$tmp"
  elif command -v whiptail >/dev/null 2>&1; then
    choice="$(whiptail --title "Health Dashboard" --menu "$body" "$(screen_lines)" "$(screen_cols)" 4 refresh "Refresh now" logs "Docker logs" quit "Quit" 2>&1 >/dev/tty)" || status=$?
  else
    clear 2>/dev/null || true
    printf '%s\n\nCommands: Enter=refresh, l=logs, q=quit\n' "$body"
    read -r -s -n 1 choice || true
    [[ -z "$choice" ]] && choice=refresh
  fi
  [[ "$status" -ne 0 || "$choice" == quit || "$choice" == q ]] && exit 0
  [[ "$choice" == logs || "$choice" == l ]] && render_logs
}

build_dashboard_text() {
  local width="$1" host ip result state detail line
  printf 'Health Dashboard | updated %s | interval %ss | timeout %ss\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$REFRESH_INTERVAL" "$(operation_timeout)"
  printf '%*s\n' "$width" '' | tr ' ' '-'
  printf 'ENDPOINTS\n%-18s %-15s %-8s %-12s %s\n' HOST IP CHECK STATUS DETAIL
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      result="$(get_ping_result "$host" "$ip")"; state="${result%%|*}"; detail="${result#*|}"; printf '%-18s %-15s %-8s %-12s %s\n' "$host" "$ip" ICMP "$state" "$detail"
      result="$(get_ssh_result "$host" "$ip")"; state="${result%%|*}"; detail="${result#*|}"; printf '%-18s %-15s %-8s %-12s %s\n' "$host" "$ip" SSH "$state" "$detail"
    done < <(host_ips "$host")
  done
  printf '\nSYSTEMD\n%-18s %-15s %-24s %-12s %s\n' HOST IP UNIT STATUS DETAIL
  for host in "${!HOST_IPS[@]}"; do while IFS= read -r ip; do while IFS='=|' read -r _ unit state detail; do [[ -n "$unit" ]] && printf '%-18s %-15s %-24s %-12s %s\n' "$host" "$ip" "$unit" "$state" "$detail"; done < <(get_systemd_statuses "$host" "$ip"); done < <(host_ips "$host"); done
  printf '\nDOCKER\n%-18s %-15s %-24s %-12s %s\n' HOST IP CONTAINER STATE HEALTH
  for host in "${!HOST_IPS[@]}"; do while IFS= read -r ip; do while IFS='=|' read -r _ container state health; do [[ -n "$container" ]] && printf '%-18s %-15s %-24s %-12s %s\n' "$host" "$ip" "$container" "$state" "$health"; done < <(get_docker_statuses "$host" "$ip"); done < <(host_ips "$host"); done
  printf '\nTIME SYNC / NTP\n%-18s %-15s %-18s %-12s %s\n' HOST IP SOURCE STATUS DETAIL
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      line="$(get_timesync_status "$host" "$ip")"; state="${line#*=}"; state="${state%%|*}"; detail="${line#*|}"
      printf '%-18s %-15s %-18s %-12s %s\n' "$host" "$ip" summary "$state" "$detail"
      while IFS='=|' read -r _ source source_detail; do
        [[ -n "$source" ]] && printf '%-18s %-15s %-18s %-12s %s\n' "$host" "$ip" "$source" SOURCE "$source_detail"
      done < <(get_timesync_statuses "$host" "$ip" | awk -F'[=|]' '$1 == "TIMESYNC_SOURCE"')
    done < <(host_ips "$host")
  done
}

render_logs() {
  local host ip
  clear 2>/dev/null || true
  for host in "${!HOST_IPS[@]}"; do while IFS= read -r ip; do printf '\n# %s %s\n' "$host" "$ip"; get_docker_logs "$host" "$ip"; done < <(host_ips "$host"); done
  printf '\nPress any key to return...'; read -r -s -n 1 _ || true
}
