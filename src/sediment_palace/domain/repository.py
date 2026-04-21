from __future__ import annotations

from typing import Protocol

from sediment_palace.domain.models import LayerName


class MemoryRepository(Protocol):
    def read_map(self) -> str: ...

    def write_memory(
        self,
        layer: LayerName,
        path: str,
        content: str,
        tags: list[str] | None,
        source_session: str,
    ) -> str: ...

    def read_memory(
        self,
        *,
        path: str | None,
        query: str | None,
        layer: LayerName | None,
    ) -> dict[str, object]: ...

    def search_room(self, *, room: str, query: str) -> dict[str, object]: ...

    def move_file(
        self, *, source: str, dest_layer: LayerName, new_path: str | None
    ) -> dict[str, str]: ...

    def update_map(self, *, action: str, details: dict[str, object]) -> dict[str, str]: ...

    def recover_journal(self) -> dict[str, object]: ...

    def purge_memory(self, *, path: str, reason: str, confirm: bool) -> dict[str, str]: ...

    def metabolize(
        self, *, dry_run: bool, days_threshold: int | None, confirm: bool
    ) -> dict[str, object]: ...
