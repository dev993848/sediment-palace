# ADR-0002: File-Native Storage With Operation Journal

- Status: Accepted
- Date: 2026-04-20
- Deciders: project maintainers

## Context
File-native markdown storage is a core product principle, but plain lock + rename does not fully solve crash consistency and replayability.

## Decision
Keep markdown as source of truth and add append-only operation journal for recovery and audit.

## Options Considered
1. Files only with lock/rename.
2. Files + operation journal.
3. Replace metadata handling with SQLite now.

## Tradeoffs
- Positive: preserves transparency while adding recovery/audit guarantees.
- Negative: extra implementation complexity vs files-only.
- Risk mitigation: keep journal format minimal and versioned.

## Rollout Plan
1. Define event schema (`OperationEvent`).
2. Write events before/after critical transitions.
3. Implement replay/recovery command.

## Follow-up
- Add crash/fault-injection tests.
- Document recovery runbook.
