# Plugin Development Guide

Plugins reside in \`modules/<name>/\`.

## Required Files
- \`manifest.yml\` (metadata, dependencies, risk tier)
- \`module.sh\` (entrypoint script)

## Execution Contract
- **--plan**: Output strictly JSON estimating targets and bytes without side-effects.
- **--execute**: Remove strictly the approved targets.
