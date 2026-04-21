# 06. MCP Config Examples

## Recommended path: generated local configs
Use the initializer to generate agent-specific local configs in your workspace:

```bat
start.bat --workspace D:\Projects\MyWork --agents codex,claude,qwen,opencode,kimi
```

Generated files:
- `.codex/config.toml`
- `.qwen/settings.json`
- `.opencode/opencode.json`
- `.kimi/settings.json`
- `.mcp.json` (Claude-style local MCP config)

## Global scope (optional)
If you want to write into user-global config files instead:

```bat
start.bat --scope global --workspace D:\Projects\MyWork --agents codex,claude
```

## Generic stdio config (manual fallback)
```json
{
  "mcpServers": {
    "sediment_palace": {
      "command": "python",
      "args": ["-m", "sediment_palace.main"],
      "cwd": "D:\\Projects\\Memory",
      "env": {
        "SEDIMENT_PROJECT_ROOT": "D:\\Projects\\MyWork"
      }
    }
  }
}
```
