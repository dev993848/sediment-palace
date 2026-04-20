from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    timeout_default_seconds: float
    timeout_metabolize_seconds: float
    write_content_budget: int
    read_query_budget: int
    search_query_budget: int
    search_room_budget: int
    purge_reason_budget: int


def load_config() -> AppConfig:
    root = Path(os.environ.get("SEDIMENT_PROJECT_ROOT", ".")).resolve()
    return AppConfig(
        project_root=root,
        timeout_default_seconds=float(os.environ.get("SEDIMENT_TIMEOUT_DEFAULT_SECONDS", "2.0")),
        timeout_metabolize_seconds=float(os.environ.get("SEDIMENT_TIMEOUT_METABOLIZE_SECONDS", "5.0")),
        write_content_budget=int(os.environ.get("SEDIMENT_BUDGET_WRITE_CONTENT", "50000")),
        read_query_budget=int(os.environ.get("SEDIMENT_BUDGET_READ_QUERY", "512")),
        search_query_budget=int(os.environ.get("SEDIMENT_BUDGET_SEARCH_QUERY", "512")),
        search_room_budget=int(os.environ.get("SEDIMENT_BUDGET_SEARCH_ROOM", "1024")),
        purge_reason_budget=int(os.environ.get("SEDIMENT_BUDGET_PURGE_REASON", "1024")),
    )
