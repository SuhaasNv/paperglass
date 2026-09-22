"""Page views (US-043): every run classified, the thumbnail present, redaction honoured."""

from __future__ import annotations

from paperglass.engine import scan_bytes
from paperglass.ingest import Limits
from paperglass.models import Tier
from paperglass.redkit.minipdf import Page, build, text

LIMITS = Limits(wall_seconds=60.0, cpu_seconds=60)


def _doc() -> bytes:
    return build(
        [Page(text("Visible words", y=700) + "\n" + text("hidden sentence", y=100, fill="1 g"))]
    )


def test_runs_are_classified_and_the_hidden_run_points_at_its_finding() -> None:
    report = scan_bytes(_doc(), limits=LIMITS, tier=Tier.FAST)
    assert report.schema_version == 2
    assert len(report.pages) == 1
    page = report.pages[0]
    assert page.number == 1 and page.width_pt and page.height_pt
    assert page.thumbnail.data_uri is not None and page.thumbnail.data_uri.startswith(
        "data:image/jpeg"
    )
    by_text = {run.text.strip(): run for run in page.runs}
    assert by_text["Visible words"].status == "visible"
    hidden = by_text["hidden sentence"]
    assert hidden.status == "hidden"
    assert hidden.finding_id == report.findings[0].id


def test_redact_drops_thumbnails_and_shortens_runs() -> None:
    report = scan_bytes(_doc(), limits=LIMITS, tier=Tier.FAST, redact=True)
    page = report.pages[0]
    assert page.thumbnail.data_uri is None and page.thumbnail.none_reason == "redacted"
    assert all(len(run.text) <= 80 for run in page.runs)


def test_text_documents_have_no_raster_so_runs_are_unverified_unless_confirmed() -> None:
    report = scan_bytes(b"plain text with nothing hidden\n", limits=LIMITS, tier=Tier.FAST)
    assert report.pages and report.pages[0].thumbnail.none_reason == "no raster for this page"
    assert {run.status for run in report.pages[0].runs} <= {"unverified", "hidden"}
