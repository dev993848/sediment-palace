from datetime import UTC, timedelta
from pathlib import Path

import pytest
from conftest import make_workdir
from sediment_palace.domain.frontmatter import compose_frontmatter, split_frontmatter
from sediment_palace.domain.models import utc_now
from sediment_palace.infrastructure.filesystem_memory_repository import (
    FileSystemMemoryRepository,
)

try:
    from hypothesis import given, settings
    from hypothesis import strategies as st
except ModuleNotFoundError:  # pragma: no cover - optional dependency in local env
    pytest.skip("hypothesis is required for property-based tests", allow_module_level=True)


def _new_project_root() -> Path:
    return make_workdir("work3")


def _seed_shallow_file(
    repo: FileSystemMemoryRepository,
    *,
    name: str,
    density: float,
    age_days: int,
    streak: int,
) -> str:
    saved = repo.write_memory(
        layer="shallow",
        path=f"ideas/{name}",
        content=f"content:{name}",
        tags=[],
        source_session="property-test",
    )
    path = repo.memory_root / saved
    raw = path.read_text(encoding="utf-8")
    metadata, body = split_frontmatter(raw)
    metadata["density"] = density
    metadata["streak"] = streak
    metadata["last_touched"] = (utc_now() - timedelta(days=age_days)).astimezone(UTC).isoformat()
    path.write_text(compose_frontmatter(metadata, body), encoding="utf-8")
    return saved


@settings(max_examples=40)
@given(
    density=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    age_days=st.integers(min_value=0, max_value=30),
    streak=st.integers(min_value=-3, max_value=10),
)
def test_metabolize_dry_run_preserves_files(density: float, age_days: int, streak: int):
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    src = _seed_shallow_file(repo, name="dryrun-prop", density=density, age_days=age_days, streak=streak)

    before = (repo.memory_root / src).read_text(encoding="utf-8")
    result = repo.metabolize(dry_run=True, days_threshold=7)
    after = (repo.memory_root / src).read_text(encoding="utf-8")

    assert before == after
    assert result["dry_run"] is True
    assert result["scanned"] >= 1


@settings(max_examples=50)
@given(
    density=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    age_days=st.integers(min_value=0, max_value=45),
    streak=st.integers(min_value=-3, max_value=10),
)
def test_metabolize_never_moves_outside_known_roots(density: float, age_days: int, streak: int):
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    _seed_shallow_file(repo, name="bounds-prop", density=density, age_days=age_days, streak=streak)

    result = repo.metabolize(confirm=True, days_threshold=7)
    valid_prefixes = ("01_Shallow/", "02_Sediment/", "03_Bedrock/", "_Archive/")

    for collection_name in ("promoted", "archived", "decaying"):
        for rel in result.get(collection_name, []):
            assert isinstance(rel, str)
            assert rel.startswith(valid_prefixes)


@settings(max_examples=50)
@given(
    density=st.floats(min_value=0.5, max_value=1.0, allow_nan=False, allow_infinity=False),
    age_days=st.integers(min_value=8, max_value=30),
    streak=st.integers(min_value=-3, max_value=10),
)
def test_shallow_high_density_stale_promotes_to_sediment(density: float, age_days: int, streak: int):
    repo = FileSystemMemoryRepository(project_root=_new_project_root())
    src = _seed_shallow_file(repo, name="promote-prop", density=density, age_days=age_days, streak=streak)
    src_path = repo.memory_root / src

    result = repo.metabolize(confirm=True, days_threshold=7)
    promoted = result["promoted"]
    assert any(item.startswith("02_Sediment/") for item in promoted)
    assert not src_path.exists()
