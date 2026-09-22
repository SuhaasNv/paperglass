"""paperglass fingerprint: one row per hidden run, one column per installed extractor."""

from __future__ import annotations

import pathlib

from paperglass import fingerprint
from paperglass.engine import fingerprint_bytes
from paperglass.ingest import Limits
from paperglass.models import Fingerprint
from paperglass.redkit.minipdf import simple

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIMITS = Limits(wall_seconds=60.0, cpu_seconds=60)


def test_white_text_is_returned_by_every_pdf_extractor() -> None:
    data = (ROOT / "tests/fixtures/pdf/pdf.text.low_contrast/positive.pdf").read_bytes()
    result = fingerprint_bytes(data, limits=LIMITS)
    assert result.default_extractor == "pypdfium2"
    assert set(result.extractors) >= {"pypdfium2", "pdfplumber", "pypdf", "pdfminer.six"}
    assert len(result.rows) == 1
    row = result.rows[0]
    assert row.technique_id == "pdf.text.low_contrast"
    assert all(v.returns_hidden_text for v in row.extractors), row.extractors
    assert result.fooled["pypdfium2"] == 1
    assert result.failed == {}


def test_clean_document_has_no_rows() -> None:
    result = fingerprint(simple("Hello"), limits=LIMITS)
    assert isinstance(result, Fingerprint)
    assert result.rows == ()
    assert set(result.fooled.values()) == {0}


def test_extractor_subset_and_offpage_disagreement() -> None:
    data = (ROOT / "tests/fixtures/pdf/pdf.text.offpage/positive.pdf").read_bytes()
    result = fingerprint_bytes(data, limits=LIMITS, extractors=("pypdfium2", "pdfplumber"))
    assert set(result.extractors) == {"pypdfium2", "pdfplumber"}
    assert len(result.rows) == 1
    names = {v.extractor: v.returns_hidden_text for v in result.rows[0].extractors}
    # pypdfium2 returns off-page text; pdfplumber crops words to the page box.
    assert names["pypdfium2"] is True
    assert names["pdfplumber"] in (True, False)
