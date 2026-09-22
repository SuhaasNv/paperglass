"""Profiles (US-044): each file loads, extends merges, and the thresholds reach the detectors."""

from __future__ import annotations

import pathlib

import pytest

from paperglass.engine import scan_bytes
from paperglass.ingest import Limits
from paperglass.models import Severity, SeverityClass, Tier, Verdict
from paperglass.profiles import load_profile, profile_names
from paperglass.redkit.minipdf import Page, build, text

LIMITS = Limits(wall_seconds=60.0, cpu_seconds=60)
FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"
HIDDEN_DATA = "Python Kubernetes Rust Terraform"


def test_every_profile_file_loads_and_names_itself() -> None:
    names = profile_names()
    assert names == ["default", "peer-review", "rag-ingest", "resume"]
    for name in names:
        assert load_profile(name).name == name


def test_unknown_profile_names_the_known_ones() -> None:
    with pytest.raises(KeyError, match="known: default, peer-review, rag-ingest, resume"):
        load_profile("nope")


def test_extends_merges_tables_and_extends_lists() -> None:
    default, resume = load_profile("default"), load_profile("resume")
    assert resume.thresholds == default.thresholds
    assert resume.verdict == default.verdict
    assert resume.allowlist.actual_text_max_chars == 0
    assert resume.allowlist.ocr_layer_min_agreement == default.allowlist.ocr_layer_min_agreement
    assert set(default.phrases.instruction) <= set(resume.phrases.instruction)
    assert "top candidate" in resume.phrases.instruction
    assert set(default.severity.instruction_critical_verbs) <= set(
        resume.severity.instruction_critical_verbs
    )


def test_resume_treats_hidden_data_as_high_and_the_verdict_follows() -> None:
    data = build([Page(text("Visible", y=700) + "\n" + text(HIDDEN_DATA, y=100, fill="1 g"))])
    default = scan_bytes(data, limits=LIMITS, tier=Tier.FAST)
    resume = scan_bytes(data, limits=LIMITS, tier=Tier.FAST, profile="resume")
    assert (default.verdict, default.findings[0].severity) == (Verdict.SUSPICIOUS, Severity.MEDIUM)
    assert (resume.verdict, resume.findings[0].severity) == (Verdict.MALICIOUS, Severity.HIGH)
    assert resume.findings[0].severity_class is SeverityClass.DATA
    assert resume.profile == "resume"


def test_resume_reports_a_ligature_actualtext_that_default_allows() -> None:
    ligature = next((FIXTURES / "pdf" / "pdf.actualtext.override").glob("negative.*")).read_bytes()
    default = scan_bytes(ligature, limits=LIMITS, tier=Tier.FAST)
    resume = scan_bytes(ligature, limits=LIMITS, tier=Tier.FAST, profile="resume")
    assert all(f.technique_id != "pdf.actualtext.override" for f in default.findings)
    assert any(f.technique_id == "pdf.actualtext.override" for f in resume.findings)


def test_profile_phrases_reach_the_severity_class() -> None:
    data = build(
        [
            Page(
                text("Visible", y=700)
                + "\n"
                + text("a top candidate for the role", y=100, fill="1 g")
            )
        ]
    )
    default = scan_bytes(data, limits=LIMITS, tier=Tier.FAST)
    resume = scan_bytes(data, limits=LIMITS, tier=Tier.FAST, profile="resume")
    assert default.findings[0].severity_class is SeverityClass.DATA
    assert resume.findings[0].severity_class is SeverityClass.INSTRUCTION


def test_rule_versions_name_the_profile_hints() -> None:
    report = scan_bytes(
        build([Page(text("Visible", y=700))]), limits=LIMITS, tier=Tier.FAST, profile="rag-ingest"
    )
    assert report.profile == "rag-ingest"
    assert report.verdict is Verdict.CLEAN
