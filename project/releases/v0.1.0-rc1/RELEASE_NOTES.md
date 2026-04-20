# Release Notes: v0.1.0-rc1

## Summary
`v0.1.0-rc1` is the first release-candidate baseline for SedimentPalace MCP with production hardening in place.

## Included
- MCP tools:
  - `read_map`, `write_memory`, `read_memory`
  - `search_room`, `move_file`, `update_map`
  - `metabolize`, `purge_memory`
  - `recover_journal`, `get_metrics`, `healthcheck`
- Reliability:
  - file locks
  - append-only operation journal
  - recovery flow for unresolved operations
  - atomic write path for mutating operations
- Safety and controls:
  - policy engine (`confirm` checks, destructive-op rate limits)
  - transport input budgets and per-tool timeout limits
  - structured JSON tool responses (`result.data`, `result.error`)
- Observability:
  - per-tool telemetry logs and aggregate metrics snapshot
- Testing:
  - unit + integration + e2e suites
  - property-based metabolize invariants (Hypothesis-backed, optional local skip if missing)
- Delivery:
  - CI workflow with `ruff`, `mypy`, `pytest`
  - runtime config via `SEDIMENT_*` env variables

## Verification Snapshot
- `python -m ruff check src tests` passed
- `python -m mypy src` passed
- `pytest -q` passed (`22 passed`)

## Known Constraints
- Property-based tests are skipped when `hypothesis` is not installed locally.
- Current policy model is config-driven but does not yet include role-based authorization.

## Upgrade Notes
- No migration required for this pre-1.0 release.
- Runtime artifacts remain under `memory/_System` and are git-ignored.
