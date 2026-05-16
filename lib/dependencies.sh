#!/usr/bin/env bash

dependency_doctor() {
  local dependencies=(
    jq
    yq
    sqlite3
    python3
    fzf
    gum
    ncdu
    dust
  )

  for dep in "${dependencies[@]}"; do
    if command -v "$dep" >/dev/null 2>&1; then
      echo "[OK] $dep"
    else
      echo "[MISSING] $dep"
    fi
  done
}