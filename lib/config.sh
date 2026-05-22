#!/usr/bin/env bash

load_config() {
  local config_path="$1"

  if [[ ! -f "$config_path" ]]; then
    echo "Missing config: $config_path"
    exit 1
  fi

  # Python validator was removed in Phase 0 architecture reset
  # Configuration validation is handled natively by modules now
}