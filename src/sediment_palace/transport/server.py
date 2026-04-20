from __future__ import annotations

from pathlib import Path
from typing import Any

from sediment_palace.application.memory_service import MemoryService
from sediment_palace.domain.errors import SedimentPalaceError
from sediment_palace.infrastructure.filesystem_memory_repository import (
    FileSystemMemoryRepository,
)


class SedimentPalaceServer:
    def __init__(self, project_root: Path) -> None:
        repository = FileSystemMemoryRepository(project_root=project_root)
        self.service = MemoryService(repository=repository)

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        request_id = request.get("id")
        method = request.get("method")
        try:
            if method == "initialize":
                return self._ok(
                    request_id,
                    {
                        "protocolVersion": "0.1.0",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "sediment-palace", "version": "0.1.0"},
                    },
                )
            if method == "tools/list":
                return self._ok(request_id, {"tools": self._tool_schemas()})
            if method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = self._call_tool(tool_name=tool_name, arguments=arguments)
                return self._ok(request_id, {"content": [{"type": "text", "text": result}]})
            return self._err(request_id, "method_not_found", f"method not found: {method}")
        except SedimentPalaceError as exc:
            payload = {
                "error_code": exc.error_code,
                "message": exc.message,
                "retryable": exc.retryable,
                "context": exc.context,
            }
            return self._ok(request_id, {"content": [{"type": "text", "text": str(payload)}], "isError": True})
        except Exception as exc:  # pragma: no cover
            return self._err(request_id, "internal_error", str(exc))

    def _call_tool(self, *, tool_name: str, arguments: dict[str, Any]) -> str:
        if tool_name == "read_map":
            return self.service.read_map()
        if tool_name == "write_memory":
            layer = arguments.get("layer", "shallow")
            path = arguments.get("path", "entry.md")
            content = arguments.get("content")
            if not content:
                raise SedimentPalaceError(
                    error_code="invalid_arguments",
                    message="write_memory requires content",
                )
            saved_path = self.service.write_memory(
                layer=layer,
                path=path,
                content=content,
                tags=arguments.get("tags"),
                source_session=arguments.get("source_session", "mcp_session"),
            )
            return f"saved:{saved_path}"
        if tool_name == "read_memory":
            response = self.service.read_memory(
                path=arguments.get("path"),
                query=arguments.get("query"),
                layer=arguments.get("layer"),
            )
            return str(response)
        raise SedimentPalaceError(
            error_code="tool_not_found",
            message=f"tool not found: {tool_name}",
            context={"tool_name": tool_name},
        )

    def _tool_schemas(self) -> list[dict[str, Any]]:
        return [
            {"name": "read_map", "description": "Read PALACE_MAP.md", "inputSchema": {"type": "object", "properties": {}}},
            {
                "name": "write_memory",
                "description": "Create or update memory entry",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "layer": {"type": "string", "enum": ["shallow", "sediment", "bedrock"]},
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "source_session": {"type": "string"},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "read_memory",
                "description": "Read by path or query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "query": {"type": "string"},
                        "layer": {"type": "string", "enum": ["shallow", "sediment", "bedrock"]},
                    },
                },
            },
        ]

    def _ok(self, request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _err(self, request_id: Any, code: str, message: str) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
