"""Run a detector over a corpus and write the results file (docs/08-benchmark/HARNESS.md)."""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import platform
import time

from pydantic import BaseModel, ConfigDict, ValidationError

from paperglass.bench.adapter import AdapterResult, Detector
from paperglass.bench.index import Corpus, Sample, sha256_file
from paperglass.bench.metrics import Metrics, SampleOutcome, compute, outcome


class Results(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    detector: str
    detector_version: str
    corpus: str
    corpus_version: str
    synthetic: bool
    command: str
    hardware: str
    date: str
    metrics: Metrics
    per_sample: tuple[SampleOutcome, ...]

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"


def hardware() -> str:
    return f"{platform.machine()} {platform.system()} Python {platform.python_version()}"


def verify_hashes(corpus: Corpus) -> list[str]:
    """Samples whose file is missing or whose bytes differ from the index."""
    problems: list[str] = []
    for sample in corpus.samples:
        path = corpus.resolve(sample)
        if not path.is_file():
            problems.append(f"{sample.sample_id}: missing {path}")
        elif sha256_file(path) != sample.sha256:
            problems.append(f"{sample.sample_id}: hash differs from the index")
    return problems


def _scan(detector: Detector, sample: Sample, path: pathlib.Path) -> SampleOutcome:
    started = time.perf_counter()
    try:
        raw = detector.scan(str(path))
        result = AdapterResult.model_validate(raw)
    except (ValidationError, Exception) as exc:  # noqa: BLE001  # a detector crash is a row
        elapsed = (time.perf_counter() - started) * 1000.0
        return SampleOutcome(
            sample_id=sample.sample_id,
            positive=sample.positive,
            labels=sample.labels,
            family=sample.family,
            injection_kind=sample.injection_kind,
            flagged=False,
            detected=(),
            confirmed=(),
            verdict="error",
            findings=0,
            verdict_driving_findings=0,
            informational_findings=0,
            latency_ms=round(elapsed, 3),
            error=f"{type(exc).__name__}: {exc}"[:200],
        )
    elapsed = (time.perf_counter() - started) * 1000.0
    return outcome(sample, result, round(elapsed, 3))


def run(corpus: Corpus, detector: Detector, *, command: str) -> Results:
    problems = verify_hashes(corpus)
    if problems:
        msg = "corpus does not match its index: " + "; ".join(problems[:5])
        raise ValueError(msg)
    outcomes = [_scan(detector, sample, corpus.resolve(sample)) for sample in corpus.samples]
    return Results(
        detector=detector.name,
        detector_version=detector.version(),
        corpus=corpus.name,
        corpus_version=corpus.version,
        synthetic=corpus.synthetic,
        command=command,
        hardware=hardware(),
        date=dt.datetime.now(dt.UTC).date().isoformat(),
        metrics=compute(outcomes),
        per_sample=tuple(outcomes),
    )


def results_path(root: pathlib.Path, results: Results) -> pathlib.Path:
    return root / results.detector / results.detector_version / f"{results.corpus}.json"


def load_results(path: pathlib.Path) -> Results:
    return Results.model_validate_json(path.read_text(encoding="utf-8"))


def same_numbers(a: Results, b: Results) -> list[str]:
    """Metric fields that differ between two runs, latency excluded (it is hardware)."""
    skip = {"latency_p50_ms", "latency_p95_ms", "latency_p50_per_page_ms"}
    left = a.metrics.model_dump()
    right = b.metrics.model_dump()
    return [k for k in left if k not in skip and left[k] != right[k]]
