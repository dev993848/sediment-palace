from __future__ import annotations

import time
from contextlib import contextmanager
from pathlib import Path

from sediment_palace.domain.errors import SedimentPalaceError


class FileLockManager:
    def __init__(self, lock_root: Path, *, stale_after_seconds: float = 30.0) -> None:
        self.lock_root = lock_root
        self.stale_after_seconds = stale_after_seconds
        self.lock_root.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def lock(self, lock_name: str, *, timeout_seconds: float = 5.0):
        lock_file = self.lock_root / f"{self._sanitize(lock_name)}.lock"
        started = time.monotonic()
        while lock_file.exists():
            try:
                age_seconds = time.time() - lock_file.stat().st_mtime
                if age_seconds > self.stale_after_seconds:
                    lock_file.unlink(missing_ok=True)
                    break
            except OSError:
                pass
            if time.monotonic() - started > timeout_seconds:
                raise SedimentPalaceError(
                    error_code="lock_timeout",
                    message=f"unable to acquire lock: {lock_name}",
                    retryable=True,
                    context={"lock_name": lock_name, "timeout_seconds": timeout_seconds},
                )
            time.sleep(0.05)

        lock_file.write_text("1", encoding="utf-8")
        try:
            yield
        finally:
            lock_file.unlink(missing_ok=True)

    def _sanitize(self, value: str) -> str:
        return value.replace("\\", "_").replace("/", "_").replace(":", "_")
