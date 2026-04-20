# Agent Work Rules

## 1. Execution Policy
- Start every task by reading:
  - `project/PROJECT_OVERVIEW.md`
  - `project/ARCHITECTURE_AND_STACK.md`
  - `project/API.md`
  - active ADRs in `project/adr/`
- Do not change architecture contracts silently.
- Any non-trivial design change requires ADR.

## 2. Status Tracking (mandatory)
Update status in task/PR at least at these points:
1. `planned` before coding.
2. `in_progress` during implementation.
3. `blocked` with concrete blocker and next action.
4. `review` when ready for verification.
5. `done` only after tests + docs updates.

Each status update must include:
- scope
- risks
- validation result
- docs updated

## 3. Documentation Discipline
On every merged change:
- Update `project/API.md` if API behavior changed.
- Update relevant architecture docs if boundaries/policies changed.
- Create/update ADR for major design decisions.
- Add concise changelog entry.

## 4. API Change Rules
- Backward-incompatible changes are forbidden without:
  1. ADR approval
  2. versioning plan
  3. migration notes
- New tool or field must include:
  - input/output schema
  - error behavior
  - tests

## 5. Testing Policy
- Mandatory: unit + integration.
- For flow changes: add/adjust e2e.
- For rule engine changes: property-based tests required.
- Do not mark done while failing tests exist.

## 6. DRY and Engineering Bar
- Duplicate logic must be removed or centralized.
- Prefer explicit, maintainable implementations.
- No hacky shortcuts in core memory consistency paths.

## 7. Definition Of Ready
Task may start only if:
- requirement is clear
- affected components identified
- acceptance criteria defined

## 8. Definition Of Done
Task is done only if:
- implementation complete
- tests pass
- docs/API/ADR updated as needed
- risks and tradeoffs documented
