# Release Checklist: v0.1.0-rc1

## Pre-Tag Checks
- [x] Working tree is clean.
- [x] `ruff` passes (`python -m ruff check src tests`).
- [x] `mypy` passes (`python -m mypy src`).
- [x] test suite passes (`pytest -q`).
- [x] API docs updated.
- [x] changelog updated.
- [x] status doc updated.

## Tagging
- [x] Release commit created for release notes/checklist.
- [x] Git tag created: `v0.1.0-rc1`.

## Post-Tag
- [ ] Push commit and tag to remote:
  - `git push`
  - `git push origin v0.1.0-rc1`
- [ ] Create remote release entry with contents of `RELEASE_NOTES.md`.
- [ ] Attach CI run link for the tagged commit.
