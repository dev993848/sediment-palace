# Architecture And Stack

## Architectural Style
Modular monolith with clear boundaries:
- `transport`: MCP protocol handling.
- `application`: use-cases (`write_memory`, `metabolize`, `update_map`, etc.).
- `domain`: sedimentation rules, policies, invariants.
- `infrastructure`: filesystem adapter, lock manager, backup/journal adapter.

## High-Level Components
1. MCP Server Adapter
- Parses JSON-RPC.
- Validates tool input.
- Maps typed domain errors to MCP error responses.
- Enforces transport-level budgets and per-tool timeout limits.

2. Memory Application Service
- Executes use-cases.
- Enforces policy checks and operation budgets.

3. Sedimentation Engine
- Deterministic state transitions (shallow/sediment/bedrock).
- Density/streak/age evaluation.
- Promotion/archive/delete decisions.
- In-place decay status updates (`active` -> `decaying`) before archival.

4. Persistence Layer (File-Native)
- Markdown files with YAML frontmatter.
- Atomic writes.
- Lock abstraction.
- Operation journal for recovery.

5. Observability
- Structured logs.
- Audit trail for destructive ops.
- Metrics: files scanned, promoted, archived, deleted, duration.
- Transport telemetry with per-tool success/error counters and latency aggregates.

6. Policy Engine
- Config-driven policy in `memory/_System/policy.yaml`.
- Destructive operation confirmation policy.
- Rate limiting for destructive operations.
- Runtime limits (search matches, metabolize scan budget).

## Data Model (v1)
Mandatory frontmatter fields:
- `id`, `layer`, `created`, `last_touched`, `density`, `decay_days`, `tags`, `status`, `source_session`.

Domain concepts:
- `MemoryEntry`
- `LayerPolicy`
- `MetabolizeDecision`
- `OperationEvent` (journal)

## Security Boundaries
- Path traversal defense: all paths resolved under `memory/` only.
- Policy engine: deny-by-default for destructive operations unless explicit.
- Quotas and rate limits for heavy operations.
- Audit logging for move/delete/purge/metabolize.

## Scaling Strategy (v1 -> v1.5)
- Incremental metabolize (changed-set first, full reconcile periodically).
- Incremental backups with periodic checkpoint.
- Append-only map link journal + compaction into `PALACE_MAP.md`.

## Recommended Stack
- Language: Python 3.11+
- MCP transport: `mcp` SDK
- Validation: `pydantic`
- YAML: `pyyaml`
- Testing: `pytest`, `pytest-cov`, `hypothesis`
- Quality: `ruff`, `mypy`
- Packaging: `uv` or `pip + venv`
- CI: GitHub Actions
- Runtime config: environment-based (`SEDIMENT_*` variables)

## Proposed Repository Layout
```text
.
├── project/
│   ├── adr/
│   └── *.md
├── src/
│   └── sediment_palace/
│       ├── transport/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── scripts/
```
