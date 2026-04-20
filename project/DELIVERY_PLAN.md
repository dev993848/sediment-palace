# Delivery Plan

## Phase 0: Foundation
- Finalize architecture boundaries and ADR baseline.
- Define API contracts for MCP tools.
- Freeze frontmatter schema.

## Phase 1: Core Engine
- Implement domain rules and invariants.
- Implement file adapter with atomic writes and locking.
- Implement operation journal + recovery flow.

## Phase 2: MCP Surface
- Implement transport adapter and tool handlers.
- Add typed error mapping.
- Add policy checks and operation budgets.

## Phase 3: Quality
- Unit tests for rules.
- Integration tests for filesystem/locking/journal.
- E2E tests for MCP tool flows.
- Property-based tests for sedimentation invariants.

## Phase 4: Ops Readiness
- Structured logs and audit trail.
- CI pipeline (lint, type-check, tests, coverage gates).
- Release checklist and versioning.

## Definition Of Done (per feature)
- Requirements linked to ADR/issue.
- Tests added and passing.
- Docs updated (`API.md`, ADR if architecture changed).
- Changelog entry included.
