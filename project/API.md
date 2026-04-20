# MCP API Contract (v1 Draft)

## Principles
- Deterministic behavior.
- Typed error responses.
- No side effects outside `memory/`.

## Tools
1. `read_map()`
- Returns current `PALACE_MAP.md`.

2. `write_memory(layer, path, content, tags?)`
- Creates/updates memory entry.
- Normalizes frontmatter.

3. `read_memory(path? | query?, layer?)`
- Reads by path or searches by query.

4. `search_room(room, query)`
- Scoped room search by content/tags.

5. `move_file(source, dest_layer, new_path?)`
- Moves file between layers.
- Updates metadata and map links.

6. `update_map(action, details)`
- Adds/removes/links references in map/journal.

7. `metabolize(days_threshold?, dry_run?)`
- Executes decay/promotion/archive workflow.

8. `purge_memory(path, reason)`
- Destructive operation; requires policy approval.
- Must always emit audit event.

## Error Model (required fields)
- `error_code`
- `message`
- `context`
- `retryable`

## Idempotency Rules
- `write_memory`: idempotent for same `(path, content)`.
- `move_file`: idempotent if source already moved to target.
- `metabolize(dry_run=true)`: no side effects.

## Compatibility
- Backward incompatible changes require ADR + major version bump.
