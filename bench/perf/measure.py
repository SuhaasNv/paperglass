"""Latency per document and per page on this machine, for BENCHMARK.md "Speed".

    uv run python bench/perf/measure.py [--runs 20]
Prints p50 and p95 per tier over the positive fixtures, with the hardware named.
"""

from __future__ import annotations

import argparse
import pathlib
import platform
import statistics
import time

from paperglass.engine import scan_bytes
from paperglass.ingest import Limits, close_pool
from paperglass.models import Tier

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = sorted((ROOT / "tests" / "fixtures" / "pdf").glob("*/positive.pdf"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=20)
    args = parser.parse_args()
    limits = Limits()
    print(
        f"machine: {platform.machine()} {platform.processor() or ''} {platform.system()} "
        f"python {platform.python_version()}, {len(FIXTURES)} one-page fixtures, "
        f"{args.runs} runs each"
    )
    for tier in (Tier.FAST, Tier.STANDARD):
        samples: list[float] = []
        pages = 0
        scan_bytes(FIXTURES[0].read_bytes(), limits=limits, tier=tier)  # warm the worker and OCR
        for path in FIXTURES:
            data = path.read_bytes()
            for _ in range(args.runs):
                started = time.perf_counter()
                report = scan_bytes(data, limits=limits, tier=tier)
                samples.append((time.perf_counter() - started) * 1000)
                pages += report.page_count
                assert report.pages_render_verified == report.page_count, report.parse_failures
        samples.sort()
        p50 = statistics.median(samples)
        p95 = samples[int(len(samples) * 0.95) - 1]
        print(
            f"{tier.value}: p50 {p50:.0f} ms, p95 {p95:.0f} ms per one-page document ({len(samples)} scans)"
        )
    close_pool()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
