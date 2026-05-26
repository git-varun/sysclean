#!/usr/bin/env bash

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

header() {
  echo -e "${BLUE}================================================${NC}"
  echo -e "${GREEN}$1${NC}"
  echo -e "${BLUE}================================================${NC}"
}

show_queue() {
  "$PYTHON" "$ROOT_DIR/python/tui/cli_queue.py"
}