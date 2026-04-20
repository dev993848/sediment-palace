from __future__ import annotations

from typing import Any

import yaml


def split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---\n"):
        return {}, raw
    parts = raw.split("---\n", 2)
    if len(parts) < 3:
        return {}, raw
    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        return {}, parts[2]
    return data, parts[2]


def compose_frontmatter(metadata: dict[str, Any], body: str) -> str:
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    clean_body = body.lstrip("\n")
    return f"---\n{fm}\n---\n\n{clean_body}"
