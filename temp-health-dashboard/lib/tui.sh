#!/usr/bin/env bash

declare -Ag SSH_PASSWORDS=()
declare -Ag SSH_PASSWORD_DECLINED=()
declare -Ag SUDO_PASSWORDS=()
declare -Ag SUDO_PASSWORD_DECLINED=()
DASHBOARD_ACTION="refresh"
LOADING_FD=""
LOADING_PID=""

screen_cols() { tput cols 2>/dev/null || echo 120; }
screen_lines() { tput lines 2>/dev/null || echo 40; }
text_width() { local w; w="$(screen_cols)"; ((w > 4)) && echo $((w - 4)) || echo 80; }

draw_loading() {
  [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]] && return 0
  local percent="$1" message="$2"
  if command -v dialog >/dev/null 2>&1; then
    dialog --title "Running health checks" --infobox "$message\n\nProgress: ${percent}%" 7 72 2>/dev/tty || true
  elif command -v whiptail >/dev/null 2>&1; then
    whiptail --title "Running health checks" --infobox "$message\n\nProgress: ${percent}%" 7 72 2>/dev/tty || true
  else
    clear 2>/dev/null || true
    printf 'Running health checks [%s%%]: %s\n' "$percent" "$message"
  fi
}

run_with_loading() {
  local start_percent="$1" end_percent="$2" message="$3" pid elapsed percent span status
  shift 3
  if [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]]; then
    "$@"
    return $?
  fi
  draw_loading "$start_percent" "$message (starting)"
  "$@" &
  pid=$!
  elapsed=0
  span=$((end_percent - start_percent)); ((span < 1)) && span=1
  while kill -0 "$pid" 2>/dev/null; do
    percent=$((start_percent + elapsed % span))
    draw_loading "$percent" "$message (elapsed ${elapsed}s)"
    sleep 1
    elapsed=$((elapsed + 1))
  done
  wait "$pid"; status=$?
  draw_loading "$end_percent" "$message complete"
  sleep 1
  return "$status"
}

render_loading() { draw_loading "${2:-10}" "$1"; }

loading_begin() { :; }
loading_step() { draw_loading "$1" "$2"; }
loading_end() { :; }

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
        run_with_loading 35 45 "Retrying SSH for $host with the provided host password" collect_ssh_for_host "$host"
      else
        SSH_PASSWORD_DECLINED[$host]=1
      fi
      break
    done < <(host_ips "$host")
  done
}

maybe_prompt_for_sudo_password() {
  local host="$1" password status=0
  [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]] && return 0
  [[ -n "${SUDO_PASSWORDS[$host]:-}" || -n "${SUDO_PASSWORD_DECLINED[$host]:-}" ]] && return 0
  if command -v dialog >/dev/null 2>&1; then
    password="$(dialog --insecure --title "Sudo password for host: $host" --passwordbox "Systemd start/stop/restart operations use sudo as '${SUDO_USER:-$SSH_USER}'. Enter the sudo password once; it will be cached separately from SSH passwords for this host during this run. Cancel attempts sudo without a password." 12 78 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    password="$(whiptail --title "Sudo password for host: $host" --passwordbox "Systemd start/stop/restart operations use sudo as '${SUDO_USER:-$SSH_USER}'. Enter the sudo password once; it will be cached separately from SSH passwords for this host during this run. Cancel attempts sudo without a password." 12 78 2>&1 >/dev/tty)" || status=$?
  else
    return 0
  fi
  if [[ "$status" -eq 0 && -n "$password" ]]; then
    SUDO_PASSWORDS[$host]="$password"
  else
    SUDO_PASSWORD_DECLINED[$host]=1
  fi
}

has_docker_logs_available() {
  local host ip containers status_file logs_file
  is_check_skipped docker && return 1
  for host in "${!HOST_IPS[@]}"; do
    containers="${HOST_CONTAINERS[$host]:-}"
    containers="${containers//[[:space:],]/}"
    [[ -n "$containers" ]] && return 0
    while IFS= read -r ip; do
      status_file="$(cache_file "$host" "$ip" docker)"
      logs_file="$(cache_file "$host" "$ip" docker_logs)"
      [[ -s "$logs_file" ]] && return 0
      [[ -f "$status_file" ]] && awk -F'[=|]' '$1 == "DOCKER" && $2 != "" && $2 != "discovery" && $2 != "generic" {found=1} END {exit !found}' "$status_file" && return 0
    done < <(host_ips "$host")
  done
  return 1
}

has_configured_docker_containers() { has_docker_logs_available; }

docker_log_menu_args() {
  local host ip container containers status_file output=""
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      status_file="$(cache_file "$host" "$ip" docker)"
      if [[ -n "${HOST_CONTAINERS[$host]:-}" ]]; then
        IFS=',' read -ra containers <<< "${HOST_CONTAINERS[$host]}"
        for container in "${containers[@]}"; do
          container="${container//[[:space:]]/}"
          [[ -n "$container" ]] && output+="$(printf 'log|%s|%s|%s\n%s (%s) %s' "$host" "$ip" "$container" "$host" "$ip" "$container")"$'\n'
        done
      elif [[ -f "$status_file" ]]; then
        while IFS='=|' read -r _ container _ _; do
          [[ -n "$container" && "$container" != discovery && "$container" != generic ]] && output+="$(printf 'log|%s|%s|%s\n%s (%s) %s' "$host" "$ip" "$container" "$host" "$ip" "$container")"$'\n'
        done < "$status_file"
      fi
    done < <(host_ips "$host")
  done
  printf '%s' "$output"
}

configured_docker_menu_args() { docker_log_menu_args; }

dashboard_row_menu_args() {
  local host ip unit state detail container health output=""
  if ! is_check_skipped systemd; then
    for host in "${!HOST_IPS[@]}"; do
      while IFS= read -r ip; do
        while IFS='=|' read -r _ unit state detail; do
          [[ -n "$unit" ]] && output+="$(printf 'systemd|%s|%s|%s\n%s (%s) systemd %s [%s]' "$host" "$ip" "$unit" "$host" "$ip" "$unit" "$state")"$'\n'
        done < <(get_systemd_statuses "$host" "$ip")
      done < <(host_ips "$host")
    done
  fi
  if ! is_check_skipped docker; then
    for host in "${!HOST_IPS[@]}"; do
      while IFS= read -r ip; do
        while IFS='=|' read -r _ container state health; do
          [[ -n "$container" && "$container" != discovery && "$container" != generic ]] && output+="$(printf 'docker|%s|%s|%s\n%s (%s) docker %s [%s/%s]' "$host" "$ip" "$container" "$host" "$ip" "$container" "$state" "$health")"$'\n'
        done < <(get_docker_statuses "$host" "$ip")
      done < <(host_ips "$host")
    done
  fi
  printf '%s' "$output"
}

show_message() {
  local title="$1" message="$2"
  if command -v dialog >/dev/null 2>&1; then
    dialog --title "$title" --msgbox "$message" 8 72 2>/dev/tty || true
  elif command -v whiptail >/dev/null 2>&1; then
    whiptail --title "$title" --msgbox "$message" 8 72 2>/dev/tty || true
  fi
}

render_summary_view() {
  local file
  file="$(mktemp)"
  build_dashboard_text "$(text_width)" > "$file"
  if command -v dialog >/dev/null 2>&1; then
    dialog --title "Health Dashboard Summary" --textbox "$file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
  elif command -v whiptail >/dev/null 2>&1; then
    whiptail --title "Health Dashboard Summary" --textbox "$file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
  fi
  rm -f "$file"
}

systemd_host_menu_args() {
  local host ip unit state detail output=""
  is_check_skipped systemd && return 0
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      while IFS='=|' read -r _ unit state detail; do
        [[ -n "$unit" && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && { output+="$(printf 'systemdhost|%s\n%s' "$host" "$host")"$'\n'; break 2; }
      done < <(get_systemd_statuses "$host" "$ip")
    done < <(host_ips "$host")
  done
  printf '%s' "$output" | awk '!seen[$0]++'
}

docker_host_menu_args() {
  local host ip container state health output=""
  is_check_skipped docker && return 0
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      while IFS='=|' read -r _ container state health; do
        [[ -n "$container" && "$container" != discovery && "$container" != generic && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && { output+="$(printf 'dockerhost|%s\n%s' "$host" "$host")"$'\n'; break 2; }
      done < <(get_docker_statuses "$host" "$ip")
    done < <(host_ips "$host")
  done
  printf '%s' "$output" | awk '!seen[$0]++'
}

systemd_unit_menu_args() {
  local host="$1" ip unit state detail output=""
  while IFS= read -r ip; do
    while IFS='=|' read -r _ unit state detail; do
      [[ -n "$unit" && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && output+="$(printf 'systemd|%s|%s|%s\n%s (%s) %s [%s]' "$host" "$ip" "$unit" "$host" "$ip" "$unit" "$state")"$'\n'
    done < <(get_systemd_statuses "$host" "$ip")
  done < <(host_ips "$host")
  printf '%s' "$output"
}

docker_container_menu_args() {
  local host="$1" ip container state health output=""
  while IFS= read -r ip; do
    while IFS='=|' read -r _ container state health; do
      [[ -n "$container" && "$container" != discovery && "$container" != generic && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && output+="$(printf 'docker|%s|%s|%s\n%s (%s) %s [%s/%s]' "$host" "$ip" "$container" "$host" "$ip" "$container" "$state" "$health")"$'\n'
    done < <(get_docker_statuses "$host" "$ip")
  done < <(host_ips "$host")
  printf '%s' "$output"
}

choose_menu() {
  local title="$1" text="$2" height="${3:-12}" choice status=0
  shift 3
  if command -v dialog >/dev/null 2>&1; then
    choice="$(dialog --cancel-label "Back" --title "$title" --menu "$text" "$(screen_lines)" "$(screen_cols)" "$height" "$@" 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    choice="$(whiptail --cancel-button "Back" --title "$title" --menu "$text" "$(screen_lines)" "$(screen_cols)" "$height" "$@" 2>&1 >/dev/tty)" || status=$?
  else
    return 1
  fi
  [[ "$status" -ne 0 ]] && return 1
  printf '%s' "$choice"
}

render_service_menu() {
  local kind="$1" choice host menu_args=()
  if [[ "$kind" == docker ]]; then
    while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(docker_host_menu_args)
  else
    while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(systemd_host_menu_args)
  fi
  ((${#menu_args[@]})) || { show_message "${kind^}" "No actionable ${kind} rows are available."; return 0; }
  choice="$(choose_menu "${kind^}" "Choose a host." 12 "${menu_args[@]}")" || return 0
  host="${choice#*|}"
  render_host_item_menu "$kind" "$host"
}

render_host_item_menu() {
  local kind="$1" host="$2" choice menu_args=()
  if [[ "$kind" == docker ]]; then
    while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(docker_container_menu_args "$host")
  else
    while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(systemd_unit_menu_args "$host")
  fi
  ((${#menu_args[@]})) || { show_message "$host" "No actionable ${kind} rows are available for $host."; return 0; }
  choice="$(choose_menu "$host ${kind^}" "Choose an item." 12 "${menu_args[@]}")" || return 0
  render_row_context "$choice"
}

render_dashboard() {
  local body choice status=0 menu_args=()
  DASHBOARD_ACTION=refresh
  body="$(build_dashboard_text "$(text_width)")"
  if [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]]; then
    printf '%s\n' "$body"
    DASHBOARD_ACTION=quit
    return 0
  fi
  menu_args+=(summary "View full scrollable summary" refresh "Refresh: re-run tests" recheck "Recheck: re-run checks & tests" docker "Docker" systemd "Systemd")
  menu_args+=(quit "Quit")
  if command -v dialog >/dev/null 2>&1; then
    choice="$(dialog --title "Health Dashboard" --menu "Choose an action. Use Summary for the full scrollable result output." "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    choice="$(whiptail --title "Health Dashboard" --menu "Choose an action. Use Summary for the full scrollable result output." "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  else
    {
      clear 2>/dev/null || true
      printf '%s\n\nCommands: Enter=refresh, r=recheck, q=quit' "$body"
      printf '\n'
    } >/dev/tty
    read -r -s -n 1 choice </dev/tty || true
    [[ -z "$choice" ]] && choice=refresh
    [[ "$choice" == r ]] && choice=recheck
  fi
  if [[ "$status" -ne 0 || "$choice" == quit || "$choice" == q ]]; then DASHBOARD_ACTION=quit; return 0; fi
  if [[ "$choice" == summary ]]; then render_summary_view; DASHBOARD_ACTION=display; return 0; fi
  if [[ "$choice" == docker || "$choice" == systemd ]]; then render_service_menu "$choice"; return 0; fi
  [[ "$choice" == recheck ]] && DASHBOARD_ACTION=recheck || DASHBOARD_ACTION=refresh
  return 0
}

build_dashboard_text() {
  local width="$1" host ip result state detail line printed
  printf 'Health Dashboard | updated %s | interval %ss | timeout %ss\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$REFRESH_INTERVAL" "$(operation_timeout)"
  printf '%*s\n' "$width" '' | tr ' ' '-'
  if ! is_check_skipped icmp || ! is_check_skipped ssh; then
    printf 'ENDPOINTS\n%-18s %-15s %-8s %-12s %s\n' HOST IP CHECK STATUS DETAIL
    for host in "${!HOST_IPS[@]}"; do
      while IFS= read -r ip; do
        if ! is_check_skipped icmp; then result="$(get_ping_result "$host" "$ip")"; state="${result%%|*}"; detail="${result#*|}"; printf '%-18s %-15s %-8s %-12s %s\n' "$host" "$ip" ICMP "$state" "$detail"; fi
        if ! is_check_skipped ssh; then result="$(get_ssh_result "$host" "$ip")"; state="${result%%|*}"; detail="${result#*|}"; printf '%-18s %-15s %-8s %-12s %s\n' "$host" "$ip" SSH "$state" "$detail"; fi
      done < <(host_ips "$host")
    done
  fi
  if ! is_check_skipped systemd; then
    printf '\nSYSTEMD\n%-18s %-15s %-24s %-12s %s\n' HOST IP UNIT STATUS DETAIL
    for host in "${!HOST_IPS[@]}"; do while IFS= read -r ip; do while IFS='=|' read -r _ unit state detail; do [[ -n "$unit" ]] && printf '%-18s %-15s %-24s %-12s %s\n' "$host" "$ip" "$unit" "$state" "$detail"; done < <(get_systemd_statuses "$host" "$ip"); done < <(host_ips "$host"); done
  fi
  if ! is_check_skipped docker; then
    printf '\nDOCKER\n%-18s %-15s %-24s %-12s %s\n' HOST IP CONTAINER STATE HEALTH
    for host in "${!HOST_IPS[@]}"; do while IFS= read -r ip; do while IFS='=|' read -r _ container state health; do [[ -n "$container" ]] && printf '%-18s %-15s %-24s %-12s %s\n' "$host" "$ip" "$container" "$state" "$health"; done < <(get_docker_statuses "$host" "$ip"); done < <(host_ips "$host"); done
  fi
  if ! is_check_skipped timesync; then
    printed=0
    for host in "${!HOST_IPS[@]}"; do
      while IFS= read -r ip; do
        line="$(get_timesync_status "$host" "$ip")"
        [[ "$line" == TIMESYNC=missing\|* ]] && continue
        if [[ "$printed" -eq 0 ]]; then printf '\nTIME SYNC / NTP\n%-18s %-18s %-12s %s\n' HOST SOURCE STATUS DETAIL; printed=1; fi
        state="${line#*=}"; state="${state%%|*}"; detail="${line#*|}"
        printf '%-18s %-18s %-12s %s\n' "$host" summary "$state" "$detail"
        while IFS='=|' read -r _ source provider source_state source_detail; do
          [[ -n "$source" ]] && printf '%-18s %-18s %-12s %s\n' "$host" "$source" "$provider/$source_state" "$source_detail"
        done < <(get_timesync_statuses "$host" "$ip" | awk -F'[=|]' '$1 == "TIMESYNC_SOURCE"')
        break
      done < <(host_ips "$host")
    done
  fi
}
render_logs_menu() {
  local choice status=0 menu_args=()
  while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(docker_log_menu_args)
  if [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]]; then render_logs; return 0; fi
  if command -v dialog >/dev/null 2>&1; then
    choice="$(dialog --cancel-label "Back" --title "Docker Logs" --menu "Select a container to stream cached logs." "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    choice="$(whiptail --cancel-button "Back" --title "Docker Logs" --menu "Select a container to stream cached logs." "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  else
    render_logs; return 0
  fi
  [[ "$status" -ne 0 ]] && return 0
  if [[ "$choice" == log\|* ]]; then IFS='|' read -r _ log_host log_ip log_container <<< "$choice"; render_logs "$log_host" "$log_ip" "$log_container"; render_logs_menu; fi
}

render_row_context() {
  local tag="$1" kind host ip name choice status=0 title
  DASHBOARD_ACTION=display
  IFS='|' read -r kind host ip name <<< "$tag"
  title="$kind: $host ($ip) $name"
  if command -v dialog >/dev/null 2>&1; then
    choice="$(dialog --cancel-label "Back" --title "$title" --menu "Choose an action." 14 76 8 logs "View logs" start "Start" stop "Stop" restart "Restart" 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    choice="$(whiptail --cancel-button "Back" --title "$title" --menu "Choose an action." 14 76 8 logs "View logs" start "Start" stop "Stop" restart "Restart" 2>&1 >/dev/tty)" || status=$?
  else
    return 0
  fi
  [[ "$status" -ne 0 ]] && return 0
  case "$kind:$choice" in
    docker:logs) render_logs "$host" "$ip" "$name" ;;
    systemd:logs) render_systemd_logs "$host" "$ip" "$name" ;;
    docker:start|docker:stop|docker:restart) run_docker_action "$host" "$ip" "$name" "$choice"; DASHBOARD_ACTION=refresh ;;
    systemd:start|systemd:stop|systemd:restart) maybe_prompt_for_sudo_password "$host"; run_systemd_action "$host" "$ip" "$name" "$choice"; DASHBOARD_ACTION=refresh ;;
  esac
}

render_systemd_logs() {
  local host="$1" ip="$2" unit="$3" src stream_file
  src="$(cache_file "$host" "$ip" systemd_logs)"
  stream_file="$(cache_file "$host" "$ip" "systemd_${unit}.stream")"
  get_systemd_logs "$host" "$ip" | awk -v u="$unit" '$0 == "===== " u " =====" {show=1; print; next} /^===== / && show {exit} show {print}' > "$stream_file"
  if [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 && -f "$stream_file" ]] && command -v dialog >/dev/null 2>&1; then
    dialog --title "Systemd Logs: $unit" --tailbox "$stream_file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
  elif [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 && -f "$stream_file" ]] && command -v whiptail >/dev/null 2>&1; then
    whiptail --title "Systemd Logs: $unit" --textbox "$stream_file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
  else
    cat "$stream_file" 2>/dev/null || true
  fi
}

render_logs() {
  local host="${1:-}" ip="${2:-}" container="${3:-}" src stream_file
  clear 2>/dev/null || true
  if [[ -n "$host" && -n "$ip" ]]; then
    src="$(cache_file "$host" "$ip" docker_logs)"
    stream_file="$src"
    if [[ -n "$container" ]]; then
      stream_file="$(cache_file "$host" "$ip" "docker_${container}.stream")"
      get_docker_logs "$host" "$ip" | awk -v c="$container" 'c == "" {print; next} $0 == "===== " c " =====" {show=1; print; next} /^===== / && show {exit} show {print}' > "$stream_file"
    fi
    if [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 && -f "$stream_file" ]] && command -v dialog >/dev/null 2>&1; then
      dialog --title "Docker Logs${container:+: $container}" --tailbox "$stream_file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
      return 0
    elif [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 && -f "$stream_file" ]] && command -v whiptail >/dev/null 2>&1; then
      whiptail --title "Docker Logs${container:+: $container}" --textbox "$stream_file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
      return 0
    fi
    printf '\n# %s %s' "$host" "$ip"; [[ -n "$container" ]] && printf ' container=%s' "$container"; printf '\n'
    cat "$stream_file" 2>/dev/null || true
  else
    for host in "${!HOST_IPS[@]}"; do while IFS= read -r ip; do printf '\n# %s %s\n' "$host" "$ip"; get_docker_logs "$host" "$ip"; done < <(host_ips "$host"); done
  fi
  [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 ]] && { printf '\nPress any key to return...'; read -r -s -n 1 _ || true; }
}
