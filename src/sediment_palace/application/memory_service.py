from __future__ import annotations

from sediment_palace.domain.models import LayerName
from sediment_palace.domain.repository import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository

    def read_map(self) -> str:
        return self.repository.read_map()

    def write_memory(
        self,
        *,
        layer: LayerName,
        path: str,
        content: str,
        tags: list[str] | None,
        source_session: str,
    ) -> str:
        return self.repository.write_memory(
            layer=layer,
            path=path,
            content=content,
            tags=tags,
            source_session=source_session,
        )

    def read_memory(
        self, *, path: str | None = None, query: str | None = None, layer: LayerName | None = None
    ) -> dict[str, object]:
        return self.repository.read_memory(path=path, query=query, layer=layer)

    def search_room(self, *, room: str, query: str) -> dict[str, object]:
        return self.repository.search_room(room=room, query=query)

    def move_file(self, *, source: str, dest_layer: LayerName, new_path: str | None = None) -> dict[str, str]:
        return self.repository.move_file(source=source, dest_layer=dest_layer, new_path=new_path)

    def update_map(self, *, action: str, details: dict[str, object]) -> dict[str, str]:
        return self.repository.update_map(action=action, details=details)

    def recover_journal(self) -> dict[str, object]:
        return self.repository.recover_journal()

    def purge_memory(self, *, path: str, reason: str, confirm: bool = False) -> dict[str, str]:
        return self.repository.purge_memory(path=path, reason=reason, confirm=confirm)

    def metabolize(
        self,
        *,
        dry_run: bool = False,
        days_threshold: int | None = None,
        confirm: bool = False,
    ) -> dict[str, object]:
        return self.repository.metabolize(
            dry_run=dry_run,
            days_threshold=days_threshold,
            confirm=confirm,
        )
