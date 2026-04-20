# SedimentPalace MCP

Local-first memory engine for AI agents with layered sedimentation, policy controls, journaling, and telemetry.

## Quick Start

```bash
python -m pip install -e ".[dev]"
pytest -q
python -m sediment_palace.main
```

## Runtime Configuration

Set via environment variables:

- `SEDIMENT_PROJECT_ROOT` (default: `.`)
- `SEDIMENT_TIMEOUT_DEFAULT_SECONDS` (default: `2.0`)
- `SEDIMENT_TIMEOUT_METABOLIZE_SECONDS` (default: `5.0`)
- `SEDIMENT_BUDGET_WRITE_CONTENT` (default: `50000`)
- `SEDIMENT_BUDGET_READ_QUERY` (default: `512`)
- `SEDIMENT_BUDGET_SEARCH_QUERY` (default: `512`)
- `SEDIMENT_BUDGET_SEARCH_ROOM` (default: `1024`)
- `SEDIMENT_BUDGET_PURGE_REASON` (default: `1024`)

## Quality Gates

- `ruff check src tests`
- `mypy src`
- `pytest -q`

CI workflow runs all three gates on push and pull requests.

## User Docs

- `docs/user/README.md`
- `docs/user/01-getting-started.md`
- `docs/user/02-daily-workflows.md`
- `docs/user/03-tools-reference.md`
- `docs/user/04-troubleshooting.md`
- `docs/user/05-faq.md`
- `docs/user/06-mcp-config-examples.md`
- `AGENT_BOOTSTRAP.md` (recommended system prompt for plug-and-play agent behavior)
