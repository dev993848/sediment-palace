import shutil
from pathlib import Path

import pytest

from sediment_palace.domain.errors import SedimentPalaceError
from sediment_palace.infrastructure.filesystem_memory_repository import (
    FileSystemMemoryRepository,
)


def _new_project_root() -> Path:
    root = Path("tests/fixtures/work1").resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_write_and_read_by_path():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    saved = repo.write_memory(
        layer="shallow",
        path="ideas/auth-flow",
        content="OAuth2 notes",
        tags=["auth"],
        source_session="test",
    )
    assert saved == "01_Shallow/ideas/auth-flow.md"
    data = repo.read_memory(path=saved)
    assert data["content"] == "OAuth2 notes"
    assert data["metadata"]["layer"] == "shallow"


def test_read_by_query_in_layer():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    repo.write_memory(
        layer="shallow",
        path="notes/a",
        content="token refresh flow",
        tags=[],
        source_session="test",
    )
    repo.write_memory(
        layer="sediment",
        path="notes/b",
        content="database schema",
        tags=[],
        source_session="test",
    )
    result = repo.read_memory(query="token", layer="shallow")
    assert len(result["matches"]) == 1
    assert result["matches"][0]["path"].startswith("01_Shallow/")


def test_path_traversal_blocked():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    with pytest.raises(SedimentPalaceError) as exc:
        repo.write_memory(
            layer="shallow",
            path="../../escape",
            content="x",
            tags=[],
            source_session="test",
        )
    assert exc.value.error_code == "path_violation"


def test_search_room_and_move_file_and_update_map():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    src_path = repo.write_memory(
        layer="shallow",
        path="ideas/sedimentation",
        content="move me to sediment layer",
        tags=["idea", "flow"],
        source_session="test",
    )
    search_result = repo.search_room(room="01_Shallow/ideas", query="sediment")
    assert len(search_result["matches"]) == 1
    assert search_result["matches"][0]["path"] == src_path

    move_result = repo.move_file(source=src_path, dest_layer="sediment")
    assert move_result["destination"].startswith("02_Sediment/")
    moved = repo.read_memory(path=move_result["destination"])
    assert moved["metadata"]["layer"] == "sediment"

    update_add = repo.update_map(action="add_link", details={"link": "[[02_Sediment/sedimentation.md]]"})
    assert update_add["action"] == "add_link"
    assert "[[02_Sediment/sedimentation.md]]" in repo.read_map()

    update_remove = repo.update_map(action="remove_link", details={"link": "[[02_Sediment/sedimentation.md]]"})
    assert update_remove["action"] == "remove_link"
    assert "[[02_Sediment/sedimentation.md]]" not in repo.read_map()
