"""docx.run.vanish: a run marked hidden in Word."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.docx._common import locate, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.views.context import PageContext


@technique(
    id="docx.run.vanish",
    formats=("docx",),
    views=("C",),
    stage=0,
    self_proving=True,
    severity_class=SeverityDefault.DATA,
    explanation="Text marked hidden in Word",
    threshold="`w:vanish` or `w:specVanish` on a run",
    rule_version="1",
    release="v0.1.0",
)
class VanishRunDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.docx is None:
            return ()
        return [
            Candidate(
                technique_id="docx.run.vanish",
                page=1,
                extracted_text=run.text,
                mechanism=f"{'w:specVanish' if run.spec_vanish else 'w:vanish'} on {locate(run)}; text {preview(run.text)!r}",
                reproduce=reproduce(run),
                confidence=0.98,
                self_proving=True,
            )
            for run in ctx.docx.runs
            if (run.vanish or run.spec_vanish) and run.text.strip()
        ]
