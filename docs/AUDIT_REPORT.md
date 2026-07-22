# Architectural and Implementation Audit Report: SysClean

> **Note (2026-07-23):** This report describes an early bash/scaffolding
> version of SysClean (`lib/*.sh`, `python/telemetry/`, `python/rollback/`,
> `python/tui/`, `python/reporting/`, `python/executor/`) that has since been
> replaced by the Python-based runtime under `python/core/`,
> `python/queue_engine/`, `python/ai/`, `python/security/`, and `python/web/`.
> The specific findings below (the `shell=True` command injection, the
> Jinja2 autoescape XSS, and the missing `requests` timeouts) do not apply to
> the current codebase — those call sites no longer exist or already pass
> `timeout=`. The Pylint score and test-coverage figures are also from that
> earlier snapshot and have not been re-measured since.
>
> This document is kept for historical context. A fresh audit against the
> current codebase is needed before treating any of the findings below as
> current.

## 1. Executive Summary
The SysClean project is currently in an early **scaffolding and blueprint phase**. While the conceptual architecture and directory structure closely align with the Product Requirements Document (PRD), the actual implementations are largely superficial placeholders. The project is far from production readiness and requires significant implementation effort to fulfill the vision outlined in the PRD. A recent automated static analysis and security audit further confirms that the code quality does not meet production standards, achieving a Pylint score of 3.23/10 and uncovering several critical security vulnerabilities.

## 2. Component-by-Component Analysis

### 2.1 Core Runtime & Orchestration
*   **CLI Orchestrator (`bin/sysclean`):** Acts as a primary router delegating commands to various bash and python scripts. However, crucial commands like `clean` and `rollback` only echo placeholder text.
*   **Execution Pipeline (`lib/execution.sh`):** Contains the conceptual skeleton for module execution (scan, plan, confirm, execute, verify) but does not integrate transactionality or error recovery.
*   **Queue Management:** There is a discrepancy between the bash implementation (`lib/queue.sh`), which uses a simple `queue.json` file, and the Python implementation (`python/telemetry/queue.py` and `db.py`), which uses SQLite. The Python implementation is currently isolated and not integrated into the main execution flow.

### 2.2 Cleanup & Optimization Modules
*   **Status:** **Not Implemented.**
*   **Details:** The core modules (`modules/apt.sh`, `modules/docker.sh`, `modules/snap.sh`) are entirely placeholders consisting of `echo "module: placeholder"`. There is no actual cleanup logic, disk space analysis, or execution of system commands.

### 2.3 Intelligence & AI Layer
*   **Local AI (`python/ai/providers/ollama.py`):** Features a basic, hardcoded `requests.post` call to a local Ollama instance (`localhost:11434`). It lacks error handling, timeouts, or fallback logic.
*   **Health Scoring (`python/intelligence/health.py`):** Implements a `HealthScorer` class with static weighting logic to produce a `HealthReport`. However, it does not currently ingest real system metrics.

### 2.4 Safety, Governance & Rollback
*   **Protected Asset Detection (`lib/guards.sh`):** Implements basic string-matching to prevent actions in protected directories (`~/.ssh`, `~/.gnupg`, etc.). While functional, it is rudimentary and lacks deep filesystem inspection.
*   **Rollback Registry:** Fragmented and non-functional.
    *   `python/rollback/engine.py` implements a simple, volatile in-memory list.
    *   `python/planner/rollback.py` inserts rollback data into a SQLite database (`runtime/state/sysclean.db`), but there is no mechanism to actually execute a restoration.

### 2.5 User Interfaces
*   **TUI (`python/tui/dashboard.py`):** Contains a barebones Textual application with a header and footer, but no live data visualization.
*   **Web UI (`python/web/server.py`):** A minimal FastAPI setup with a single `/health` endpoint returning `{"status": "ok"}`. None of the planned remote management or Plotly visualizations are implemented.

## 3. Code Quality and Security Audit
An automated security and static analysis sweep was performed using Bandit, Pylint, Flake8, and Pytest.

### 3.1 Security Findings (Bandit)
*   **High Severity: Command Injection Vulnerability.** `python/executor/runtime.py` uses `subprocess.run(command, shell=True)` where the command parameter is derived from the operation queue. This allows arbitrary command execution if the queue is compromised.
*   **High Severity: XSS Vulnerability.** `python/reporting/html.py` initializes the Jinja2 `Environment()` without enabling autoescape, leading to potential Cross-Site Scripting (XSS) if untrusted data is rendered in the dashboard.
*   **Medium Severity: Denial of Service.** `python/security/cve.py` and `python/ai/providers/ollama.py` perform `requests.post()` calls without specifying a timeout. This can cause the process to hang indefinitely if the network or API endpoint is unresponsive.

### 3.2 Code Quality (Pylint & Flake8)
*   **Pylint Score: 3.23/10.** The codebase relies heavily on skeleton files lacking documentation and proper formatting.
*   **Missing Docstrings:** Overwhelming majority of Python modules, classes, and functions are missing docstrings (`C0114`, `C0115`, `C0116`).
*   **Missing Newlines:** Many files do not end with a newline character.
*   **Unused Imports & Arguments:** Several modules import objects without using them, or define function arguments that remain unused (e.g., `telemetry` parameter in `python/cognition/runtime.py`).

### 3.3 Test Coverage
*   **Minimal Testing:** There is only one functional Python test file (`tests/python/test_health.py`), which passes but has imports out of order.
*   **Bash Testing Missing:** The `bats-core` framework is referenced, but tests are currently missing or failing to run effectively due to missing installation. The `tests/bash/test_guards.bats` is an unexecuted placeholder.

## 4. Actionable Recommendations & Next Steps
1.  **Remediate Security Flaws Immediately:**
    *   Remove `shell=True` from `subprocess.run` in `python/executor/runtime.py` and use list-based command execution.
    *   Initialize Jinja2 with `autoescape=True` in `python/reporting/html.py`.
    *   Add timeouts to all `requests.post()` and `requests.get()` calls.
2.  **Unify the Data Layer:** Standardize exclusively on SQLite for the queue, registry, and telemetry as dictated by the PRD. Remove the bash-based `queue.json` implementation.
3.  **Establish Testing Infrastructure:** Before writing more logic, properly install `bats-core` and execute bash tests. Greatly expand `pytest` coverage for the Python layers.
4.  **Implement Core Modules:** Develop the actual logic for `apt.sh`, `docker.sh`, and `snap.sh`. Ensure they perform dry-runs (size estimation) and hook into the execution pipeline accurately.
5.  **Fix Code Quality:** Address the Pylint and Flake8 findings by adding proper docstrings, fixing formatting, and removing unused imports/arguments to bring the code up to production standards.
