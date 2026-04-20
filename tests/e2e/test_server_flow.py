import shutil
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
    assert "saved:01_Shallow/ideas/t1.md" in write_response["result"]["content"][0]["text"]

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
    assert "01_Shallow/ideas/t1.md" in read_response["result"]["content"][0]["text"]


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
    assert "01_Shallow/ideas/t2.md" in search_response["result"]["content"][0]["text"]

    move_response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {"name": "move_file", "arguments": {"source": "01_Shallow/ideas/t2.md", "dest_layer": "sediment"}},
        }
    )
    assert "02_Sediment/t2.md" in move_response["result"]["content"][0]["text"]

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
    assert "add_link" in add_link_response["result"]["content"][0]["text"]
