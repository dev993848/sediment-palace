from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import yaml

from sediment_palace.domain.errors import SedimentPalaceError

DEFAULT_POLICY: dict[str, Any] = {
    "destructive_require_confirm": True,
    "limits": {
        "max_search_matches": 100,
        "max_metabolize_scan": 5000,
    },
    "rate_limit": {
        "window_seconds": 60,
        "max_destructive_ops": 20,
    },
}


class PolicyEngine:
    def __init__(self, system_root: Path) -> None:
        self.system_root = system_root
        self.policy_file = self.system_root / "policy.yaml"
        self.events_file = self.system_root / "policy_events.log"
        self.system_root.mkdir(parents=True, exist_ok=True)
        if not self.policy_file.exists():
            self.policy_file.write_text(yaml.safe_dump(DEFAULT_POLICY, sort_keys=False), encoding="utf-8")
        if not self.events_file.exists():
            self.events_file.write_text("", encoding="utf-8")

    def max_search_matches(self) -> int:
        policy = self._load_policy()
        return int(policy.get("limits", {}).get("max_search_matches", 100))

    def max_metabolize_scan(self) -> int:
        policy = self._load_policy()
        return int(policy.get("limits", {}).get("max_metabolize_scan", 5000))

    def assert_destructive_allowed(self, *, confirm: bool, operation: str) -> None:
        policy = self._load_policy()
        require_confirm = bool(policy.get("destructive_require_confirm", True))
        if require_confirm and not confirm:
            raise SedimentPalaceError(
                error_code="policy_violation",
                message=f"{operation} requires confirm=true",
                context={"operation": operation},
            )

        window_seconds = int(policy.get("rate_limit", {}).get("window_seconds", 60))
        max_ops = int(policy.get("rate_limit", {}).get("max_destructive_ops", 20))
        now = time.time()
        recent_count = self._count_recent_destructive_events(now=now, window_seconds=window_seconds)
        if recent_count >= max_ops:
            raise SedimentPalaceError(
                error_code="rate_limited",
                message=f"destructive operation rate limit exceeded for {operation}",
                retryable=True,
                context={"window_seconds": window_seconds, "max_destructive_ops": max_ops},
            )

        self._append_event({"timestamp": now, "type": "destructive_op", "operation": operation})

    def _load_policy(self) -> dict[str, Any]:
        loaded = yaml.safe_load(self.policy_file.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            return DEFAULT_POLICY
        return loaded

    def _append_event(self, event: dict[str, Any]) -> None:
        with self.events_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _count_recent_destructive_events(self, *, now: float, window_seconds: int) -> int:
        count = 0
        for line in self.events_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
                if payload.get("type") != "destructive_op":
                    continue
                ts = float(payload.get("timestamp", 0))
                if now - ts <= window_seconds:
                    count += 1
            except (ValueError, json.JSONDecodeError):
                continue
        return count
