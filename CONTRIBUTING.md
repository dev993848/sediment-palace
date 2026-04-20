# Contributing

## Ground Rules
- Prioritize correctness and edge cases over implementation speed.
- Keep solutions explicit and maintainable.
- Flag duplication aggressively and keep code DRY.
- Avoid fragile shortcuts in core consistency paths.

## Required Read Before Any Change
1. `README.md`
2. `docs/en/README.md` (or `docs/ru/README.md`)
3. `docs/en/user/03-tools-reference.md`
4. `AGENT_BOOTSTRAP.md`

## Workflow
1. Set task status to `planned`.
2. Move to `in_progress` once implementation starts.
3. Use `blocked` with concrete blocker and next action if needed.
4. Move to `review` when validation is ready.
5. Mark `done` only after tests and docs updates are complete.

Each status update must include:
- Scope
- Risks
- Validation results
- Docs updated

## Documentation Requirements
For every merged change:
- Update user docs (`docs/en/user` and/or `docs/ru/user`) if behavior changed.
- Update `README.md` when setup/runtime behavior changes.
- Add changelog entry in `CHANGELOG.md`.

## Testing Requirements
- Mandatory: unit + integration tests.
- Flow/protocol changes: add/adjust e2e tests.
- Rule engine changes: property-based tests required.
- No merge with failing tests.

## API Change Policy
- Backward-incompatible changes require:
1. ADR approval
2. Versioning strategy
3. Migration notes

## Pull Request Checklist
- [ ] Scope and risks documented
- [ ] Tests added/updated and passing
- [ ] Docs/API/ADR updated as needed
- [ ] Changelog updated
