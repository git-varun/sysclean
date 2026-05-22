# SysClean Runbook

## Managing the Daemon
The SysClean execution engine runs via `syscleand.service`.
- **Status**: `systemctl status syscleand`
- **Restart**: `sudo systemctl restart syscleand`
- **Logs**: `journalctl -u syscleand -f`

## Telemetry
SysClean emits append-only JSONL event logs containing timestamped telemetry for all operations.
- **Location**: `~/.local/share/sysclean/runtime/events/events.jsonl`

## Observability Dashboard
To view a live snapshot of the queue, rollback history, and reclaimable storage without executing commands, use the TUI:
```bash
sysclean-cli tui
```

## AI Advisory
To fetch safe cleanup recommendations without directly enqueuing them:
```bash
sysclean-cli advise docker
sysclean-cli advise apt
sysclean-cli advise storage
```
