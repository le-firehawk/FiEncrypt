#!/usr/bin/env bash

get_ping_result() {
  local key
  key="$(safe_key "$1_$2")"
  cat "$CACHE_DIR/${key}.ping" 2>/dev/null || echo "FAIL|missing"
}

get_snapshot() {
  local key
  key="$(safe_key "$1_$2")"
  cat "$CACHE_DIR/${key}.snapshot" 2>/dev/null || echo "BOOTSTRAP=FAIL"
}

status_icon() {
  case "$1" in
    PASS|active|healthy|running) printf '✓' ;;
    WARN) printf '!' ;;
    *) printf '✗' ;;
  esac
}

status_color() {
  case "$1" in
    PASS|active|healthy|running) printf '\033[32m' ;;
    WARN) printf '\033[33m' ;;
    *) printf '\033[31m' ;;
  esac
}
