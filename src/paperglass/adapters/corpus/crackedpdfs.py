"""CrackedPDFs (UC Berkeley, MIT): 29,322 synthetic PDFs, 9,774 injected, from the Hugging
Face dataset at the paper's pinned revision. The index keeps the paper's frozen test split and
records the September 2026 erratum on every row: placement labels record the requested, not the
realised, position, and realised placement straddles the page edge for every regime but
`extreme_off_page`, so a number here mostly measures off-page and render-mode detection.
"""

from __future__ import annotations

import json
import random
import tarfile
from pathlib import Path
from typing import Any

from paperglass.adapters.corpus import FetchResult
from paperglass.bench.index import Family, InjectionKind, Sample, Split, sha256_file

REPO = "volkthienpreecha/crackedpdfs"
REVISION = "245bc98ec7e838346ee6fd5bdf5fed1b16d2a3e5"
"""The paper release, pinned (paper-v1/DATASET.md)."""
LICENCE = "MIT"
ERRATUM = (
    "CrackedPDFs 2026-09 erratum: regime fields record the requested placement; realised "
    "placement straddles the page edge for every regime but extreme_off_page; injected "
    "payloads carry DATASET_SAMPLE_ID markers and are longer than their confounders"
)

RENDERING_TO_TECHNIQUE: dict[str, str] = {
    "invisible_render_mode": "pdf.render.mode",
    "white_text": "pdf.text.low_contrast",
    "tiny_font": "pdf.text.tiny",
}
OFF_PAGE_REGIMES = frozenset({"negative_off_page", "extreme_off_page"})


def labels_for(row: dict[str, Any]) -> tuple[str, ...]:
    """Technique ids for one injected row; a visible in-page payload is `visible.instruction`,
    which Paperglass defers by contract (the row stays so the boundary is measured)."""
    if int(row.get("label", 0)) != 1:
        return ()
    labels: list[str] = []
    technique = RENDERING_TO_TECHNIQUE.get(str(row.get("rendering_regime", "")))
    if technique:
        labels.append(technique)
    if str(row.get("spatial_regime", "")) in OFF_PAGE_REGIMES:
        labels.append("pdf.text.offpage")
    if not labels:
        labels.append("visible.instruction")
    return tuple(labels)


def family_for(labels: tuple[str, ...]) -> Family:
    if not labels:
        return "none"
    if labels == ("visible.instruction",):
        return "visible"
    return "visual"


def split_for(row: dict[str, Any], test_ids: frozenset[str]) -> Split:
    if str(row.get("pdf_id", "")) in test_ids:
        return "test"
    return "train"


def sample_for(row: dict[str, Any], *, path: Path, root: Path, test_ids: frozenset[str]) -> Sample:
    labels = labels_for(row)
    kind: InjectionKind = "instruction" if labels else "none"
    caveat = ERRATUM
    confounder = str(row.get("benign_confounder_family", "none"))
    if not labels and confounder != "none":
        caveat = f"benign confounder: {confounder}; " + ERRATUM
    return Sample(
        sample_id=f"crackedpdfs-{row['pdf_id']}",
        path=str(path.relative_to(root)),
        sha256=sha256_file(path),
        source="crackedpdfs",
        source_version=f"hf:{REVISION[:12]}",
        licence=LICENCE,
        format="pdf",
        labels=labels,
        family=family_for(labels),
        injection_kind=kind,
        base_document=f"crackedpdfs-{row['base_pdf_id']}",
        split=split_for(row, test_ids),
        caveat=caveat,
    )


def _rows(
    labels_parquet: Path,
) -> list[dict[str, Any]]:  # pragma: no cover
    import pyarrow.parquet as pq  # noqa: PLC0415  # arrives with the bench extra (datasets)

    columns = [
        "pdf_id",
        "sample_id",
        "base_pdf_id",
        "pdf_role",
        "file_path",
        "label",
        "spatial_regime",
        "rendering_regime",
        "message_type",
        "attack_family",
        "dataset_split",
        "benign_confounder_family",
    ]
    table = pq.read_table(labels_parquet, columns=columns)
    rows: list[dict[str, Any]] = table.to_pylist()
    return rows


def choose_bases(
    rows: list[dict[str, Any]], *, test_ids: frozenset[str], limit: int | None, seed: int
) -> set[str]:
    """Whole base documents from the paper's test split, a seeded sample of `limit` of them."""
    bases = sorted({str(r["base_pdf_id"]) for r in rows if str(r["pdf_id"]) in test_ids})
    if limit is None or limit >= len(bases):
        return set(bases)
    rng = random.Random(seed)  # noqa: S311  # a seeded sample, not a secret
    return set(rng.sample(bases, limit))


def _extract(tar_path: Path, wanted: set[str], target: Path) -> dict[str, Path]:  # pragma: no cover
    """Extract the wanted members (by their trailing `benign/...` or `injected/...` path)."""
    found: dict[str, Path] = {}
    with tarfile.open(tar_path, "r:gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            name = member.name
            for want in wanted:
                if name.endswith(want):
                    out = target / want
                    out.parent.mkdir(parents=True, exist_ok=True)
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        continue
                    out.write_bytes(extracted.read())
                    found[want] = out
                    break
    return found


def fetch(
    root: Path, *, limit: int | None = None, seed: int = 1
) -> FetchResult:  # pragma: no cover
    try:
        from huggingface_hub import hf_hub_download  # noqa: PLC0415
    except ImportError:
        return FetchResult(
            "crackedpdfs",
            skipped="huggingface_hub is not installed: pip install 'paperglass[bench]'",
        )
    cache = root / "cache" / "crackedpdfs"
    cache.mkdir(parents=True, exist_ok=True)
    labels_path = Path(
        hf_hub_download(
            REPO, "data/labels.parquet", repo_type="dataset", revision=REVISION, cache_dir=cache
        )
    )
    splits_path = Path(
        hf_hub_download(
            REPO, "data/splits.json", repo_type="dataset", revision=REVISION, cache_dir=cache
        )
    )
    test_ids = frozenset(json.loads(splits_path.read_text(encoding="utf-8"))["test_ids"])
    rows = _rows(labels_path)
    bases = choose_bases(rows, test_ids=test_ids, limit=limit, seed=seed)
    chosen = [r for r in rows if str(r["base_pdf_id"]) in bases]
    wanted = {str(r["file_path"]) for r in chosen}
    files_root = root / "files" / "crackedpdfs"
    found: dict[str, Path] = {}
    for archive_name in ("pdfs/benign.tar.gz", "pdfs/injected.tar.gz"):
        needed = {w for w in wanted if w.startswith(archive_name.split("/")[1].split(".")[0])}
        if not needed:
            continue
        tar_path = Path(
            hf_hub_download(
                REPO, archive_name, repo_type="dataset", revision=REVISION, cache_dir=cache
            )
        )
        found.update(_extract(tar_path, needed, files_root))
    samples = tuple(
        sample_for(r, path=found[str(r["file_path"])], root=root, test_ids=test_ids)
        for r in chosen
        if str(r["file_path"]) in found
    )
    missing = len(chosen) - len(samples)
    notes: tuple[str, ...] = (
        f"{len(samples)} samples from {len(bases)} base documents of the paper's test split",
    )
    if missing:
        notes = (*notes, f"{missing} rows had no file in the archives")
    return FetchResult("crackedpdfs", samples=samples, notes=notes)
