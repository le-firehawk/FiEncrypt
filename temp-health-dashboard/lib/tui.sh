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
    password="$(dialog --insecure --title "Sudo password: $host" --passwordbox "Enter the sudo password for '${SUDO_USER:-$SSH_USER}' on $host. It is cached for this run only. Cancel tries passwordless sudo." 10 76 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    password="$(whiptail --title "Sudo password: $host" --passwordbox "Enter the sudo password for '${SUDO_USER:-$SSH_USER}' on $host. It is cached for this run only. Cancel tries passwordless sudo." 10 76 2>&1 >/dev/tty)" || status=$?
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

auth_failure_output() {
  grep -Eiq 'permission denied|authentication failed|incorrect password|try again|sorry' <<< "${1:-}"
}

show_operation_result() {
  local title="$1" status="$2" output="$3"
  if [[ "$status" -eq 0 ]]; then
    show_message "$title" "Done."
  else
    show_message "$title" "Failed (exit $status).${output:+\n\n$output}"
  fi
}

stream_remote_logs() {
  local title="$1" host="$2" ip="$3" command="$4" target="${5:-}" file pid
  file="$(mktemp)"
  [[ -n "$target" ]] || target="$(ssh_target_for_ip "$ip")"
  if [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 ]] && command -v dialog >/dev/null 2>&1; then
    (run_ssh "$host" "$target" "$command" > "$file" 2>&1) &
    pid=$!
    dialog --title "$title" --tailbox "$file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  else
    run_ssh "$host" "$target" "$command" 2>&1 | tee "$file"
    [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 ]] && { printf '\nPress any key to return...'; read -r -s -n 1 _ || true; }
  fi
  rm -f "$file"
}

stream_remote_sudo_logs() {
  local title="$1" host="$2" ip="$3" command="$4" target="$5" file pid
  file="$(mktemp)"
  if [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 ]] && command -v dialog >/dev/null 2>&1; then
    (run_sudo_ssh "$host" "$target" "$command" > "$file" 2>&1) &
    pid=$!
    dialog --title "$title" --tailbox "$file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  else
    run_sudo_ssh "$host" "$target" "$command" 2>&1 | tee "$file"
    [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 ]] && { printf '\nPress any key to return...'; read -r -s -n 1 _ || true; }
  fi
  rm -f "$file"
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
        [[ -n "$unit" && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && { output+="$(printf '%s\n ' "$host")"$'\n'; break 2; }
      done < <(get_systemd_statuses "$host" "$ip")
    done < <(host_ips "$host")
  done
  printf '%s' "$output"
}

docker_host_menu_args() {
  local host ip container state health output=""
  is_check_skipped docker && return 0
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      while IFS='=|' read -r _ container state health; do
        [[ -n "$container" && "$container" != discovery && "$container" != generic && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && { output+="$(printf '%s\n ' "$host")"$'\n'; break 2; }
      done < <(get_docker_statuses "$host" "$ip")
    done < <(host_ips "$host")
  done
  printf '%s' "$output"
}

systemd_unit_menu_args() {
  local host="$1" ip unit state detail output=""
  while IFS= read -r ip; do
    while IFS='=|' read -r _ unit state detail; do
      [[ -n "$unit" && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && output+="$(printf '%s\n%s' "$unit" "$state")"$'\n'
    done < <(get_systemd_statuses "$host" "$ip")
  done < <(host_ips "$host")
  printf '%s' "$output"
}

docker_container_menu_args() {
  local host="$1" ip container state health output=""
  while IFS= read -r ip; do
    while IFS='=|' read -r _ container state health; do
      [[ -n "$container" && "$container" != discovery && "$container" != generic && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && output+="$(printf '%s\n%s/%s' "$container" "$state" "$health")"$'\n'
    done < <(get_docker_statuses "$host" "$ip")
  done < <(host_ips "$host")
  printf '%s' "$output"
}

systemd_ip_for_unit() {
  local host="$1" unit="$2" ip name state detail
  while IFS= read -r ip; do
    while IFS='=|' read -r _ name state detail; do
      [[ "$name" == "$unit" && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && { printf '%s' "$ip"; return 0; }
    done < <(get_systemd_statuses "$host" "$ip")
  done < <(host_ips "$host")
  return 1
}

docker_ip_for_container() {
  local host="$1" container="$2" ip name state health
  while IFS= read -r ip; do
    while IFS='=|' read -r _ name state health; do
      [[ "$name" == "$container" && "$state" != SKIPPED && "$state" != SSH_FAILED && "$state" != missing ]] && { printf '%s' "$ip"; return 0; }
    done < <(get_docker_statuses "$host" "$ip")
  done < <(host_ips "$host")
  return 1
}

has_host_streams() {
  local host streams
  for host in "${!HOST_STREAMS[@]}"; do
    streams="${HOST_STREAMS[$host]//[[:space:],]/}"
    [[ -n "$streams" ]] && return 0
  done
  return 1
}

stream_host_menu_args() {
  local host streams output=""
  for host in "${!HOST_STREAMS[@]}"; do
    streams="${HOST_STREAMS[$host]//[[:space:],]/}"
    [[ -n "$streams" ]] && output+="$(printf '%s\n ' "$host")"$'\n'
  done
  printf '%s' "$output"
}

stream_url_menu_args() {
  local host="$1" stream output=""
  IFS=',' read -ra streams <<< "${HOST_STREAMS[$host]:-}"
  for stream in "${streams[@]}"; do
    stream="${stream//[[:space:]]/}"
    [[ -n "$stream" ]] && output+="$(printf '%s\n ' "$stream")"$'\n'
  done
  printf '%s' "$output"
}

ntp_host_menu_args() {
  local host ip line output=""
  is_check_skipped timesync && return 0
  for host in "${!HOST_IPS[@]}"; do
    while IFS= read -r ip; do
      line="$(get_timesync_status "$host" "$ip")"
      [[ "$line" == TIMESYNC=missing\|* ]] && continue
      output+="$(printf '%s\n ' "$host")"$'\n'
      break
    done < <(host_ips "$host")
  done
  printf '%s' "$output"
}

ntp_sources_text() {
  local host="$1" ip source provider source_state source_detail line state detail printed=0
  printf 'NTP Sources for %s\n' "$host"
  printf '%s\n' '--------------------'
  while IFS= read -r ip; do
    line="$(get_timesync_status "$host" "$ip")"
    [[ "$line" == TIMESYNC=missing\|* ]] && continue
    state="${line#*=}"; state="${state%%|*}"; detail="${line#*|}"
    printf 'Summary: %s - %s\n\n' "$state" "$detail"
    while IFS='=|' read -r _ source provider source_state source_detail; do
      [[ -z "$source" ]] && continue
      printed=1
      printf '%-24s %-12s %s\n' "$source" "$provider/$source_state" "$source_detail"
    done < <(get_timesync_statuses "$host" "$ip" | awk -F'[=|]' '$1 == "TIMESYNC_SOURCE"')
    break
  done < <(host_ips "$host")
  [[ "$printed" -eq 0 ]] && printf 'No source details were reported for this host.\n'
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
  while true; do
    menu_args=()
    if [[ "$kind" == docker ]]; then
      while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(docker_host_menu_args)
    else
      while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(systemd_host_menu_args)
    fi
    ((${#menu_args[@]})) || { show_message "${kind^}" "No actionable ${kind} rows are available."; return 0; }
    choice="$(choose_menu "${kind^}" "Choose a host." 12 "${menu_args[@]}")" || return 0
    host="$choice"
    render_host_item_menu "$kind" "$host"
  done
}

render_host_item_menu() {
  local kind="$1" host="$2" choice ip menu_args=()
  while true; do
    menu_args=()
    if [[ "$kind" == docker ]]; then
      while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(docker_container_menu_args "$host")
    else
      while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(systemd_unit_menu_args "$host")
    fi
    ((${#menu_args[@]})) || { show_message "$host" "No actionable ${kind} rows are available for $host."; return 0; }
    choice="$(choose_menu "$host ${kind^}" "Choose an item." 12 "${menu_args[@]}")" || return 0
    if [[ "$kind" == docker ]]; then ip="$(docker_ip_for_container "$host" "$choice" || true)"; else ip="$(systemd_ip_for_unit "$host" "$choice" || true)"; fi
    [[ -n "$ip" ]] && render_row_context "$kind|$host|$ip|$choice"
  done
}

render_streams_menu() {
  local choice host url menu_args=()
  while true; do
    menu_args=()
    while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(stream_host_menu_args)
    ((${#menu_args[@]})) || { show_message "Host Streams" "No host streams are configured."; return 0; }
    choice="$(choose_menu "Host Streams" "Choose a host." 12 "${menu_args[@]}")" || return 0
    host="$choice"
    while true; do
      menu_args=()
      while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(stream_url_menu_args "$host")
      ((${#menu_args[@]})) || { show_message "$host streams" "No streams are configured for $host."; break; }
      url="$(choose_menu "$host streams" "Choose a stream URL." 12 "${menu_args[@]}")" || break
      open_host_stream "$host" "$url"
    done
  done
}

render_ntp_sources_menu() {
  local choice file menu_args=()
  while true; do
    menu_args=()
    while IFS= read -r tag && IFS= read -r label; do menu_args+=("$tag" "$label"); done < <(ntp_host_menu_args)
    ((${#menu_args[@]})) || { show_message "NTP Sources" "No NTP results are available."; return 0; }
    choice="$(choose_menu "NTP Sources" "Choose a host." 12 "${menu_args[@]}")" || return 0
    file="$(mktemp)"
    ntp_sources_text "$choice" > "$file"
    if command -v dialog >/dev/null 2>&1; then
      dialog --title "NTP Sources: $choice" --textbox "$file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
    elif command -v whiptail >/dev/null 2>&1; then
      whiptail --title "NTP Sources: $choice" --textbox "$file" "$(screen_lines)" "$(screen_cols)" 2>/dev/tty || true
    else
      cat "$file"
    fi
    rm -f "$file"
  done
}

start_stream_tunnel() {
  local host="$1" ip="$2" local_port="$3" hostpart="$4" url_port="$5"
  local target password timeout_s jump
  local jump_args=()
  target="$(ssh_target_for_ip "$ip")"
  password="$(ssh_password_for_host "$host")"
  timeout_s="$(operation_timeout)"
  jump="$(ssh_proxy_jump_for_host "$host" 2>/dev/null || true)"
  [[ -n "$jump" ]] && jump_args=(-J "$jump")
  if [[ -n "$password" ]] && command -v sshpass >/dev/null 2>&1; then
    env SSHPASS="$password" SSH_ASKPASS=/bin/false SSH_ASKPASS_REQUIRE=never DISPLAY= \
      sshpass -e ssh -f -N $SSH_OPTS \
      "${jump_args[@]}" \
      -o ExitOnForwardFailure=yes \
      -o BatchMode=no \
      -o PubkeyAuthentication=no \
      -o PreferredAuthentications=password,keyboard-interactive \
      -o NumberOfPasswordPrompts=1 \
      -o ConnectTimeout="$timeout_s" \
      -o IdentitiesOnly=yes \
      -o IdentityAgent=none \
      -L "127.0.0.1:${local_port}:${hostpart}:${url_port}" "$target"
  else
    env SSH_ASKPASS=/bin/false SSH_ASKPASS_REQUIRE=never DISPLAY= \
      ssh -f -N $SSH_OPTS \
      "${jump_args[@]}" \
      -o ExitOnForwardFailure=yes \
      -o BatchMode=yes \
      -o PasswordAuthentication=no \
      -o KbdInteractiveAuthentication=no \
      -o NumberOfPasswordPrompts=0 \
      -o ConnectTimeout="$timeout_s" \
      -o IdentitiesOnly=yes \
      -o IdentityAgent=none \
      -L "127.0.0.1:${local_port}:${hostpart}:${url_port}" "$target"
  fi
}

launch_ffplay() {
  local url="$1" log_file pid
  log_file="$(mktemp)"
  if command -v setsid >/dev/null 2>&1; then
    setsid ffplay "$url" >"$log_file" 2>&1 &
  else
    ffplay "$url" >"$log_file" 2>&1 &
  fi
  pid=$!
  sleep 1
  if ! kill -0 "$pid" 2>/dev/null; then
    show_operation_result "Open stream" 1 "$(cat "$log_file" 2>/dev/null || printf 'ffplay exited immediately')"
    rm -f "$log_file"
    return 1
  fi
  rm -f "$log_file"
  disown "$pid" 2>/dev/null || true
  show_message "Open stream" "ffplay started."
}

open_host_stream() {
  local host="$1" url="$2" ip hostpart url_port local_port rewritten output status
  command -v ffplay >/dev/null 2>&1 || { show_message "ffplay missing" "ffplay is required to open streams."; return 0; }
  ip="$(first_host_ip "$host")"
  hostpart="$(sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://([^/:]+).*#\1#' <<< "$url")"
  url_port="$(sed -nE 's#^[a-zA-Z][a-zA-Z0-9+.-]*://[^/:]+:([0-9]+).*#\1#p' <<< "$url")"
  case "$url" in
    http://*) : "${url_port:=80}" ;;
    https://*) : "${url_port:=443}" ;;
    rtsp://*) : "${url_port:=554}" ;;
    *) launch_ffplay "$url"; return 0 ;;
  esac
  local_port="$((20000 + RANDOM % 20000))"
  if [[ "$hostpart" != "$url" && -n "$url_port" ]]; then
    output="$(start_stream_tunnel "$host" "$ip" "$local_port" "$hostpart" "$url_port" 2>&1)"
    status=$?
    if [[ "$status" -ne 0 ]]; then
      show_operation_result "Open stream" "$status" "${output:-Could not create SSH tunnel.}"
      return 0
    fi
    rewritten="$(sed -E "s#^([a-zA-Z][a-zA-Z0-9+.-]*://)[^/:]+(:[0-9]+)?#\\1127.0.0.1:${local_port}#" <<< "$url")"
    launch_ffplay "$rewritten"
  else
    launch_ffplay "$url"
  fi
}

render_dashboard() {
  local body prompt choice status=0 menu_args=()
  DASHBOARD_ACTION=display
  body="$(build_dashboard_text "$(text_width)")"
  if [[ "${RUN_ONCE:-0}" -eq 1 || ! -t 1 ]]; then
    printf '%s\n' "$body"
    DASHBOARD_ACTION=quit
    return 0
  fi
  render_summary_view
  menu_args+=(summary "View full scrollable summary" refresh "Refresh: re-run tests" recheck "Recheck: re-run checks & tests" docker "Docker" systemd "Systemd")
  is_check_skipped timesync || menu_args+=(ntp "NTP Sources")
  has_host_streams && menu_args+=(streams "Host Streams")
  menu_args+=(quit "Quit")
  prompt="$(printf '%s\n\n%s' "$(printf '%s\n' "$body" | sed -n '1,18p')" "Choose an action. Summary opens the full output.")"
  if command -v dialog >/dev/null 2>&1; then
    choice="$(dialog --title "Health Dashboard" --menu "$prompt" "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
  elif command -v whiptail >/dev/null 2>&1; then
    choice="$(whiptail --title "Health Dashboard" --menu "$prompt" "$(screen_lines)" "$(screen_cols)" 12 "${menu_args[@]}" 2>&1 >/dev/tty)" || status=$?
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
  if [[ "$choice" == docker || "$choice" == systemd ]]; then render_service_menu "$choice"; DASHBOARD_ACTION=display; return 0; fi
  if [[ "$choice" == ntp ]]; then render_ntp_sources_menu; DASHBOARD_ACTION=display; return 0; fi
  if [[ "$choice" == streams ]]; then render_streams_menu; DASHBOARD_ACTION=display; return 0; fi
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
  local tag="$1" kind host ip name choice status=0 title output
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
    docker:start|docker:stop|docker:restart)
      output="$(run_docker_action "$host" "$ip" "$name" "$choice" 2>&1)"; status=$?
      show_operation_result "Docker $choice: $name" "$status" "$output"
      [[ "$status" -eq 0 ]] && run_with_loading 70 90 "Refreshing Docker result for $host" collect_docker_for_host "$host"
      DASHBOARD_ACTION=display ;;
    systemd:start|systemd:stop|systemd:restart)
      maybe_prompt_for_sudo_password "$host"
      output="$(run_systemd_action "$host" "$ip" "$name" "$choice" 2>&1)"; status=$?
      if [[ "$status" -ne 0 ]] && auth_failure_output "$output"; then unset "SUDO_PASSWORDS[$host]"; unset "SSH_PASSWORDS[$host]"; fi
      show_operation_result "Systemd $choice: $name" "$status" "$output"
      [[ "$status" -eq 0 ]] && run_with_loading 70 90 "Refreshing systemd result for $host" collect_systemd_for_host "$host"
      DASHBOARD_ACTION=display ;;
  esac
}

render_systemd_logs() {
  local host="$1" ip="$2" unit="$3" src stream_file command target
  maybe_prompt_for_sudo_password "$host"
  command="$(sudo_journalctl_command "$host" "$unit")"
  target="$(sudo_target_for_ip "$ip")"
  if [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 ]] && command -v dialog >/dev/null 2>&1; then
    stream_remote_sudo_logs "Systemd Logs: $unit" "$host" "$ip" "$command" "$target"
    return 0
  fi
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
    if [[ "${RUN_ONCE:-0}" -eq 0 && -t 1 && -n "$container" ]] && command -v dialog >/dev/null 2>&1; then
      stream_remote_logs "Docker Logs: $container" "$host" "$ip" "docker logs --tail '$DOCKER_LOG_LINES' -f '$container' 2>&1"
      return 0
    fi
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
