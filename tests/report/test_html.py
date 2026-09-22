"""The one-file HTML report: self-contained, deterministic, honest about what it shows."""

from __future__ import annotations

import json
import pathlib
import re

from paperglass.engine import scan_bytes
from paperglass.ingest import Limits
from paperglass.models import Report, Tier
from paperglass.redkit.minipdf import Page, build, text
from paperglass.report import render_html

LIMITS = Limits(wall_seconds=60.0, cpu_seconds=60)
FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"


def _low_contrast() -> Report:
    data = next((FIXTURES / "pdf" / "pdf.text.low_contrast").glob("positive.*")).read_bytes()
    return scan_bytes(data, limits=LIMITS, tier=Tier.FAST, profile="resume")


def test_report_is_one_file_with_no_external_request() -> None:
    html = render_html(_low_contrast(), file_name="resume.pdf")
    assert html.startswith("<!doctype html>")
    assert "<script src" not in html and "<link " not in html
    # The only URLs are the data: crops and the disclosure link, which is a link, not a request.
    urls = set(re.findall(r"https?://[^\s\"\'<>]+", html))
    assert urls <= {"https://github.com/SuhaasNv/paperglass/blob/main/SECURITY.md"}, urls
    assert "data:image/png;base64," in html
    assert "\u2014" not in html  # no em dash


def test_report_carries_the_evidence_and_the_verdict() -> None:
    report = _low_contrast()
    html = render_html(report, file_name="resume.pdf")
    finding = report.findings[0]
    assert "MALICIOUS" in html
    assert finding.why_hidden in html
    assert finding.reproduce.replace("FILE", "resume.pdf") in html
    assert "1 1 1 rg" in html  # the mechanism, escaped as needed
    assert 'id="paperglass-report"' in html
    embedded = html.split('id="paperglass-report">', 1)[1].split("</script>", 1)[0]
    assert json.loads(embedded.replace("<\\/", "</"))["verdict"] == "malicious"
    assert "fraud" not in html.lower() and "cheat" not in html.lower()


def test_report_is_deterministic_and_handles_a_clean_document() -> None:
    report = _low_contrast()
    assert render_html(report, file_name="a.pdf") == render_html(report, file_name="a.pdf")
    clean = scan_bytes(build([Page(text("Visible", y=700))]), limits=LIMITS, tier=Tier.FAST)
    html = render_html(clean, file_name="clean.pdf")
    assert "CLEAN" in html and "No findings." in html
    assert "nothing to put under the glass" in html
