# 04. Troubleshooting

## `policy_violation`
- Для destructive-операций добавьте `confirm=true`.

## `rate_limited`
- Превышен лимит операций из `memory/_System/policy.yaml`.

## `budget_exceeded`
- Уменьшите payload или увеличьте `SEDIMENT_BUDGET_*`.

## `timeout_exceeded`
- Увеличьте `SEDIMENT_TIMEOUT_*` или уменьшите scope операции.

## После прерывания/сбоя
1. Вызвать `recover_journal`.
2. Проверить `result.data.recovered`.
3. Проверить `memory/_System/journal.log`.
