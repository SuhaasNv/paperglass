"""The scan: stage 0 pages, detectors, stage 1 and 2 promotion, severity, verdict, report.

Tiers name the stages that run (docs/03-architecture/VIEWS.md): fast is stages 0 and 1,
standard adds stage 2 (OCR on crops), deep is opt-in and lands later.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import paperglass.detectors  # noqa: F401  # registration
from paperglass import __version__
from paperglass.detectors import REGISTRY, Candidate, SeverityDefault
from paperglass.engine.hints import hints_for
from paperglass.engine.profile import Profile, load_profile
from paperglass.engine.promote import ocr_layer_is_benign, promote
from paperglass.engine.severity import classify
from paperglass.ingest import Limits
from paperglass.models import (
    Finding,
    FindingStatus,
    PageRaster,
    ParseFailure,
    RenderCrop,
    Report,
    Severity,
    SeverityClass,
    Tier,
    Verdict,
    sha256_of,
)
from paperglass.views.context import PageContext
from paperglass.views.pages import Stage0, build_pages
from paperglass.views.render import choose_dpi, render_document

TIER_TOP_STAGE: dict[Tier, int] = {Tier.FAST: 1, Tier.STANDARD: 2, Tier.DEEP: 4}


@dataclass
class _Timer:
    marks: dict[str, float] = field(default_factory=dict)
    started: float = field(default_factory=time.perf_counter)

    def lap(self, name: str) -> None:
        now = time.perf_counter()
        self.marks[name] = round((now - self.started) * 1000.0, 3)
        self.started = now


def scan_bytes(  # noqa: PLR0913  # the public entry point takes one keyword per option
    data: bytes,
    *,
    limits: Limits | None = None,
    tier: Tier = Tier.STANDARD,
    profile: str = "default",
    extractor: str | None = None,
    redact: bool = False,
) -> Report:
    """Scan one document held in memory. Never raises for a bad document."""
    limits = limits or Limits.from_env()
    prof = load_profile(profile)
    timer = _Timer()
    stage0 = build_pages(data, limits=limits, extractor=extractor, profile=prof)
    timer.lap("stage0")

    rasters, render_failure, dpi = _render(data, stage0, limits, tier)
    failures: list[ParseFailure] = list(stage0.failures)
    if render_failure is not None:
        failures.append(render_failure)
    timer.lap("render")

    candidates = _run_detectors(stage0, rasters)
    timer.lap("detectors")

    use_ocr = TIER_TOP_STAGE[tier] >= 2
    findings = _promote_all(candidates, rasters, prof, use_ocr=use_ocr, extractor=stage0.extractor)
    timer.lap("promote")

    if redact:
        findings = [_redacted(f) for f in findings]

    confirmed = [f for f in findings if f.status is FindingStatus.CONFIRMED]
    counts = dict.fromkeys(Severity, 0)
    for finding in confirmed:
        counts[finding.severity] += 1
    verdict = _verdict(confirmed, failures, prof)
    timer.lap("verdict")

    rule_versions = REGISTRY.rule_versions()
    for hint in hints_for(prof):
        rule_versions[f"hint.{hint.name}"] = hint.version

    return Report(
        tool_version=__version__,
        rule_versions=rule_versions,
        input_sha256=sha256_of(data),
        input_type=stage0.input_type.value,
        extractor=stage0.extractor,
        tier=tier,
        profile=prof.name,
        page_count=stage0.page_count,
        pages_render_verified=len(rasters),
        dpi=dpi if rasters else None,
        verdict=verdict,
        severity_counts=counts,
        findings=tuple(sorted(findings, key=_finding_order)),
        parse_failures=tuple(failures),
        network_used=(),
        timing_ms=timer.marks,
    )


def _run_detectors(
    stage0: Stage0, rasters: dict[int, PageRaster]
) -> list[tuple[PageContext, Candidate]]:
    found: list[tuple[PageContext, Candidate]] = []
    for bare in stage0.pages:
        raster = rasters.get(bare.page_number)
        page = bare.model_copy(update={"raster": raster}) if raster is not None else bare
        for technique_id in REGISTRY:
            detector = REGISTRY.detector(technique_id)()
            found.extend((page, candidate) for candidate in detector.probe(page))
    return found


def _render(
    data: bytes, stage0: Stage0, limits: Limits, tier: Tier
) -> tuple[dict[int, PageRaster], ParseFailure | None, int]:
    dpi = choose_dpi(stage0.structure)
    if TIER_TOP_STAGE[tier] < 1 or stage0.input_type.value != "pdf" or not stage0.pages:
        return {}, None, dpi
    numbers = tuple(page.page_number for page in stage0.pages)
    outcome = render_document(data, limits=limits, numbers=numbers, dpi=dpi)
    return {r.number: r for r in outcome.rasters}, outcome.failure, dpi


def _promote_all(
    candidates: list[tuple[PageContext, Candidate]],
    rasters: dict[int, PageRaster],
    profile: Profile,
    *,
    use_ocr: bool,
    extractor: str,
) -> list[Finding]:
    findings: list[Finding] = []
    for page, candidate in candidates:
        spec = REGISTRY.spec(candidate.technique_id)
        raster = rasters.get(candidate.page) if candidate.page is not None else None
        benign_read = ocr_layer_is_benign(candidate, raster, profile=profile, use_ocr=use_ocr)
        structure_only = spec.severity_class is SeverityDefault.STRUCTURE_ONLY
        promotion = promote(
            candidate, raster, profile=profile, use_ocr=use_ocr, structure_only=structure_only
        )
        if promotion.status is None:
            continue
        if benign_read is not None:
            severity_class, severity = SeverityClass.BENIGN_HIDDEN, profile.severity.benign_hidden
            why = "OCR text layer on a scanned page: the render shows the same words"
        elif (
            structure_only and promotion.status is FindingStatus.CONFIRMED and promotion.stage >= 2
        ):
            # Stage 2 proved the model reads different words than the page shows.
            severity_class, severity = classify(
                spec.model_copy(update={"severity_class": SeverityDefault.DATA}),
                candidate.extracted_text,
                profile,
            )
            why = spec.explanation
        else:
            severity_class, severity = classify(spec, candidate.extracted_text, profile)
            why = spec.explanation
        findings.append(
            Finding(
                id=f"f-{len(findings) + 1}",
                technique_id=candidate.technique_id,
                status=promotion.status,
                page=candidate.page,
                bbox=candidate.bbox,
                extracted_text=candidate.extracted_text,
                render_crop=promotion.crop,
                why_hidden=why,
                mechanism=candidate.mechanism,
                reproduce=candidate.reproduce,
                severity=severity,
                severity_class=severity_class,
                confidence=candidate.confidence,
                views=tuple(sorted(set(promotion.views) | set(spec.views))),  # type: ignore[arg-type]  # Literal views
                stage=max(promotion.stage, spec.stage),
                atr_rule=spec.atr_rule,
                extractor=page.extractor or extractor,
            )
        )
    return findings


def _verdict(confirmed: list[Finding], failures: list[ParseFailure], profile: Profile) -> Verdict:
    levels = {f.severity for f in confirmed}
    if levels & set(profile.verdict.malicious):
        return Verdict.MALICIOUS
    if levels & set(profile.verdict.suspicious):
        return Verdict.SUSPICIOUS
    if failures and profile.verdict.parse_failure_verdict == "suspicious":
        return Verdict.SUSPICIOUS
    if any(f.severity_class is SeverityClass.BENIGN_HIDDEN for f in confirmed):
        return Verdict.BENIGN_HIDDEN
    return Verdict.CLEAN


def _redacted(finding: Finding) -> Finding:
    """--redact: shorten the text and drop the crop, so a report carries the least content."""
    text = finding.extracted_text
    if len(text) > 80:
        text = text[:77] + "..."
    crop = RenderCrop(none_reason="redacted")
    return finding.model_copy(update={"extracted_text": text, "render_crop": crop})


_SEVERITY_RANK = {level: index for index, level in enumerate(Severity)}


def _finding_order(finding: Finding) -> tuple[int, int, int, str]:
    return (
        0 if finding.status is FindingStatus.CONFIRMED else 1,
        -_SEVERITY_RANK[finding.severity],
        finding.page or 0,
        finding.technique_id,
    )
