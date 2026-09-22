"""The bytes behind a finding, for `paperglass show`. Runs inside the sandbox; prints nothing,
returns text the CLI prints. Nothing is executed."""

from __future__ import annotations

import io
import zipfile


def pdf_instruction(data: bytes, page: int, index: int) -> str:
    import pikepdf  # noqa: PLC0415

    with pikepdf.open(io.BytesIO(data)) as pdf:
        target = pdf.pages[page - 1]
        instructions = list(pikepdf.parse_content_stream(target))
        lo, hi = max(0, index - 3), min(len(instructions), index + 4)
        lines = []
        for position in range(lo, hi):
            ins = instructions[position]
            operands = " ".join(_operand(o) for o in ins.operands)
            marker = ">>" if position == index else "  "
            lines.append(f"{marker} {position:5d}  {operands} {ins.operator}".rstrip())
        contents = target.obj.get("/Contents")
        number = contents.objgen[0] if contents is not None and contents.is_indirect else "inline"
        return (
            f"page {page} content stream (object {number}), instructions {lo} to {hi - 1}:\n"
            + "\n".join(lines)
        )


def _operand(value: object) -> str:
    text = str(value)
    return text if len(text) <= 120 else text[:117] + "..."


def pdf_object(data: bytes, number: int) -> str:
    import pikepdf  # noqa: PLC0415

    with pikepdf.open(io.BytesIO(data)) as pdf:
        obj = pdf.get_object((number, 0))
        text = obj.unparse(resolved=False).decode("latin-1", "replace")
        if isinstance(obj, pikepdf.Stream):
            try:
                body = obj.read_bytes()[:2000].decode("latin-1", "replace")
            except Exception as exc:  # noqa: BLE001  # a broken stream is still shown
                body = f"<stream not readable: {type(exc).__name__}>"
            text += "\nstream (first 2000 bytes):\n" + body
        return f"object {number} 0:\n{text[:6000]}"


def pdf_font(data: bytes, page: int, resource: str) -> str:
    import pikepdf  # noqa: PLC0415

    with pikepdf.open(io.BytesIO(data)) as pdf:
        resources = pdf.pages[page - 1].Resources
        font = resources.get("/Font", pikepdf.Dictionary()).get(f"/{resource}")
        if font is None:
            return f"no font /{resource} on page {page}"
        text = font.unparse(resolved=False).decode("latin-1", "replace")
        out = f"font /{resource} on page {page}:\n{text[:3000]}"
        to_unicode = font.get("/ToUnicode")
        if to_unicode is not None:
            out += "\nToUnicode CMap:\n" + to_unicode.read_bytes()[:3000].decode(
                "latin-1", "replace"
            )
        return out


def pdf_annotation(data: bytes, page: int, index: int) -> str:
    import pikepdf  # noqa: PLC0415

    with pikepdf.open(io.BytesIO(data)) as pdf:
        annots = list(pdf.pages[page - 1].get("/Annots", []))
        if index >= len(annots):
            return f"page {page} has {len(annots)} annotations"
        text = annots[index].unparse(resolved=True).decode("latin-1", "replace")
        return f"annotation {index} on page {page}:\n{text[:3000]}"


def pdf_info(data: bytes) -> str:
    import pikepdf  # noqa: PLC0415

    with pikepdf.open(io.BytesIO(data)) as pdf:
        return "Info dictionary:\n" + "\n".join(
            f"{k}: {str(v)[:500]}" for k, v in dict(pdf.docinfo).items()
        )


def pdf_xmp(data: bytes) -> str:
    import pikepdf  # noqa: PLC0415

    with (
        pikepdf.open(io.BytesIO(data)) as pdf,
        pdf.open_metadata(set_pikepdf_as_editor=False, update_docinfo=False) as meta,
    ):
        return "XMP packet:\n" + str(meta)[:6000]


def pdf_actions(data: bytes) -> str:
    import pikepdf  # noqa: PLC0415

    with pikepdf.open(io.BytesIO(data)) as pdf:
        root = pdf.Root
        parts = []
        for key in ("/OpenAction", "/AA", "/Names"):
            if key in root:
                parts.append(
                    f"{key}: "
                    + root[key].unparse(resolved=False).decode("latin-1", "replace")[:1500]
                )
        return "document actions (never executed):\n" + ("\n".join(parts) or "none")


def pdf_embedded(data: bytes) -> str:
    import pikepdf  # noqa: PLC0415

    with pikepdf.open(io.BytesIO(data)) as pdf:
        names = pdf.Root.get("/Names")
        if names is None or "/EmbeddedFiles" not in names:
            return "no embedded files"
        tree = pikepdf.NameTree(names["/EmbeddedFiles"])
        return "embedded files (not opened):\n" + "\n".join(str(k) for k in tree)


def docx_part(data: bytes, part: str, paragraph: int | None, run: int | None) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if part not in archive.namelist():
            return f"no part {part}; parts: {', '.join(archive.namelist())}"
        xml = archive.read(part).decode("utf-8", "replace")
    if paragraph is None:
        return f"{part} (first 6000 characters):\n{xml[:6000]}"
    paragraphs = xml.split("<w:p>")
    if paragraph + 1 >= len(paragraphs):
        return f"{part} has {len(paragraphs) - 1} paragraphs"
    body = "<w:p>" + paragraphs[paragraph + 1].split("</w:p>")[0] + "</w:p>"
    if run is not None:
        runs = body.split("<w:r>")
        if run + 1 < len(runs):
            body = "<w:r>" + runs[run + 1].split("</w:r>")[0] + "</w:r>"
    return f"{part} paragraph {paragraph}{'' if run is None else f' run {run}'}:\n{body[:4000]}"


def text_run(data: bytes, run: int) -> str:
    lines = [line for line in data.decode("utf-8", "replace").splitlines() if line.strip()]
    if run >= len(lines):
        return f"{len(lines)} non-empty lines"
    line = lines[run]
    points = " ".join(f"U+{ord(c):04X}" for c in line)
    return f"run {run}:\n{line!r}\ncode points: {points}"
