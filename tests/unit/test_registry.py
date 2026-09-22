"""The registry contract, and the rule that code and THREATS.md never disagree.

Every registered technique must have a THREATS.md row whose plain-language sentence and
threshold text equal the spec, whose status is not "planned", and a fixture pair under
tests/fixtures/<format>/<technique>/. Rows still marked planned need no detector yet.
"""

from __future__ import annotations

import pathlib
import re
from collections.abc import Iterable

import pytest

import paperglass.detectors  # noqa: F401  # imports every detector module
from paperglass.detectors import (
    REGISTRY,
    Candidate,
    Detector,
    SeverityDefault,
    TechniqueRegistry,
    TechniqueSpec,
    technique,
)
from paperglass.views.context import PageContext

ROOT = pathlib.Path(__file__).resolve().parents[2]
THREATS = ROOT / "THREATS.md"
FIXTURES = ROOT / "tests" / "fixtures"

FIXTURE_FORMAT_DIRS = {
    "pdf": "pdf",
    "docx": "docx",
    "pptx": "pptx",
    "html": "html",
    "md": "md",
    "png": "png",
    "jpg": "png",
    "tiff": "png",
    "any": "text",
}


class ThreatRow:
    def __init__(self, cells: list[str]) -> None:
        self.technique_id = cells[0].strip("`")
        self.explanation = cells[1]
        self.threshold = cells[3]
        self.status = cells[7]


def threat_rows() -> dict[str, ThreatRow]:
    rows: dict[str, ThreatRow] = {}
    for line in THREATS.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == 8:
            row = ThreatRow(cells)
            rows[row.technique_id] = row
    return rows


def fixture_pair_exists(spec: TechniqueSpec) -> bool:
    for fmt in spec.formats:
        folder = FIXTURES / FIXTURE_FORMAT_DIRS[fmt] / spec.id
        positive = list(folder.glob("positive.*"))
        negative = list(folder.glob("negative.*"))
        if not (positive and negative):
            return False
    return True


def test_threats_table_parses_every_technique_row() -> None:
    rows = threat_rows()
    assert len(rows) >= 29
    assert all(re.fullmatch(r"[a-z]+(\.[a-z_0-9]+)+", technique_id) for technique_id in rows)


def test_every_registered_technique_has_a_matching_threats_row() -> None:
    rows = threat_rows()
    problems: list[str] = []
    for technique_id, spec in REGISTRY.specs().items():
        row = rows.get(technique_id)
        if row is None:
            problems.append(f"{technique_id}: no THREATS.md row")
            continue
        if row.explanation != spec.explanation:
            problems.append(f"{technique_id}: explanation differs from THREATS.md")
        if row.threshold != spec.threshold:
            problems.append(f"{technique_id}: threshold differs from THREATS.md")
        if row.status == "planned":
            problems.append(f"{technique_id}: registered but THREATS.md still says planned")
        if not fixture_pair_exists(spec):
            problems.append(f"{technique_id}: missing positive or negative fixture")
    assert not problems, "\n".join(problems)


def test_every_covered_threats_row_is_registered() -> None:
    missing = [
        technique_id
        for technique_id, row in threat_rows().items()
        if row.status in {"covered", "partial"} and technique_id not in REGISTRY
    ]
    assert not missing, f"THREATS.md claims coverage without a detector: {missing}"


class _Probe(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        return ()


def _spec(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "test.thing.hidden",
        "formats": ("pdf",),
        "views": ("C",),
        "stage": 0,
        "severity_class": SeverityDefault.DATA,
        "explanation": "A test sentence.",
        "threshold": "always",
        "rule_version": "1",
        "release": "v0.1.0",
    }
    base.update(overrides)
    return base


def test_decorator_registers_and_attaches_spec() -> None:
    registry = TechniqueRegistry()
    decorated = technique(registry=registry, **_spec())(_Probe)  # type: ignore[arg-type]
    assert "test.thing.hidden" in registry
    assert registry.detector("test.thing.hidden") is decorated
    assert registry.rule_versions() == {"test.thing.hidden": "1"}
    assert registry.spec("test.thing.hidden").explanation == "A test sentence."


def test_duplicate_id_is_refused() -> None:
    registry = TechniqueRegistry()
    technique(registry=registry, **_spec())(_Probe)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="already registered"):
        technique(registry=registry, **_spec())(_Probe)  # type: ignore[arg-type]


def test_bad_id_is_refused() -> None:
    registry = TechniqueRegistry()
    with pytest.raises(ValueError):
        technique(registry=registry, **_spec(id="BadId"))(_Probe)  # type: ignore[arg-type]


def test_non_detector_is_refused() -> None:
    registry = TechniqueRegistry()

    class NotADetector:
        pass

    with pytest.raises(TypeError):
        technique(registry=registry, **_spec())(NotADetector)  # type: ignore[arg-type]


def test_candidate_requires_mechanism_and_reproduce() -> None:
    with pytest.raises(ValueError):
        Candidate(technique_id="pdf.text.tiny", mechanism="", reproduce="x", confidence=1.0)
    with pytest.raises(ValueError):
        Candidate(technique_id="pdf.text.tiny", mechanism="x", reproduce="", confidence=1.0)
