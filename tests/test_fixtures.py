"""Every registered technique: its positive fixture yields exactly one candidate of that
technique with confidence above 0.9; its negative fixture yields none. Other techniques
must stay quiet on both, so a fixture proves one thing.
"""

from __future__ import annotations

import pathlib

import pytest

import paperglass.detectors  # noqa: F401  # registration
from paperglass.detectors import REGISTRY, Candidate
from paperglass.ingest import Limits
from paperglass.views.pages import build_pages

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
LIMITS = Limits(wall_seconds=60.0, cpu_seconds=60)
FOLDER = {"pdf": "pdf", "any": "text", "docx": "docx", "pptx": "pptx", "html": "html", "md": "md"}


def candidates_for(data: bytes) -> list[Candidate]:
    stage0 = build_pages(data, limits=LIMITS)
    assert not stage0.failures, stage0.failures
    found: list[Candidate] = []
    for page in stage0.pages:
        for technique_id in REGISTRY:
            detector = REGISTRY.detector(technique_id)()
            found.extend(detector.probe(page))
    return found


def fixture_pair(technique_id: str) -> tuple[bytes, bytes]:
    spec = REGISTRY.spec(technique_id)
    folder = FIXTURES / FOLDER[spec.formats[0]] / technique_id
    positive = next(folder.glob("positive.*")).read_bytes()
    negative = next(folder.glob("negative.*")).read_bytes()
    return positive, negative


@pytest.mark.parametrize("technique_id", sorted(REGISTRY))
def test_positive_fixture_yields_exactly_one_confident_candidate(technique_id: str) -> None:
    positive, _ = fixture_pair(technique_id)
    found = candidates_for(positive)
    mine = [c for c in found if c.technique_id == technique_id]
    others = [c for c in found if c.technique_id != technique_id]
    assert len(mine) == 1, [c.mechanism for c in mine]
    assert mine[0].confidence > 0.9
    assert mine[0].mechanism and mine[0].reproduce
    assert not others, [f"{c.technique_id}: {c.mechanism}" for c in others]


@pytest.mark.parametrize("technique_id", sorted(REGISTRY))
def test_negative_fixture_is_quiet(technique_id: str) -> None:
    _, negative = fixture_pair(technique_id)
    found = candidates_for(negative)
    assert not found, [f"{c.technique_id}: {c.mechanism}" for c in found]
