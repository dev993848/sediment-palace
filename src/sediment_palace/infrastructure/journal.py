from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC
from pathlib import Path
from typing import Any
from uuid import uuid4

from sediment_palace.domain.models import utc_now


@dataclass(slots=True)
class JournalEvent:
    timestamp: str
    operation_id: str
    operation: str
    state: str
    payload: dict[str, Any]


class OperationJournal:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def start(self, operation: str, payload: dict[str, Any]) -> str:
        operation_id = uuid4().hex
        self.append(
            JournalEvent(
                timestamp=utc_now().astimezone(UTC).isoformat(),
                operation_id=operation_id,
                operation=operation,
                state="started",
                payload=payload,
            )
        )
        return operation_id

    def complete(self, operation_id: str, operation: str, payload: dict[str, Any]) -> None:
        self.append(
            JournalEvent(
                timestamp=utc_now().astimezone(UTC).isoformat(),
                operation_id=operation_id,
                operation=operation,
                state="completed",
                payload=payload,
            )
        )

    def append(self, event: JournalEvent) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def read_all(self) -> list[JournalEvent]:
        events: list[JournalEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            raw = json.loads(line)
            events.append(
                JournalEvent(
                    timestamp=str(raw.get("timestamp", "")),
                    operation_id=str(raw.get("operation_id", "")),
                    operation=str(raw.get("operation", "")),
                    state=str(raw.get("state", "")),
                    payload=dict(raw.get("payload", {})),
                )
            )
        return events
