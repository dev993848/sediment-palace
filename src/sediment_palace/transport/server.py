from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
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
        self.tool_timeouts_seconds: dict[str, float] = {
            "read_map": 1.0,
            "write_memory": 2.0,
            "read_memory": 2.0,
            "search_room": 2.0,
            "move_file": 2.0,
            "update_map": 1.0,
            "recover_journal": 3.0,
            "metabolize": 5.0,
            "purge_memory": 2.0,
        }
        self.tool_input_budgets: dict[str, int] = {
            "write_memory.content": 50_000,
            "read_memory.query": 512,
            "search_room.query": 512,
            "search_room.room": 1_024,
            "purge_memory.reason": 1_024,
        }

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
                self._validate_budgets(tool_name=tool_name, arguments=arguments)
                result = self._execute_with_timeout(tool_name=tool_name, arguments=arguments)
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
        if tool_name == "search_room":
            room = arguments.get("room")
            query = arguments.get("query")
            if not room or not query:
                raise SedimentPalaceError(
                    error_code="invalid_arguments",
                    message="search_room requires room and query",
                )
            response = self.service.search_room(room=room, query=query)
            return str(response)
        if tool_name == "move_file":
            source = arguments.get("source")
            dest_layer = arguments.get("dest_layer")
            if not source or not dest_layer:
                raise SedimentPalaceError(
                    error_code="invalid_arguments",
                    message="move_file requires source and dest_layer",
                )
            response = self.service.move_file(
                source=source,
                dest_layer=dest_layer,
                new_path=arguments.get("new_path"),
            )
            return str(response)
        if tool_name == "update_map":
            action = arguments.get("action")
            details = arguments.get("details", {})
            if not action:
                raise SedimentPalaceError(
                    error_code="invalid_arguments",
                    message="update_map requires action",
                )
            response = self.service.update_map(action=action, details=details)
            return str(response)
        if tool_name == "recover_journal":
            response = self.service.recover_journal()
            return str(response)
        if tool_name == "metabolize":
            response = self.service.metabolize(
                dry_run=bool(arguments.get("dry_run", False)),
                days_threshold=arguments.get("days_threshold"),
                confirm=bool(arguments.get("confirm", False)),
            )
            return str(response)
        if tool_name == "purge_memory":
            path = arguments.get("path")
            reason = arguments.get("reason", "unspecified")
            if not path:
                raise SedimentPalaceError(
                    error_code="invalid_arguments",
                    message="purge_memory requires path",
                )
            response = self.service.purge_memory(
                path=path,
                reason=reason,
                confirm=bool(arguments.get("confirm", False)),
            )
            return str(response)
        raise SedimentPalaceError(
            error_code="tool_not_found",
            message=f"tool not found: {tool_name}",
            context={"tool_name": tool_name},
        )

    def _execute_with_timeout(self, *, tool_name: str, arguments: dict[str, Any]) -> str:
        timeout = self.tool_timeouts_seconds.get(tool_name, 2.0)
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self._call_tool, tool_name=tool_name, arguments=arguments)
            try:
                return future.result(timeout=timeout)
            except FutureTimeoutError as exc:
                raise SedimentPalaceError(
                    error_code="timeout_exceeded",
                    message=f"{tool_name} exceeded timeout budget",
                    retryable=True,
                    context={"tool_name": tool_name, "timeout_seconds": timeout},
                ) from exc

    def _validate_budgets(self, *, tool_name: str, arguments: dict[str, Any]) -> None:
        for key, max_size in self.tool_input_budgets.items():
            budget_tool, budget_field = key.split(".", 1)
            if budget_tool != tool_name:
                continue
            value = arguments.get(budget_field)
            if value is None:
                continue
            if len(str(value)) > max_size:
                raise SedimentPalaceError(
                    error_code="budget_exceeded",
                    message=f"input budget exceeded for {tool_name}.{budget_field}",
                    context={"max_size": max_size, "actual_size": len(str(value))},
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
            {
                "name": "search_room",
                "description": "Search room directory by query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "room": {"type": "string"},
                        "query": {"type": "string"},
                    },
                    "required": ["room", "query"],
                },
            },
            {
                "name": "move_file",
                "description": "Move file to another layer",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "dest_layer": {"type": "string", "enum": ["shallow", "sediment", "bedrock"]},
                        "new_path": {"type": "string"},
                    },
                    "required": ["source", "dest_layer"],
                },
            },
            {
                "name": "update_map",
                "description": "Add or remove links in PALACE_MAP.md",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["add_link", "remove_link"]},
                        "details": {"type": "object"},
                    },
                    "required": ["action", "details"],
                },
            },
            {
                "name": "recover_journal",
                "description": "Recover unresolved operations from operation journal",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "metabolize",
                "description": "Apply decay and promotion rules across memory layers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dry_run": {"type": "boolean"},
                        "days_threshold": {"type": "integer"},
                        "confirm": {"type": "boolean"},
                    },
                },
            },
            {
                "name": "purge_memory",
                "description": "Archive and remove a memory entry (destructive)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "reason": {"type": "string"},
                        "confirm": {"type": "boolean"},
                    },
                    "required": ["path"],
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
