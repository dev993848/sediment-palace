from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sediment_palace.domain.errors import SedimentPalaceError
from sediment_palace.domain.frontmatter import compose_frontmatter, split_frontmatter
from sediment_palace.domain.models import LayerName, MemoryEntry, utc_now

LAYER_DIRS: dict[LayerName, str] = {
    "shallow": "01_Shallow",
    "sediment": "02_Sediment",
    "bedrock": "03_Bedrock",
}

DEFAULT_DECAY_DAYS: dict[LayerName, int] = {
    "shallow": 7,
    "sediment": 60,
    "bedrock": 36500,
}


class FileSystemMemoryRepository:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.memory_root = (self.project_root / "memory").resolve()
        self.map_file = self.memory_root / "PALACE_MAP.md"

    def ensure_layout(self) -> None:
        self.memory_root.mkdir(parents=True, exist_ok=True)
        for dirname in LAYER_DIRS.values():
            (self.memory_root / dirname).mkdir(parents=True, exist_ok=True)
        if not self.map_file.exists():
            self.map_file.write_text("# PALACE MAP\n", encoding="utf-8")

    def read_map(self) -> str:
        self.ensure_layout()
        return self.map_file.read_text(encoding="utf-8")

    def write_memory(
        self,
        layer: LayerName,
        path: str,
        content: str,
        tags: list[str] | None = None,
        source_session: str = "unknown_session",
    ) -> str:
        self.ensure_layout()
        target = self._resolve_target(layer=layer, relative_path=path)
        target.parent.mkdir(parents=True, exist_ok=True)
        now = utc_now()

        existing = self._read_entry_if_exists(target)
        if existing is None:
            entry = MemoryEntry(
                entry_id=f"mem_{uuid4().hex[:12]}",
                layer=layer,
                created=now,
                last_touched=now,
                density=0.2,
                decay_days=DEFAULT_DECAY_DAYS[layer],
                tags=tags or [],
                status="active",
                source_session=source_session,
                content=content,
            )
        else:
            entry = MemoryEntry(
                entry_id=existing.entry_id,
                layer=layer,
                created=existing.created,
                last_touched=now,
                density=existing.density,
                decay_days=existing.decay_days,
                tags=tags if tags is not None else existing.tags,
                status=existing.status,
                source_session=source_session or existing.source_session,
                content=content,
            )

        target.write_text(self._serialize_entry(entry), encoding="utf-8")
        return str(target.relative_to(self.memory_root)).replace("\\", "/")

    def read_memory(
        self,
        *,
        path: str | None = None,
        query: str | None = None,
        layer: LayerName | None = None,
    ) -> dict[str, object]:
        self.ensure_layout()
        if path:
            target = self._resolve_path_in_memory(path)
            if not target.exists():
                raise SedimentPalaceError(
                    error_code="not_found",
                    message=f"memory file not found: {path}",
                    context={"path": path},
                )
            raw = target.read_text(encoding="utf-8")
            metadata, body = split_frontmatter(raw)
            return {
                "path": str(target.relative_to(self.memory_root)).replace("\\", "/"),
                "metadata": metadata,
                "content": body.strip(),
            }

        if not query:
            raise SedimentPalaceError(
                error_code="invalid_arguments",
                message="read_memory requires either path or query",
            )

        search_root = self.memory_root
        if layer:
            search_root = self.memory_root / LAYER_DIRS[layer]

        matches: list[dict[str, str]] = []
        for md_file in search_root.rglob("*.md"):
            raw = md_file.read_text(encoding="utf-8")
            metadata, body = split_frontmatter(raw)
            haystack = f"{metadata}\n{body}".lower()
            if query.lower() in haystack:
                matches.append(
                    {
                        "path": str(md_file.relative_to(self.memory_root)).replace("\\", "/"),
                        "snippet": body.strip()[:200],
                    }
                )
        return {"query": query, "layer": layer, "matches": matches}

    def _resolve_target(self, *, layer: LayerName, relative_path: str) -> Path:
        layer_dir = self.memory_root / LAYER_DIRS[layer]
        rel = Path(relative_path)
        if rel.suffix.lower() != ".md":
            rel = rel.with_suffix(".md")
        candidate = (layer_dir / rel).resolve()
        if not str(candidate).startswith(str(layer_dir.resolve())):
            raise SedimentPalaceError(
                error_code="path_violation",
                message="target path escapes layer boundary",
                context={"path": relative_path, "layer": layer},
            )
        return candidate

    def _resolve_path_in_memory(self, relative_path: str) -> Path:
        candidate = (self.memory_root / relative_path).resolve()
        if not str(candidate).startswith(str(self.memory_root)):
            raise SedimentPalaceError(
                error_code="path_violation",
                message="path escapes memory root",
                context={"path": relative_path},
            )
        return candidate

    def _read_entry_if_exists(self, file_path: Path) -> MemoryEntry | None:
        if not file_path.exists():
            return None
        raw = file_path.read_text(encoding="utf-8")
        metadata, body = split_frontmatter(raw)
        if not metadata:
            return None

        created = self._parse_iso(str(metadata.get("created")))
        last_touched = self._parse_iso(str(metadata.get("last_touched")))
        layer = str(metadata.get("layer", "shallow"))
        if layer not in {"shallow", "sediment", "bedrock"}:
            layer = "shallow"

        return MemoryEntry(
            entry_id=str(metadata.get("id", f"mem_{uuid4().hex[:12]}")),
            layer=layer,  # type: ignore[arg-type]
            created=created,
            last_touched=last_touched,
            density=float(metadata.get("density", 0.2)),
            decay_days=int(metadata.get("decay_days", 7)),
            tags=list(metadata.get("tags", [])),
            status=str(metadata.get("status", "active")),
            source_session=str(metadata.get("source_session", "unknown_session")),
            content=body.strip(),
        )

    def _serialize_entry(self, entry: MemoryEntry) -> str:
        metadata = {
            "id": entry.entry_id,
            "layer": entry.layer,
            "created": entry.created.astimezone(timezone.utc).isoformat(),
            "last_touched": entry.last_touched.astimezone(timezone.utc).isoformat(),
            "density": float(entry.density),
            "decay_days": int(entry.decay_days),
            "tags": list(entry.tags),
            "status": entry.status,
            "source_session": entry.source_session,
        }
        return compose_frontmatter(metadata=metadata, body=entry.content)

    def _parse_iso(self, value: str):
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            return utc_now()
