#!/usr/bin/env bash

PROTECTED_PATHS=(
  "$HOME/.ssh"
  "$HOME/.gnupg"
  "$HOME/.aws"
  "$HOME/.kube"
)

validate_environment() {
  if [[ "$EUID" -eq 0 ]]; then
    echo "Do not run as root"
    exit 1
  fi

  command -v python3 >/dev/null || {
    echo "python3 required"
    exit 1
  }
}

is_protected_path() {
  local path="$1"

  for protected in "${PROTECTED_PATHS[@]}"; do
    if [[ "$path" == "$protected"* ]]; then
      return 0
    fi
  done

  return 1
}