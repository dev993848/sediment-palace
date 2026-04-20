# 05. FAQ

## Где хранятся данные?
В локальной папке проекта, в `memory/`.

## Можно ли использовать без облака?
Да, система local-first и работает на файловой системе.

## Можно ли менять правила седиментации?
Да, через `memory/_System/policy.yaml` и runtime env-переменные.

## Что безопаснее: `metabolize` или `purge_memory`?
- `metabolize` — управляемый процесс правил.
- `purge_memory` — точечная destructive операция, требует `confirm=true`.

## Как понять, что система перегружена?
Смотреть `get_metrics`: рост `error`, `timeout_exceeded`, `budget_exceeded`, увеличение `avg_duration_ms`.

## Нужно ли запускать `recover_journal` регулярно?
Обычно нет. Запускайте после падений/прерываний или при подозрении на незавершённые операции.

## Какой минимальный операционный цикл?
1. `healthcheck`
2. рабочие операции (`write/read/search/move`)
3. `metabolize` (dry-run, затем confirm)
4. `get_metrics`
