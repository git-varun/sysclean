# SysClean Rollback Guide

SysClean creates \`tar.gz\` snapshots using deterministic hashing.

## How to rollback
1. Identify the rollback ID from the TUI or SQLite DB.
2. Run \`sysclean-cli rollback <id>\`.

The engine validates the \`tar.gz\` hash before attempting restore to prevent corruption.
