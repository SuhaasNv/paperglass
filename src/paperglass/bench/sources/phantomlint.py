"""PhantomLint fixtures (University of Melbourne, BSD-3): real arXiv papers and CVs with and
without hidden prompts, from the repository's tests/bad and tests/good at a pinned commit. The
technique of each hidden prompt is not labelled upstream, so positives carry the wildcard label
`*` (hidden text of unspecified technique). HTML files wait for v0.4.0.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from paperglass.bench.index import Sample, sha256_file
from paperglass.bench.sources import FetchResult

REPO = "tobycmurray/phantom-lint"
COMMIT = "7f6200145abf9d1592118780e117d14541a18dae"
LICENCE = "BSD-3-Clause"
API = f"https://api.github.com/repos/{REPO}/contents"
RAW = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}"


def _listing(folder: str) -> list[dict[str, object]]:
    with urllib.request.urlopen(f"{API}/tests/{folder}?ref={COMMIT}", timeout=60) as response:  # noqa: S310  # https, pinned host
        payload = json.load(response)
    return [entry for entry in payload if isinstance(entry, dict)]


def _download(folder: str, name: str, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_file():
        with urllib.request.urlopen(f"{RAW}/tests/{folder}/{name}", timeout=300) as response:  # noqa: S310  # https, pinned host
            target.write_bytes(response.read())
    return target


def sample_for(*, folder: str, name: str, path: Path, root: Path) -> Sample:
    positive = folder == "bad"
    return Sample(
        sample_id=f"phantomlint-{folder}-{Path(name).stem}",
        path=str(path.relative_to(root)),
        sha256=sha256_file(path),
        source="phantomlint",
        source_version=f"git:{COMMIT[:12]}",
        licence=LICENCE,
        format="pdf",
        labels=("*",) if positive else (),
        family="none",
        injection_kind="instruction" if positive else "none",
        base_document=f"phantomlint-{Path(name).stem}",
        split="test",
        caveat="real document; the hiding technique is not labelled upstream"
        if positive
        else "real document with no hidden prompt",
    )


def fetch(
    root: Path, *, limit: int | None = None, seed: int = 1
) -> FetchResult:  # every fixture is small; the sample is the whole set
    samples: list[Sample] = []
    skipped_html = 0
    for folder in ("bad", "good"):
        for entry in _listing(folder):
            name = str(entry.get("name", ""))
            if entry.get("type") != "file":
                continue
            if not name.lower().endswith(".pdf"):
                skipped_html += 1
                continue
            path = _download(folder, name, root / "files" / "phantomlint" / folder / name)
            samples.append(sample_for(folder=folder, name=name, path=path, root=root))
            if limit is not None and len(samples) >= limit:
                break
    notes = (
        f"{len(samples)} PDFs; {skipped_html} non-PDF files skipped until HTML lands (v0.4.0)",
    )
    return FetchResult("phantomlint", samples=tuple(samples), notes=notes)
