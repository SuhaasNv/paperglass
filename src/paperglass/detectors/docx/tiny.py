"""docx.run.tiny: run size below 2 pt."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.docx._common import locate, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.views.context import PageContext

TINY_PT = 2.0


@technique(
    id="docx.run.tiny",
    formats=("docx",),
    views=("C",),
    stage=0,
    self_proving=True,
    severity_class=SeverityDefault.DATA,
    explanation="Text too small to read",
    threshold="run size below 2 pt (`w:sz` below 4)",
    rule_version="1",
    release="v0.1.0",
)
class TinyRunDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.docx is None:
            return ()
        return [
            Candidate(
                technique_id="docx.run.tiny",
                page=1,
                extracted_text=run.text,
                mechanism=f"w:sz {run.size_pt * 2:g} ({run.size_pt:g} pt) on {locate(run)}; text {preview(run.text)!r}",
                reproduce=reproduce(run),
                confidence=0.95,
                self_proving=True,
            )
            for run in ctx.docx.runs
            if run.size_pt is not None
            and run.size_pt < TINY_PT
            and run.text.strip()
            and not run.vanish
        ]
