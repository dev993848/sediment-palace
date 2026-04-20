# 06. MCP Config Examples

## Generic stdio config
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

## Windows
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
