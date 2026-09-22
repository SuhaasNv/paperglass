"""Write the Report JSON schema to schemas/report-v<N>.json. Run after any schema change."""

from __future__ import annotations

import json
import pathlib
import sys

from paperglass.models import SCHEMA_VERSION, json_schema


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    target = root / "schemas" / f"report-v{SCHEMA_VERSION}.json"
    target.write_text(json.dumps(json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(target.relative_to(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
