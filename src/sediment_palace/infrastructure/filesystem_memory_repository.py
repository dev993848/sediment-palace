from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sediment_palace.domain.errors import SedimentPalaceError
from sediment_palace.domain.frontmatter import compose_frontmatter, split_frontmatter
from sediment_palace.domain.models import LayerName, MemoryEntry, utc_now
from sediment_palace.infrastructure.journal import OperationJournal
from sediment_palace.infrastructure.lock_manager import FileLockManager
from sediment_palace.infrastructure.policy import PolicyEngine

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
    def __init__(self, project_root: Path, *, failpoints: dict[str, bool] | None = None) -> None:
        self.project_root = project_root.resolve()
        self.memory_root = (self.project_root / "memory").resolve()
        self.map_file = self.memory_root / "PALACE_MAP.md"
        self.system_root = self.memory_root / "_System"
        self.archive_root = self.memory_root / "_Archive"
        self.lock_manager = FileLockManager(lock_root=self.system_root / "locks")
        self.journal = OperationJournal(path=self.system_root / "journal.log")
        self.policy = PolicyEngine(system_root=self.system_root)
        self.failpoints = failpoints or {}

    def ensure_layout(self) -> None:
        self.memory_root.mkdir(parents=True, exist_ok=True)
        for dirname in LAYER_DIRS.values():
            (self.memory_root / dirname).mkdir(parents=True, exist_ok=True)
        self.system_root.mkdir(parents=True, exist_ok=True)
        self.archive_root.mkdir(parents=True, exist_ok=True)
        if not self.map_file.exists():
            self.map_file.write_text("# PALACE MAP\n", encoding="utf-8")
        for tmp in self.memory_root.rglob("*.md.tmp"):
            tmp.unlink(missing_ok=True)

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
        op_id = self.journal.start(
            "write_memory",
            {"layer": layer, "path": str(target.relative_to(self.memory_root)).replace("\\", "/")},
        )

        def _action() -> str:
            self._maybe_fail("write_memory_after_start")
            now = utc_now()
            existing = self._read_entry_if_exists(target)
            if existing is None:
                entry = MemoryEntry(
                    entry_id=f"mem_{uuid4().hex[:12]}",
                    layer=layer,
                    created=now,
                    last_touched=now,
                    density=0.2,
                    streak=0,
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
                    streak=existing.streak,
                    decay_days=existing.decay_days,
                    tags=tags if tags is not None else existing.tags,
                    status=existing.status,
                    source_session=source_session or existing.source_session,
                    content=content,
                )

            self._atomic_write(target, self._serialize_entry(entry))
            return str(target.relative_to(self.memory_root)).replace("\\", "/")

        result = self._with_lock(f"write:{target}", _action)
        self.journal.complete(op_id, "write_memory", {"saved_path": result})
        return result

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
        max_matches = self.policy.max_search_matches()
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
                if len(matches) >= max_matches:
                    break
        return {"query": query, "layer": layer, "matches": matches}

    def search_room(self, *, room: str, query: str) -> dict[str, object]:
        self.ensure_layout()
        room_path = self._resolve_path_in_memory(room)
        if not room_path.exists() or not room_path.is_dir():
            raise SedimentPalaceError(
                error_code="not_found",
                message=f"room not found: {room}",
                context={"room": room},
            )

        matches: list[dict[str, str]] = []
        needle = query.lower()
        max_matches = self.policy.max_search_matches()
        for md_file in room_path.rglob("*.md"):
            raw = md_file.read_text(encoding="utf-8")
            metadata, body = split_frontmatter(raw)
            tags = metadata.get("tags", [])
            haystack = f"{body}\n{tags}".lower()
            if needle in haystack:
                matches.append(
                    {
                        "path": str(md_file.relative_to(self.memory_root)).replace("\\", "/"),
                        "snippet": body.strip()[:200],
                    }
                )
                if len(matches) >= max_matches:
                    break
        return {"room": room, "query": query, "matches": matches}

    def move_file(self, *, source: str, dest_layer: LayerName, new_path: str | None = None) -> dict[str, str]:
        self.ensure_layout()
        source_file = self._resolve_path_in_memory(source)
        if not source_file.exists() or not source_file.is_file():
            raise SedimentPalaceError(
                error_code="not_found",
                message=f"source file not found: {source}",
                context={"source": source},
            )

        destination_relative = new_path or source_file.name
        destination_file = self._resolve_target(layer=dest_layer, relative_path=destination_relative)
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        if destination_file.exists():
            raise SedimentPalaceError(
                error_code="conflict",
                message="destination file already exists",
                context={
                    "source": str(source_file.relative_to(self.memory_root)).replace("\\", "/"),
                    "destination": str(destination_file.relative_to(self.memory_root)).replace("\\", "/"),
                },
            )

        op_id = self.journal.start(
            "move_file",
            {
                "source": source,
                "dest_layer": dest_layer,
                "destination": str(destination_file.relative_to(self.memory_root)).replace("\\", "/"),
            },
        )

        def _action() -> dict[str, str]:
            self._maybe_fail("move_file_after_start")
            raw = source_file.read_text(encoding="utf-8")
            metadata, body = split_frontmatter(raw)
            metadata["layer"] = dest_layer
            metadata["last_touched"] = utc_now().astimezone(UTC).isoformat()
            self._atomic_write(destination_file, compose_frontmatter(metadata, body.strip()))
            source_file.unlink()
            return {
                "source": source,
                "destination": str(destination_file.relative_to(self.memory_root)).replace("\\", "/"),
            }

        result = self._with_lock(f"move:{source_file}:{destination_file}", _action)
        self.journal.complete(op_id, "move_file", result)
        return result

    def update_map(self, *, action: str, details: dict[str, object]) -> dict[str, str]:
        self.ensure_layout()
        if action not in {"add_link", "remove_link"}:
            raise SedimentPalaceError(
                error_code="invalid_arguments",
                message="update_map action must be add_link or remove_link",
                context={"action": action},
            )

        link = str(details.get("link", "")).strip()
        if not link:
            raise SedimentPalaceError(
                error_code="invalid_arguments",
                message="update_map requires details.link",
            )

        op_id = self.journal.start("update_map", {"action": action, "link": link})

        def _action() -> dict[str, str]:
            self._maybe_fail("update_map_after_start")
            current = self.map_file.read_text(encoding="utf-8")
            lines = current.splitlines()
            marker = "## Links"
            if marker not in lines:
                lines.extend(["", marker])
            marker_idx = lines.index(marker)
            payload_line = f"- {link}"
            link_lines = lines[marker_idx + 1 :]

            if action == "add_link":
                if payload_line not in link_lines:
                    lines.append(payload_line)
            else:
                lines = [line for line in lines if line != payload_line]

            self._atomic_write(self.map_file, "\n".join(lines).strip() + "\n")
            return {"action": action, "link": link}

        result = self._with_lock("map:update", _action)
        self.journal.complete(op_id, "update_map", result)
        return result

    def recover_journal(self) -> dict[str, object]:
        self.ensure_layout()
        events = self.journal.read_all()
        started: dict[str, tuple[str, dict[str, object]]] = {}
        completed: set[str] = set()
        for event in events:
            if event.state == "started":
                started[event.operation_id] = (event.operation, event.payload)
            elif event.state == "completed":
                completed.add(event.operation_id)

        unresolved = [
            {"operation_id": op_id, "operation": op, "payload": payload}
            for op_id, (op, payload) in started.items()
            if op_id not in completed
        ]

        recovered: list[dict[str, str]] = []
        for item in unresolved:
            operation = str(item["operation"])
            raw_payload = item["payload"]
            payload = raw_payload if isinstance(raw_payload, dict) else {}
            if operation == "write_memory":
                rel = str(payload.get("path", ""))
                target = self._resolve_path_in_memory(rel)
                status = "completed" if target.exists() else "missing_target"
            elif operation == "move_file":
                src = str(payload.get("source", ""))
                dst = str(payload.get("destination", ""))
                src_file = self._resolve_path_in_memory(src) if src else None
                dst_file = self._resolve_path_in_memory(dst) if dst else None
                if dst_file and dst_file.exists() and src_file and not src_file.exists():
                    status = "completed"
                elif src_file and src_file.exists():
                    status = "rolled_back_source_present"
                else:
                    status = "unknown_state"
            elif operation == "update_map":
                status = "manual_check_required"
            else:
                status = "unknown_operation"

            self.journal.complete(
                str(item["operation_id"]),
                operation,
                {"recovery_status": status},
            )
            recovered.append({"operation_id": str(item["operation_id"]), "status": status})

        return {
            "unresolved_count": len(unresolved),
            "recovered_count": len(recovered),
            "recovered": recovered,
        }

    def purge_memory(self, *, path: str, reason: str, confirm: bool = False) -> dict[str, str]:
        self.ensure_layout()
        self.policy.assert_destructive_allowed(confirm=confirm, operation="purge_memory")
        target = self._resolve_path_in_memory(path)
        if not target.exists() or not target.is_file():
            raise SedimentPalaceError(
                error_code="not_found",
                message=f"memory file not found: {path}",
                context={"path": path},
            )
        archive_target = (self.archive_root / target.relative_to(self.memory_root)).resolve()
        archive_target.parent.mkdir(parents=True, exist_ok=True)
        op_id = self.journal.start(
            "purge_memory",
            {
                "path": path,
                "reason": reason,
                "archive_target": str(archive_target.relative_to(self.memory_root)).replace("\\", "/"),
            },
        )

        def _action() -> dict[str, str]:
            self._maybe_fail("purge_memory_after_start")
            raw = target.read_text(encoding="utf-8")
            metadata, body = split_frontmatter(raw)
            if metadata:
                metadata["status"] = "archived"
                metadata["last_touched"] = utc_now().astimezone(UTC).isoformat()
                metadata["tags"] = list(set([*list(metadata.get("tags", [])), "purged"]))
                self._atomic_write(archive_target, compose_frontmatter(metadata, body.strip()))
            else:
                self._atomic_write(archive_target, body.strip())
            target.unlink()
            return {
                "path": path,
                "archived_to": str(archive_target.relative_to(self.memory_root)).replace("\\", "/"),
                "reason": reason,
            }

        result = self._with_lock(f"purge:{target}", _action)
        self.journal.complete(op_id, "purge_memory", result)
        return result

    def metabolize(
        self,
        *,
        dry_run: bool = False,
        days_threshold: int | None = None,
        confirm: bool = False,
    ) -> dict[str, object]:
        self.ensure_layout()
        if not dry_run:
            self.policy.assert_destructive_allowed(confirm=confirm, operation="metabolize")

        op_id = self.journal.start(
            "metabolize",
            {"dry_run": dry_run, "days_threshold": days_threshold},
        )

        def _action() -> dict[str, object]:
            self._maybe_fail("metabolize_after_start")
            promoted: list[str] = []
            archived: list[str] = []
            decaying: list[str] = []
            scanned = 0
            now = utc_now()
            scan_budget = self.policy.max_metabolize_scan()

            for md_file in self.memory_root.rglob("*.md"):
                if md_file == self.map_file:
                    continue
                if "_System" in md_file.parts or "_Archive" in md_file.parts:
                    continue
                scanned += 1
                if scanned > scan_budget:
                    break
                raw = md_file.read_text(encoding="utf-8")
                metadata, body = split_frontmatter(raw)
                if not metadata:
                    continue

                layer = str(metadata.get("layer", "shallow"))
                touched = self._parse_iso(str(metadata.get("last_touched", now.isoformat())))
                age_days = max(0, int((now - touched).total_seconds() // 86400))
                decay_days = int(metadata.get("decay_days", 7))
                density = float(metadata.get("density", 0.0))
                stale_threshold = days_threshold if days_threshold is not None else decay_days
                streak = int(metadata.get("streak", 0))

                if layer == "shallow" and age_days > stale_threshold:
                    streak = max(-3, streak - 1)
                    metadata["streak"] = streak
                    metadata["status"] = "decaying"
                    if density >= 0.5:
                        destination = self._resolve_target(
                            layer="sediment",
                            relative_path=str(md_file.relative_to(self.memory_root / LAYER_DIRS["shallow"])),
                        )
                        promoted.append(str(destination.relative_to(self.memory_root)).replace("\\", "/"))
                        if not dry_run:
                            self._move_with_metadata(
                                source=md_file,
                                destination=destination,
                                body=body,
                                metadata=metadata,
                                layer="sediment",
                                status="active",
                            )
                    elif streak <= -2:
                        archive_path = self.archive_root / md_file.relative_to(self.memory_root)
                        archived.append(str(archive_path.relative_to(self.memory_root)).replace("\\", "/"))
                        if not dry_run:
                            self._move_to_archive(
                                source=md_file,
                                destination=archive_path,
                                body=body,
                                metadata=metadata,
                            )
                    else:
                        decaying.append(str(md_file.relative_to(self.memory_root)).replace("\\", "/"))
                        if not dry_run:
                            self._atomic_write(md_file, compose_frontmatter(metadata, body.strip()))

                elif layer == "shallow":
                    metadata["streak"] = min(10, streak + 1)
                    metadata["status"] = "active"
                    if not dry_run:
                        self._atomic_write(md_file, compose_frontmatter(metadata, body.strip()))

                if layer == "sediment":
                    if age_days > 30 and (density >= 0.8 or streak >= 5):
                        destination = self._resolve_target(
                            layer="bedrock",
                            relative_path=str(md_file.relative_to(self.memory_root / LAYER_DIRS["sediment"])),
                        )
                        promoted.append(str(destination.relative_to(self.memory_root)).replace("\\", "/"))
                        if not dry_run:
                            self._move_with_metadata(
                                source=md_file,
                                destination=destination,
                                body=body,
                                metadata=metadata,
                                layer="bedrock",
                                status="crystallized",
                            )
                    elif age_days > stale_threshold and density < 0.2:
                        metadata["streak"] = max(-3, streak - 1)
                        metadata["status"] = "decaying"
                        decaying.append(str(md_file.relative_to(self.memory_root)).replace("\\", "/"))
                        if not dry_run:
                            self._atomic_write(md_file, compose_frontmatter(metadata, body.strip()))
                    else:
                        metadata["streak"] = min(10, streak + 1)
                        metadata["status"] = "active"
                        if not dry_run:
                            self._atomic_write(md_file, compose_frontmatter(metadata, body.strip()))

            return {
                "dry_run": dry_run,
                "scanned": scanned,
                "promoted_count": len(promoted),
                "archived_count": len(archived),
                "decaying_count": len(decaying),
                "promoted": promoted,
                "archived": archived,
                "decaying": decaying,
            }

        result = self._with_lock("metabolize", _action)
        self.journal.complete(op_id, "metabolize", {"summary": result})
        return result

    def _resolve_target(self, *, layer: LayerName, relative_path: str) -> Path:
        layer_dir = self.memory_root / LAYER_DIRS[layer]
        rel = Path(relative_path)
        if rel.suffix.lower() != ".md":
            rel = rel.with_suffix(".md")
        candidate = (layer_dir / rel).resolve()
        if not self._is_within(candidate, layer_dir.resolve()):
            raise SedimentPalaceError(
                error_code="path_violation",
                message="target path escapes layer boundary",
                context={"path": relative_path, "layer": layer},
            )
        return candidate

    def _resolve_path_in_memory(self, relative_path: str) -> Path:
        candidate = (self.memory_root / relative_path).resolve()
        if not self._is_within(candidate, self.memory_root):
            raise SedimentPalaceError(
                error_code="path_violation",
                message="path escapes memory root",
                context={"path": relative_path},
            )
        return candidate

    def _is_within(self, candidate: Path, root: Path) -> bool:
        try:
            candidate.relative_to(root)
            return True
        except ValueError:
            return False

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
            streak=int(metadata.get("streak", 0)),
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
            "created": entry.created.astimezone(UTC).isoformat(),
            "last_touched": entry.last_touched.astimezone(UTC).isoformat(),
            "density": float(entry.density),
            "streak": int(entry.streak),
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
                return parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC)
        except ValueError:
            return utc_now()

    def _atomic_write(self, file_path: Path, content: str) -> None:
        temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(file_path)

    def _with_lock(self, lock_name: str, callback: Callable[[], object]):
        with self.lock_manager.lock(lock_name):
            return callback()

    def _move_with_metadata(
        self,
        *,
        source: Path,
        destination: Path,
        metadata: dict[str, object],
        body: str,
        layer: LayerName,
        status: str,
    ) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        metadata["layer"] = layer
        metadata["status"] = status
        metadata["last_touched"] = utc_now().astimezone(UTC).isoformat()
        self._atomic_write(destination, compose_frontmatter(metadata, body.strip()))
        source.unlink()

    def _move_to_archive(
        self,
        *,
        source: Path,
        destination: Path,
        metadata: dict[str, object],
        body: str,
    ) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        metadata["status"] = "archived"
        metadata["last_touched"] = utc_now().astimezone(UTC).isoformat()
        self._atomic_write(destination, compose_frontmatter(metadata, body.strip()))
        source.unlink()

    def _maybe_fail(self, key: str) -> None:
        if self.failpoints.get(key, False):
            raise SedimentPalaceError(
                error_code="injected_failure",
                message=f"injected failure at {key}",
                retryable=True,
                context={"failpoint": key},
            )
