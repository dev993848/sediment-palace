# 04. Troubleshooting

## `policy_violation`
- Add `confirm=true` for destructive operations.

## `rate_limited`
- You hit destructive-operation limits from `memory/_System/policy.yaml`.

## `budget_exceeded`
- Reduce request payload size or increase `SEDIMENT_BUDGET_*` limits.

## `timeout_exceeded`
- Increase `SEDIMENT_TIMEOUT_*` or reduce operation scope.

## Crash/interruption recovery
1. Call `recover_journal`.
2. Check `result.data.recovered`.
3. Check `memory/_System/journal.log`.
