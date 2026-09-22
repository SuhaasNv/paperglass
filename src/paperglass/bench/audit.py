"""Audits that catch a broken benchmark (docs/08-benchmark/BENCHMARK_DESIGN.md, Hygiene).

Label shuffle: with the labels permuted, a detector's F1 must fall to what chance gives; if it
does not, the labels leak into the detector or the harness. Shortcut audit: a text-only
classifier on View A must not score well on the provenance split; if it does, the split is
separable by surface text and a detector could pass it without reading the document.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from paperglass.bench.index import Corpus
from paperglass.bench.metrics import SampleOutcome, compute

CHANCE_MARGIN = 0.15
"""A shuffled F1 within this of the chance F1 counts as collapsed."""
SHORTCUT_THRESHOLD = 0.8
"""A text-only classifier above this accuracy on the test side says the split is a shortcut."""


class ShuffleCheck(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    f1_real: float | None
    f1_shuffled: float | None
    f1_chance: float | None
    """F1 of a detector that flags everything, the reference for a shuffled label set."""
    collapsed: bool
    rounds: int
    seed: int


def label_shuffle_check(
    outcomes: list[SampleOutcome], *, rounds: int = 20, seed: int = 1
) -> ShuffleCheck:
    """Permute which samples count as positive, recompute F1 each round, compare to chance."""
    real = compute(outcomes)
    rng = random.Random(seed)  # noqa: S311  # a seeded permutation, not a secret
    positives = sum(1 for o in outcomes if o.positive)
    shuffled: list[float] = []
    for _ in range(rounds):
        flags = [o.positive for o in outcomes]
        rng.shuffle(flags)
        permuted = [
            o.model_copy(update={"positive": flag}) for o, flag in zip(outcomes, flags, strict=True)
        ]
        f1 = compute(permuted).f1
        if f1 is not None:
            shuffled.append(f1)
    f1_shuffled = round(sum(shuffled) / len(shuffled), 4) if shuffled else None
    share = positives / len(outcomes) if outcomes else 0.0
    f1_chance = round(2 * share / (1 + share), 4) if outcomes else None
    collapsed = (
        f1_shuffled is not None
        and f1_chance is not None
        and f1_shuffled <= f1_chance + CHANCE_MARGIN
    )
    return ShuffleCheck(
        f1_real=real.f1,
        f1_shuffled=f1_shuffled,
        f1_chance=f1_chance,
        collapsed=collapsed,
        rounds=rounds,
        seed=seed,
    )


class ShortcutAudit(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    ran: bool
    reason: str
    """Why it did not run, or what it did."""
    train_samples: int = 0
    test_samples: int = 0
    text_only_accuracy: float | None = None
    text_only_f1: float | None = None
    shortcut: bool = False
    """True when the text-only classifier beats the threshold: the split is separable by text."""


@dataclass(frozen=True)
class TextSample:
    text: str
    positive: bool
    split: str


def view_a_text(path: str) -> str:
    """What the model reads, as the harness feeds it to the text-only baseline: View A only,
    no metadata, no path, no id, so the audit measures the text and nothing else."""
    from paperglass.engine import scan_bytes  # noqa: PLC0415  # bench stays light to import
    from paperglass.models import Tier  # noqa: PLC0415

    with open(path, "rb") as handle:  # a path from the index, not a Path
        report = scan_bytes(handle.read(), tier=Tier.FAST)
    return "\n".join(run.text for page in report.pages for run in page.runs)


def shortcut_audit(corpus: Corpus, *, texts: dict[str, str] | None = None) -> ShortcutAudit:
    """A TF-IDF logistic regression on View A text, fit on train, scored on test."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: PLC0415
        from sklearn.linear_model import LogisticRegression  # noqa: PLC0415
        from sklearn.metrics import accuracy_score, f1_score  # noqa: PLC0415
        from sklearn.pipeline import make_pipeline  # noqa: PLC0415
    except ImportError:
        return ShortcutAudit(
            ran=False, reason="scikit-learn is not installed: pip install 'paperglass[bench]'"
        )
    rows: list[TextSample] = []
    for sample in corpus.samples:
        text = (
            texts[sample.sample_id]
            if texts is not None and sample.sample_id in texts
            else view_a_text(str(corpus.resolve(sample)))
        )
        rows.append(TextSample(text=text, positive=sample.positive, split=sample.split))
    train = [r for r in rows if r.split == "train"]
    test = [r for r in rows if r.split == "test"]
    if len({r.positive for r in train}) < 2 or not test:
        return ShortcutAudit(
            ran=False,
            reason="the split leaves no train side with both classes, or no test side; split first",
            train_samples=len(train),
            test_samples=len(test),
        )
    model = make_pipeline(
        TfidfVectorizer(min_df=1, ngram_range=(1, 2)), LogisticRegression(max_iter=1000)
    )
    model.fit([r.text for r in train], [r.positive for r in train])
    predicted = model.predict([r.text for r in test])
    truth = [r.positive for r in test]
    accuracy = float(accuracy_score(truth, predicted))
    f1 = float(f1_score(truth, predicted, zero_division=0))
    return ShortcutAudit(
        ran=True,
        reason="TF-IDF (1 and 2-grams) logistic regression on View A text, fit on train, "
        "scored on test",
        train_samples=len(train),
        test_samples=len(test),
        text_only_accuracy=round(accuracy, 4),
        text_only_f1=round(f1, 4),
        shortcut=accuracy > SHORTCUT_THRESHOLD,
    )
