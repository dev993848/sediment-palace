from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class TelemetryRecorder:
    def __init__(self, system_root: Path) -> None:
        self.system_root = system_root
        self.log_file = self.system_root / "telemetry.log"
        self.metrics_file = self.system_root / "metrics.json"
        self.system_root.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            self.log_file.write_text("", encoding="utf-8")
        if not self.metrics_file.exists():
            self.metrics_file.write_text("{}", encoding="utf-8")

    def record(
        self,
        *,
        tool_name: str,
        status: str,
        duration_ms: float,
        error_code: str | None = None,
    ) -> None:
        now = time.time()
        event: dict[str, Any] = {
            "timestamp": now,
            "tool_name": tool_name,
            "status": status,
            "duration_ms": round(duration_ms, 3),
        }
        if error_code:
            event["error_code"] = error_code

        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        metrics = self._read_metrics()
        tool_metrics = metrics.setdefault(tool_name, {"count": 0, "success": 0, "error": 0, "total_duration_ms": 0.0})
        tool_metrics["count"] += 1
        tool_metrics["total_duration_ms"] += float(duration_ms)
        if status == "success":
            tool_metrics["success"] += 1
        else:
            tool_metrics["error"] += 1
        tool_metrics["avg_duration_ms"] = tool_metrics["total_duration_ms"] / max(tool_metrics["count"], 1)

        if error_code:
            error_buckets = tool_metrics.setdefault("errors_by_code", {})
            error_buckets[error_code] = int(error_buckets.get(error_code, 0)) + 1

        self.metrics_file.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    def snapshot(self) -> dict[str, Any]:
        return self._read_metrics()

    def _read_metrics(self) -> dict[str, Any]:
        raw = self.metrics_file.read_text(encoding="utf-8").strip()
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
