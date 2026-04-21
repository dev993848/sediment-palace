# 06. Примеры MCP Конфигурации

## Рекомендуемый путь: автогенерация локальных конфигов
Используйте инициализатор, чтобы сгенерировать локальные конфиги агентов в workspace:

```bat
start.bat --workspace D:\Projects\MyWork --agents codex,claude,qwen,opencode,kimi
```

Будут созданы:
- `.codex/config.toml`
- `.qwen/settings.json`
- `.opencode/opencode.json`
- `.kimi/settings.json`
- `.mcp.json` (локальный MCP-конфиг в стиле Claude)

## Глобальный режим (опционально)
Если нужно писать в глобальные пользовательские конфиги:

```bat
start.bat --scope global --workspace D:\Projects\MyWork --agents codex,claude
```

## Универсальный stdio-конфиг (ручной fallback)
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
