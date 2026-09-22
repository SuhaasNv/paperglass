"""The benchmark harness (US-052): adapter shape, metrics, the fixtures corpus, results files."""

from __future__ import annotations

import json
import pathlib

import pytest

from paperglass import __version__
from paperglass.bench import (
    Results,
    collect,
    compute,
    fixtures_corpus,
    load_detector,
    read_index,
    render,
    run,
    same_numbers,
    splice,
    write_index,
)
from paperglass.bench.adapter import AdapterResult
from paperglass.bench.index import Sample
from paperglass.bench.metrics import outcome
from paperglass.bench.run import verify_hashes

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"


def sample(sample_id: str, labels: tuple[str, ...], kind: str = "data") -> Sample:
    return Sample(
        sample_id=sample_id,
        path="x",
        sha256="0" * 64,
        source="test",
        source_version="1",
        licence="Apache-2.0",
        format="pdf",
        labels=labels,
        family="visual" if labels else "none",
        injection_kind=kind if labels else "none",  # type: ignore[arg-type]  # test literal
        base_document="b",
    )


def result(
    verdict: str, *techniques: str, status: str = "confirmed", severity: str = "medium"
) -> AdapterResult:
    return AdapterResult.model_validate(
        {
            "verdict": verdict,
            "findings": [
                {"technique_id": t, "severity": severity, "confidence": 0.9, "status": status}
                for t in techniques
            ],
        }
    )


def test_metrics_separate_verdict_recall_from_detection_recall() -> None:
    outcomes = [
        outcome(
            sample("p1", ("pdf.text.tiny",), "instruction"),
            result("malicious", "pdf.text.tiny"),
            10,
        ),
        outcome(
            sample("p2", ("pdf.font.tounicode_mismatch",)),
            result("clean", "pdf.font.tounicode_mismatch", status="possible", severity="info"),
            20,
        ),
        outcome(sample("p3", ("docx.run.vanish",)), result("clean"), 30),
        outcome(sample("n1", ()), result("clean"), 5),
        outcome(sample("n2", ()), result("suspicious", "pdf.text.covered"), 6),
        outcome(
            sample("n3", ()), result("clean", "pdf.font.decoding_fallback", severity="info"), 7
        ),
    ]
    m = compute(outcomes)
    assert (m.positives, m.negatives) == (3, 3)
    assert m.recall == pytest.approx(1 / 3, abs=1e-3)
    assert m.detection_recall == pytest.approx(2 / 3, abs=1e-3)
    assert m.precision == pytest.approx(0.5)
    assert m.recall_per_technique == {
        "pdf.text.tiny": 1.0,
        "pdf.font.tounicode_mismatch": 1.0,
        "docx.run.vanish": 0.0,
    }
    assert m.recall_instruction == 1.0 and m.recall_data == 0.0
    assert m.false_positive_rate_verdict_driving == pytest.approx(1 / 3, abs=1e-3)
    assert m.false_positive_rate_informational == pytest.approx(1 / 3, abs=1e-3)
    assert m.latency_p50_ms == 8.5 and m.latency_p95_ms == 30


def test_fixtures_corpus_has_a_pair_per_technique_and_round_trips(tmp_path: pathlib.Path) -> None:
    corpus = fixtures_corpus(FIXTURES, version=__version__)
    assert corpus.synthetic and len(corpus.samples) == 36
    assert sum(1 for s in corpus.samples if s.positive) == 18
    assert verify_hashes(corpus) == []
    write_index(corpus, tmp_path / "index.jsonl")
    again = read_index(tmp_path / "index.jsonl", pathlib.Path(corpus.root))
    assert again == corpus
    families = {s.family for s in corpus.samples if s.positive}
    assert families == {"visual", "structural", "semantic-override", "unicode", "metadata"}


def test_paperglass_adapter_runs_the_fixtures_and_the_numbers_reproduce() -> None:
    corpus = fixtures_corpus(FIXTURES, version=__version__)
    detector = load_detector("paperglass", tier="fast")
    first = run(corpus, detector, command="test")
    assert first.metrics.errors == 0
    assert first.metrics.detection_recall == 1.0
    assert first.metrics.false_positive_rate_verdict_driving == 0.0
    assert first.metrics.benign_hidden_called_malicious == 0
    # Structure-only techniques never drive a verdict, so verdict recall is below detection recall.
    assert first.metrics.recall is not None and first.metrics.recall < 1.0
    second = run(corpus, detector, command="test")
    assert same_numbers(first, second) == []
    text = first.to_json()
    assert Results.model_validate_json(text).metrics == first.metrics


def test_committed_results_file_reproduces() -> None:
    """The file in results/ is what CI checks; a detector change regenerates it with a reason."""
    committed = collect(ROOT / "results")
    ours = [r for r in committed if r.detector == "paperglass-fast" and r.corpus == "fixtures"]
    assert ours, "results/paperglass-fast/<version>/fixtures.json is missing"
    corpus = fixtures_corpus(FIXTURES, version=__version__)
    fresh = run(corpus, load_detector("paperglass", tier="fast"), command=ours[-1].command)
    assert same_numbers(ours[-1], fresh) == []


def test_unknown_detector_and_bad_shape_are_errors() -> None:
    with pytest.raises(ValueError, match="module:function"):
        load_detector("nope")
    with pytest.raises(ImportError):
        load_detector("no_such_module:scan")
    corpus = fixtures_corpus(FIXTURES, version=__version__)
    broken = load_detector("tests.bench.test_harness:broken_scan")
    results = run(corpus, broken, command="test")
    assert results.metrics.errors == len(corpus.samples)
    assert all(o.error and "KeyError" in o.error for o in results.per_sample)


def broken_scan(path: str) -> dict[str, object]:
    raise KeyError(path)


def version() -> str:
    return "broken"


def test_report_renders_and_splices(tmp_path: pathlib.Path) -> None:
    results = collect(ROOT / "results")
    table = render(results)
    assert "synthetic; never a headline number" in table
    assert "| paperglass-fast |" in table
    document = "# B\n\nintro\n"
    once = splice(document, table)
    twice = splice(once, table)
    assert once == twice and once.count("<!-- bench:start -->") == 1
    payload = json.loads(
        (ROOT / "results" / "paperglass-fast" / __version__ / "fixtures.json").read_text()
    )
    assert payload["synthetic"] is True and payload["command"].startswith("paperglass bench run")
