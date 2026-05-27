# SysClean Runbook

## Running the Web UI & Daemon
The SysClean service is run as a unified FastAPI Web application. It starts the Uvicorn web server and handles background workers for database queue operations.
- **Start Service:** Run the launcher binary `sysclean`
- **Standard Execution:** `sysclean` (by default binds to port `8080`)
- **Development Mode:** `SYSCLEAN_ENV=dev sysclean` (runs on port `8000` with DEBUG logging enabled)

## Telemetry & Logging
SysClean emits append-only JSONL event logs containing timestamped telemetry for all planning and execution operations.
- **Events Log Path:** `~/.local/share/sysclean/events.jsonl`
- **Application Database:** `~/.local/share/sysclean/sysclean.db`

## Observability Dashboard
SysClean features a modern glassmorphism React Web UI. Once you launch `sysclean`, navigate to:
`http://localhost:8080/` (or port `8000` in dev mode)
This dashboard allows you to:
- Trigger full system scans to analyze docker caches, apt packages, and system temp directories.
- Approve and enqueue generated cleanup tasks.
- Track active executions and view database telemetry in real-time.
- View rollback metadata archives.

## AI Advisory Integration
To consult the AI Advisory Engine for recommendations (leveraging local Ollama or cloud-based Gemini APIs), click the **Ask AI Advisory** button on the Web Dashboard. You can request reports on:
1. **Queue Analysis / Storage:** Overview of queue status and potential space savings.
2. **Docker:** Unused containers, dangling images, and system pruning safety.
3. **APT:** Package dependencies, orphan packages, and package cache state.

