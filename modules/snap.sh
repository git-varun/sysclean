#!/usr/bin/env bash
set -euo pipefail

snap_scan() {
  if ! command -v snap >/dev/null 2>&1; then
    echo "snap not found. Skipping snap module."
    export SNAP_SKIPPED=1
    return 0
  fi
  export SNAP_SKIPPED=0
  
  # Rough heuristic: disabled snaps take up space
  SNAP_DISABLED_COUNT=$(snap list --all 2>/dev/null | awk '/disabled/{print $1, $3}' | wc -l || echo "0")
  export SNAP_DISABLED_COUNT
}

snap_plan() {
  if [[ "$SNAP_SKIPPED" -eq 1 ]]; then
    echo "Plan: Skip snap cleanup (snap not installed)."
    return 0
  fi
  echo "Plan: Remove old/disabled snap revisions."
  echo "Estimated disabled snaps to remove: $SNAP_DISABLED_COUNT"
}

snap_execute() {
  if [[ "$SNAP_SKIPPED" -eq 1 ]]; then return 0; fi
  if [[ "$SNAP_DISABLED_COUNT" -eq 0 ]]; then
    echo "No disabled snaps to remove."
    return 0
  fi
  
  # Loop to remove disabled snaps
  snap list --all | awk '/disabled/{print $1, $3}' |
    while read snapname revision; do
        if [[ "$EUID" -ne 0 ]]; then
            sudo snap remove "$snapname" --revision="$revision" || true
        else
            snap remove "$snapname" --revision="$revision" || true
        fi
    done
}

snap_verify() {
  if [[ "$SNAP_SKIPPED" -eq 1 ]]; then return 0; fi
  NEW_SNAP_DISABLED_COUNT=$(snap list --all 2>/dev/null | awk '/disabled/{print $1, $3}' | wc -l || echo "0")
  echo "Disabled snaps remaining: $NEW_SNAP_DISABLED_COUNT"
}
