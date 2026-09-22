"""Malformed inputs never raise out of stage 0: they come back as parse failures or as
an empty scan. The corpus runs on every push; hypothesis mutations run with a fixed seed
in CI (docs/06-security/FUZZING.md).
"""

from __future__ import annotations

import os
import pathlib

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

import paperglass.detectors  # noqa: F401
from paperglass.detectors import REGISTRY
from paperglass.ingest import Limits
from paperglass.redkit.minipdf import simple
from paperglass.views.pages import build_pages

CORPUS = pathlib.Path(__file__).parent / "corpus"
LIMITS = Limits(wall_seconds=30.0, cpu_seconds=30, max_file_mb=5, max_pages=20)
EXAMPLES = int(os.environ.get("PAPERGLASS_FUZZ_EXAMPLES", "15"))

pytestmark = pytest.mark.fuzz


def scan_never_raises(data: bytes) -> None:
    stage0 = build_pages(data, limits=LIMITS)
    for page in stage0.pages:
        for technique_id in REGISTRY:
            list(REGISTRY.detector(technique_id)().probe(page))


@pytest.mark.parametrize("path", sorted(CORPUS.rglob("*.*")), ids=lambda p: p.name)
def test_corpus_file_does_not_raise(path: pathlib.Path) -> None:
    if path.name == "INDEX.md":
        pytest.skip("index")
    scan_never_raises(path.read_bytes())


BASE = simple("Hello Paperglass")


@settings(max_examples=EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    position=st.integers(min_value=0, max_value=len(BASE) - 1),
    replacement=st.binary(min_size=0, max_size=64),
)
def test_mutated_pdf_does_not_raise(position: int, replacement: bytes) -> None:
    scan_never_raises(BASE[:position] + replacement + BASE[position + len(replacement) :])


@settings(max_examples=EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(cut=st.integers(min_value=1, max_value=len(BASE)))
def test_truncated_pdf_does_not_raise(cut: int) -> None:
    scan_never_raises(BASE[:cut])


@settings(max_examples=EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.binary(min_size=0, max_size=512))
def test_random_bytes_do_not_raise(data: bytes) -> None:
    scan_never_raises(data)
