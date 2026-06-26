#!/usr/bin/env bash

declare -Ag SSH_PASSWORDS=()
declare -Ag SSH_PASSWORD_PROMPT_DECLINED_HOSTS=()
declare -Ag SSH_PASSWORD_ATTEMPTED_HOSTS=()
LOADING_ACTIVE=0
LOADING_PIPE=""
LOADING_FD=""
LOADING_PID=""
LOADING_DIALOGRC=""
LOADING_STATE_FILE=""
LOADING_HEARTBEAT_PID=""
LOADING_STARTED_AT=0

require_tui_or_once() {
  if [[ "$RUN_ONCE" -eq 0 && ! -t 1 ]]; then
    echo "Interactive TUI mode requires a TTY. Use --once for non-interactive output." >&2
    exit 2
  fi
  if [[ "$RUN_ONCE" -eq 0 ]] && ! command -v dialog >/dev/null 2>&1 && ! command -v whiptail >/dev/null 2>&1; then
    echo "Warning: dialog or whiptail is recommended for the interactive TUI. Install one of: dialog whiptail. Falling back to CLI stdin/stdout controls." >&2
  fi
}


collect_dashboard_cycle() {
  collection_loading_start
  collection_loading_update 5 "Preparing checks" "Clearing previous cycle data and preparing the health-check cache."
  clear_cycle_cache
  collection_loading_update 15 "ICMP checks" "Pinging every configured host/IP endpoint."
  collect_ping_parallel
  collection_loading_update 35 "SSH checks" "Testing SSH connectivity for every configured host/IP endpoint."
  collect_ssh_parallel
  if [[ "$RUN_ONCE" -eq 0 && -t 1 ]]; then
    collection_loading_stop
    maybe_prompt_for_ssh_password || true
    collection_loading_start
  fi
  collection_loading_update 60 "Systemd checks" "Checking configured systemd units on the first SSH-successful IP per host."
  collect_systemd_parallel
  collection_loading_update 80 "Docker checks" "Collecting Docker container status and recent log snippets."
  collect_docker_parallel
  collection_loading_update 95 "Time sync checks" "Checking NTP synchronization and source health."
  collect_timesync_parallel
  collection_loading_update 100 "Rendering summary" "Health checks finished; rendering the updated dashboard."
  collection_loading_stop
}

maybe_prompt_for_ssh_password() {
  local host password status
  local -a password_hosts
  mapfile -t password_hosts < <(ssh_password_candidate_hosts)
  [[ ${#password_hosts[@]} -eq 0 ]] && return 0
  if ! command -v sshpass >/dev/null 2>&1; then
    if command -v dialog >/dev/null 2>&1; then
      dialog --title "SSH password authentication" --msgbox "One or more SSH checks failed. If the target permits password authentication, install sshpass or configure SSH keys/agent forwarding, then refresh." 10 72 2>/dev/tty || true
    elif command -v whiptail >/dev/null 2>&1; then
      whiptail --title "SSH password authentication" --msgbox "One or more SSH checks failed. If the target permits password authentication, install sshpass or configure SSH keys/agent forwarding, then refresh." 10 72 2>/dev/tty || true
    fi
    for host in "${password_hosts[@]}"; do
      SSH_PASSWORD_PROMPT_DECLINED_HOSTS[$host]=1
      mark_ssh_password_prompt_cancelled "$host" "sshpass unavailable; SSH-dependent checks skipped"
    done
    return 0
  fi
  for host in "${password_hosts[@]}"; do
    status=0
    if command -v dialog >/dev/null 2>&1; then
      password="$(dialog --insecure --title "SSH password authentication: $host" --passwordbox "SSH checks failed for host '$host'. If this host permits password authentication, enter the password once; it will be reused for every configured IP on this host during this run. Cancel to keep SSH-dependent checks skipped for this host." 13 78 2>&1 >/dev/tty)" || status=$?
    elif command -v whiptail >/dev/null 2>&1; then
      password="$(whiptail --title "SSH password authentication: $host" --passwordbox "SSH checks failed for host '$host'. If this host permits password authentication, enter the password once; it will be reused for every configured IP on this host during this run. Cancel to keep SSH-dependent checks skipped for this host." 13 78 2>&1 >/dev/tty)" || status=$?
    else
      return 0
    fi
    if [[ "$status" -ne 0 || -z "$password" ]]; then
      SSH_PASSWORD_PROMPT_DECLINED_HOSTS[$host]=1
      mark_ssh_password_prompt_cancelled "$host" "password prompt cancelled; SSH-dependent checks skipped"
      continue
    fi
    SSH_PASSWORDS[$host]="$password"
    SSH_PASSWORD_ATTEMPTED_HOSTS[$host]=1
    collection_loading_start
    collection_loading_update 40 "Retrying SSH authentication" "Password accepted for host '$host'. Retrying SSH checks on every configured IP for this host before rendering the updated dashboard summary."
    collect_ssh_for_host "$host"
    collection_loading_stop
  done
}

show_loading_popup() {
  local title="$1" message="$2"
  [[ "$RUN_ONCE" -eq 1 || ! -t 1 ]] && return 0
  if command -v dialog >/dev/null 2>&1; then
    local dialogrc
    dialogrc="$(write_dark_dialogrc)"
    DIALOGRC="$dialogrc" dialog --colors --title "$title" --infobox "$message" 7 72 2>/dev/tty || true
    rm -f "$dialogrc"
  elif command -v whiptail >/dev/null 2>&1; then
    whiptail --title "$title" --infobox "$message" 7 72 2>/dev/tty || true
  fi
}

collection_loading_update() {
  local percent="$1" stage="$2" detail="$3"
  [[ "$RUN_ONCE" -eq 1 ]] && return 0
  if [[ "$LOADING_ACTIVE" -eq 1 && -n "$LOADING_FD" ]]; then
    collection_loading_set_state "$percent" "$stage" "$detail"
    collection_loading_write "$percent" "$stage" "$detail"
  elif [[ -t 1 ]]; then
    clear 2>/dev/null || true
    printf 'Running health checks (%s%%)\n\n%s\n\n%s\n\nThe dashboard will refresh automatically when this cycle completes.\n' "$percent" "$stage" "$detail"
  fi
}

collection_loading_start() {
  [[ "$RUN_ONCE" -eq 1 || ! -t 1 || "$LOADING_ACTIVE" -eq 1 ]] && return 0
  if command -v dialog >/dev/null 2>&1 || command -v whiptail >/dev/null 2>&1; then
    LOADING_PIPE="$(mktemp -u "${TMPDIR:-/tmp}/health-loading.XXXXXX")"
    LOADING_STATE_FILE="$(mktemp "${TMPDIR:-/tmp}/health-loading-state.XXXXXX")"
    LOADING_STARTED_AT="$(date +%s)"
    mkfifo "$LOADING_PIPE"
    if command -v dialog >/dev/null 2>&1; then
      LOADING_DIALOGRC="$(write_dark_dialogrc)"
      DIALOGRC="$LOADING_DIALOGRC" dialog --colors --title "Running health checks" --gauge "Starting health checks..." 10 78 0 < "$LOADING_PIPE" 2>/dev/tty &
    else
      whiptail --title "Running health checks" --gauge "Starting health checks..." 10 78 0 < "$LOADING_PIPE" 2>/dev/tty &
    fi
    LOADING_PID=$!
    exec {LOADING_FD}>"$LOADING_PIPE"
    collection_loading_set_state 0 "Starting health checks" "Preparing the loading screen."
    collection_loading_heartbeat &
    LOADING_HEARTBEAT_PID=$!
  fi
  LOADING_ACTIVE=1
}

collection_loading_stop() {
  [[ "$LOADING_ACTIVE" -eq 0 ]] && return 0
  [[ -n "$LOADING_HEARTBEAT_PID" ]] && kill "$LOADING_HEARTBEAT_PID" 2>/dev/null || true
  [[ -n "$LOADING_HEARTBEAT_PID" ]] && wait "$LOADING_HEARTBEAT_PID" 2>/dev/null || true
  if [[ -n "$LOADING_FD" ]]; then
    exec {LOADING_FD}>&- || true
    LOADING_FD=""
  fi
  [[ -n "$LOADING_PID" ]] && wait "$LOADING_PID" 2>/dev/null || true
  [[ -n "$LOADING_PIPE" ]] && rm -f "$LOADING_PIPE"
  [[ -n "$LOADING_DIALOGRC" ]] && rm -f "$LOADING_DIALOGRC"
  [[ -n "$LOADING_STATE_FILE" ]] && rm -f "$LOADING_STATE_FILE"
  LOADING_PIPE=""
  LOADING_PID=""
  LOADING_DIALOGRC=""
  LOADING_STATE_FILE=""
  LOADING_HEARTBEAT_PID=""
  LOADING_ACTIVE=0
}

collection_loading_set_state() {
  local percent="$1" stage="$2" detail="$3"
  [[ -z "$LOADING_STATE_FILE" ]] && return 0
  {
    printf '%s\n' "$percent"
    printf '%s\n' "$stage"
    printf '%s\n' "$detail"
  } > "$LOADING_STATE_FILE"
}

collection_loading_heartbeat() {
  local percent stage detail now elapsed
  while :; do
    if [[ -n "$LOADING_STATE_FILE" && -r "$LOADING_STATE_FILE" ]]; then
      {
        IFS= read -r percent || percent=0
        IFS= read -r stage || stage="Running health checks"
        IFS= read -r detail || detail=""
      } < "$LOADING_STATE_FILE"
      now="$(date +%s)"
      elapsed=$((now - LOADING_STARTED_AT))
      collection_loading_write "$percent" "$stage (elapsed ${elapsed}s)" "$detail"
    fi
    sleep 1
  done
}

collection_loading_write() {
  local percent="$1" stage="$2" detail="$3"
  [[ -z "$LOADING_FD" ]] && return 0
  {
    printf 'XXX\n%s\n%s\n\n%s\n\nThe dashboard is still running checks and will refresh automatically when this cycle completes.\nXXX\n' "$percent" "$stage" "$detail"
  } >&"$LOADING_FD" || true
}

mark_ssh_password_prompt_cancelled() {
  local host="$1" reason="$2" ip key current
  while IFS= read -r ip; do
    current="$(get_ssh_result "$host" "$ip")"
    [[ "${current%%|*}" == PASS ]] && continue
    key="$(safe_key "${host}_${ip}")"
    printf 'FAIL|%s\n' "$reason" > "$CACHE_DIR/${key}.ssh"
    log_event WARN "ssh password prompt cancelled host=$host ip=$ip reason=$reason"
  done < <(host_ips "$host")
}

ssh_password_candidate_hosts() {
  local host ip key
  for host in "${!HOST_IPS[@]}"; do
    [[ -n "${SSH_PASSWORDS[$host]:-}" ]] && continue
    [[ -n "${SSH_PASSWORD_ATTEMPTED_HOSTS[$host]:-}" ]] && continue
    [[ -n "${SSH_PASSWORD_PROMPT_DECLINED_HOSTS[$host]:-}" ]] && continue
    while IFS= read -r ip; do
      key="$(safe_key "${host}_${ip}")"
      if { [[ -f "$CACHE_DIR/${key}.ssh" ]] && grep -Eiq 'FAIL|permission denied|password|keyboard-interactive|publickey|authentication|auth' "$CACHE_DIR/${key}.ssh"; } ||
         { [[ -f "$CACHE_DIR/${key}.ssh.err" ]] && grep -Eiq 'permission denied|password|keyboard-interactive|publickey|authentication|auth' "$CACHE_DIR/${key}.ssh.err"; }; then
        printf '%s\n' "$host"
        break
      fi
    done < <(host_ips "$host")
  done
}

render_dashboard() {
  if [[ "$RUN_ONCE" -eq 1 || ! -t 1 ]]; then
    render_plain_dashboard
  elif command -v dialog >/dev/null 2>&1 || command -v whiptail >/dev/null 2>&1; then
    render_external_tui
  else
    render_cli_dashboard
  fi
}

screen_cols() { tput cols 2>/dev/null || echo 120; }
screen_lines() { tput lines 2>/dev/null || echo 40; }

dashboard_text_width() {
  local width="$1"
  width=$((width - 4))
  (( width < 60 )) && width=60
  printf '%s' "$width"
}

render_external_tui() {
  local tmp width height status=0 colorize=0 choice=""
  width="$(screen_cols)"; height="$(screen_lines)"
  tmp="$(mktemp "${TMPDIR:-/tmp}/health-dashboard.XXXXXX")"
  if command -v dialog >/dev/null 2>&1; then
    colorize=1
  fi
  build_dashboard_text "$(dashboard_text_width "$width")" "$colorize" > "$tmp"
  if command -v dialog >/dev/null 2>&1; then
    local dialogrc
    dialogrc="$(write_dark_dialogrc)"
    choice="$(DIALOGRC="$dialogrc" dialog --colors --clear --title "Health Dashboard" --cancel-label "q Quit" --menu "$(cat "$tmp")" "$height" "$width" 4       refresh "Refresh now"       logs "Docker logs"       q "Quit"       2>&1 >/dev/tty)" || status=$?
    rm -f "$dialogrc" "$tmp"
  else
    choice="$(whiptail --title "Health Dashboard" --cancel-button "q Quit" --menu "$(cat "$tmp")" "$height" "$width" 4       refresh "Refresh now"       logs "Docker logs"       q "Quit"       2>&1 >/dev/tty)" || status=$?
    rm -f "$tmp"
  fi
  if [[ "$status" -ne 0 ]]; then
    if [[ "${NEEDS_REDRAW:-0}" -eq 1 ]]; then
      NEEDS_REDRAW=0
      REFRESH_NOW=1
      return 0
    fi
    exit 0
  fi
  case "$choice" in
    refresh) REFRESH_NOW=1 ;;
    logs) render_docker_logs_picker; REFRESH_NOW=1 ;;
    q) exit 0 ;;
  esac
}

render_cli_dashboard() {
  local key=""
  clear 2>/dev/null || true
  build_dashboard_text "$(dashboard_text_width "$(screen_cols)")" 0
  printf '\n[Fallback CLI] Install dialog or whiptail for the full TUI. Commands: r=refresh now, l=docker logs, q=quit. Auto-refresh in %ss.\n' "$REFRESH_INTERVAL"
  read -r -s -t "$REFRESH_INTERVAL" -n 1 key || true
  case "${key:-}" in
    r|R) REFRESH_NOW=1 ;;
    l|L) render_cli_docker_logs; REFRESH_NOW=1 ;;
    q|Q) exit 0 ;;
  esac
}

render_cli_docker_logs() {
  clear 2>/dev/null || true
  render_logs_section "$(dashboard_text_width "$(screen_cols)")"
  printf '\nPress any key to return to the dashboard...\n'
  read -r -s -n 1 _ || true
}

render_plain_dashboard() {
  build_dashboard_text "$(dashboard_text_width "$(screen_cols)")" 0
}

build_dashboard_text() {
  local width="$1" colorize="${2:-0}"
  if [[ "$colorize" -eq 0 ]]; then
    print_banner "HEALTH DASHBOARD" "$width" "$colorize"
  fi
  echo "Updated $(date '+%Y-%m-%d %H:%M:%S') | interval ${REFRESH_INTERVAL}s | operation timeout $(operation_timeout)s"
  echo
  render_endpoint_table "$width" "$colorize"
  echo
  render_systemd_table "$width" "$colorize"
  echo
  render_docker_table "$width" "$colorize"
  echo
  render_timesync_table "$width" "$colorize"

}

separator() {
  local width="$1"
  (( width < 1 )) && width=1
  printf '%*s\n' "$((width - 1))" '' | tr ' ' '-'
}

print_banner() {
  local title="$1" width="$2" colorize="$3" line text
  text="  $title  "
  line="$(printf '%*s' "$((width - 1))" '' | tr ' ' '=')"
  if [[ "$colorize" -eq 1 ]]; then
    printf '\Zb\Z6%s\Zn\n' "$line"
    printf '\Zb\Z6%*s\Zn\n' $(((width + ${#text}) / 2)) "$text"
    printf '\Zb\Z6%s\Zn\n' "$line"
  else
    printf '%s\n' "$line"
    printf '%*s\n' $(((width + ${#text}) / 2)) "$text"
    printf '%s\n' "$line"
  fi
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
  detail_w=$((width - host_w - ip_w - check_w - status_w - 4))
  if (( detail_w < 16 )); then
    detail_w=16
    ip_w=$((width - host_w - check_w - status_w - detail_w - 4))
    (( ip_w < 10 )) && ip_w=10
  fi
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
  detail_w=$((width - host_w - ip_w - unit_w - status_w - 4))
  if (( detail_w < 16 )); then
    detail_w=16
    unit_w=$((width - host_w - ip_w - status_w - detail_w - 4))
    (( unit_w < 10 )) && unit_w=10
  fi
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

render_timesync_table() {
  local width="$1" colorize="${2:-0}" host_w=18 ip_w=15 status_w=12 detail_w
  detail_w=$((width - host_w - ip_w - status_w - 3))
  (( detail_w < 16 )) && detail_w=16
  print_subtitle "TIME SYNC / NTP" "$width" "$colorize"
  printf '%-*s %-*s %-*s %s\n' "$host_w" HOST "$ip_w" IP "$status_w" STATUS DETAIL
  separator "$width"
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      local line state detail
      line="$(get_timesync_status "$host" "$ip")"
      state="${line#*=}"; state="${state%%|*}"; detail="${line#*|}"
      emit_wrapped_row "$host_w" "$ip_w" 1 "$status_w" "$detail_w" "$colorize" "$host" "$ip" "" "$state" "$detail"
    done < <(host_ips "$host")
  done
  return 0
}

render_docker_table() {
  local width="$1" colorize="${2:-0}" host_w=18 ip_w=15 container_w=28 status_w=12 detail_w
  detail_w=$((width - host_w - ip_w - container_w - status_w - 4))
  if (( detail_w < 16 )); then
    detail_w=16
    container_w=$((width - host_w - ip_w - status_w - detail_w - 4))
    (( container_w < 10 )) && container_w=10
  fi
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

render_docker_logs_picker() {
  local width height choice status=0 dialogrc
  width="$(screen_cols)"; height="$(screen_lines)"
  if command -v dialog >/dev/null 2>&1; then
    mapfile -t docker_choices < <(docker_log_choices)
    if [[ ${#docker_choices[@]} -eq 0 ]]; then
      dialog --title "Docker Logs" --msgbox "No Docker containers are available in the current cycle." 8 60 2>/dev/tty || true
      return 0
    fi
    dialogrc="$(write_dark_dialogrc)"
    choice="$(DIALOGRC="$dialogrc" dialog --colors --clear --title "Docker Logs" --menu "Choose a container log screen" "$height" "$width" $((height - 8)) "${docker_choices[@]}" 2>&1 >/dev/tty)" || status=$?
    rm -f "$dialogrc"
    [[ "$status" -ne 0 || -z "$choice" ]] && return 0
    render_selected_docker_logs "$choice"
  fi
}

docker_log_choices() {
  local host ip line kind container state health tag desc
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      while IFS='=|' read -r kind container state health; do
        [[ "$kind" != DOCKER ]] && continue
        tag="${host}|${ip}|${container}"
        desc="${state} ${health}"
        printf '%s\n%s\n' "$tag" "$desc"
      done < <(get_docker_statuses "$host" "$ip")
    done < <(host_ips "$host")
  done
}

render_selected_docker_logs() {
  local choice="$1" host ip container tmp width height logs in_container=0 line status=0 dialogrc
  IFS='|' read -r host ip container <<< "$choice"
  width="$(screen_cols)"; height="$(screen_lines)"
  tmp="$(mktemp "${TMPDIR:-/tmp}/health-dashboard-logs.XXXXXX")"
  {
    print_banner "DOCKER LOGS: $host $ip $container" "$width" 1
    logs="$(get_docker_logs "$host" "$ip")"
    if [[ -z "$logs" ]]; then
      echo "No logs captured for this container."
    else
      while IFS= read -r line; do
        if [[ "$line" == "===== $container =====" ]]; then
          in_container=1
          echo "$line"
          continue
        fi
        if [[ "$line" == =====*===== && "$in_container" -eq 1 ]]; then
          break
        fi
        [[ "$in_container" -eq 1 ]] && wrap_text "$line" "$((width - 2))"
      done <<< "$logs"
    fi
  } > "$tmp"
  dialogrc="$(write_dark_dialogrc)"
  DIALOGRC="$dialogrc" dialog --colors --clear --title "Docker Logs" --textbox "$tmp" "$height" "$width" 2>/dev/tty || status=$?
  rm -f "$dialogrc" "$tmp"
  return 0
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
