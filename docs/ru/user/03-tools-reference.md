# 03. Справочник Инструментов

Инструменты вызываются через JSON-RPC `tools/call`.

Успех:
- `result.data`

Ошибка:
- `result.isError = true`
- `result.error`

## Инструменты
- `read_map`
- `write_memory`
- `read_memory`
- `search_room`
- `move_file`
- `update_map`
- `metabolize`
- `purge_memory`
- `recover_journal`
- `get_metrics`
- `healthcheck`

## Основные коды ошибок
- `invalid_arguments`
- `not_found`
- `path_violation`
- `policy_violation`
- `rate_limited`
- `budget_exceeded`
- `timeout_exceeded`
