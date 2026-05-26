<!-- DOCUMENT HEADER -->
# Product Requirements Document (PRD): SysClean

## 1. Executive Summary
SysClean is a modular, AI-assisted workstation operations platform designed to maintain, optimize, and secure developer environments. Originally a cleanup utility, it is evolving into an autonomous remediation and predictive maintenance system for Ubuntu-first developer workstations.

<!-- CORE VISION -->
## 2. Product Vision & Objectives
### 2.1 Vision
To become the AI-native operating layer for developer infrastructure, providing autonomous, self-healing, and predictive maintenance capabilities.

### 2.2 Strategic Objectives
- **Safety First:** Ensure zero-risk cleanup through sophisticated rollback mechanisms and protected asset detection.
- **Intelligence:** Leverage local AI (Ollama) and semantic infrastructure graphs to provide actionable insights.
- **Modularity:** Support a manifest-based plugin architecture for extensible system management.
- **Scalability:** Transition from single-workstation optimization to distributed fleet orchestration.

## 3. Target Audience
- **Individual Developers:** Optimization of local environments (Ubuntu-first).
- **DevOps/SRE Teams:** Standardizing workstation health and compliance across fleets.
- **AI/ML Engineers:** Managing heavy local resources (Docker, GPU drivers, large datasets).

<!-- DETAILED REQUIREMENTS -->
<!-- Add new functional requirements here as the project evolves -->
## 4. Functional Requirements

### 4.1 Core Runtime & Orchestration
- **Dual-Engine Execution:** Bash for low-level CLI/runtime orchestration; Python for high-level intelligence and logic.
- **Transactional Queue:** SQLite-backed queue to ensure persistent execution state and atomic operations.
- **Event Stream:** Append-only JSONL telemetry for auditing and real-time monitoring.

### 4.2 Cleanup & Optimization Modules
- **Standard Modules:** Support for `apt`, `snap`, `docker`, and generic system caches.
- **Developer Caches:** Targeted cleanup for IDEs (VSCode, IntelliJ), Package Managers (npm, pip, go), and Build Systems.
- **Analysis:** Pre-cleanup entropy analysis to identify high-impact targets.

### 4.3 Intelligence & AI Layer
- **Local AI Integration:** Integration with Ollama for local LLM-based recommendations and analysis.
- **Health Scoring:** Algorithm to quantify system health across multiple vectors (storage, performance, security).
- **Forecasting:** Predictive modeling of resource consumption (e.g., storage exhaustion).
- **Resource Graph:** Semantic representation of system resources and their interdependencies.

### 4.4 Safety, Governance & Rollback
- **Protected Asset Detection:** Automated detection of sensitive files (.ssh, .gnupg, wallets, private keys) to prevent accidental deletion.
- **Risk Tiers:** Configurable execution modes: `safe`, `balanced`, `aggressive`.
- **Governance Constraints:** Capability-gated execution and mandatory approvals for destructive actions.
- **Rollback Registry:** Mandatory metadata recording for every operation to allow single-command restoration.

### 4.5 Plugin Architecture
- **Manifest-Driven:** Plugins defined by YAML manifests specifying versioning, risk level, and required capabilities.
- **Capability Gating:** Strict control over plugin access to filesystem, networking, or package managers.

### 4.6 User Interfaces
- **CLI:** Primary interface for automation and standard operations.
- **Web UI (React/Vite & FastAPI):** A modern, real-time dashboard for monitoring queue state, health, and reclaimable storage. Fully replaces the legacy Textual TUI.

<!-- SYSTEM METRICS & NFRs -->
## 5. Non-Functional Requirements

### 5.1 Reliability
- 100% success rate for rollback operations.
- Transactional integrity for all queue operations.

### 5.2 Performance
- Minimal footprint during background scans.
- Fast startup (< 500ms for CLI status checks).

### 5.3 Security
- No transmission of sensitive telemetry to external servers.
- Encryption for local telemetry/logs if sensitive data is present.

## 6. Technical Stack
- **Languages:** Bash 5.0+, Python 3.11+.
- **Database:** SQLite 3 for operational data.
- **AI:** Ollama (Local), Sentence-Transformers, NetworkX (Graph).
- **Web/UI:** FastAPI, React, Vite.

<!-- TIMELINE & PLANNING -->
## 7. Roadmap & Milestones

### Phase 1: Foundation (Current Priority)
- Stabilize execution engine and SQLite queue.
- Implement robust rollback registration.
- Finalize core safety guards and protected asset detection.

### Phase 2: Implementation
- Deliver production-ready modules for `apt`, `docker`, and `snap`.
- Integrate local AI recommendations via Ollama.
- Deploy the React Web UI dashboard.

### Phase 3: Advanced Intelligence
- Implement Infrastructure Memory Graph.
- Enable autonomous self-healing loops.
- Launch distributed fleet telemetry.

## 8. User Stories
- **Safe Cleanup:** "As a developer, I want to reclaim disk space from old Docker images and unused packages without breaking my environment, so I can focus on coding without storage anxiety."
- **Proactive Maintenance:** "As a DevOps engineer, I want to see a health score for my workstation to know when maintenance is required before it impacts my productivity."
- **Privacy & Security:** "As a security-conscious user, I want to ensure my private keys and secrets are never touched by cleanup scripts and that all AI analysis happens locally."

<!-- RISK MANAGEMENT -->
## 9. Risk & Mitigation
| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Data Loss** | High | Mandatory rollback registry; Protected asset detection (.ssh, .env, wallets). |
| **System Instability** | High | Capability-gated execution; Strict risk-tier validation (safe/balanced/aggressive). |
| **Privacy Leakage** | Medium | Local-first AI integration (Ollama); No external telemetry by default. |
| **Plugin Malfunction** | Medium | Manifest-driven validation; Future zero-trust isolation runtime. |

## 10. Success Metrics (KPIs)
- **Disk Recovery:** Average GBs reclaimed per cleanup.
- **System Stability:** Number of system failures vs. successful rollbacks.
- **User Engagement:** Frequency of Web dashboard usage.
- **AI Accuracy:** Relevance score of AI-generated maintenance recommendations.
