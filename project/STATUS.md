# Project Status

## Current
- Date: 2026-04-20
- Status: `in_progress`
- Active phase: `Phase 1 - Core Engine (MVP slice)`

## Completed In Current Iteration
- Repo scaffold for layered architecture:
  - `src/sediment_palace/transport`
  - `src/sediment_palace/application`
  - `src/sediment_palace/domain`
  - `src/sediment_palace/infrastructure`
- Implemented MVP tools:
- `read_map`
- `write_memory`
- `read_memory` (path/query mode)
- `search_room`
- `move_file`
- `update_map`
- `recover_journal`
- `metabolize`
- `purge_memory`
- Added typed domain errors and frontmatter helpers.
- Added infrastructure reliability pieces:
- file lock manager
- append-only operation journal
- atomic write helper for mutating operations
- policy checks for destructive operations (`confirm=true`)
- policy engine with config-driven limits and destructive-op rate limiting
- fault-injection path for crash-consistency tests
- transport-level input budgets and per-tool timeout enforcement
- streak-aware metabolize transitions with decaying intermediate state
- structured `tools/call` responses (`result.data` / `result.error`) replacing string payload parsing
- per-tool telemetry recorder with counters and duration aggregates
- `get_metrics` tool for runtime telemetry snapshot
- property-based tests for `metabolize` invariants (Hypothesis-backed)
- Added tests:
- unit: frontmatter parsing/serialization
- integration: filesystem repository behaviors
- e2e: JSON-RPC tool flow

## Validation
- Command: `pytest -q`
- Result: `20 passed`
  - Property-based suite is auto-skipped when `hypothesis` is unavailable.

## Next
- add tool-level tracing correlation IDs across journal + telemetry.
- enforce Hypothesis in CI dev environment to execute property suite on every run.
