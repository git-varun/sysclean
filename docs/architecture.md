# SysClean Architecture

SysClean implements a strictly isolated, state-machine-driven architecture designed to manage automated and user-directed system cleanups with safety guarantees.

## Client-Server Separation
SysClean is composed of two primary components:
1. **FastAPI Backend (`bin/sysclean`):** Boots the Python web application and initializes the SQLite WAL database engine. It handles IPC requests, mounts React static assets, runs background planning modules, and triggers execution.
2. **React Web UI:** A modern single-page dashboard serving as the control interface. It allows users to orchestrate scans, approve actions, monitor execution logs, view the rollback registry, and query AI analysis.

## Queue Engine (State Machine)
All operations pass through a strict state machine:
`PROPOSED` → `APPROVED` → `EXECUTING` → `VERIFYING` → `COMPLETED` | `FAILED`

The queue engine automatically handles crash recovery by identifying `EXECUTING` tasks on startup and transitioning them to `FAILED`. Stale tasks are routinely cleared.

## Security & Isolation
- **Validation**: Strict validation prevents deletion of `.ssh`, `.gnupg`, and other protected files/directories.
- **Rollback**: Snapshot-based rollback capabilities compress target metadata/files before destructive operations proceed.
- **AI Bound**: The AI Advisory Engine (`python/ai/advisory.py`) is granted explicit boundaries: it can synthesize and recommend, but cannot execute or bypass the queue validation layer.
- **Root Elevation**: Interactive execution commands that require root privileges are safely wrapped inside `pkexec` to leverage the GUI password prompts without hanging background scripts.
