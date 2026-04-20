# 06. MCP Config Examples (Console Agents)

Below are ready-to-use examples for stdio MCP connection.

## Generic stdio config (template)
```json
{
  "mcpServers": {
    "sediment_palace": {
      "command": "python",
      "args": ["-m", "sediment_palace.main"],
      "cwd": "/absolute/path/to/project",
      "env": {
        "SEDIMENT_PROJECT_ROOT": "/absolute/path/to/project"
      }
    }
  }
}
```

## Windows (PowerShell / cmd)
```json
{
  "mcpServers": {
    "sediment_palace": {
      "command": "python",
      "args": ["-m", "sediment_palace.main"],
      "cwd": "D:\\Projects\\Memory",
      "env": {
        "SEDIMENT_PROJECT_ROOT": "D:\\Projects\\Memory"
      }
    }
  }
}
```

## Linux/macOS
```json
{
  "mcpServers": {
    "sediment_palace": {
      "command": "python3",
      "args": ["-m", "sediment_palace.main"],
      "cwd": "/home/user/Memory",
      "env": {
        "SEDIMENT_PROJECT_ROOT": "/home/user/Memory"
      }
    }
  }
}
```

## Recommended agent startup prompt
Use `AGENT_BOOTSTRAP.md` as system/developer prompt so the agent always starts with:
1. `healthcheck`
2. `tools/list`
3. `read_map`

This enables “run server -> connect MCP -> work” without extra skill.
