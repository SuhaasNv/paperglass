"""pdf.active.content: JavaScript or actions are present; Paperglass never runs them."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.views.context import PageContext


@technique(
    id="pdf.active.content",
    formats=("pdf",),
    views=("C",),
    stage=0,
    self_proving=True,
    severity_class=SeverityDefault.STRUCTURE_ONLY,
    explanation="The file carries JavaScript or an open action; Paperglass never runs it",
    threshold="`/JS`, `/JavaScript`, `/OpenAction`, `/AA` present; the scan stops for that carrier (malware is DEFERRED)",
    rule_version="1",
    release="v0.1.0",
)
class ActiveContentDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        found: list[Candidate] = []
        if ctx.page_number == 1 and ctx.document is not None:
            carriers = [
                name
                for name, present in (
                    ("JavaScript", ctx.document.has_javascript),
                    ("OpenAction", ctx.document.has_open_action),
                    ("additional actions", ctx.document.has_additional_actions),
                )
                if present
            ]
            if carriers:
                found.append(
                    Candidate(
                        technique_id="pdf.active.content",
                        page=None,
                        extracted_text="",
                        mechanism=f"document carries {', '.join(carriers)}; not executed",
                        reproduce="paperglass show --actions FILE",
                        confidence=1.0,
                        self_proving=True,
                    )
                )
        if ctx.structure is not None:
            for index, annot in enumerate(ctx.structure.annotations):
                if annot.has_javascript:
                    found.append(
                        Candidate(
                            technique_id="pdf.active.content",
                            page=ctx.page_number,
                            bbox=annot.rect,
                            extracted_text="",
                            mechanism=f"{annot.subtype or 'annotation'} {index} on page {ctx.page_number} has a JavaScript action; not executed",
                            reproduce=f"paperglass show --page {ctx.page_number} --annotation {index} FILE",
                            confidence=1.0,
                            self_proving=True,
                        )
                    )
        return found
