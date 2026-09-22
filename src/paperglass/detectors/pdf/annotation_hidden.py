"""pdf.annotation.hidden: text in annotations, fields or attachments a person did not open."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.views.context import PageContext


@technique(
    id="pdf.annotation.hidden",
    formats=("pdf",),
    views=("C",),
    stage=0,
    severity_class=SeverityDefault.DATA,
    explanation="Text in notes, form fields, tooltips or attachments a person did not open",
    threshold="annotation with hidden or no-view flags, form field values, embedded files",
    rule_version="1",
    release="v0.1.0",
)
class HiddenAnnotationDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        found: list[Candidate] = []
        if ctx.structure is not None:
            for index, annot in enumerate(ctx.structure.annotations):
                text = annot.field_value or annot.contents
                if not text or not (annot.hidden or annot.no_view):
                    continue
                flag = "hidden" if annot.hidden else "no-view"
                where = (
                    f"object {annot.object_number}"
                    if annot.object_number
                    else f"annotation {index}"
                )
                found.append(
                    Candidate(
                        technique_id="pdf.annotation.hidden",
                        page=ctx.page_number,
                        bbox=annot.rect,
                        extracted_text=text,
                        mechanism=f"{annot.subtype or 'annotation'} {where} on page {ctx.page_number} has the {flag} flag and carries text",
                        reproduce=f"paperglass show --page {ctx.page_number} --annotation {index} FILE",
                        confidence=0.95,
                    )
                )
        if ctx.page_number == 1 and ctx.document is not None:
            for name in ctx.document.embedded_files:
                found.append(
                    Candidate(
                        technique_id="pdf.annotation.hidden",
                        page=None,
                        extracted_text=name,
                        mechanism=f"embedded file {name!r} in the document name tree",
                        reproduce="paperglass show --embedded FILE",
                        confidence=0.8,
                    )
                )
        return found
