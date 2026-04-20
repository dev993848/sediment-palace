from __future__ import annotations

import shutil
from pathlib import Path


def make_workdir(name: str) -> Path:
    root = Path(f"tests/fixtures/{name}").resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root
