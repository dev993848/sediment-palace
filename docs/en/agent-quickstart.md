# Agent Quickstart (English)

Use this for a true plug-and-play setup:

1. Start server:
```bash
python -m sediment_palace.main
```
2. Connect MCP in your console agent using `docs/en/user/06-mcp-config-examples.md`.
3. Set `AGENT_BOOTSTRAP.md` as your agent system/developer prompt.
4. Start session and verify startup sequence:
   - `healthcheck`
   - `tools/list`
   - `read_map`

No extra skill is required for normal usage.
