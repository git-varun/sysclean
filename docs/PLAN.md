
  Phase 1: Zero-Trust Architecture & Security Remediation
  What: Decouple the intelligence layer from the execution layer and remediate all Bandit/Pylint security findings. AI and web servers should never run as root.
  How:

   1. Implement a client-server architecture locally. sysclean-cli runs as the standard user, interacting with LLMs and building the execution plan. syscleand runs as root, listening on a restricted Unix Domain Socket to execute validated plans.
   2. Refactor subprocess.run calls to use arrays (e.g., ["docker", "system", "prune"]) instead of shell=True to prevent command injection.
   3. Configure Jinja2 in the HTML reporter with autoescape=True.
   4. Add global timeout decorators to all requests calls to prevent hanging.
  Impacted Files:

- bin/sysclean (Refactor to client/daemon multiplexer)
- python/executor/runtime.py, python/executor/worker.py (Remove shell=True, implement socket listener)
- python/reporting/html.py (Fix Jinja2 XSS)
- python/ai/providers/ollama.py, python/security/cve.py (Add HTTP timeouts)
- lib/execution.sh (Harden IPC boundary)
  Acceptance Criteria: Bandit reports 0 high/medium issues. Pylint score is > 8.0. The daemon can receive a command via socket and execute it without shell=True.

  Phase 2: High-Concurrency State Management (SQLite WAL)
  What: Build a thread-safe, transactional database layer that supports concurrent reads (UI/CLI) and writes (Background Daemon).
  How:

   1. Delete the legacy JSON queue logic.
   2. Initialize SQLite with PRAGMA journal_mode=WAL; and PRAGMA synchronous=NORMAL; for high concurrency.
   3. Introduce alembic for database migrations. Create the initial schema: queue, telemetry_journal, rollback_registry, and state_locks.
   4. Implement atomic queue state transitions (Proposed -> Approved -> Locked -> Executing -> Verified -> Completed/Failed) using explicit SQLite transactions and FOR UPDATE locks.
  Impacted Files:

- lib/queue.sh, queue.json (Deleted)
- python/telemetry/db.py (Rewrite connection pool, enable WAL)
- python/telemetry/queue.py (Rewrite to enforce atomic state transitions)
- requirements.txt (Add alembic, sqlalchemy)
- python/migrations/ (New directory for Alembic scripts)
  Acceptance Criteria: 10 concurrent threads can write to the queue simultaneously without database is locked errors. The database schema is versioned.

  Phase 3: The Deterministic Execution Engine & Chaos Resilience
  What: Build an execution runner that cannot fail silently and recovers perfectly from crashes (SIGKILL, power loss).
  How:

   1. Isolate module execution using Linux namespaces (via bwrap or unshare in the bash runner) or strict cgroups to limit CPU/Memory/Filesystem access per plugin.
   2. Register signal handlers in python/executor/runtime.py to catch SIGTERM/SIGINT. If interrupted, mark the active queue task as Failed (Interrupted).
   3. Build a recovery routine on daemon boot that scans for tasks stuck in the Executing state and rolls them back before accepting new work.
  Impacted Files:

- python/executor/runtime.py (Signal handlers, cgroup wrapping)
- lib/execution.sh (Namespace isolation)
- python/automation/autonomous.py (Boot recovery routine)
- tests/python/test_executor.py (New: Chaos testing simulating crashes)
  Acceptance Criteria: A kill -9 on the executor process while processing a task results in the daemon automatically reverting the partial state upon restart.

  Phase 4: eBPF-Powered Rollback & Observability
  What: Guarantee perfect restoration by tracing exactly what files the execution engine deletes or modifies.
  How:

   1. Instead of relying on plugins to honestly report what they delete, use an inotify watcher (or BCC/eBPF via python) bound to the PID of the executing module.
   2. Trace all unlink and rmdir syscalls.
   3. Before the syscall completes (or immediately prior based on the plan), compress the target files into an AES-encrypted tarball.
   4. Store the tarball path and hash in the SQLite rollback_registry tied to the transaction ID.
   5. python/rollback/engine.py reads the registry, decrypts the tarball, and replaces the exact files.
  Impacted Files:

- python/rollback/engine.py (Complete rewrite for tarball restoration)
- python/telemetry/events.py (Syscall tracing integration)
- runtime/state/rollbacks/ (New directory for encrypted tarballs)
  Acceptance Criteria: Deleting a cache directory via SysClean, altering the system state, and then running sysclean rollback <id> restores the exact bytes deleted.

  Phase 5: Deep Safety & Governance Guardrails
  What: Prevent catastrophic user or AI errors (e.g., deleting /etc or ~/.ssh).
  How:

   1. Enhance lib/guards.sh and python/protection/classifier.py to use strict regex, path canonicalization (to prevent ../../ attacks), and magic-byte checks.
   2. Hardcode Risk Tiers: safe requires no interaction, balanced requires standard CLI confirmation, aggressive requires a special --force-aggressive flag and TTY presence.
   3. Implement JSON schema validation for all plugins in modules/*/manifest.yml. Reject loading plugins missing capabilities or signatures.
  Impacted Files:

- lib/guards.sh (Canonicalization, deep traversal blocks)
- python/protection/classifier.py (Magic byte detection)
- python/evolution/governance.py (Risk tier enforcement)
- config/plugin.schema.json (Strict validation)
  Acceptance Criteria: The engine forcibly rejects a plugin attempting to delete ~/.ssh/id_rsa regardless of queue state or AI recommendation.

  Phase 6: Core Remediation Plugins (Plan & Execute)
  What: Deliver the actual cleanup capabilities (APT, Snap, Docker, Caches).
  How:

   1. Each bash module must support two flags: --plan and --execute.
   2. --plan outputs strict JSON: {"targets": ["/var/cache/apt/..."], "reclaimable_bytes": 102400}.
   3. --execute performs the action but ONLY on the targets output by the plan phase.
   4. Implement developer cache targeting (npm, pip, yarn) by scanning user home directories securely.
  Impacted Files:

- modules/apt.sh, modules/docker.sh, modules/snap.sh (Implement logic)
- modules/dev_caches.sh (New module)
- lib/execution.sh (Enforce plan-before-execute lifecycle)
  Acceptance Criteria: sysclean clean --dry-run accurately calculates reclaimable space without modifying the filesystem.

  Phase 7: Semantic Infrastructure Graph & AI Reasoning
  What: Give the system contextual awareness so the AI can make intelligent recommendations based on dependencies.
  How:

   1. Use networkx to build a directed graph of resources (python/graph/resource_graph.py). Nodes = Packages, Containers, Caches. Edges = "depends_on", "used_by".
   2. Feed graph sub-sections to the Ollama provider alongside the telemetry state. Prompt the LLM to output structured JSON recommendations ({"action": "clean", "target": "docker_images", "confidence": 0.9}).
   3. The AI reasoning engine (python/ai_runtime/reasoner.py) pushes these as Proposed tasks to the queue.
  Impacted Files:

- python/graph/resource_graph.py (Graph construction)
- python/ai/providers/ollama.py (Prompt engineering, JSON schema enforcement)
- python/ai_runtime/reasoner.py (AI to Queue bridge)
  Acceptance Criteria: The AI proposes a cleanup of an orphaned Docker volume, but explicitly avoids a volume currently bound to a running container, based on graph analysis.

  Phase 8: Autonomous Self-Healing Daemon
  What: Transform SysClean from a manual tool into a proactive, predictive background operator.
  How:

   1. Create a systemd service file for the SysClean daemon.
   2. Implement an Entropy Watcher loop (python/automation/scheduler.py) that wakes up every N hours.
   3. Use scikit-learn in python/forecasting/ml_forecast.py to run linear regression on the telemetry journal's storage metrics, predicting when the disk will hit 95%.
   4. If predicted exhaustion is < 48 hours, the daemon automatically enqueues and executes safe-tier cleanup tasks.
  Impacted Files:

- systemd/syscleand.service (New file)
- python/automation/scheduler.py (Watcher loop)
- python/forecasting/ml_forecast.py (Predictive models)
- python/automation/autonomous.py (Trigger logic)
  Acceptance Criteria: The system daemon autonomously clears system caches when disk space is forecasted to run out, generating an audit log without user intervention.

  Phase 9: Enterprise Fleet Federation
  What: Scale the system to allow central management of hundreds of workstations.
  How:

   1. Finalize the append-only JSONL event system (python/telemetry/journal.py). Ensure logs rotate at 10MB.
   2. Build the Federation Gateway in python/federation/gateway.py using a secure, token-authenticated mTLS channel to aggregate metrics.
   3. Expand the FastAPI server (python/web/server.py) to expose a Plotly-rendered dashboard showing the health distribution of the entire fleet.
  Impacted Files:

- python/telemetry/journal.py (Log rotation, PII redaction)
- python/federation/gateway.py (mTLS syncing)
- python/web/server.py, python/web/fleet_ws.py (Fleet dashboard API)
- python/web/templates/fleet.html (Plotly UI)
  Acceptance Criteria: A central server successfully aggregates and displays real-time health scores and reclaimed bytes from at least 3 distinct SysClean instances.

  Phase 10: Immutable Packaging, TUI & Polish
  What: Deliver a seamless, zero-friction developer and user experience.
  How:

   1. Use PyInstaller or shiv to compile the entire Python environment and dependencies into a single static binary.
   2. Build a .deb package containing the binary, bash modules, and systemd units for native Ubuntu installation.
   3. Finalize python/tui/dashboard.py using textual to provide a real-time top-like interface for SysClean metrics, the queue, and current health score.
   4. Complete all documentation.
  Impacted Files:

- Makefile or build.sh (Packaging logic)
- debian/ (Debian packaging specs)
- python/tui/dashboard.py (Finalize UI components)
- docs/ARCHITECTURE.md, docs/RUNBOOK.md (New files)
  Acceptance Criteria: A user can run dpkg -i sysclean.deb, start the service, and type sysclean dashboard to view a fully functional, live-updating Textual interface, with zero manual python environment setup.
