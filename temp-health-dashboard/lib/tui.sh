#!/usr/bin/env bash

declare -Ag SSH_PASSWORDS=()
declare -Ag SSH_PASSWORD_DECLINED=()
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

has_configured_docker_containers() {
  local host containers
  for host in "${!HOST_IPS[@]}"; do
    containers="${HOST_CONTAINERS[$host]:-}"
    containers="${containers//[[:space:],]/}"
    [[ -n "$containers" ]] && return 0
  done
  return 1
}

configured_docker_menu_args() {
  local host ip container containers
  for host in "${!HOST_IPS[@]}"; do
    [[ -n "${HOST_CONTAINERS[$host]:-}" ]] || continue
    while IFS= read -r ip; do
      IFS=',' read -ra containers <<< "${HOST_CONTAINERS[$host]}"
      for container in "${containers[@]}"; do
        container="${container//[[:space:]]/}"
        [[ -n "$container" ]] && printf 'log|%s|%s|%s\n%s %s\n' "$host" "$ip" "$container" "$host/$ip" "$container"
      done
    done < <(host_ips "$host")
  done
}

render_dashboard() {
  local body choice status=0 menu_args=()
  body="$(build_dashboard_text "$(text_width)")"
  if [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]]; then
    printf '%s\n' "$body"
    return 0
  fi
  menu_args+=(refresh "Refresh display" recheck "Recheck now")
  has_configured_docker_containers && menu_args+=(logs "Docker Logs")
  menu_args+=(quit "Quit")
  if command -v dialog >/dev/null 2>&1; then
    choice="$(dialog --title "Health Dashboard" --menu "$body" "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    choice="$(whiptail --title "Health Dashboard" --menu "$body" "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  else
    clear 2>/dev/null || true
    printf '%s\n\nCommands: Enter=refresh, q=quit' "$body"
    has_configured_docker_containers && printf ', l=logs'
    printf '\n'
    read -r -s -n 1 choice || true
    [[ -z "$choice" ]] && choice=refresh
  fi
  [[ "$status" -ne 0 || "$choice" == quit || "$choice" == q ]] && { printf '%s\n' quit; return 0; }
  [[ "$choice" == logs || "$choice" == l ]] && has_configured_docker_containers && { render_logs_menu; printf '%s\n' refresh; return 0; }
  [[ "$choice" == recheck ]] && printf '%s\n' recheck || printf '%s\n' refresh
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
  while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(configured_docker_menu_args)
  menu_args+=(back "Back to summary")
  if [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]]; then render_logs; return 0; fi
  if command -v dialog >/dev/null 2>&1; then
    choice="$(dialog --title "Docker Logs" --menu "Select a configured container to stream cached logs." "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    choice="$(whiptail --title "Docker Logs" --menu "Select a configured container to stream cached logs." "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  else
    render_logs; return 0
  fi
  [[ "$status" -ne 0 || "$choice" == back ]] && return 0
  if [[ "$choice" == log\|* ]]; then IFS='|' read -r _ log_host log_ip log_container <<< "$choice"; render_logs "$log_host" "$log_ip" "$log_container"; render_logs_menu; fi
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
