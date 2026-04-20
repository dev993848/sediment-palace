from __future__ import annotations

import json
import sys
from pathlib import Path

from sediment_palace.transport.server import SedimentPalaceServer


def main() -> int:
    server = SedimentPalaceServer(project_root=Path("."))
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = server.handle_request(request)
        print(json.dumps(response, ensure_ascii=False))
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
