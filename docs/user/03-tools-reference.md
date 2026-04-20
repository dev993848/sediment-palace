# 03. Справочник Инструментов

Все инструменты вызываются через JSON-RPC `tools/call` и возвращают:
- успех: `result.data`
- ошибка: `result.isError=true`, `result.error`

## read_map
- Назначение: вернуть `PALACE_MAP.md`.
- Аргументы: `{}`.

## write_memory
- Назначение: создать/обновить заметку.
- Аргументы:
  - `layer`: `shallow|sediment|bedrock`
  - `path`: путь без обязательного `.md`
  - `content`: текст
  - `tags`: список строк (опционально)
  - `source_session`: строка (опционально)

## read_memory
- Назначение: прочитать по пути или найти по запросу.
- Аргументы:
  - либо `path`
  - либо `query` (+ `layer` опционально)

## search_room
- Назначение: поиск в конкретной папке.
- Аргументы: `room`, `query`.

## move_file
- Назначение: переместить файл между слоями.
- Аргументы: `source`, `dest_layer`, `new_path` (опционально).

## update_map
- Назначение: добавить/удалить ссылку в карте.
- Аргументы:
  - `action`: `add_link|remove_link`
  - `details.link`: строка ссылки

## metabolize
- Назначение: автоматические переходы/архивация по правилам возраста, плотности и streak.
- Аргументы:
  - `dry_run`: bool
  - `days_threshold`: int (опционально)
  - `confirm`: bool (обязательно для `dry_run=false`)

## purge_memory
- Назначение: архивировать и удалить запись из активного слоя.
- Аргументы: `path`, `reason`, `confirm=true`.

## recover_journal
- Назначение: обработка незавершённых операций в журнале.
- Аргументы: `{}`.

## get_metrics
- Назначение: вернуть агрегированную телеметрию по инструментам.
- Аргументы: `{}`.

## healthcheck
- Назначение: базовая проверка работоспособности сервиса.
- Аргументы: `{}`.

## Основные коды ошибок
- `invalid_arguments`
- `not_found`
- `path_violation`
- `policy_violation`
- `rate_limited`
- `budget_exceeded`
- `timeout_exceeded`
- `injected_failure` (тестовый fault-injection)
