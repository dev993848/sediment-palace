# ADR-0001: Modular Monolith Boundaries

- Status: Accepted
- Date: 2026-04-20
- Deciders: project maintainers

## Context
The initial draft mixes protocol handling, business rules, and file operations in one module. This increases coupling and regression risk.

## Decision
Adopt a modular monolith with strict boundaries:
- `transport`
- `application`
- `domain`
- `infrastructure`

## Options Considered
1. Single-file/server-centric implementation.
2. Modular monolith.
3. Early microservices split.

## Tradeoffs
- Positive: improved testability, maintainability, and explicit dependencies.
- Negative: slightly more boilerplate initially.
- Risk mitigation: keep scope narrow and avoid premature service split.

## Rollout Plan
1. Define package structure.
2. Move existing logic by boundary.
3. Add contract tests per boundary.

## Follow-up
- Update architecture doc and API contract mapping.
- Enforce dependency direction in reviews.
