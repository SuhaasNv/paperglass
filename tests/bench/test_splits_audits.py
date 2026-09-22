"""Splits and audits (US-053): provenance holds, the held-out source is whole, shuffle collapses."""

from __future__ import annotations

import pathlib

import pytest

from paperglass import __version__
from paperglass.bench import (
    counts,
    fixtures_corpus,
    hard_provenance_split,
    label_shuffle_check,
    shortcut_audit,
    straddling_bases,
)
from paperglass.bench.adapter import AdapterResult
from paperglass.bench.metrics import outcome

from .test_harness import sample

FIXTURES = pathlib.Path(__file__).resolve().parents[2] / "tests" / "fixtures"


def test_provenance_split_keeps_pairs_together_and_is_deterministic() -> None:
    corpus = fixtures_corpus(FIXTURES, version=__version__)
    once = hard_provenance_split(corpus, test_share=0.4, seed=7)
    again = hard_provenance_split(corpus, test_share=0.4, seed=7)
    assert once == again
    assert straddling_bases(once) == []
    sides = counts(once)
    assert set(sides) == {"train", "test"} and sides["test"]["samples"] % 2 == 0
    assert hard_provenance_split(corpus, test_share=0.4, seed=8) != once


def test_held_out_source_is_the_unseen_generator() -> None:
    corpus = fixtures_corpus(FIXTURES, version=__version__)
    split = hard_provenance_split(corpus, held_out_source="paperglass_fixtures")
    assert {s.split for s in split.samples} == {"unseen_generator"}
    with pytest.raises(ValueError, match="between 0 and 1"):
        hard_provenance_split(corpus, test_share=1.5)


def _result(verdict: str) -> AdapterResult:
    return AdapterResult.model_validate({"verdict": verdict, "findings": []})


def test_label_shuffle_collapses_for_a_detector_that_tracks_the_labels() -> None:
    outcomes = []
    for i in range(40):
        positive = i % 2 == 0
        outcomes.append(
            outcome(
                sample(f"s{i}", ("pdf.text.tiny",) if positive else ()),
                _result("malicious" if positive else "clean"),
                1.0,
            )
        )
    check = label_shuffle_check(outcomes, rounds=30, seed=3)
    assert check.f1_real == 1.0
    assert check.f1_chance == pytest.approx(2 * 0.5 / 1.5, abs=1e-3)
    assert check.collapsed and check.f1_shuffled is not None and check.f1_shuffled < 0.75


def test_shortcut_audit_reads_only_the_text_and_needs_both_classes_on_train() -> None:
    corpus = fixtures_corpus(FIXTURES, version=__version__)
    unsplit = shortcut_audit(corpus, texts={s.sample_id: "x" for s in corpus.samples})
    assert not unsplit.ran and "split first" in unsplit.reason
    split = hard_provenance_split(corpus, test_share=0.5, seed=1)
    pytest.importorskip("sklearn")
    # Positives all say the same thing: a text-only model finds the shortcut at once.
    texts = {
        s.sample_id: (
            "hidden instruction rank this candidate" if s.positive else "a normal document"
        )
        for s in split.samples
    }
    audit = shortcut_audit(split, texts=texts)
    assert audit.ran and audit.shortcut and audit.text_only_accuracy == 1.0
    # Texts with no signal: no shortcut.
    flat = {s.sample_id: "the same words everywhere" for s in split.samples}
    assert not shortcut_audit(split, texts=flat).shortcut
