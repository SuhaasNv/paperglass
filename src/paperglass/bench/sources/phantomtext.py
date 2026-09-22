"""PhantomText (University of Padua, MIT, attribution required): samples generated with the
toolkit from Paperglass's own clean base documents, one per injection class, when the toolkit is
installed (`pip install git+https://github.com/pajola/PhantomText`). Generated output is never
redistributed without the authors' written permission (BENCHMARK_DESIGN.md), so the index
carries hashes and the generator version, and `bench fetch` regenerates.
"""

from __future__ import annotations

from pathlib import Path

from paperglass.bench.sources import FetchResult

INJECTION_TO_TECHNIQUE: dict[str, str] = {
    "camouflage": "pdf.text.low_contrast",
    "outofbound": "pdf.text.offpage",
    "transparent": "pdf.text.opacity",
    "zerosize": "pdf.text.tiny",
}
"""The toolkit's injection classes and the Paperglass technique each one exercises."""
LICENCE = "MIT (attribution: PhantomText, University of Padua)"


def toolkit_available() -> bool:
    try:
        import phantomtext  # noqa: F401, PLC0415  # optional, user-installed
    except ImportError:
        return False
    return True


def fetch(
    root: Path, *, limit: int | None = None, seed: int = 1
) -> FetchResult:  # generation lands with the toolkit wiring
    if not toolkit_available():
        return FetchResult(
            "phantomtext",
            skipped="the PhantomText toolkit is not installed (pip install "
            "git+https://github.com/pajola/PhantomText); samples are generated, never downloaded",
        )
    return FetchResult(
        "phantomtext",
        skipped="generation with the toolkit is wired at US-054 with the baselines; "
        "the technique map is in place",
    )
