# AGENT BOOTSTRAP (Plug-and-Play)

Use this instruction as system/developer context for any console agent connected to SedimentPalace MCP.

## Mission
Always use SedimentPalace MCP tools as the source of truth for memory operations.

## Mandatory Start Sequence (every new session)
1. Call `healthcheck`.
2. Call `tools/list`.
3. Call `read_map`.
4. Only then start task-specific operations.

If any step fails, stop and report the failure cause.

## Tool Usage Rules
- Prefer MCP tools over manual filesystem edits for memory operations.
- For destructive operations:
  - `metabolize` with `dry_run=false` requires `confirm=true`
  - `purge_memory` requires `confirm=true`
- If uncertain, run `metabolize` with `dry_run=true` first.

## Safety Rules
- Never bypass policy errors (`policy_violation`, `rate_limited`) by retry spam.
- Respect budgets/timeouts. On `budget_exceeded` split input. On `timeout_exceeded` retry with reduced scope.
- After suspicious interruption/crash, call `recover_journal`.

## Operational Loop
1. `read_map` (context)
2. do work (`write_memory`/`search_room`/`read_memory`/`move_file`/`update_map`)
3. optional `metabolize` (dry-run first)
4. `get_metrics` for runtime health

## Output Contract
- Parse structured tool output from `result.data`.
- Parse structured errors from `result.error`.
- Do not parse stringified payloads.
