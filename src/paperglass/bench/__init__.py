"""Corpus index, harness, metrics, results (docs/08-benchmark/). Baselines land at US-054."""

from paperglass.bench.adapter import Detector, load_detector, paperglass_detector
from paperglass.bench.index import Corpus, Sample, fixtures_corpus, read_index, write_index
from paperglass.bench.metrics import Metrics, compute
from paperglass.bench.report import collect, render, splice
from paperglass.bench.run import Results, load_results, results_path, run, same_numbers

__all__ = [
    "Corpus",
    "Detector",
    "Metrics",
    "Results",
    "Sample",
    "collect",
    "compute",
    "fixtures_corpus",
    "load_detector",
    "load_results",
    "paperglass_detector",
    "read_index",
    "render",
    "results_path",
    "run",
    "same_numbers",
    "splice",
    "write_index",
]
