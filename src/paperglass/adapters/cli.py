"""The paperglass command line (docs/04-report-design/CLI_DESIGN.md).

Exit codes: 0 clean or benign-hidden, 1 suspicious, 2 malicious, 3 error. A directory scan
returns the highest code among its files. No telemetry; no network unless asked.
"""

from __future__ import annotations

import json
import pathlib
from typing import Annotated

import typer

from paperglass import __version__

app = typer.Typer(
    name="paperglass",
    help="See exactly what the model reads.",
    no_args_is_help=True,
    add_completion=False,
)

EXIT = {"clean": 0, "benign-hidden": 0, "suspicious": 1, "malicious": 2}
SUPPORTED = {".pdf", ".docx", ".txt", ".md", ".markdown"}
SHAPES = {
    "critical": "[octagon]",
    "high": "[triangle]",
    "medium": "[diamond]",
    "low": "[circle]",
    "info": "[ring]",
    "benign-hidden": "[square]",
}


@app.callback()
def main() -> None:
    """See exactly what the model reads."""


@app.command()
def version() -> None:
    """Print the tool version and the rule versions."""
    from paperglass.detectors import REGISTRY  # noqa: PLC0415  # keep `version` fast

    typer.echo(f"paperglass {__version__}")
    for technique_id, rule_version in sorted(REGISTRY.rule_versions().items()):
        typer.echo(f"  {technique_id} rule {rule_version}")


@app.command()
def profiles() -> None:
    """List the profiles and where their thresholds live."""
    from paperglass.engine import load_profile, profile_names  # noqa: PLC0415

    for name in profile_names():
        profile = load_profile(name)
        thresholds = profile.thresholds
        typer.echo(
            f"{name} (version {profile.version}): contrast {thresholds.contrast:.4f}, "
            f"tiny {thresholds.tiny_pt} pt, alpha {thresholds.alpha}, "
            f"ocr hidden below {thresholds.ocr_agreement_hidden}, benign above {thresholds.ocr_agreement_benign}"
        )


def _read(path: pathlib.Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        typer.echo(f"error: cannot read {path}: {exc}", err=True)
        raise typer.Exit(3) from exc


def _files(target: pathlib.Path) -> list[pathlib.Path]:
    if target.is_dir():
        return sorted(p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
    return [target]


@app.command()
def scan(  # noqa: PLR0913  # one option per documented flag
    path: Annotated[
        pathlib.Path, typer.Argument(exists=True, readable=True, help="A file or a directory.")
    ],
    tier: Annotated[str, typer.Option(help="fast, standard or deep.")] = "standard",
    profile: Annotated[
        str, typer.Option(help="default, or a profile from `paperglass profiles`.")
    ] = "default",
    extractor: Annotated[str | None, typer.Option(help="Force a View A backend.")] = None,
    redact: Annotated[
        bool, typer.Option("--redact", help="Shorten extracted text; drop crops outside findings.")
    ] = False,
    as_json: Annotated[bool, typer.Option("--json", help="Print the report as JSON.")] = False,
    output: Annotated[
        pathlib.Path | None, typer.Option("--out", help="Write the JSON report here.")
    ] = None,
) -> None:
    """Scan a document and print the verdict with evidence."""
    from paperglass.engine import scan_bytes  # noqa: PLC0415
    from paperglass.models import Tier  # noqa: PLC0415

    try:
        tier_value = Tier(tier)
    except ValueError as exc:
        typer.echo(f"error: unknown tier {tier!r}; use fast, standard or deep", err=True)
        raise typer.Exit(3) from exc
    worst = 0
    reports = []
    for file in _files(path):
        try:
            report = scan_bytes(
                _read(file), tier=tier_value, profile=profile, extractor=extractor, redact=redact
            )
        except KeyError as exc:
            typer.echo(f"error: {exc.args[0]}", err=True)
            raise typer.Exit(3) from exc
        reports.append((file, report))
        worst = max(worst, EXIT[report.verdict.value])
    if as_json:
        payload = [json.loads(r.to_json()) for _, r in reports]
        typer.echo(
            json.dumps(payload[0] if len(payload) == 1 else payload, indent=2, sort_keys=True)
        )
    else:
        for file, report in reports:
            _print_report(file, report)
    if output is not None:
        output.write_text(
            reports[0][1].to_json()
            if len(reports) == 1
            else json.dumps(
                [json.loads(r.to_json()) for _, r in reports], indent=2, sort_keys=True
            ),
            encoding="utf-8",
        )
    raise typer.Exit(worst)


def _print_report(file: pathlib.Path, report: object) -> None:
    from paperglass.models import Report  # noqa: PLC0415

    assert isinstance(report, Report)
    counts = ", ".join(f"{level.value} {n}" for level, n in report.severity_counts.items() if n)
    typer.echo(f"{file}: {report.verdict.value.upper()} {SHAPES.get(report.verdict.value, '')}")
    typer.echo(
        f"  {report.input_type} via {report.extractor}, tier {report.tier.value}, profile {report.profile}, "
        f"pages {report.pages_render_verified} of {report.page_count} render-verified"
        + (f" at {report.dpi} dpi" if report.dpi else "")
        + (f"; counts: {counts}" if counts else "")
    )
    for failure in report.parse_failures:
        typer.echo(f"  parse failure: {failure.parser} {failure.reason} {failure.message}".rstrip())
    for finding in report.findings:
        where = f"page {finding.page}" if finding.page else "document"
        typer.echo(
            f"  {SHAPES[finding.severity.value]} {finding.severity.value} {finding.status.value} "
            f"{finding.technique_id} ({where}, confidence {finding.confidence:.2f})"
        )
        typer.echo(f"      {finding.why_hidden}")
        typer.echo(f"      mechanism: {finding.mechanism}")
        typer.echo(f"      reproduce: {finding.reproduce.replace('FILE', str(file))}")
        if finding.extracted_text.strip():
            preview = finding.extracted_text.replace("\n", " ")
            typer.echo(f"      text: {preview[:200]}{'...' if len(preview) > 200 else ''}")


@app.command()
def fingerprint(
    path: Annotated[pathlib.Path, typer.Argument(exists=True, readable=True, dir_okay=False)],
    extractors: Annotated[str | None, typer.Option(help="Comma-separated backend names.")] = None,
    profile: Annotated[str, typer.Option()] = "default",
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Which installed extractors hand each hidden run to a model."""
    from paperglass.engine import fingerprint_bytes  # noqa: PLC0415

    chosen = tuple(e.strip() for e in extractors.split(",")) if extractors else None
    result = fingerprint_bytes(_read(path), profile=profile, extractors=chosen)
    if as_json:
        typer.echo(result.model_dump_json(indent=2))
        raise typer.Exit(0)
    names = list(result.extractors)
    typer.echo(
        f"{path}: {len(result.rows)} hidden run(s); extractors: "
        + ", ".join(f"{n} {v}" for n, v in result.extractors.items())
    )
    if not result.rows:
        raise typer.Exit(0)
    header = f"{'finding':<10}{'technique':<30}{'page':<6}" + "".join(f"{n:<14}" for n in names)
    typer.echo(header)
    for row in result.rows:
        cells = {v.extractor: v for v in row.extractors}
        line = f"{row.finding_id:<10}{row.technique_id:<30}{row.page or '-'!s:<6}"
        for name in names:
            verdict = cells.get(name)
            mark = (
                "failed"
                if verdict is None or verdict.returns_hidden_text is None
                else ("fooled" if verdict.returns_hidden_text else "clean")
            )
            line += f"{mark:<14}"
        typer.echo(line)
        typer.echo(f"{'':<10}{row.text_preview}")
    fooled = result.fooled
    typer.echo("fooled by: " + ", ".join(f"{n} {fooled[n]}/{len(result.rows)}" for n in names))
    raise typer.Exit(0)


@app.command()
def show(  # noqa: PLR0913, PLR0912  # one option per locator in a reproduce command
    path: Annotated[pathlib.Path, typer.Argument(exists=True, readable=True, dir_okay=False)],
    page: Annotated[int | None, typer.Option()] = None,
    instruction: Annotated[int | None, typer.Option()] = None,
    object_number: Annotated[int | None, typer.Option("--object")] = None,
    font: Annotated[str | None, typer.Option()] = None,
    annotation: Annotated[int | None, typer.Option()] = None,
    run: Annotated[int | None, typer.Option()] = None,
    part: Annotated[str | None, typer.Option()] = None,
    paragraph: Annotated[int | None, typer.Option()] = None,
    info: Annotated[bool, typer.Option("--info")] = False,
    xmp: Annotated[bool, typer.Option("--xmp")] = False,
    actions: Annotated[bool, typer.Option("--actions")] = False,
    embedded: Annotated[bool, typer.Option("--embedded")] = False,
    codepoints: Annotated[bool, typer.Option("--codepoints")] = False,
    ink: Annotated[bool, typer.Option("--ink")] = False,
) -> None:
    """Print the bytes behind a finding: the reproduce command's target."""
    from paperglass.ingest import Limits  # noqa: PLC0415
    from paperglass.views.show import show as show_target  # noqa: PLC0415

    data = _read(path)
    target: str
    args: tuple[object, ...]
    if part is not None:
        target, args = "part", (data, part, paragraph, run)
    elif codepoints and run is not None:
        target, args = "text_run", (data, run)
    elif ink and run is not None and page is not None:
        _show_ink(data, page, run)
        raise typer.Exit(0)
    elif info:
        target, args = "info", (data,)
    elif xmp:
        target, args = "xmp", (data,)
    elif actions:
        target, args = "actions", (data,)
    elif embedded:
        target, args = "embedded", (data,)
    elif font is not None and page is not None:
        target, args = "font", (data, page, font)
    elif annotation is not None and page is not None:
        target, args = "annotation", (data, page, annotation)
    elif instruction is not None and page is not None:
        target, args = "instruction", (data, page, instruction)
    elif object_number is not None:
        target, args = "object", (data, object_number)
    else:
        typer.echo(
            "error: say what to show (--page N --instruction I, --object N, --font F, ...)",
            err=True,
        )
        raise typer.Exit(3)
    text, failure = show_target(target, args, limits=Limits.from_env())
    if text is None:
        typer.echo(f"error: {failure.message if failure else 'no output'}", err=True)
        raise typer.Exit(3)
    typer.echo(text)
    raise typer.Exit(0)


def _show_ink(data: bytes, page: int, run: int) -> None:
    from paperglass.ingest import Limits  # noqa: PLC0415
    from paperglass.views.pages import build_pages  # noqa: PLC0415
    from paperglass.views.render import choose_dpi, ink_check, render_document  # noqa: PLC0415

    limits = Limits.from_env()
    stage0 = build_pages(data, limits=limits)
    if page > len(stage0.pages):
        typer.echo(f"error: {len(stage0.pages)} pages", err=True)
        raise typer.Exit(3)
    runs = stage0.pages[page - 1].runs
    if run >= len(runs) or runs[run].bbox is None:
        typer.echo(f"error: page {page} has {len(runs)} runs with positions", err=True)
        raise typer.Exit(3)
    dpi = choose_dpi(stage0.structure)
    rendered = render_document(data, limits=limits, numbers=(page,), dpi=dpi)
    if not rendered.rasters:
        typer.echo(f"error: render failed: {rendered.failure}", err=True)
        raise typer.Exit(3)
    bbox = runs[run].bbox
    assert bbox is not None
    result = ink_check(rendered.rasters[0], bbox)
    typer.echo(
        f"run {run} on page {page}: {runs[run].text!r}\nbbox ({bbox.x0:.1f}, {bbox.y0:.1f}, {bbox.x1:.1f}, {bbox.y1:.1f}) at {dpi} dpi\n"
        f"ink fraction {result.ink_fraction:.4f}, contrast {result.contrast:.3f}, background {result.background:.3f}, "
        f"pixels {result.pixels}: {result.classification}"
    )


if __name__ == "__main__":  # pragma: no cover
    app()
