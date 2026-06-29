#!/usr/bin/env bash

host_ips() {
  local host="$1"
  IFS=',' read -ra ips <<< "${HOST_IPS[$host]}"
  printf '%s\n' "${ips[@]}" | sed 's/[[:space:]]//g' | sed '/^$/d'
}

clear_cycle_cache() { mkdir -p "$CACHE_DIR"; rm -f "$CACHE_DIR"/*; }


mark_check_skipped() {
  local check="$1" host ip service container
  for host in "${!HOST_IPS[@]}"; do
    case "$check" in
      icmp)
        while IFS= read -r ip; do printf 'SKIPPED|disabled by --skip-checks\n' > "$(cache_file "$host" "$ip" ping)"; done < <(host_ips "$host") ;;
      ssh)
        while IFS= read -r ip; do printf 'SKIPPED|disabled by --skip-checks\n' > "$(cache_file "$host" "$ip" ssh)"; done < <(host_ips "$host") ;;
      systemd)
        while IFS= read -r ip; do
          : > "$(cache_file "$host" "$ip" systemd)"
          IFS=',' read -ra services <<< "${HOST_SERVICES[$host]:-}"
          for service in "${services[@]}"; do service="${service//[[:space:]]/}"; [[ -n "$service" ]] && printf 'SYSTEMD=%s|SKIPPED|disabled by --skip-checks\n' "$service" >> "$(cache_file "$host" "$ip" systemd)"; done
        done < <(host_ips "$host") ;;
      docker)
        while IFS= read -r ip; do
          : > "$(cache_file "$host" "$ip" docker_logs)"
          : > "$(cache_file "$host" "$ip" docker)"
          if [[ -n "${HOST_CONTAINERS[$host]:-}" ]]; then
            IFS=',' read -ra containers <<< "${HOST_CONTAINERS[$host]}"
            for container in "${containers[@]}"; do container="${container//[[:space:]]/}"; [[ -n "$container" ]] && printf 'DOCKER=%s|SKIPPED|disabled by --skip-checks\n' "$container" >> "$(cache_file "$host" "$ip" docker)"; done
          else
            printf 'DOCKER=discovery|SKIPPED|disabled by --skip-checks\n' > "$(cache_file "$host" "$ip" docker)"
          fi
        done < <(host_ips "$host") ;;
      timesync|ntp)
        while IFS= read -r ip; do printf 'TIMESYNC=SKIPPED|disabled by --skip-checks\n' > "$(cache_file "$host" "$ip" timesync)"; done < <(host_ips "$host") ;;
    esac
  done
}


collect_all() {
  clear_cycle_cache
  render_loading "Running ICMP checks..."
  collect_ping_parallel
  render_loading "Running SSH checks..."
  collect_ssh_parallel
  maybe_prompt_for_ssh_password
  render_loading "Running systemd checks..."
  collect_systemd_parallel
  render_loading "Running Docker checks..."
  collect_docker_parallel
  render_loading "Running NTP/time-sync checks..."
  collect_timesync_parallel
}

ping_one() {
  local host="$1" ip="$2" tmp timeout_s lat
  tmp="$(cache_file "$host" "$ip" ping.raw)"
  timeout_s="$(operation_timeout)"
  if ping -n -c1 -W"$timeout_s" "$ip" > "$tmp" 2>/dev/null; then
    lat="$(sed -n 's/.*time=\([0-9.]*\).*/\1/p' "$tmp" | head -1)"
    printf 'PASS|%sms\n' "${lat:-unknown}"
  else
    log_event WARN "icmp ping failed host=$host ip=$ip timeout=${timeout_s}s"
    printf 'FAIL|unreachable\n'
  fi
  rm -f "$tmp"
}

collect_ping_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do
    (
      local ip
      while IFS= read -r ip; do
        log_event INFO "icmp ping host=$host ip=$ip"
        ping_one "$host" "$ip" > "$(cache_file "$host" "$ip" ping)"
      done < <(host_ips "$host")
    ) &
  done
  wait
}

ssh_password_for_host() {
  local host="$1"
  [[ -n "${SSH_PASSWORDS[$host]:-}" ]] && printf '%s' "${SSH_PASSWORDS[$host]}" || printf '%s' "${SSH_PASSWORD:-}"
}

run_ssh() {
  local host="$1" target="$2" command="$3" password timeout_s jump jump_args=()
  password="$(ssh_password_for_host "$host")"
  timeout_s="$(operation_timeout)"
  jump="$(ssh_proxy_jump_for_host "$host" 2>/dev/null || true)"
  [[ -n "$jump" ]] && jump_args=(-J "$jump")
  if [[ -n "$password" ]] && command -v sshpass >/dev/null 2>&1; then
    env SSHPASS="$password" SSH_ASKPASS=/bin/false SSH_ASKPASS_REQUIRE=never DISPLAY= \
      timeout "${timeout_s}s" sshpass -e ssh -T $SSH_OPTS \
      "${jump_args[@]}" \
      -o BatchMode=no \
      -o PubkeyAuthentication=no \
      -o PreferredAuthentications=password,keyboard-interactive \
      -o NumberOfPasswordPrompts=1 \
      -o ConnectTimeout="$timeout_s" \
      -o IdentitiesOnly=yes \
      -o IdentityAgent=none \
      "$target" "$command"
  else
    env SSH_ASKPASS=/bin/false SSH_ASKPASS_REQUIRE=never DISPLAY= \
      timeout "${timeout_s}s" ssh -n -T $SSH_OPTS \
      "${jump_args[@]}" \
      -o BatchMode=yes \
      -o PasswordAuthentication=no \
      -o KbdInteractiveAuthentication=no \
      -o NumberOfPasswordPrompts=0 \
      -o ConnectTimeout="$timeout_s" \
      -o IdentitiesOnly=yes \
      -o IdentityAgent=none \
      "$target" "$command"
  fi
}

ssh_error_reason_text() {
  local output="$1" status="${2:-}"
  awk 'NF && $0 !~ /^\+/ { print; found=1; exit } END { if (!found) printf "%s", "connection_failed" }' <<< "$output"
  [[ -n "$status" && -z "$output" && "$status" == 124 ]] && printf 'timeout after %ss' "$(operation_timeout)"
  return 0
}

collect_ssh_for_host() {
  local host="$1" ip key target output status reason attempt max_attempts
  while IFS= read -r ip; do
    key="$(cache_file "$host" "$ip" ssh)"
    target="$(ssh_target_for_ip "$ip")"
    max_attempts=$((SSH_CHECK_RETRIES + 1))
    for ((attempt=1; attempt<=max_attempts; attempt++)); do
      if output="$(run_ssh "$host" "$target" true 2>&1)"; then
        : > "$(cache_file "$host" "$ip" ssh.err)"
        printf 'PASS|connected\n' > "$key"
        break
      fi
      status=$?
      reason="$(ssh_error_reason_text "$output" "$status")"
      printf '%s\n' "$output" > "$(cache_file "$host" "$ip" ssh.err)"
      printf 'FAIL|%s\n' "$reason" > "$key"
    done
  done < <(host_ips "$host")
}

collect_ssh_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do collect_ssh_for_host "$host" & done
  wait
}

ssh_ok_ip() {
  local host="$1" ip result
  while IFS= read -r ip; do
    result="$(get_ssh_result "$host" "$ip")"
    [[ "${result%%|*}" == PASS ]] && { printf '%s' "$ip"; return 0; }
  done < <(host_ips "$host")
  return 1
}

ssh_failed_reason() { local r; r="$(get_ssh_result "$1" "$2")"; printf '%s' "${r#*|}"; }

systemd_result_message() {
  case "$2" in
    active) printf '%s is active and running' "$1" ;;
    failed) printf '%s is failed; inspect journalctl -u %s' "$1" "$1" ;;
    inactive) printf '%s is inactive' "$1" ;;
    *) printf '%s returned systemd state %s' "$1" "$2" ;;
  esac
}

ntp_sources_command() {
  cat <<'REMOTE'
chronyc -n sources 2>/dev/null | awk '
function detail(state) {
  if (state == "*") return "selected source currently disciplining the clock";
  if (state == "+") return "acceptable source combined with the selected source";
  if (state == "-") return "acceptable source excluded by the selection algorithm";
  if (state == "?") return "unreachable or not enough measurements";
  if (state == "x") return "false ticker rejected by chrony";
  if (state == "~") return "source has too much time variability";
  return "chrony source state " state;
}
/^[\^=][*+?x~ -]/ {state=substr($1,2,1); print $2 "|chrony|" state "|" detail(state)}'
ntpq -pn 2>/dev/null | awk '
function detail(state) {
  if (state == "*") return "selected peer currently synchronizing the clock";
  if (state == "+") return "candidate peer included by the clock selection algorithm";
  if (state == "#") return "selected backup peer, more than the maximum number of sources";
  if (state == "o") return "PPS peer currently synchronizing the clock";
  if (state == "x") return "false ticker rejected by ntpd";
  if (state == ".") return "discarded because of table overflow or sanity checks";
  if (state == "-") return "discarded by the cluster algorithm";
  if (state == " ") return "reachable peer not currently selected";
  return "ntpd peer state " state;
}
NR > 2 && $1 !~ /^=+$/ {
  state=substr($0,1,1); peer=$1;
  if (state ~ /[*+#ox.-]/) sub(/^./, "", peer); else state=" ";
  if (peer != "" && peer != "remote") print peer "|ntpq|" state "|" detail(state);
}'
timedatectl show-timesync --property=ServerName --value 2>/dev/null | awk 'NF {print $0 "|timedatectl|server|configured systemd-timesyncd server"}'
REMOTE
}

ntp_source_command() { ntp_sources_command; }

collect_systemd_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do
    (
      local selected ip service state reason target logs_file
      selected="$(ssh_ok_ip "$host" || true)"
      while IFS= read -r ip; do
        : > "$(cache_file "$host" "$ip" systemd)"
        logs_file="$(cache_file "$host" "$ip" systemd_logs)"
        : > "$logs_file"
        IFS=',' read -ra services <<< "${HOST_SERVICES[$host]:-}"
        for service in "${services[@]}"; do
          service="${service//[[:space:]]/}"; [[ -z "$service" ]] && continue
          if [[ -z "$selected" || "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" != PASS ]]; then
            reason="$(ssh_failed_reason "$host" "$ip")"
            if [[ "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" == SKIPPED ]]; then
              printf 'SYSTEMD=%s|SKIPPED|SSH skipped: %s\n' "$service" "$reason" >> "$(cache_file "$host" "$ip" systemd)"
            else
              printf 'SYSTEMD=%s|SSH_FAILED|%s\n' "$service" "$reason" >> "$(cache_file "$host" "$ip" systemd)"
            fi
          elif [[ "$ip" != "$selected" ]]; then
            printf 'SYSTEMD=%s|SKIPPED|checked via %s\n' "$service" "$selected" >> "$(cache_file "$host" "$ip" systemd)"
          else
            target="$(ssh_target_for_ip "$ip")"
            state="$(run_ssh "$host" "$target" "systemctl is-active '$service' 2>/dev/null || true" 2>/dev/null || true)"
            [[ -z "$state" ]] && state=unknown
            printf 'SYSTEMD=%s|%s|%s\n' "$service" "$state" "$(systemd_result_message "$service" "$state")" >> "$(cache_file "$host" "$ip" systemd)"
            { printf '===== %s =====\n' "$service"; run_ssh "$host" "$target" "journalctl -u '$service' -n '$DOCKER_LOG_LINES' --no-pager 2>&1" 2>/dev/null || true; } >> "$logs_file"
          fi
        done
      done < <(host_ips "$host")
    ) &
  done
  wait
}

run_systemd_action() {
  local host="$1" ip="$2" unit="$3" action="$4" target
  target="$(ssh_target_for_ip "$ip")"
  run_ssh "$host" "$target" "sudo -n systemctl '$action' '$unit'" >/dev/null 2>&1 || true
}

run_docker_action() {
  local host="$1" ip="$2" container="$3" action="$4" target
  target="$(ssh_target_for_ip "$ip")"
  run_ssh "$host" "$target" "docker '$action' '$container'" >/dev/null 2>&1 || true
}

collect_docker_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do
    (
      local selected ip reason target names container inspect state health logs_file status_file
      selected="$(ssh_ok_ip "$host" || true)"
      while IFS= read -r ip; do
        status_file="$(cache_file "$host" "$ip" docker)"; logs_file="$(cache_file "$host" "$ip" docker_logs)"
        : > "$status_file"; : > "$logs_file"
        if [[ -z "$selected" || "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" != PASS ]]; then
          reason="$(ssh_failed_reason "$host" "$ip")"
          if [[ "$(get_ssh_result "$host" "$ip" | cut -d'|' -f1)" == SKIPPED ]]; then
            printf 'DOCKER=discovery|SKIPPED|SSH skipped: %s\n' "$reason" > "$status_file"
          else
            printf 'DOCKER=discovery|SSH_FAILED|%s\n' "$reason" > "$status_file"
          fi
          continue
        fi
        [[ "$ip" != "$selected" ]] && { printf 'DOCKER=generic|SKIPPED|checked via %s\n' "$selected" > "$status_file"; continue; }
        target="$(ssh_target_for_ip "$ip")"
        if [[ -n "${HOST_CONTAINERS[$host]:-}" ]]; then IFS=',' read -ra names <<< "${HOST_CONTAINERS[$host]}"; else mapfile -t names < <(run_ssh "$host" "$target" "docker ps --format '{{.Names}}'" 2>/dev/null || true); fi
        for container in "${names[@]}"; do
          container="${container//[[:space:]]/}"; [[ -z "$container" ]] && continue
          inspect="$(run_ssh "$host" "$target" "docker inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' '$container'" 2>/dev/null || true)"
          state="${inspect%%|*}"; health="${inspect#*|}"; [[ -z "$inspect" || "$state" == "$inspect" ]] && { state=missing; health=unknown; }
          printf 'DOCKER=%s|%s|%s\n' "$container" "$state" "$health" >> "$status_file"
          { printf '===== %s =====\n' "$container"; run_ssh "$host" "$target" "docker logs --tail '$DOCKER_LOG_LINES' '$container' 2>&1" 2>/dev/null || true; } >> "$logs_file"
        done
      done < <(host_ips "$host")
    ) &
  done
  wait
}

collect_timesync_parallel() {
  local host
  for host in "${!HOST_IPS[@]}"; do
    (
      local selected ip target sync sources source provider source_state detail status_file primary
      selected="$(ssh_ok_ip "$host" || true)"
      while IFS= read -r ip; do : > "$(cache_file "$host" "$ip" timesync)"; done < <(host_ips "$host")
      ip="$(host_ips "$host" | head -1)"
      status_file="$(cache_file "$host" "$ip" timesync)"
      if [[ "${HOST_TIMESYNC[$host]:-1}" =~ ^(0|no|false|disabled)$ ]]; then printf 'TIMESYNC=SKIPPED|disabled in HOST_TIMESYNC\n' > "$status_file"; exit 0; fi
      if [[ -z "$selected" ]]; then printf 'TIMESYNC=SKIPPED|SSH failed: %s\n' "$(ssh_failed_reason "$host" "$ip")" > "$status_file"; exit 0; fi
      target="$(ssh_target_for_ip "$selected")"
      sync="$(run_ssh "$host" "$target" "timedatectl show -p NTPSynchronized --value 2>/dev/null || true" 2>/dev/null || true)"
      sources="$(run_ssh "$host" "$target" "$(ntp_sources_command)" 2>/dev/null | sed '/^$/d' || true)"
      [[ -z "$sources" ]] && exit 0
      primary="$(printf '%s\n' "$sources" | awk -F'|' '$3 == "*" || $3 == "o" {print $1; found=1; exit} END {if (!found) exit 1}' || printf '%s\n' "$sources" | cut -d'|' -f1 | head -1)"
      [[ -z "$primary" ]] && primary=unknown
      if [[ "$sync" == yes ]]; then printf 'TIMESYNC=PASS|synchronized=yes primary=%s\n' "$primary" > "$status_file"; else printf 'TIMESYNC=FAIL|synchronized=%s primary=%s\n' "${sync:-unknown}" "$primary" > "$status_file"; fi
      while IFS='|' read -r source provider source_state detail; do
        [[ -n "$source" ]] && printf 'TIMESYNC_SOURCE=%s|%s|%s|%s\n' "$source" "${provider:-unknown}" "${source_state:-unknown}" "${detail:-source reported}"
      done <<< "$sources" >> "$status_file"
    ) &
  done
  wait
}
