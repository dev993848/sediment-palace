# Agent Quickstart (English)

Use this for a true plug-and-play setup:

1. Initialize your workspace:
```bat
start.bat --workspace D:\Projects\MyWork --agents codex,claude,qwen,opencode,kimi
```
2. Open the agent in that workspace.
3. Verify startup sequence:
   - `healthcheck`
   - `tools/list`
   - `read_map`

Notes:
- The initializer creates `AGENT_BOOTSTRAP.md` and agent instruction files automatically.
- Local config scope is default; use `--scope global` only if needed.
