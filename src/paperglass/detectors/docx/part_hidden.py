"""docx.part.hidden: text in comments, tracked changes, field codes, headers, footers, alt
text or document properties. Alt text and properties are benign-hidden under length and
phrasing constraints from the profile allowlist."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.docx._common import preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.profiles import Allowlist
from paperglass.views.context import PageContext

BENIGN_KINDS = {"alt_text", "property"}
STANDARD_PROPERTIES = {
    "title",
    "subject",
    "creator",
    "keywords",
    "description",
    "lastModifiedBy",
    "revision",
    "created",
    "modified",
    "category",
    "language",
    "contentStatus",
    "version",
}
INSTRUCTION_CUES = ("ignore", "instruction", "rank", "recommend", "candidate", "you are", "system")


def benign(kind: str, name: str, text: str, allowlist: Allowlist) -> bool:
    if kind not in BENIGN_KINDS:
        return False
    limit = allowlist.alt_text_max_chars if kind == "alt_text" else allowlist.properties_max_chars
    if len(text) > limit:
        return False
    if kind == "property" and name not in STANDARD_PROPERTIES:
        return False
    lowered = text.casefold()
    return not any(cue in lowered for cue in INSTRUCTION_CUES)


@technique(
    id="docx.part.hidden",
    formats=("docx",),
    views=("C",),
    stage=0,
    self_proving=True,
    severity_class=SeverityDefault.DATA,
    explanation="Text in comments, tracked changes, field codes, headers, footers, alt text or document properties",
    threshold="the part exists and carries text the body does not; alt text and properties are benign-hidden under length and phrasing constraints",
    rule_version="1",
    release="v0.1.0",
)
class HiddenPartDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.docx is None:
            return ()
        found: list[Candidate] = []
        for part in ctx.docx.parts:
            if not part.text.strip() or benign(
                part.kind, part.name, part.text, ctx.profile.allowlist
            ):
                continue
            found.append(
                Candidate(
                    technique_id="docx.part.hidden",
                    page=None,
                    extracted_text=part.text,
                    mechanism=f"{part.kind} part {part.name} carries text the body does not: {preview(part.text)!r}",
                    reproduce=f"paperglass show --part {part.name} FILE",
                    confidence=0.95,
                    self_proving=True,
                )
            )
        for run in ctx.docx.runs:
            if not run.text.strip():
                continue
            if run.deleted:
                found.append(
                    Candidate(
                        technique_id="docx.part.hidden",
                        page=1,
                        extracted_text=run.text,
                        mechanism=f"tracked deletion (w:del) still carries text at run {run.index} of paragraph {run.paragraph}: {preview(run.text)!r}",
                        reproduce=reproduce(run),
                        confidence=0.95,
                        self_proving=True,
                    )
                )
            elif run.field_code:
                found.append(
                    Candidate(
                        technique_id="docx.part.hidden",
                        page=1,
                        extracted_text=run.text,
                        mechanism=f"field code (w:instrText) at run {run.index} of paragraph {run.paragraph}: {preview(run.text)!r}",
                        reproduce=reproduce(run),
                        confidence=0.9,
                        self_proving=True,
                    )
                )
        return found
