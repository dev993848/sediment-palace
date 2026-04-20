import shutil
import time
from pathlib import Path

from sediment_palace.transport.server import SedimentPalaceServer


def _new_project_root() -> Path:
    root = Path("tests/fixtures/work2").resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_initialize():
    server = SedimentPalaceServer(project_root=Path("."))
    response = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert response["result"]["serverInfo"]["name"] == "sediment-palace"


def test_write_then_read():
    server = SedimentPalaceServer(project_root=_new_project_root())

    write_response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "write_memory",
                "arguments": {"layer": "shallow", "path": "ideas/t1", "content": "hello world"},
            },
        }
    )
    assert write_response["result"]["data"]["saved_path"] == "01_Shallow/ideas/t1.md"

    read_response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "read_memory",
                "arguments": {"query": "hello", "layer": "shallow"},
            },
        }
    )
    matches = read_response["result"]["data"]["matches"]
    assert matches[0]["path"] == "01_Shallow/ideas/t1.md"


def test_search_move_update_map_flow():
    server = SedimentPalaceServer(project_root=_new_project_root())

    server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "write_memory",
                "arguments": {"layer": "shallow", "path": "ideas/t2", "content": "queryable content"},
            },
        }
    )

    search_response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "search_room", "arguments": {"room": "01_Shallow/ideas", "query": "queryable"}},
        }
    )
    assert search_response["result"]["data"]["matches"][0]["path"] == "01_Shallow/ideas/t2.md"

    move_response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {"name": "move_file", "arguments": {"source": "01_Shallow/ideas/t2.md", "dest_layer": "sediment"}},
        }
    )
    assert move_response["result"]["data"]["destination"] == "02_Sediment/t2.md"

    add_link_response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {
                "name": "update_map",
                "arguments": {"action": "add_link", "details": {"link": "[[02_Sediment/t2.md]]"}},
            },
        }
    )
    assert add_link_response["result"]["data"]["action"] == "add_link"


def test_recover_journal_tool():
    server = SedimentPalaceServer(project_root=_new_project_root())
    server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {
                "name": "write_memory",
                "arguments": {"layer": "shallow", "path": "ideas/t3", "content": "recover flow"},
            },
        }
    )

    recover_response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {"name": "recover_journal", "arguments": {}},
        }
    )
    assert "recovered_count" in recover_response["result"]["data"]


def test_metabolize_and_purge_policy_flow():
    server = SedimentPalaceServer(project_root=_new_project_root())
    server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 30,
            "method": "tools/call",
            "params": {
                "name": "write_memory",
                "arguments": {"layer": "shallow", "path": "ideas/to-purge", "content": "x"},
            },
        }
    )

    denied = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 31,
            "method": "tools/call",
            "params": {"name": "purge_memory", "arguments": {"path": "01_Shallow/ideas/to-purge.md"}},
        }
    )
    assert denied["result"]["isError"] is True
    assert denied["result"]["error"]["error_code"] == "policy_violation"

    allowed = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 32,
            "method": "tools/call",
            "params": {
                "name": "purge_memory",
                "arguments": {"path": "01_Shallow/ideas/to-purge.md", "reason": "cleanup", "confirm": True},
            },
        }
    )
    assert allowed["result"]["data"]["archived_to"].startswith("_Archive/")

    dry_metabolize = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 33,
            "method": "tools/call",
            "params": {"name": "metabolize", "arguments": {"dry_run": True}},
        }
    )
    assert dry_metabolize["result"]["data"]["dry_run"] is True


def test_transport_timeout_budget():
    server = SedimentPalaceServer(project_root=_new_project_root())
    server.tool_timeouts_seconds["read_map"] = 0.01

    original = server.service.read_map

    def slow_read_map():
        time.sleep(0.05)
        return original()

    server.service.read_map = slow_read_map  # type: ignore[method-assign]
    response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 40,
            "method": "tools/call",
            "params": {"name": "read_map", "arguments": {}},
        }
    )
    assert response["result"]["isError"] is True
    assert response["result"]["error"]["error_code"] == "timeout_exceeded"


def test_transport_input_budget():
    server = SedimentPalaceServer(project_root=_new_project_root())
    too_long_query = "x" * 1025
    response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 41,
            "method": "tools/call",
            "params": {"name": "search_room", "arguments": {"room": too_long_query, "query": "q"}},
        }
    )
    assert response["result"]["isError"] is True
    assert response["result"]["error"]["error_code"] == "budget_exceeded"
