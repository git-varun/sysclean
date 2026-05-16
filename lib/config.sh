#!/usr/bin/env bash

load_config() {
  local config_path="$1"

  if [[ ! -f "$config_path" ]]; then
    echo "Missing config: $config_path"
    exit 1
  fi

  python3 python/validation/validator.py "$config_path"
}