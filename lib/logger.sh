#!/usr/bin/env bash

LOG_DIR="${HOME}/.local/state/sysclean/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/sysclean-$(date +%F).log"

init_logger() {
  exec > >(tee -a "$LOG_FILE") 2>&1
}

info() {
  echo "[INFO] $*"
}

warn() {
  echo "[WARN] $*"
}

error() {
  echo "[ERROR] $*"
}