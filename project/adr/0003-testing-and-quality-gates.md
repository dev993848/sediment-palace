# ADR-0003: Testing Strategy And Quality Gates

- Status: Accepted
- Date: 2026-04-20
- Deciders: project maintainers

## Context
The system manipulates project memory and destructive actions are possible. Weak test discipline risks silent corruption and regressions.

## Decision
Adopt mandatory test pyramid with quality gates:
- Unit tests for domain rules.
- Integration tests for file/lock/journal behavior.
- E2E tests for MCP tool flows.
- Property-based tests for rule invariants.
- Coverage and CI gates for merges.

## Options Considered
1. Mostly manual testing.
2. Full test pyramid with gates.
3. E2E-heavy only.

## Tradeoffs
- Positive: high confidence and safer refactoring.
- Negative: longer initial setup and CI time.
- Risk mitigation: parallel CI jobs and targeted suites.

## Rollout Plan
1. Create test matrix per tool and failure class.
2. Implement baseline suites and gates.
3. Add fault-injection paths for crash consistency.

## Follow-up
- Document minimal local test command set.
- Track flaky tests and enforce remediation.
