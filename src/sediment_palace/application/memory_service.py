from __future__ import annotations

from sediment_palace.domain.models import LayerName
from sediment_palace.infrastructure.filesystem_memory_repository import (
    FileSystemMemoryRepository,
)


class MemoryService:
    def __init__(self, repository: FileSystemMemoryRepository) -> None:
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
