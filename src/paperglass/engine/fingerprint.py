"""paperglass fingerprint: does each installed extractor hand the hidden text to a model?

The default scan decides what is hidden; every extractor that handles the input type is
then run (in the sandbox) and its View A is searched for each confirmed finding's text.
"""

from __future__ import annotations

from rapidfuzz import fuzz

from paperglass.engine.scan import scan_bytes
from paperglass.ingest import Limits, sniff
from paperglass.models import FindingStatus, Report, Tier
from paperglass.models.fingerprint import ExtractorVerdict, Fingerprint, FingerprintRow
from paperglass.views.extract import available

AGREEMENT_THRESHOLD = 0.8
PREVIEW = 60


def _contains(haystack: str, needle: str) -> float:
    needle = needle.strip()
    if not needle:
        return 0.0
    if needle in haystack:
        return 1.0
    return float(fuzz.partial_ratio(needle.casefold(), haystack.casefold())) / 100.0


def fingerprint_bytes(
    data: bytes,
    *,
    limits: Limits | None = None,
    profile: str = "default",
    extractors: tuple[str, ...] | None = None,
    report: Report | None = None,
) -> Fingerprint:
    limits = limits or Limits.from_env()
    report = report or scan_bytes(data, limits=limits, tier=Tier.FAST, profile=profile)
    input_type = sniff(data)
    candidates = [e for e in available(input_type) if extractors is None or e.name in extractors]
    texts: dict[str, str] = {}
    versions: dict[str, str] = {}
    failed: dict[str, str] = {}
    for extractor in candidates:
        outcome = extractor.extract(data, limits=limits)
        versions[extractor.name] = extractor.version()
        if outcome.document is None:
            failed[extractor.name] = outcome.failure.reason if outcome.failure else "no text"
            continue
        texts[extractor.name] = outcome.document.text
    rows: list[FingerprintRow] = []
    for finding in report.findings:
        if finding.status is not FindingStatus.CONFIRMED or not finding.extracted_text.strip():
            continue
        verdicts: list[ExtractorVerdict] = []
        for extractor in candidates:
            if extractor.name in failed:
                verdicts.append(
                    ExtractorVerdict(
                        extractor=extractor.name,
                        version=versions[extractor.name],
                        returns_hidden_text=None,
                        agreement=0.0,
                    )
                )
                continue
            score = _contains(texts[extractor.name], finding.extracted_text)
            verdicts.append(
                ExtractorVerdict(
                    extractor=extractor.name,
                    version=versions[extractor.name],
                    returns_hidden_text=score >= AGREEMENT_THRESHOLD,
                    agreement=score,
                )
            )
        preview = finding.extracted_text.replace("\n", " ")
        rows.append(
            FingerprintRow(
                finding_id=finding.id,
                technique_id=finding.technique_id,
                page=finding.page,
                text_preview=preview if len(preview) <= PREVIEW else preview[: PREVIEW - 3] + "...",
                extractors=tuple(verdicts),
            )
        )
    return Fingerprint(
        input_sha256=report.input_sha256,
        input_type=input_type.value,
        default_extractor=report.extractor,
        extractors=versions,
        failed=failed,
        rows=tuple(rows),
    )
