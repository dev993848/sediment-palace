# 01. Быстрый Старт

## 1) Установка
```bash
python -m pip install -e ".[dev]"
```

## 2) Запуск сервера
```bash
python -m sediment_palace.main
```

Сервер читает JSON-RPC из `stdin` и пишет ответы в `stdout`.

## 3) Первая проверка
Отправьте запрос `initialize`, затем `tools/list`, затем `tools/call` для `healthcheck`.

Пример `tools/call`:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "healthcheck",
    "arguments": {}
  }
}
```

Ожидаемый результат:
- `result.data.status = "ok"`
- `result.data.service = "sediment-palace"`
