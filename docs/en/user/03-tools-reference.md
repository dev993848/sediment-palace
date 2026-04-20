# 03. Tools Reference

Tools are called via JSON-RPC `tools/call`.

Success:
- `result.data`

Error:
- `result.isError = true`
- `result.error`

## Tools
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

## Common Error Codes
- `invalid_arguments`
- `not_found`
- `path_violation`
- `policy_violation`
- `rate_limited`
- `budget_exceeded`
- `timeout_exceeded`
