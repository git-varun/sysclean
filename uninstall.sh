#!/usr/bin/env bash

set -euo pipefail

rm -f "$HOME/.local/bin/sysclean"
rm -rf "$HOME/.config/sysclean"
rm -rf "$HOME/.local/share/sysclean"
rm -rf "$HOME/.local/state/sysclean"

echo "SysClean removed"