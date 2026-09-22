"""Metrics per detector (docs/08-benchmark/BENCHMARK_DESIGN.md), plain Python, no learning."""

from __future__ import annotations

from collections import defaultdict
from statistics import median

from pydantic import BaseModel, ConfigDict, Field

from paperglass.bench.adapter import AdapterResult
from paperglass.bench.index import WILDCARD, Sample

VERDICT_DRIVING: frozenset[str] = frozenset({"medium", "high", "critical"})


class SampleOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    sample_id: str
    positive: bool
    labels: tuple[str, ...]
    family: str
    injection_kind: str
    flagged: bool
    """The detector's verdict was suspicious or malicious."""
    detected: tuple[str, ...]
    """Which of the sample's labels the detector named with a finding of any status."""
    confirmed: tuple[str, ...]
    """Which of them it named with a confirmed finding (the ones that can drive a verdict)."""
    verdict: str
    findings: int
    verdict_driving_findings: int
    informational_findings: int
    latency_ms: float
    error: str | None = None


def outcome(sample: Sample, result: AdapterResult, latency_ms: float) -> SampleOutcome:
    named = {f.technique_id for f in result.findings}
    confirmed = {f.technique_id for f in result.findings if f.status == "confirmed"}
    if named:
        named.add(WILDCARD)
    if confirmed:
        confirmed.add(WILDCARD)
    return SampleOutcome(
        sample_id=sample.sample_id,
        positive=sample.positive,
        labels=sample.labels,
        family=sample.family,
        injection_kind=sample.injection_kind,
        flagged=result.flagged,
        detected=tuple(label for label in sample.labels if label in named),
        confirmed=tuple(label for label in sample.labels if label in confirmed),
        verdict=result.verdict,
        findings=len(result.findings),
        verdict_driving_findings=sum(1 for f in result.findings if f.severity in VERDICT_DRIVING),
        informational_findings=sum(1 for f in result.findings if f.severity not in VERDICT_DRIVING),
        latency_ms=latency_ms,
    )


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def _percentile(values: list[float], share: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round(share * (len(ordered) - 1))))
    return round(ordered[index], 3)


class Metrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    samples: int
    positives: int
    negatives: int
    errors: int
    precision: float | None
    recall: float | None
    """Verdict-level: the share of positives the detector called suspicious or malicious.
    Structure-only techniques never drive a verdict by contract, so this is the sanity number."""
    f1: float | None
    detection_recall: float | None
    """The share of positives where every label was named by a finding of any status."""
    recall_per_technique: dict[str, float | None]
    """Per technique: named by a finding of any status (possible counts; the report says so)."""
    recall_per_family: dict[str, float | None]
    recall_instruction: float | None
    recall_data: float | None
    false_positive_rate_verdict_driving: float | None
    """Share of negatives the detector flagged: the target is at or below 0.001."""
    false_positive_rate_informational: float | None
    """Share of negatives with any informational finding: reported, no target."""
    benign_hidden_called_malicious: int
    latency_p50_ms: float | None
    latency_p95_ms: float | None
    latency_p50_per_page_ms: float | None = Field(default=None)


def compute(outcomes: list[SampleOutcome]) -> Metrics:
    positives = [o for o in outcomes if o.positive]
    negatives = [o for o in outcomes if not o.positive]
    tp = sum(1 for o in positives if o.flagged)
    fp = sum(1 for o in negatives if o.flagged)
    fn = len(positives) - tp
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    f1 = (
        round(2 * precision * recall / (precision + recall), 4)
        if precision and recall and (precision + recall)
        else (0.0 if positives else None)
    )
    per_technique: dict[str, list[bool]] = defaultdict(list)
    per_family: dict[str, list[bool]] = defaultdict(list)
    per_kind: dict[str, list[bool]] = defaultdict(list)
    for o in positives:
        for label in o.labels:
            per_technique[label].append(label in o.detected)
        per_family[o.family].append(o.flagged)
        per_kind[o.injection_kind].append(o.flagged)
    latencies = [o.latency_ms for o in outcomes if o.error is None]
    return Metrics(
        samples=len(outcomes),
        positives=len(positives),
        negatives=len(negatives),
        errors=sum(1 for o in outcomes if o.error is not None),
        precision=precision,
        recall=recall,
        f1=f1,
        detection_recall=_ratio(
            sum(1 for o in positives if set(o.labels) <= set(o.detected)), len(positives)
        ),
        recall_per_technique={k: _ratio(sum(v), len(v)) for k, v in sorted(per_technique.items())},
        recall_per_family={k: _ratio(sum(v), len(v)) for k, v in sorted(per_family.items())},
        recall_instruction=_ratio(sum(per_kind["instruction"]), len(per_kind["instruction"])),
        recall_data=_ratio(sum(per_kind["data"]), len(per_kind["data"])),
        false_positive_rate_verdict_driving=_ratio(fp, len(negatives)),
        false_positive_rate_informational=_ratio(
            sum(1 for o in negatives if o.informational_findings), len(negatives)
        ),
        benign_hidden_called_malicious=sum(
            1 for o in negatives if o.verdict == "malicious" and o.informational_findings
        ),
        latency_p50_ms=round(median(latencies), 3) if latencies else None,
        latency_p95_ms=_percentile(latencies, 0.95),
    )
