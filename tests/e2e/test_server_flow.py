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
