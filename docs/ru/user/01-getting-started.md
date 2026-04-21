# 01. Быстрый Старт

## Рекомендуется: инициализация одной командой
Из корня репозитория запустите:

```bat
start.bat --workspace D:\Projects\MyWork --agents codex,claude,qwen,opencode,kimi
```

Скрипт автоматически:
- проверит/установит Python-зависимости,
- создаст структуру `memory/` в выбранной рабочей папке,
- скопирует `AGENT_BOOTSTRAP.md`,
- создаст instruction-файлы агентов (`AGENTS.md`, `CLAUDE.md`, `QWEN.md` и т.д.),
- создаст локальные конфиги агентов в workspace.

## Ручная установка (если нужно)
```bash
python -m pip install -e ".[dev]"
```

## Ручной запуск сервера (для отладки)
```bash
python -m sediment_palace.main
```

Сервер читает JSON-RPC из `stdin` и пишет ответы в `stdout`.

## Первая проверка
Вызовите по порядку:
1. `initialize`
2. `tools/list`
3. `tools/call` с `healthcheck`

Ожидаемый результат:
- `result.data.status = "ok"`
- `result.data.service = "sediment-palace"`
