#!/usr/bin/env bash
set -euo pipefail

docker_scan() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker not found. Skipping docker module."
    export DOCKER_SKIPPED=1
    return 0
  fi
  export DOCKER_SKIPPED=0
  DOCKER_RECLAIMABLE=$(docker system df --format '{{.Reclaimable}}' | awk '{ sum+=$1 } END { print sum }' || echo "0")
  export DOCKER_RECLAIMABLE
}

docker_plan() {
  if [[ "$DOCKER_SKIPPED" -eq 1 ]]; then
    echo "Plan: Skip docker cleanup (docker not installed)."
    return 0
  fi
  echo "Plan: Run 'docker system prune -f'."
  echo "Estimated reclaimable space: ${DOCKER_RECLAIMABLE}B"
}

docker_execute() {
  if [[ "$DOCKER_SKIPPED" -eq 1 ]]; then return 0; fi
  docker system prune -f || echo "Docker prune failed or partially completed."
}

docker_verify() {
  if [[ "$DOCKER_SKIPPED" -eq 1 ]]; then return 0; fi
  NEW_DOCKER_RECLAIMABLE=$(docker system df --format '{{.Reclaimable}}' | awk '{ sum+=$1 } END { print sum }' || echo "0")
  echo "Docker reclaimable space is now: ${NEW_DOCKER_RECLAIMABLE}B"
}
