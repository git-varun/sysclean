#!/usr/bin/env bash
set -euo pipefail

cache_scan() {
  export CACHE_DIR="$HOME/.cache"
  if [ -d "$CACHE_DIR" ]; then
    CACHE_SIZE=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")
    export CACHE_SIZE
  else
    export CACHE_SIZE="0"
  fi
}

cache_plan() {
  echo "Plan: Clear the user's .cache directory."
  echo "Estimated space to free: $CACHE_SIZE"
}

cache_execute() {
  if [ -d "$CACHE_DIR" ]; then
    # We will safely remove the contents of the cache directory, leaving the directory itself
    find "$CACHE_DIR" -mindepth 1 -delete || true
  else
    echo "No cache directory found to clean."
  fi
}

cache_verify() {
  if [ -d "$CACHE_DIR" ]; then
    NEW_CACHE_SIZE=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")
    echo "Cache size is now: $NEW_CACHE_SIZE"
  fi
}
