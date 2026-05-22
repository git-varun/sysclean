# SysClean Core — Execution Plan

## Goal

Ship a stable, maintainable, rollback-safe workstation cleanup engine.

Focus:

* deterministic execution,
* safety,
* operational correctness,
* production readiness.

Do not expand scope during implementation.

---

# Phase 0 — Architecture Reset (1–2 Days)

## Objective

Remove speculative architecture permanently.

## Tasks

### Delete Directories

Remove:

```text id="7sjav7"
adaptive/
agents/
awareness/
behavior/
cognition/
consensus/
copilots/
drift/
embeddings/
evolution/
federation/
forecasting/
generation/
governance/
incidents/
mesh/
orchestration_ai/
orchestration_rl/
prediction/
prevention/
reinforcement/
simulation/
synthesis/
trust/
twin/
twins/
```

### Collapse Structure

Target:

```text id="xhhvg4"
python/
├── core/
├── queue/
├── plugins/
├── security/
├── ai/
├── tui/
└── web/
```

### Deliverables

* simplified repo,
* dependency cleanup,
* updated imports,
* architecture baseline.

---

# Phase 1 — Secure Runtime Foundation (3–5 Days)

## Objective

Build a safe execution boundary.

## Tasks

### Daemon Separation

Implement:

```text id="2kj10s"
sysclean-cli  → user
syscleand     → privileged daemon
```

Communication:

* Unix Domain Socket only.

### Remove Dangerous Execution

Replace:

```python id="nh4gw5"
shell=True
```

with:

```python id="lb1k44"
["docker", "system", "prune"]
```

### Add

* global subprocess timeout,
* request timeout,
* structured errors,
* signal handlers.

### Deliverables

* stable daemon,
* IPC layer,
* no shell injection risk.

---

# Phase 2 — Queue & State Engine (3–4 Days)

## Objective

Build deterministic state management.

## Tasks

### SQLite WAL

Enable:

```sql id="7d9phz"
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
```

### Queue Schema

Tables:

* queue
* rollback_registry
* telemetry_events

### State Machine

```text id="cyhjlwm"
PROPOSED
→ APPROVED
→ EXECUTING
→ VERIFYING
→ COMPLETED
→ FAILED
```

### Add

* atomic transitions,
* crash recovery,
* stale execution recovery.

### Deliverables

* reliable queue engine,
* recovery logic,
* migration system.

---

# Phase 3 — Rollback Engine (4–5 Days)

## Objective

Guarantee safe reversibility.

## Tasks

### Snapshot Strategy

Before execution:

* enumerate targets,
* compress snapshots,
* hash archives,
* register metadata.

### Rollback

Implement:

```bash id="h0z6gw"
sysclean rollback <id>
```

### Explicitly Avoid

* eBPF,
* syscall tracing,
* kernel hooks.

### Deliverables

* deterministic rollback,
* verified restore flow.

---

# Phase 4 — Security & Validation (3–4 Days)

## Objective

Prevent destructive mistakes.

## Tasks

### Protected Paths

Block:

```text id="z53d6r"
~/.ssh
~/.gnupg
.env
wallets
kube configs
cloud credentials
```

### Add

* path canonicalization,
* symlink escape protection,
* traversal prevention,
* manifest schema validation.

### Risk Tiers

```text id="jlwm2u"
safe
balanced
aggressive
```

### Deliverables

* hardened validation layer,
* enforced safety rules.

---

# Phase 5 — Core Cleanup Plugins (5–7 Days)

## Objective

Build the actual product.

## Plugins

### Implement

* apt
* docker
* snap
* dev_caches
* tempfiles
* logs

### Plugin Rules

Every plugin:

```bash id="9bqof0"
--plan
--execute
```

### Execution Contract

* execute only approved targets,
* no discovery during execution,
* strict JSON outputs.

### Deliverables

* production-ready cleanup engine.

---

# Phase 6 — Verification & Chaos Testing (3–5 Days)

## Objective

Prove operational correctness.

## Tests

### Add

* interrupted execution tests,
* corrupted queue tests,
* rollback integrity tests,
* partial failure recovery,
* concurrent queue access.

### Simulate

```bash id="l5fj9s"
kill -9
daemon crash
power interruption
```

### Deliverables

* stability validation,
* recovery guarantees.

---

# Phase 7 — TUI & Observability (3–4 Days)

## Objective

Improve operator visibility.

## Build

### TUI

Show:

* queue state,
* active execution,
* reclaimable storage,
* rollback history.

### Telemetry

Append-only JSONL logs.

### Rules

TUI is:

* read-only,
* non-executing,
* observational only.

### Deliverables

* operational dashboard,
* execution visibility.

---

# Phase 8 — AI Advisory Layer (Optional) (3–5 Days)

## Objective

Add bounded intelligence safely.

## Tasks

### Ollama Integration

AI may:

* summarize,
* recommend,
* estimate reclaimable storage.

AI may NOT:

* execute,
* enqueue directly,
* bypass validation.

### Resource Awareness

Only:

* docker relationships,
* mounted volumes,
* package dependencies.

Avoid generalized graph systems.

### Deliverables

* optional advisory engine,
* bounded AI scope.

---

# Phase 9 — Packaging & Release (2–4 Days)

## Objective

Ship usable software.

## Tasks

### Packaging

Build:

* `.deb`
* standalone binary
* systemd unit

### Documentation

Write:

* architecture.md
* runbook.md
* rollback.md
* plugin_dev.md

### Deliverables

* installable release,
* production documentation.

---

# Definition of Done

SysClean Core is complete when:

* cleanup operations are deterministic,
* rollback works reliably,
* protected assets cannot be deleted,
* crashes recover safely,
* queue integrity survives interruption,
* plugins are production-ready,
* architecture remains minimal and traceable.

---

# Hard Constraints

## Never Add

* federation,
* distributed orchestration,
* mesh systems,
* autonomous execution,
* AI governance,
* digital twins,
* reinforcement learning,
* speculative abstractions.

---

# Core Rule

Every new subsystem must justify:

1. operational necessity,
2. measurable user value,
3. failure reduction,
4. maintenance cost.

If not, reject it.
