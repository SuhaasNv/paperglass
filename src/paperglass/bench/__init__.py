"""Corpus index, harness, metrics, results (docs/08-benchmark/). Baselines land at US-054."""

from paperglass.bench.adapter import Detector, load_detector, paperglass_detector
from paperglass.bench.audit import ShortcutAudit, ShuffleCheck, label_shuffle_check, shortcut_audit
from paperglass.bench.index import Corpus, Sample, fixtures_corpus, read_index, write_index
from paperglass.bench.metrics import Metrics, compute
from paperglass.bench.report import collect, render, splice
from paperglass.bench.run import Results, load_results, results_path, run, same_numbers
from paperglass.bench.splits import counts, hard_provenance_split, straddling_bases

__all__ = [
    "Corpus",
    "Detector",
    "Metrics",
    "Results",
    "Sample",
    "ShortcutAudit",
    "ShuffleCheck",
    "collect",
    "compute",
    "counts",
    "fixtures_corpus",
    "hard_provenance_split",
    "label_shuffle_check",
    "load_detector",
    "load_results",
    "paperglass_detector",
    "read_index",
    "render",
    "results_path",
    "run",
    "same_numbers",
    "shortcut_audit",
    "splice",
    "straddling_bases",
    "write_index",
]
