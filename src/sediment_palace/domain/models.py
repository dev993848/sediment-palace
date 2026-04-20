from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

LayerName = Literal["shallow", "sediment", "bedrock"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class MemoryEntry:
    entry_id: str
    layer: LayerName
    created: datetime
    last_touched: datetime
    density: float
    streak: int
    decay_days: int
    tags: list[str]
    status: str
    source_session: str
    content: str
