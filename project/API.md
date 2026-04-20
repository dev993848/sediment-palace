# MCP API Contract (v1 Draft)

## Principles
- Deterministic behavior.
- Typed error responses.
- No side effects outside `memory/`.

## Tools
1. `read_map()`  `implemented in MVP`
- Returns current `PALACE_MAP.md`.

2. `write_memory(layer, path, content, tags?)`  `implemented in MVP`
- Creates/updates memory entry.
- Normalizes frontmatter.

3. `read_memory(path? | query?, layer?)`  `implemented in MVP`
- Reads by path or searches by query.

4. `search_room(room, query)`  `implemented in MVP`
- Scoped room search by content/tags.

5. `move_file(source, dest_layer, new_path?)`  `implemented in MVP`
- Moves file between layers.
- Updates metadata and map links.

6. `update_map(action, details)`  `implemented in MVP`
- Adds/removes/links references in map/journal.

7. `metabolize(days_threshold?, dry_run?, confirm?)`  `implemented in MVP`
- Executes decay/promotion/archive workflow.

8. `purge_memory(path, reason, confirm?)`  `implemented in MVP`
- Destructive operation; requires policy approval.
- Must always emit audit event.

9. `recover_journal()`  `implemented in MVP`
- Scans operation journal for unresolved operations.
- Appends recovery completion events with `recovery_status`.

## Error Model (required fields)
- `error_code`
- `message`
- `context`
- `retryable`

## Idempotency Rules
- `write_memory`: idempotent for same `(path, content)`.
- `move_file`: idempotent if source already moved to target.
- `metabolize(dry_run=true)`: no side effects.
- `purge_memory`: not idempotent after first successful purge.

## Compatibility
- Backward incompatible changes require ADR + major version bump.
