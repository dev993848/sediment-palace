# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog principles and this project follows semantic intent for change classification.

## [Unreleased]

### Added
- Contribution process and engineering workflow requirements.
- Python backend MVP scaffold under `src/sediment_palace`.
- MCP JSON-RPC server core with tools: `read_map`, `write_memory`, `read_memory`.
- Extended MCP tools: `search_room`, `move_file`, `update_map`.
- Added `recover_journal` tool.
- Added `metabolize` and `purge_memory` tools with destructive-operation policy checks.
- Domain/frontmatter modules and filesystem repository.
- Added file lock manager and append-only operation journal.
- Added atomic write path for mutating repository operations.
- Added policy engine with config-based limits and destructive-op rate limiting.
- Added fault-injection test path for crash-consistency/recovery validation.
- Added transport-level input budgets and per-tool timeout enforcement.
- Expanded metabolize rules with streak-based transitions and decaying intermediate state.
- Switched transport tool responses to structured JSON payloads (`result.data` / `result.error`).
- Added per-tool telemetry recorder and `get_metrics` tool.
- Added Hypothesis-based property test module for metabolize invariants.
- Added runtime config loading from environment variables.
- Added `healthcheck` tool and CI pipeline (`ruff`, `mypy`, `pytest`).
- Test suites (unit/integration/e2e/property) for MVP flows.
- Local quality gates verified green (`ruff`, `mypy`, `pytest`).
- Added end-user documentation package under `docs/user`.
- Project status tracker `project/STATUS.md`.

## [2026-04-20]

### Added
- Project documentation baseline in `project/`.
- ADR system and initial architecture decisions.
- Role prompts for backend/frontend/devops contributors.
- Agent work rules, API contract draft, and delivery plan.
- Repository `.gitignore`.
