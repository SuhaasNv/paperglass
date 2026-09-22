"""The one-file HTML report (docs/04-report-design/REPORT_DESIGN.md).

One file, opens from file:// with the browser offline, no external request: CSS inline, crops as
data URIs, the findings as JSON in a script tag, a few lines of inline script for the lens.
Reads models only. Deterministic: the same report renders the same bytes.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Final

from jinja2 import Environment, StrictUndefined, select_autoescape

from paperglass.models import Finding, Report, Severity, Verdict

TEMPLATES: Final[str] = "paperglass.report.templates"


@lru_cache(maxsize=4)
def _asset(name: str) -> str:
    return (resources.files(TEMPLATES) / name).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _shapes() -> dict[str, str]:
    shapes: dict[str, str] = {}
    for line in _asset("shapes.tsv").splitlines():
        if line.strip():
            level, svg = line.split("\t", 1)
            shapes[level] = svg
    return shapes


VERDICT_SHAPE: Final[dict[Verdict, str]] = {
    Verdict.MALICIOUS: "critical",
    Verdict.SUSPICIOUS: "medium",
    Verdict.BENIGN_HIDDEN: "benign-hidden",
    Verdict.CLEAN: "low",
}
DEFERRED: Final[str] = (
    "semantic injection in visible text, malware and macros (presence flagged, never analysed), "
    "image steganography, float-array carriers, acrostics"
)
DISCLOSURE: Final[str] = "https://github.com/SuhaasNv/paperglass/blob/main/SECURITY.md"


_LEVELS: Final[tuple[str, ...]] = tuple(level.value for level in Severity)


def _where(finding: Finding) -> str:
    return "document" if finding.page is None else f"page {finding.page}"


def _shape(level: str, size: int) -> str:
    return _shapes()[level].format(s=size)


def _lede(report: Report) -> str:
    confirmed = [f for f in report.findings if f.status.value == "confirmed"]
    count = (
        "One confirmed finding" if len(confirmed) == 1 else f"{len(confirmed)} confirmed findings"
    )
    if report.verdict is Verdict.MALICIOUS:
        top = confirmed[0].severity.value if confirmed else "critical"
        return (
            f"Hidden text found. {count} at {top} severity: text the model reads that the page "
            "does not show. The verdict follows from confirmed findings only."
        )
    if report.verdict is Verdict.SUSPICIOUS:
        return (
            f"Hidden text found. {count}, none phrased as an instruction. The verdict follows from "
            "confirmed findings only."
        )
    if report.verdict is Verdict.BENIGN_HIDDEN:
        return (
            "Hidden text found, all of it allowed by a public rule: alt text, ligature ActualText, "
            "an OCR layer on a scan. Nothing here is an attack."
        )
    return (
        "Nothing the model reads is missing from the page. Every extracted run left ink where the "
        "extractor said it would."
    )


def render_html(report: Report, *, file_name: str) -> str:
    """The report as one self-contained HTML document."""
    env = Environment(autoescape=select_autoescape(["html"]), undefined=StrictUndefined)
    template = env.from_string(_asset("report.html.j2"))
    unmatched = [
        f for f in report.findings if f.status.value == "confirmed" and f.extracted_text.strip()
    ]
    confirmed = sum(1 for f in report.findings if f.status.value == "confirmed")
    report_json = json.dumps(
        json.loads(report.to_json()), sort_keys=True, separators=(",", ":")
    ).replace("</", "<\\/")
    return template.render(
        report=report,
        file_name=file_name,
        css=_asset("report.css"),
        js=_asset("report.js"),
        shape=_shape,
        where=_where,
        lede=_lede(report),
        levels=_LEVELS,
        level_enum={level.value: level for level in Severity},
        verdict_shape=VERDICT_SHAPE[report.verdict],
        unmatched=unmatched,
        confirmed=confirmed,
        deferred=DEFERRED,
        disclosure=DISCLOSURE,
        report_json=report_json,
    )
