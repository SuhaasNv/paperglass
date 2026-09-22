"""View C for PDF: walk every page's content stream with pikepdf and record, for each text
object, the state that decides whether a person can see it. Runs inside the sandbox.

Nothing here executes anything: JavaScript, actions and embedded files are noted, never
opened. Fonts are read as dictionaries; no font program runs.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from importlib.metadata import version as _version
from typing import Final

from paperglass.models import BBox
from paperglass.models.structure import (
    DocumentStructure,
    PageStructure,
    PdfAnnotation,
    PdfColour,
    PdfFontInfo,
    PdfMetadata,
    PdfTextObject,
)

_WIDTH_PER_CHAR_EM: Final = 0.5
"""Width estimate per character in em when no glyph widths are consulted; View B refines."""

_ANNOT_FLAG_HIDDEN: Final = 1 << 1
_ANNOT_FLAG_NOVIEW: Final = 1 << 5

_BFCHAR: Final = re.compile(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>")
_BFRANGE: Final = re.compile(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>")

Matrix = tuple[float, float, float, float, float, float]
IDENTITY: Final[Matrix] = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _multiply(a: Matrix, b: Matrix) -> Matrix:
    """a then b, PDF convention (row vectors)."""
    return (
        a[0] * b[0] + a[1] * b[2],
        a[0] * b[1] + a[1] * b[3],
        a[2] * b[0] + a[3] * b[2],
        a[2] * b[1] + a[3] * b[3],
        a[4] * b[0] + a[5] * b[2] + b[4],
        a[4] * b[1] + a[5] * b[3] + b[5],
    )


def _apply(m: Matrix, x: float, y: float) -> tuple[float, float]:
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def _scale(m: Matrix) -> float:
    """Approximate uniform scale of a matrix (geometric mean of the axis scales)."""
    sx = float((m[0] ** 2 + m[1] ** 2) ** 0.5)
    sy = float((m[2] ** 2 + m[3] ** 2) ** 0.5)
    return float((sx * sy) ** 0.5) if sx and sy else max(sx, sy)


def _num(value: object) -> float:
    """A content-stream operand as a float; pikepdf gives Decimal-like objects or ints."""
    return float(str(value))


def _raw(operand: object) -> bytes:
    """The bytes of a string operand (pikepdf.String exposes __bytes__)."""
    if isinstance(operand, bytes):
        return operand
    to_bytes = getattr(operand, "__bytes__", None)
    if callable(to_bytes):
        return bytes(to_bytes())
    return str(operand).encode("latin-1", "replace")


@dataclass
class _GraphicsState:
    ctm: Matrix = IDENTITY
    fill: PdfColour | None = None
    fill_alpha: float = 1.0
    blend_mode: str | None = None
    clip: BBox | None = None
    render_mode: int = 0
    font_resource: str | None = None
    font_size: float = 0.0
    char_spacing: float = 0.0
    word_spacing: float = 0.0
    horizontal_scale: float = 1.0
    leading: float = 0.0
    rise: float = 0.0

    def copy(self) -> _GraphicsState:
        return _GraphicsState(**self.__dict__)


@dataclass
class _TextState:
    tm: Matrix = IDENTITY
    tlm: Matrix = IDENTITY


@dataclass
class _MarkedContent:
    ocg: str | None = None
    actual_text: str | None = None


@dataclass
class _PageWalk:
    fonts: dict[str, PdfFontInfo]
    to_unicode: dict[str, dict[int, str]]
    ext_gstates: dict[str, dict[str, object]]
    ocg_names: dict[str, str]
    """Resource name (/OC1) to OCG display name."""
    ocgs_off: frozenset[str]
    gs_stack: list[_GraphicsState] = field(default_factory=list)
    gs: _GraphicsState = field(default_factory=_GraphicsState)
    text: _TextState = field(default_factory=_TextState)
    marked: list[_MarkedContent] = field(default_factory=list)
    pending_rect: BBox | None = None
    pending_clip: bool = False
    objects: list[PdfTextObject] = field(default_factory=list)


def pikepdf_structure(data: bytes) -> DocumentStructure:
    import pikepdf  # noqa: PLC0415  # parsers import inside the sandboxed call

    pdf = pikepdf.open(io.BytesIO(data))
    try:
        ocgs_all, ocgs_off = _optional_content(pdf)
        pages: list[PageStructure] = []
        for index, page in enumerate(pdf.pages):
            pages.append(_walk_page(pikepdf, page, index + 1, ocgs_off))
        root = pdf.Root
        names = root.get("/Names")
        has_js = bool(names is not None and "/JavaScript" in names) or _tree_has_key(
            root.get("/OpenAction"), "/JS"
        )
        embedded = _embedded_files(pikepdf, names)
        return DocumentStructure(
            parser_version=_version("pikepdf"),
            page_count=len(pdf.pages),
            pages=tuple(pages),
            ocgs_off=tuple(sorted(ocgs_off)),
            ocgs_all=tuple(sorted(ocgs_all)),
            metadata=_metadata(pdf),
            has_javascript=has_js,
            has_open_action="/OpenAction" in root,
            has_additional_actions="/AA" in root or any("/AA" in p.obj for p in pdf.pages),
            embedded_files=tuple(embedded),
            encrypted=pdf.is_encrypted,
        )
    finally:
        pdf.close()


def _optional_content(pdf: object) -> tuple[set[str], set[str]]:
    root = pdf.Root  # type: ignore[attr-defined]
    props = root.get("/OCProperties")
    if props is None:
        return set(), set()
    names_by_id: dict[tuple[int, int], str] = {}
    for ocg in props.get("/OCGs", []):
        names_by_id[ocg.objgen] = str(ocg.get("/Name", "")) or f"ocg-{ocg.objgen[0]}"
    default = props.get("/D")
    off: set[str] = set()
    if default is not None:
        for ocg in default.get("/OFF", []):
            off.add(names_by_id.get(ocg.objgen, f"ocg-{ocg.objgen[0]}"))
    return set(names_by_id.values()), off


def _tree_has_key(obj: object, key: str) -> bool:
    try:
        return obj is not None and key in obj  # type: ignore[operator]
    except TypeError:
        return False


def _embedded_files(pikepdf: object, names: object) -> list[str]:
    if names is None or "/EmbeddedFiles" not in names:  # type: ignore[operator]
        return []
    found: list[str] = []
    try:
        tree = pikepdf.NameTree(names["/EmbeddedFiles"])  # type: ignore[attr-defined, index]
        found.extend(str(key) for key in tree)
    except (KeyError, TypeError, ValueError):
        found.append("unreadable")
    return found


def _metadata(pdf: object) -> PdfMetadata:
    info: dict[str, str] = {}
    docinfo = getattr(pdf, "docinfo", None)
    if docinfo is not None:
        for key, value in dict(docinfo).items():
            info[str(key).lstrip("/")] = str(value)[:2000]
    xmp_text: str | None = None
    xmp_length = 0
    try:
        with pdf.open_metadata(set_pikepdf_as_editor=False, update_docinfo=False) as meta:  # type: ignore[attr-defined]
            xmp_text = str(meta)
            xmp_length = len(xmp_text)
    except Exception:  # noqa: BLE001  # unreadable XMP is a fact to report, not a crash
        xmp_text = None
    return PdfMetadata(
        info=info, xmp_length=xmp_length, xmp_text=xmp_text[:20000] if xmp_text else None
    )


def _fonts(page: object) -> tuple[dict[str, PdfFontInfo], dict[str, dict[int, str]]]:
    fonts: dict[str, PdfFontInfo] = {}
    cmaps: dict[str, dict[int, str]] = {}
    resources = page.get("/Resources")  # type: ignore[attr-defined]
    font_dict = resources.get("/Font") if resources is not None else None
    if font_dict is None:
        return fonts, cmaps
    for name, font in font_dict.items():
        resource = str(name).lstrip("/")
        subtype = str(font.get("/Subtype", "")).lstrip("/") or None
        descriptor = font.get("/FontDescriptor")
        if subtype == "Type0":
            descendants = font.get("/DescendantFonts")
            if descendants:
                descriptor = descendants[0].get("/FontDescriptor")
        embedded = bool(
            descriptor is not None
            and any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))
        )
        to_unicode = font.get("/ToUnicode")
        encoding = font.get("/Encoding")
        fonts[resource] = PdfFontInfo(
            resource=resource,
            base_font=str(font.get("/BaseFont", "")).lstrip("/") or None,
            subtype=subtype,
            has_to_unicode=to_unicode is not None,
            embedded=embedded,
            is_type3=subtype == "Type3",
            is_type0=subtype == "Type0",
            encoding=str(encoding).lstrip("/")
            if encoding is not None and not _is_dictionary(encoding)
            else None,
            object_number=font.objgen[0] if font.is_indirect else None,
        )
        if to_unicode is not None:
            try:
                cmaps[resource] = _parse_to_unicode(to_unicode.read_bytes())
            except Exception:  # noqa: BLE001  # a broken CMap is a finding for US-014, not a crash
                cmaps[resource] = {}
    return fonts, cmaps


def _parse_to_unicode(data: bytes) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for section in re.finditer(rb"beginbfchar(.*?)endbfchar", data, re.S):
        for src, dst in _BFCHAR.findall(section.group(1)):
            mapping[int(src, 16)] = _hex_to_text(dst)
    for section in re.finditer(rb"beginbfrange(.*?)endbfrange", data, re.S):
        for lo, hi, dst in _BFRANGE.findall(section.group(1)):
            start, end = int(lo, 16), int(hi, 16)
            base = _hex_to_text(dst)
            if len(base) == 1 and end - start < 65536:
                for code in range(start, end + 1):
                    mapping[code] = chr(ord(base) + code - start)
    return mapping


def _hex_to_text(hexed: bytes) -> str:
    raw = bytes.fromhex(hexed.decode("ascii"))
    if len(raw) % 2 == 0:
        try:
            return raw.decode("utf-16-be")
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1")


def _decode(raw: bytes, walk: _PageWalk) -> str:
    """Best-effort text for a string operand: ToUnicode when present, else single-byte latin-1."""
    resource = walk.gs.font_resource
    cmap = walk.to_unicode.get(resource or "")
    font = walk.fonts.get(resource or "")
    if cmap:
        width = 2 if font is not None and font.is_type0 else 1
        out: list[str] = []
        for position in range(0, len(raw), width):
            code = int.from_bytes(raw[position : position + width], "big")
            out.append(cmap.get(code, "�"))
        return "".join(out)
    if font is not None and font.is_type0:
        return "".join(
            chr(int.from_bytes(raw[i : i + 2], "big")) for i in range(0, len(raw) - 1, 2)
        )
    return raw.decode("latin-1")


def _ext_gstates(page: object) -> dict[str, dict[str, object]]:
    resources = page.get("/Resources")  # type: ignore[attr-defined]
    states = resources.get("/ExtGState") if resources is not None else None
    if states is None:
        return {}
    out: dict[str, dict[str, object]] = {}
    for name, state in states.items():
        entry: dict[str, object] = {}
        if "/ca" in state:
            entry["ca"] = _num(state["/ca"])
        if "/CA" in state:
            entry["CA"] = _num(state["/CA"])
        if "/BM" in state:
            entry["BM"] = str(state["/BM"]).lstrip("/")
        out[str(name).lstrip("/")] = entry
    return out


def _ocg_resources(page: object, ocgs_off: frozenset[str]) -> dict[str, str]:
    resources = page.get("/Resources")  # type: ignore[attr-defined]
    props = resources.get("/Properties") if resources is not None else None
    if props is None:
        return {}
    out: dict[str, str] = {}
    for name, obj in props.items():
        try:
            display = str(obj.get("/Name", "")) or f"ocg-{obj.objgen[0]}"
        except (AttributeError, TypeError):
            display = str(name).lstrip("/")
        out[str(name).lstrip("/")] = display
    return out


def _walk_page(pikepdf: object, page: object, number: int, ocgs_off: set[str]) -> PageStructure:
    media = [float(v) for v in page.get("/MediaBox", [0, 0, 612, 792])]  # type: ignore[attr-defined]
    width = abs(media[2] - media[0]) or 612.0
    height = abs(media[3] - media[1]) or 792.0
    crop = page.get("/CropBox")  # type: ignore[attr-defined]
    crop_box = None
    if crop is not None:
        values = [float(v) for v in crop]
        crop_box = BBox(
            x0=min(values[0], values[2]),
            y0=min(values[1], values[3]),
            x1=max(values[0], values[2]),
            y1=max(values[1], values[3]),
        )
    fonts, cmaps = _fonts(page)
    walk = _PageWalk(
        fonts=fonts,
        to_unicode=cmaps,
        ext_gstates=_ext_gstates(page),
        ocg_names=_ocg_resources(page, frozenset(ocgs_off)),
        ocgs_off=frozenset(ocgs_off),
    )
    note: str | None = None
    try:
        instructions = pikepdf.parse_content_stream(page)  # type: ignore[attr-defined]
    except Exception as exc:  # noqa: BLE001  # an unparseable stream is reported on the page
        instructions = []
        note = f"content stream not parsed: {type(exc).__name__}"
    for index, instruction in enumerate(instructions):
        try:
            _step(walk, index, str(instruction.operator), list(instruction.operands))
        except Exception as exc:  # noqa: BLE001  # one bad operand must not hide the rest of the page
            note = note or f"instruction {index} skipped: {type(exc).__name__}"
    contents = page.obj.get("/Contents")  # type: ignore[attr-defined]
    content_object = None
    if contents is not None and getattr(contents, "is_indirect", False):
        content_object = contents.objgen[0]
    return PageStructure(
        number=number,
        width=width,
        height=height,
        crop_box=crop_box,
        content_object=content_object,
        text_objects=tuple(walk.objects),
        fonts=tuple(fonts.values()),
        annotations=tuple(_annotations(page)),
        parse_note=note,
    )


def _annotations(page: object) -> list[PdfAnnotation]:
    out: list[PdfAnnotation] = []
    for annot in page.get("/Annots", []):  # type: ignore[attr-defined]
        try:
            flags = int(annot.get("/F", 0))
            rect_values = annot.get("/Rect")
            rect = None
            if rect_values is not None:
                r = [float(v) for v in rect_values]
                rect = BBox(
                    x0=min(r[0], r[2]), y0=min(r[1], r[3]), x1=max(r[0], r[2]), y1=max(r[1], r[3])
                )
            value = annot.get("/V")
            action = annot.get("/A")
            out.append(
                PdfAnnotation(
                    subtype=str(annot.get("/Subtype", "")).lstrip("/") or None,
                    hidden=bool(flags & _ANNOT_FLAG_HIDDEN),
                    no_view=bool(flags & _ANNOT_FLAG_NOVIEW),
                    contents=str(annot["/Contents"])[:2000] if "/Contents" in annot else None,
                    field_value=str(value)[:2000] if value is not None else None,
                    rect=rect,
                    has_javascript=bool(action is not None and "/JS" in action),
                    object_number=annot.objgen[0] if annot.is_indirect else None,
                )
            )
        except Exception:  # noqa: BLE001  # a malformed annotation is still an annotation
            out.append(PdfAnnotation(subtype="unreadable"))
    return out


def _colour(operator: str, operands: list[object]) -> PdfColour:
    values = tuple(_num(v) for v in operands if _is_number(v))
    grey: float | None
    if operator in ("g",) and len(values) == 1:
        grey = values[0]
    elif operator in ("rg",) and len(values) == 3:
        grey = 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]
    elif operator in ("k",) and len(values) == 4:
        c, m, y, k = values
        grey = 1.0 - min(
            1.0, 0.2126 * min(1.0, c + k) + 0.7152 * min(1.0, m + k) + 0.0722 * min(1.0, y + k)
        )
    elif operator in ("sc", "scn") and len(values) in (1, 3, 4):
        return _colour({1: "g", 3: "rg", 4: "k"}[len(values)], list(values))
    else:
        grey = None
    return PdfColour(
        operator=operator,
        components=values,
        grey=grey if grey is None else max(0.0, min(1.0, grey)),
    )


def _is_dictionary(value: object) -> bool:
    return isinstance(value, dict) or getattr(value, "_type_name", None) == "dictionary"


def _is_number(value: object) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int | float):
        return True
    try:
        float(str(value))
    except ValueError:
        return False
    return not _is_dictionary(value) and not str(value).startswith("/")


def _matrix(operands: list[object]) -> Matrix:
    a, b, c, d, e, f = (_num(v) for v in operands[:6])
    return (a, b, c, d, e, f)


def _step(walk: _PageWalk, index: int, op: str, operands: list[object]) -> None:  # noqa: PLR0912, PLR0915  # a content-stream interpreter is one big switch
    gs = walk.gs
    if op == "q":
        walk.gs_stack.append(gs.copy())
    elif op == "Q":
        if walk.gs_stack:
            walk.gs = walk.gs_stack.pop()
    elif op == "cm" and len(operands) == 6:
        gs.ctm = _multiply(_matrix(operands), gs.ctm)
    elif op == "gs" and operands:
        state = walk.ext_gstates.get(str(operands[0]).lstrip("/"), {})
        if "ca" in state:
            gs.fill_alpha = _num(state["ca"])
        if "BM" in state:
            gs.blend_mode = str(state["BM"])
    elif op in ("g", "rg", "k", "sc", "scn"):
        gs.fill = _colour(op, operands)
    elif op == "re" and len(operands) == 4:
        x, y, w, h = (_num(v) for v in operands)
        p0 = _apply(gs.ctm, x, y)
        p1 = _apply(gs.ctm, x + w, y + h)
        walk.pending_rect = BBox(
            x0=min(p0[0], p1[0]), y0=min(p0[1], p1[1]), x1=max(p0[0], p1[0]), y1=max(p0[1], p1[1])
        )
    elif op in ("W", "W*"):
        walk.pending_clip = True
    elif op in ("n", "f", "F", "f*", "B", "B*", "b", "b*", "S", "s"):
        if walk.pending_clip and walk.pending_rect is not None:
            gs.clip = _intersect(gs.clip, walk.pending_rect)
        walk.pending_clip = False
        walk.pending_rect = None
    elif op == "BT":
        walk.text = _TextState()
    elif op == "Tf" and len(operands) == 2:
        gs.font_resource = str(operands[0]).lstrip("/")
        gs.font_size = _num(operands[1])
    elif op == "Tr" and operands:
        gs.render_mode = int(_num(operands[0]))
    elif op == "Tc" and operands:
        gs.char_spacing = _num(operands[0])
    elif op == "Tw" and operands:
        gs.word_spacing = _num(operands[0])
    elif op == "Tz" and operands:
        gs.horizontal_scale = _num(operands[0]) / 100.0
    elif op == "TL" and operands:
        gs.leading = _num(operands[0])
    elif op == "Ts" and operands:
        gs.rise = _num(operands[0])
    elif op == "Tm" and len(operands) == 6:
        walk.text.tlm = _matrix(operands)
        walk.text.tm = walk.text.tlm
    elif op in ("Td", "TD") and len(operands) == 2:
        tx, ty = _num(operands[0]), _num(operands[1])
        if op == "TD":
            gs.leading = -ty
        walk.text.tlm = _multiply((1, 0, 0, 1, tx, ty), walk.text.tlm)
        walk.text.tm = walk.text.tlm
    elif op == "T*":
        walk.text.tlm = _multiply((1, 0, 0, 1, 0, -gs.leading), walk.text.tlm)
        walk.text.tm = walk.text.tlm
    elif op in ("Tj", "'", '"'):
        if op != "Tj":
            walk.text.tlm = _multiply((1, 0, 0, 1, 0, -gs.leading), walk.text.tlm)
            walk.text.tm = walk.text.tlm
        if operands:
            _show(walk, index, operands[-1])
    elif op == "TJ" and operands:
        array = operands[0]
        for element in array:  # type: ignore[attr-defined]
            if _is_number(element):
                shift = -_num(element) / 1000.0 * gs.font_size * gs.horizontal_scale
                walk.text.tm = _multiply((1, 0, 0, 1, shift, 0), walk.text.tm)
            else:
                _show(walk, index, element)
    elif op == "BDC" and len(operands) == 2:
        tag = str(operands[0]).lstrip("/")
        props = operands[1]
        marked = _MarkedContent()
        if tag == "OC":
            name = None if _is_dictionary(props) else str(props).lstrip("/")
            marked.ocg = walk.ocg_names.get(name or "", name)
        elif _is_dictionary(props) and "/ActualText" in props:  # type: ignore[operator]
            marked.actual_text = str(props["/ActualText"])  # type: ignore[index]
        walk.marked.append(marked)
    elif op == "BMC":
        walk.marked.append(_MarkedContent())
    elif op == "EMC" and walk.marked:
        walk.marked.pop()


def _intersect(a: BBox | None, b: BBox) -> BBox:
    if a is None:
        return b
    x0, y0 = max(a.x0, b.x0), max(a.y0, b.y0)
    x1, y1 = min(a.x1, b.x1), min(a.y1, b.y1)
    if x1 < x0 or y1 < y0:
        return BBox(x0=x0, y0=y0, x1=x0, y1=y0)
    return BBox(x0=x0, y0=y0, x1=x1, y1=y1)


def _show(walk: _PageWalk, index: int, operand: object) -> None:
    raw = _raw(operand)
    text = _decode(raw, walk)
    gs = walk.gs
    full = _multiply(walk.text.tm, gs.ctm)
    origin = _apply(full, 0.0, gs.rise)
    size = gs.font_size * _scale(full)
    advance = (
        len(text) * _WIDTH_PER_CHAR_EM * gs.font_size + gs.char_spacing * len(text)
    ) * gs.horizontal_scale
    end = _apply(full, advance, gs.rise + gs.font_size)
    bbox = (
        BBox(
            x0=min(origin[0], end[0]),
            y0=min(origin[1], end[1]),
            x1=max(origin[0], end[0]),
            y1=max(origin[1], end[1]),
        )
        if size > 0
        else None
    )
    ocg = next((m.ocg for m in reversed(walk.marked) if m.ocg), None)
    actual = next((m.actual_text for m in reversed(walk.marked) if m.actual_text is not None), None)
    walk.objects.append(
        PdfTextObject(
            instruction=index,
            text=text,
            raw_bytes=len(raw),
            font_resource=gs.font_resource,
            font_size=size if size > 0 else None,
            render_mode=gs.render_mode,
            fill=gs.fill,
            fill_alpha=gs.fill_alpha,
            blend_mode=gs.blend_mode,
            origin=origin,
            bbox=bbox,
            clip=gs.clip,
            ocg=ocg,
            ocg_hidden=bool(ocg and ocg in walk.ocgs_off),
            actual_text=actual,
            marked_content_depth=len(walk.marked),
        )
    )
    walk.text.tm = _multiply((1, 0, 0, 1, advance, 0), walk.text.tm)
