# Init Script

Initialize SedimentPalace MCP for selected local agents and a chosen workspace.

Default behavior writes project-local configs into the selected workspace (`--scope local`).
It also initializes the memory app folder structure in that workspace.
The script also syncs `AGENT_BOOTSTRAP.md` into workspace root.
And auto-generates agent instruction files from it.

## Quick Run (Windows PowerShell)

```powershell
.\start\init_memory.ps1 --workspace D:\Projects\MyWork --agents codex,claude,qwen,opencode
```

## Quick Run (Root launcher)

```bat
start.bat --workspace D:\Projects\MyWork --agents codex,claude,qwen,opencode
```

Without arguments, `start.bat` opens an interactive checkbox menu for agent selection.

## Python Direct Run

```powershell
python .\start\init_memory.py --workspace D:\Projects\MyWork --agents codex,claude
```

## Global Scope (Optional)

```powershell
python .\start\init_memory.py --scope global --workspace D:\Projects\MyWork --agents codex,claude
```

## Dry Run

```powershell
python .\start\init_memory.py --workspace D:\Projects\MyWork --agents codex,qwen --dry-run
```

## Notes

- The script checks required Python deps (`pyyaml`, `sediment_palace`) and installs missing ones by default via:
  - `python -m pip install -e .[dev]`
- The script initializes memory layout in workspace:
  - `memory/01_Shallow`
  - `memory/02_Sediment`
  - `memory/03_Bedrock`
  - `memory/_System`
  - `memory/_Archive`
  - `memory/PALACE_MAP.md`
- The script syncs:
  - `AGENT_BOOTSTRAP.md` -> `<workspace>/AGENT_BOOTSTRAP.md`
- The script also generates per-agent instruction files:
  - `codex`: `AGENTS.md`, `CODEX.md`
  - `claude`: `CLAUDE.md`, `AGENTS.md`
  - `qwen`: `QWEN.md`, `AGENTS.md`
  - `opencode`: `AGENTS.md`, `OPENCODE.md`
  - `kimi`: `AGENTS.md`, `KIMI.md`
- Existing config files are backed up as `*.bak.YYYYMMDD_HHMMSS`.
- Local scope paths are created in workspace:
  - `.codex/config.toml`
  - `.opencode/opencode.json`
  - `.qwen/settings.json`
  - `.kimi/settings.json`
  - `.mcp.json` (for Claude)
