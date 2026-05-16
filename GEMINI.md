# SysClean Project Instructions

## Project Overview
SysClean is an AI-assisted workstation operations platform for Ubuntu developer environments. It handles cleanup, optimization, and predictive maintenance.

## Core Conventions
- **Language Blend:** Bash for low-level CLI/orchestration; Python 3.11+ for intelligence, analytics, and complex logic.
- **Safety First:** All destructive operations MUST be rollback-aware and validated against governance constraints.
- **Data Persistence:** Use SQLite for local operational data (queue, journal, registry, telemetry).
- **AI Integration:** Prefer local AI via Ollama for recommendations and semantic analysis.
- **UI Standards:** Textual for TUI, FastAPI for Web UI, Rich for CLI formatting.

## Architecture
- **Queue-Based Execution:** All cleanup tasks MUST be enqueued and processed via the transactional queue engine.
- **Plugin System:** Use manifest-based plugins (YAML) with capability gating.
- **Safety Model:** Implement risk tiers (`safe`, `balanced`, `aggressive`) and protected asset detection (`.ssh`, `.env`, wallets, etc.).

## Documentation
- **PRD:** Located at `docs/PRD.md`.
