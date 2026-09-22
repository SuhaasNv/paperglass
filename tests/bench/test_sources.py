"""Corpus sources (US-050): row mapping on recorded metadata, no network in tests."""

from __future__ import annotations

import pathlib
from typing import Any

from paperglass.bench.adapter import AdapterResult
from paperglass.bench.index import Sample
from paperglass.bench.metrics import compute, outcome
from paperglass.bench.sources import FetchResult, crackedpdfs, phantomlint, phantomtext, sources

INJECTED: dict[str, Any] = {
    "pdf_id": "sample_0032.injected",
    "sample_id": "sample_0032",
    "base_pdf_id": "base_080764",
    "pdf_role": "injected_attack",
    "file_path": "injected/sample_0032.injected.pdf",
    "label": 1,
    "spatial_regime": "extreme_off_page",
    "rendering_regime": "white_text",
    "message_type": "instruction_override",
    "attack_family": "in_page_white_text",
    "dataset_split": "test",
    "benign_confounder_family": "none",
}
CONFOUNDER: dict[str, Any] = {
    **INJECTED,
    "pdf_id": "sample_0032.benign_confounder",
    "pdf_role": "benign_confounder",
    "file_path": "benign/sample_0032.benign-confounder.pdf",
    "label": 0,
    "spatial_regime": "none",
    "rendering_regime": "none",
    "message_type": "none",
    "attack_family": "none",
    "benign_confounder_family": "benign_in_page_white_watermark",
}


def test_crackedpdfs_labels_follow_the_regimes_and_record_the_erratum(
    tmp_path: pathlib.Path,
) -> None:
    assert crackedpdfs.labels_for(INJECTED) == ("pdf.text.low_contrast", "pdf.text.offpage")
    assert crackedpdfs.labels_for(
        {**INJECTED, "rendering_regime": "invisible_render_mode", "spatial_regime": "inside_page"}
    ) == ("pdf.render.mode",)
    assert crackedpdfs.labels_for(
        {**INJECTED, "rendering_regime": "tiny_font", "spatial_regime": "near_margin"}
    ) == ("pdf.text.tiny",)
    assert crackedpdfs.labels_for(
        {**INJECTED, "rendering_regime": "normal_visible", "spatial_regime": "inside_page"}
    ) == ("visible.instruction",)
    assert crackedpdfs.labels_for(CONFOUNDER) == ()
    path = tmp_path / "files" / "crackedpdfs" / "injected" / "sample_0032.injected.pdf"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"%PDF-1.4 test")
    sample = crackedpdfs.sample_for(
        INJECTED, path=path, root=tmp_path, test_ids=frozenset({"sample_0032.injected"})
    )
    assert (
        sample.split == "test"
        and sample.family == "visual"
        and sample.injection_kind == "instruction"
    )
    assert sample.base_document == "crackedpdfs-base_080764" and sample.licence == "MIT"
    assert "erratum" in sample.caveat and sample.source_version.startswith("hf:")
    confounder_path = tmp_path / "files" / "crackedpdfs" / "benign" / "c.pdf"
    confounder_path.parent.mkdir(parents=True)
    confounder_path.write_bytes(b"%PDF-1.4 c")
    confounder = crackedpdfs.sample_for(
        CONFOUNDER, path=confounder_path, root=tmp_path, test_ids=frozenset()
    )
    assert not confounder.positive and confounder.split == "train"
    assert confounder.caveat.startswith("benign confounder: benign_in_page_white_watermark")
    visible = crackedpdfs.sample_for(
        {**INJECTED, "rendering_regime": "normal_visible", "spatial_regime": "inside_page"},
        path=path,
        root=tmp_path,
        test_ids=frozenset(),
    )
    assert visible.family == "visible"


def test_crackedpdfs_sample_keeps_whole_base_documents() -> None:
    rows = [
        {**INJECTED, "base_pdf_id": f"base_{i}", "pdf_id": f"sample_{i}.injected"}
        for i in range(10)
    ]
    test_ids = frozenset(r["pdf_id"] for r in rows)
    chosen = crackedpdfs.choose_bases(rows, test_ids=test_ids, limit=3, seed=5)
    assert len(chosen) == 3 and chosen == crackedpdfs.choose_bases(
        rows, test_ids=test_ids, limit=3, seed=5
    )
    assert crackedpdfs.choose_bases(rows, test_ids=test_ids, limit=None, seed=5) == {
        f"base_{i}" for i in range(10)
    }


def test_phantomlint_rows_carry_the_wildcard_and_the_licence(tmp_path: pathlib.Path) -> None:
    bad = tmp_path / "files" / "phantomlint" / "bad" / "2212.08983v2.pdf"
    bad.parent.mkdir(parents=True)
    bad.write_bytes(b"%PDF-1.4 bad")
    sample = phantomlint.sample_for(folder="bad", name="2212.08983v2.pdf", path=bad, root=tmp_path)
    assert sample.labels == ("*",) and sample.licence == "BSD-3-Clause" and sample.split == "test"
    good = tmp_path / "files" / "phantomlint" / "good" / "alexander-fenster.pdf"
    good.parent.mkdir(parents=True)
    good.write_bytes(b"%PDF-1.4 good")
    negative = phantomlint.sample_for(
        folder="good", name="alexander-fenster.pdf", path=good, root=tmp_path
    )
    assert negative.labels == () and negative.injection_kind == "none"


def test_wildcard_label_counts_any_named_technique() -> None:
    row = Sample(
        sample_id="p",
        path="x",
        sha256="0" * 64,
        source="phantomlint",
        source_version="1",
        licence="BSD-3-Clause",
        format="pdf",
        labels=("*",),
        family="none",
        injection_kind="instruction",
        base_document="b",
    )
    hit = AdapterResult.model_validate(
        {
            "verdict": "malicious",
            "findings": [{"technique_id": "pdf.text.tiny", "severity": "high", "confidence": 0.9}],
        }
    )
    miss = AdapterResult.model_validate({"verdict": "clean", "findings": []})
    assert outcome(row, hit, 1.0).detected == ("*",)
    assert outcome(row, miss, 1.0).detected == ()
    assert compute([outcome(row, hit, 1.0)]).recall_per_technique == {"*": 1.0}


def test_phantomtext_is_skipped_without_the_toolkit(tmp_path: pathlib.Path) -> None:
    result = phantomtext.fetch(tmp_path)
    assert isinstance(result, FetchResult)
    if not phantomtext.toolkit_available():
        assert result.skipped and "not installed" in result.skipped
    assert set(phantomtext.INJECTION_TO_TECHNIQUE.values()) <= {
        "pdf.text.low_contrast",
        "pdf.text.offpage",
        "pdf.text.opacity",
        "pdf.text.tiny",
    }
    assert set(sources()) == {"crackedpdfs", "phantomlint", "phantomtext"}
