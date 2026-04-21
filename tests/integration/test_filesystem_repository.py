from datetime import UTC, timedelta
from pathlib import Path

import pytest
from conftest import make_workdir

from sediment_palace.domain.errors import SedimentPalaceError
from sediment_palace.domain.frontmatter import compose_frontmatter, split_frontmatter
from sediment_palace.domain.models import utc_now
from sediment_palace.infrastructure.filesystem_memory_repository import (
    FileSystemMemoryRepository,
)


def _new_project_root() -> Path:
    return make_workdir("work1")


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


def test_path_prefix_escape_blocked_for_target_layer():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    with pytest.raises(SedimentPalaceError) as exc:
        repo.write_memory(
            layer="shallow",
            path="../01_Shallow2/evil",
            content="x",
            tags=[],
            source_session="test",
        )
    assert exc.value.error_code == "path_violation"


def test_path_prefix_escape_blocked_for_memory_root():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    with pytest.raises(SedimentPalaceError) as exc:
        repo.read_memory(path="../memory_evil/owned.md")
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

    journal_text = (repo.memory_root / "_System" / "journal.log").read_text(encoding="utf-8")
    assert '"state": "started"' in journal_text
    assert '"state": "completed"' in journal_text


def test_recover_journal_handles_unresolved_events():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    saved = repo.write_memory(
        layer="shallow",
        path="ideas/recover-me",
        content="recovery check",
        tags=[],
        source_session="test",
    )
    orphan_op = repo.journal.start("write_memory", {"path": saved})

    result = repo.recover_journal()
    assert result["unresolved_count"] >= 1
    assert result["recovered_count"] >= 1

    journal_text = (repo.memory_root / "_System" / "journal.log").read_text(encoding="utf-8")
    assert orphan_op in journal_text
    assert '"recovery_status": "completed"' in journal_text


def test_metabolize_promotes_and_archives_with_confirm():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    promote_src = repo.write_memory(
        layer="shallow",
        path="ideas/promote-me",
        content="promote",
        tags=[],
        source_session="test",
    )
    archive_src = repo.write_memory(
        layer="shallow",
        path="ideas/archive-me",
        content="archive",
        tags=[],
        source_session="test",
    )

    promote_path = repo.memory_root / promote_src
    archive_path = repo.memory_root / archive_src
    for file_path, density in ((promote_path, 0.9), (archive_path, 0.1)):
        raw = file_path.read_text(encoding="utf-8")
        metadata, body = split_frontmatter(raw)
        metadata["density"] = density
        if density < 0.2:
            metadata["streak"] = -2
        metadata["last_touched"] = (utc_now() - timedelta(days=10)).astimezone(UTC).isoformat()
        file_path.write_text(compose_frontmatter(metadata, body), encoding="utf-8")

    result = repo.metabolize(confirm=True)
    assert result["promoted_count"] >= 1
    assert result["archived_count"] >= 1
    assert (repo.memory_root / "02_Sediment/ideas/promote-me.md").exists()
    assert (repo.memory_root / "_Archive/01_Shallow/ideas/archive-me.md").exists()


def test_metabolize_dry_run_does_not_mutate():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    src = repo.write_memory(
        layer="shallow",
        path="ideas/dry-run",
        content="dry run",
        tags=[],
        source_session="test",
    )
    src_path = repo.memory_root / src
    raw = src_path.read_text(encoding="utf-8")
    metadata, body = split_frontmatter(raw)
    metadata["density"] = 0.9
    metadata["last_touched"] = (utc_now() - timedelta(days=14)).astimezone(UTC).isoformat()
    src_path.write_text(compose_frontmatter(metadata, body), encoding="utf-8")

    result = repo.metabolize(dry_run=True)
    assert result["promoted_count"] >= 1
    assert src_path.exists()
    assert not (repo.memory_root / "02_Sediment/ideas/dry-run.md").exists()


def test_metabolize_updates_streak_and_decaying_status():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    src = repo.write_memory(
        layer="shallow",
        path="ideas/slow-decay",
        content="decay check",
        tags=[],
        source_session="test",
    )
    src_path = repo.memory_root / src
    raw = src_path.read_text(encoding="utf-8")
    metadata, body = split_frontmatter(raw)
    metadata["density"] = 0.3
    metadata["streak"] = 1
    metadata["last_touched"] = (utc_now() - timedelta(days=9)).astimezone(UTC).isoformat()
    src_path.write_text(compose_frontmatter(metadata, body), encoding="utf-8")

    result = repo.metabolize(confirm=True, days_threshold=7)
    assert result["decaying_count"] >= 1
    updated = repo.read_memory(path=src)
    assert updated["metadata"]["status"] == "decaying"
    assert int(updated["metadata"]["streak"]) == 0


def test_purge_memory_requires_confirm():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    src = repo.write_memory(
        layer="shallow",
        path="ideas/purge-me",
        content="purge",
        tags=[],
        source_session="test",
    )
    with pytest.raises(SedimentPalaceError) as exc:
        repo.purge_memory(path=src, reason="test")
    assert exc.value.error_code == "policy_violation"

    result = repo.purge_memory(path=src, reason="test", confirm=True)
    assert result["archived_to"].startswith("_Archive/")
    assert not (repo.memory_root / src).exists()


def test_policy_rate_limit_for_destructive_ops():
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    policy_file = repo.memory_root / "_System" / "policy.yaml"
    policy_file.write_text(
        (
            "destructive_require_confirm: true\n"
            "limits:\n"
            "  max_search_matches: 100\n"
            "  max_metabolize_scan: 5000\n"
            "rate_limit:\n"
            "  window_seconds: 3600\n"
            "  max_destructive_ops: 1\n"
        ),
        encoding="utf-8",
    )
    repo.metabolize(dry_run=False, confirm=True)
    with pytest.raises(SedimentPalaceError) as exc:
        repo.metabolize(dry_run=False, confirm=True)
    assert exc.value.error_code == "rate_limited"


def test_fault_injection_and_recovery_flow():
    repo = FileSystemMemoryRepository(
        project_root=_new_project_root(),
        failpoints={"write_memory_after_start": True},
    )
    with pytest.raises(SedimentPalaceError) as exc:
        repo.write_memory(
            layer="shallow",
            path="ideas/faulty",
            content="boom",
            tags=[],
            source_session="test",
        )
    assert exc.value.error_code == "injected_failure"

    recovered = repo.recover_journal()
    assert recovered["unresolved_count"] >= 1
    assert recovered["recovered_count"] >= 1
    assert not (repo.memory_root / "01_Shallow/ideas/faulty.md").exists()
