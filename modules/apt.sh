#!/usr/bin/env bash
set -euo pipefail

apt_scan() {
  if ! command -v apt-get >/dev/null 2>&1; then
    echo "apt-get not found. Skipping apt module."
    export APT_SKIPPED=1
    return 0
  fi
  export APT_SKIPPED=0
  APT_CACHE_SIZE=$(du -sh /var/cache/apt/archives 2>/dev/null | cut -f1 || echo "0")
  export APT_CACHE_SIZE
}

apt_plan() {
  if [[ "$APT_SKIPPED" -eq 1 ]]; then
    echo "Plan: Skip apt cleanup (apt not installed)."
    return 0
  fi
  echo "Plan: Run 'apt-get autoremove' and 'apt-get clean'."
  echo "Estimated space to free from cache: $APT_CACHE_SIZE"
}

apt_execute() {
  if [[ "$APT_SKIPPED" -eq 1 ]]; then return 0; fi
  
  if [[ "$EUID" -ne 0 ]]; then
    echo "Warning: apt cleanup requires root privileges. Prefixing with sudo."
    sudo apt-get autoremove -y || true
    sudo apt-get clean || true
  else
    apt-get autoremove -y || true
    apt-get clean || true
  fi
}

apt_verify() {
  if [[ "$APT_SKIPPED" -eq 1 ]]; then return 0; fi
  NEW_APT_CACHE_SIZE=$(du -sh /var/cache/apt/archives 2>/dev/null | cut -f1 || echo "0")
  echo "Apt cache size is now: $NEW_APT_CACHE_SIZE"
}
