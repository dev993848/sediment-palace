from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SedimentPalaceError(Exception):
    error_code: str
    message: str
    retryable: bool = False
    context: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"

