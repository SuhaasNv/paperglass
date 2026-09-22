"""Splits that make a score mean generalisation (docs/08-benchmark/BENCHMARK_DESIGN.md).

Hard provenance: every sample of one base document lands on the same side, so an injected
sample and its clean control never straddle train and test. Unseen generator: one source held
out entirely, to measure what the detector does on samples nothing it was tuned on produced.
"""

from __future__ import annotations

import hashlib

from paperglass.bench.index import Corpus, Sample, Split


def _bucket(base_document: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}:{base_document}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def hard_provenance_split(
    corpus: Corpus, *, test_share: float = 0.3, seed: int = 1, held_out_source: str | None = None
) -> Corpus:
    """Assign whole base documents to train or test by a seeded hash; a held-out source goes
    to `unseen_generator` in full. Deterministic: the same corpus and seed give the same split."""
    if not 0.0 < test_share < 1.0:
        msg = "test_share must be between 0 and 1"
        raise ValueError(msg)
    samples: list[Sample] = []
    for sample in corpus.samples:
        split: Split
        if held_out_source is not None and sample.source == held_out_source:
            split = "unseen_generator"
        else:
            split = "test" if _bucket(sample.base_document, seed) < test_share else "train"
        samples.append(sample.model_copy(update={"split": split}))
    return corpus.model_copy(update={"samples": tuple(samples)})


def straddling_bases(corpus: Corpus) -> list[str]:
    """Base documents with samples on more than one side: must be empty for a valid split."""
    sides: dict[str, set[str]] = {}
    for sample in corpus.samples:
        sides.setdefault(sample.base_document, set()).add(sample.split)
    return sorted(base for base, found in sides.items() if len(found) > 1)


def counts(corpus: Corpus) -> dict[str, dict[str, int]]:
    """Samples and positives per split, for the report."""
    out: dict[str, dict[str, int]] = {}
    for sample in corpus.samples:
        row = out.setdefault(sample.split, {"samples": 0, "positives": 0})
        row["samples"] += 1
        row["positives"] += int(sample.positive)
    return out
