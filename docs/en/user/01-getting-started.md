# 01. Getting Started

## Recommended: one-command initializer
From repository root, run:

```bat
start.bat --workspace D:\Projects\MyWork --agents codex,claude,qwen,opencode,kimi
```

This will:
- install/check Python dependencies,
- create `memory/` structure in the target workspace,
- sync `AGENT_BOOTSTRAP.md`,
- generate agent instruction files (`AGENTS.md`, `CLAUDE.md`, `QWEN.md`, etc.),
- generate local agent configs in the workspace.

## Manual install (if needed)
```bash
python -m pip install -e ".[dev]"
```

## Manual run (debug mode)
```bash
python -m sediment_palace.main
```

The server reads JSON-RPC from `stdin` and writes responses to `stdout`.

## First checks
Run, in order:
1. `initialize`
2. `tools/list`
3. `tools/call` with `healthcheck`

Expected:
- `result.data.status = "ok"`
- `result.data.service = "sediment-palace"`
