#!/usr/bin/env bash

set -euo pipefail

PREFIX="${HOME}/.local"
BIN_DIR="${PREFIX}/bin"
CONFIG_DIR="${HOME}/.config/sysclean"
DATA_DIR="${HOME}/.local/share/sysclean"
LOG_DIR="${HOME}/.local/state/sysclean"

mkdir -p "$BIN_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$LOG_DIR"

cp -r config "$CONFIG_DIR/"
cp -r runtime "$DATA_DIR/"

chmod +x bin/sysclean
ln -sf "$(pwd)/bin/sysclean" "$BIN_DIR/sysclean"

if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

cat <<EOF

SysClean installed successfully.

Binary:
  ~/.local/bin/sysclean

Config:
  ~/.config/sysclean

Logs:
  ~/.local/state/sysclean

EOF