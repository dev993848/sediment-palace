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
- Added tests:
- unit: frontmatter parsing/serialization
- integration: filesystem repository behaviors
- e2e: JSON-RPC tool flow

## Validation
- Command: `pytest -q`
- Result: `14 passed`

## Next
- Add stronger policy engine (role/allowlist/rate-limits).
- Extend metabolize rules (streak-based transitions, archival policies).
