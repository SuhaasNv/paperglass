"""Stage 0: turn bytes into one PageContext per page (View A plus View C where it exists)."""

from __future__ import annotations

from dataclasses import dataclass, field

from paperglass.ingest import Limits, guard_pages, guard_size, guard_zip, sniff
from paperglass.ingest.sniff import InputType
from paperglass.models import DocumentStructure, DocumentText, ParseFailure
from paperglass.models.docx import DocxStructure
from paperglass.profiles import Profile, load_profile
from paperglass.views.context import PageContext
from paperglass.views.extract import Extractor, default_for, get
from paperglass.views.structure import docx_structure, pdf_structure

ZIP_TYPES = frozenset({InputType.DOCX, InputType.PPTX, InputType.XLSX, InputType.ZIP})


@dataclass(frozen=True)
class Stage0:
    """Everything stage 0 learned. Failures are reported, never raised."""

    input_type: InputType
    extractor: str
    pages: tuple[PageContext, ...]
    text: DocumentText | None
    structure: DocumentStructure | None
    failures: tuple[ParseFailure, ...] = field(default_factory=tuple)

    @property
    def page_count(self) -> int:
        if self.structure is not None:
            return self.structure.page_count
        return self.text.page_count if self.text is not None else 0


def build_pages(
    data: bytes, *, limits: Limits, extractor: str | None = None, profile: Profile | None = None
) -> Stage0:
    """Sniff, guard, extract (View A) and probe (View C), then zip the two per page."""
    prof = profile or load_profile()
    input_type = sniff(data)
    failures: list[ParseFailure] = []
    for failure in (
        guard_size(data, limits),
        guard_zip(data, limits) if input_type in ZIP_TYPES else None,
    ):
        if failure is not None:
            failures.append(failure)
    chosen: Extractor | None = get(extractor) if extractor else default_for(input_type)
    if failures or chosen is None:
        if chosen is None and not failures:
            failures.append(
                ParseFailure(
                    stage=0,
                    parser="ingest",
                    reason="crash",
                    message=f"no extractor for {input_type}",
                )
            )
        return Stage0(
            input_type, chosen.name if chosen else "none", (), None, None, tuple(failures)
        )

    text_outcome = chosen.extract(data, limits=limits)
    if text_outcome.failure is not None:
        failures.append(text_outcome.failure)
    text = text_outcome.document

    structure: DocumentStructure | None = None
    docx: DocxStructure | None = None
    if input_type is InputType.PDF:
        outcome = pdf_structure(data, limits=limits)
        if outcome.failure is not None:
            failures.append(outcome.failure)
        structure = outcome.structure
    elif input_type is InputType.DOCX:
        docx_outcome = docx_structure(data, limits=limits)
        if docx_outcome.failure is not None:
            failures.append(docx_outcome.failure)
        docx = docx_outcome.structure

    page_count = structure.page_count if structure is not None else (text.page_count if text else 0)
    if (cap := guard_pages(page_count, limits)) is not None:
        failures.append(cap)
        page_count = limits.max_pages

    pages: list[PageContext] = []
    for number in range(1, page_count + 1):
        page_text = (
            text.pages[number - 1] if text is not None and number <= text.page_count else None
        )
        page_structure = (
            structure.pages[number - 1]
            if structure is not None and number <= len(structure.pages)
            else None
        )
        pages.append(
            PageContext(
                page_number=number,
                page_count=page_count,
                input_type=input_type.value,
                extractor=chosen.name,
                profile=prof,
                runs=page_text.runs if page_text is not None else (),
                width=page_text.width
                if page_text is not None
                else (page_structure.width if page_structure else None),
                height=page_text.height
                if page_text is not None
                else (page_structure.height if page_structure else None),
                structure=page_structure,
                document=structure,
                docx=docx,
            )
        )
    return Stage0(input_type, chosen.name, tuple(pages), text, structure, tuple(failures))
