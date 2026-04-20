# 04. Troubleshooting

## `policy_violation`
Симптом:
- операция `metabolize`/`purge_memory` отклонена.

Причина:
- для destructive-операций нужен `confirm=true`.

Решение:
- повторить вызов с `confirm: true`.

## `rate_limited`
Симптом:
- destructive-операция блокируется.

Причина:
- превышен лимит операций в окне времени из `memory/_System/policy.yaml`.

Решение:
- подождать окно лимита или скорректировать policy.

## `budget_exceeded`
Симптом:
- отклонён слишком большой input.

Причина:
- превышен транспортный budget (длина `content/query/room/reason`).

Решение:
- уменьшить payload или увеличить budget через `SEDIMENT_BUDGET_*`.

## `timeout_exceeded`
Симптом:
- tool завершился по таймауту.

Причина:
- операция превысила per-tool timeout.

Решение:
- увеличить `SEDIMENT_TIMEOUT_*` или сократить объём обработки.

## Неожиданный результат после сбоя
Решение:
1. Вызвать `recover_journal`.
2. Проверить `result.data.recovered`.
3. Проверить `memory/_System/journal.log`.

## Диагностика состояния
1. `healthcheck` — жив ли сервис.
2. `get_metrics` — есть ли рост ошибок по tool.
3. Проверка файлов:
  - `memory/_System/journal.log`
  - `memory/_System/metrics.json`
  - `memory/_System/telemetry.log`
