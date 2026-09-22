"""Regenerate the golden reports under tests/golden/reports (one per positive fixture).

Run only after an intended change to the schema, a detector or the engine, and say why in
the commit body. The golden form drops timings and the version and replaces crops.
"""

from __future__ import annotations

import sys

from tests.unit.test_engine import EXPECTED_VERDICT, GOLDEN, LIMITS, fixture, normalised

from paperglass.engine import scan_bytes
from paperglass.models import Tier


def main() -> int:
    GOLDEN.mkdir(parents=True, exist_ok=True)
    for technique_id in sorted(EXPECTED_VERDICT):
        report = scan_bytes(fixture(technique_id, "positive"), limits=LIMITS, tier=Tier.FAST)
        (GOLDEN / f"{technique_id}.json").write_text(normalised(report), encoding="utf-8")
        print(technique_id, report.verdict.value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
