# 02. Daily Workflows

## Workflow A: Store a new idea
1. Call `write_memory`.
2. Verify with `read_memory` by `path`.

## Workflow B: Search notes by topic
1. Call `search_room`.
2. Inspect `result.data.matches`.

## Workflow C: Promote a note manually
1. Call `move_file`.
2. Verify `result.data.destination`.

## Workflow D: Maintain map links
1. Add/remove links via `update_map`.

## Workflow E: Run sedimentation safely
1. Run `metabolize` with `dry_run=true`.
2. Run real action with `confirm=true`.

## Workflow F: Archive a bad note
Call `purge_memory` with `confirm=true`.
