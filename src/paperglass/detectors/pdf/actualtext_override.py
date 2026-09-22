"""pdf.actualtext.override: marked content replaces the painted text with something else.
Ligatures and hyphenation (a few characters) are benign-hidden; longer overrides are a
candidate that stage 2 confirms by reading the painted glyphs."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.pdf._common import preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.views.context import PageContext


@technique(
    id="pdf.actualtext.override",
    formats=("pdf",),
    views=("B", "C"),
    stage=2,
    severity_class=SeverityDefault.STRUCTURE_ONLY,
    explanation="A hidden replacement text overrides what the page shows",
    threshold="`/ActualText` differs from the painted glyphs; ligatures and hyphenation are benign-hidden when the ActualText is at most a few characters",
    rule_version="1",
    release="v0.1.0",
)
class ActualTextOverrideDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.structure is None:
            return ()
        found: list[Candidate] = []
        for obj in ctx.structure.text_objects:
            actual = obj.actual_text
            if actual is None or actual == obj.text:
                continue
            if len(actual) <= ctx.profile.allowlist.actual_text_max_chars:
                continue
            found.append(
                Candidate(
                    technique_id="pdf.actualtext.override",
                    page=ctx.page_number,
                    bbox=obj.bbox,
                    extracted_text=actual,
                    mechanism=(
                        f"/ActualText {preview(actual)!r} replaces painted text {preview(obj.text)!r} "
                        f"at instruction {obj.instruction} of the page {ctx.page_number} content stream"
                    ),
                    reproduce=reproduce(ctx, obj),
                    confidence=0.92,
                )
            )
        return found
