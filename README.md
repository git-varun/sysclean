<!-- TITLE AND OVERVIEW -->
# SysClean

**AI-Assisted Workstation Operations Platform**

SysClean is a modular, AI-native operating layer for Ubuntu developer environments. Originally conceived as a cleanup utility, it has evolved into an autonomous remediation, predictive maintenance, and workstation health system. SysClean combines the low-level reliability of Bash orchestration with the high-level intelligence of Python, enabling safe, autonomous, and self-healing local infrastructure management.

<!-- FEATURE LIST -->
<!-- Update this section when adding new core capabilities -->
## 🚀 Key Features

- **Safety First & Perfect Rollback:** Zero-risk operations backed by an eBPF-powered (or syscall-tracing) rollback registry. Every deletion is meticulously recorded and encrypted into a tarball, allowing single-command perfect restoration. Protected asset detection automatically shields sensitive files (`.ssh`, `.gnupg`, wallets, etc.).
- **Local AI Intelligence:** Integrated with Ollama, Sentence-Transformers, and semantic infrastructure graphs (NetworkX). SysClean understands the dependencies of your system (packages, containers, caches) and provides highly confident, actionable maintenance recommendations without sending data to external servers.
- **Autonomous & Predictive:** A background daemon continuously monitors telemetry and storage metrics. Using machine learning models (scikit-learn), SysClean forecasts disk exhaustion and can autonomously enqueue and execute safe-tier cleanup tasks before critical failures occur.
- **Transactional Execution Queue:** High-concurrency state management backed by SQLite (WAL mode). All operations transition atomically through explicit states (`Proposed` -> `Approved` -> `Locked` -> `Executing` -> `Verified` -> `Completed`/`Failed`), ensuring the system can recover perfectly even from a hard crash or power loss.
- **Modular Plugin Architecture:** Capability-gated, manifest-driven plugins for cleaning APT, Snap, Docker, and developer caches (npm, pip, yarn). Plugins operate under strict risk tiers (`safe`, `balanced`, `aggressive`).
- **Rich Interfaces:** 
  - **CLI:** Fast, standard interface for automation.
  - **Web UI (React + FastAPI):** A modern, dynamic real-time dashboard for monitoring queue state, rollback history, and system health (replacing the legacy Textual TUI).

<!-- ARCHITECTURE OVERVIEW -->
## 🏗 Architecture

SysClean operates on a **Dual-Engine** architecture to decouple intelligence from high-privilege execution:
1. **Client-Server Model:** `sysclean-cli` runs as a standard user, interacting with local LLMs and constructing execution plans. The `syscleand` background daemon auto-spawns on demand, listening on a local user-owned Unix Domain Socket (`~/.local/share/sysclean/sysclean.sock`) to execute validated plans safely without manual sudo interventions.
2. **Deterministic Execution Engine:** Uses Linux namespaces or cgroups to isolate module execution, ensuring plugins only touch what they are authorized to touch.
3. **Semantic Infrastructure Graph:** Models system resources and dependencies as a directed graph, providing the AI with the necessary context to avoid breaking running services (e.g., avoiding the deletion of a Docker volume currently attached to an active container).

<!-- SAFETY GUARANTEES -->
## 🛡 Safety & Governance Guardrails

SysClean employs deep safety mechanisms to prevent catastrophic errors (whether user-driven or AI-hallucinated):
- **Risk Tiers:** 
  - `safe`: Requires no interaction (ideal for autonomous background cleanup).
  - `balanced`: Requires standard CLI confirmation.
  - `aggressive`: Requires explicit `--force-aggressive` flags and a TTY presence.
- **Guardrails:** Uses strict regex, canonicalization (blocking `../../` attacks), and magic-byte checks. The execution engine strictly enforces a "Plan-before-Execute" lifecycle. Plugins must declare their targets in JSON before any destructive action is permitted.

<!-- INSTALLATION INSTRUCTIONS -->
## 📦 Installation

*(Note: SysClean is currently undergoing active development. The installation process below outlines the intended deployment model via immutable packaging.)*

```bash
# 1. Clone the repository
git clone https://github.com/your-org/sysclean.git
cd sysclean

# 2. Setup the environment (Python 3.11+, SQLite 3, Ollama)
./install.sh

# 3. Start the SysClean daemon
sudo systemctl enable --now syscleand
```

<!-- USAGE EXAMPLES -->
## 💻 How to Use

### Command Line Interface (CLI)
The CLI is the primary interface for manual operation.

```bash
# Run a dry-run to see what would be cleaned
sysclean clean --dry-run

# Execute standard cleanup (Interactive)
sysclean clean

# Rollback a specific transaction
sysclean rollback <transaction-id>
```

### Web Dashboard
Start the local FastAPI server and React frontend to view detailed telemetry, queue states, and health overview in your browser.

```bash
./bin/sysclean-cli ui
```

<!-- PROJECT ROADMAP -->
## 🗺 Roadmap & Phases

SysClean is being built in distinct phases to ensure stability and security:
- **Phase 1-3:** Zero-Trust Architecture, SQLite WAL State Management, and Deterministic Execution.
- **Phase 4-5:** eBPF-Powered Perfect Rollback and Deep Safety Guardrails.
- **Phase 6-7:** Core Remediation Plugins and Semantic Graph/AI Reasoning Integration.
- **Phase 8-10:** Autonomous Self-Healing Daemon, Enterprise Fleet Federation, and Web UI Polish.

<!-- DOCUMENTATION LINKS -->
## 📄 Documentation

For deeper dives into the architecture and planning, please refer to the `docs/` directory:
- `docs/PRD.md`: Product Requirements Document.
- `docs/PLAN.md`: Step-by-step implementation plan.
- `docs/AUDIT_REPORT.md`: Security and architecture audit.
- `GEMINI.md`: Core system conventions and guidelines.
