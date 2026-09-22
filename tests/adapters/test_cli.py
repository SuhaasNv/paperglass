"""The command line: exit codes, output modes, show targets."""

from __future__ import annotations

import json
import pathlib

import pytest
from typer.testing import CliRunner

from paperglass.adapters.cli import app
from paperglass.redkit.minipdf import simple

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"
runner = CliRunner()


def positive(technique_id: str) -> pathlib.Path:
    folder = (
        FIXTURES
        / ("text" if technique_id.startswith("text.") else technique_id.split(".", maxsplit=1)[0])
        / technique_id
    )
    return next(folder.glob("positive.*"))


def test_scan_malicious_exits_two_and_prints_evidence() -> None:
    result = runner.invoke(app, ["scan", str(positive("pdf.text.low_contrast")), "--tier", "fast"])
    assert result.exit_code == 2, result.output
    assert "MALICIOUS" in result.output
    assert "pdf.text.low_contrast" in result.output
    assert "reproduce: paperglass show --page 1 --instruction" in result.output
    assert "FILE" not in result.output


def test_scan_clean_exits_zero(tmp_path: pathlib.Path) -> None:
    file = tmp_path / "clean.pdf"
    file.write_bytes(simple("Hello"))
    result = runner.invoke(app, ["scan", str(file), "--tier", "fast"])
    assert result.exit_code == 0, result.output
    assert "CLEAN" in result.output


def test_scan_suspicious_exits_one(tmp_path: pathlib.Path) -> None:
    file = tmp_path / "broken.pdf"
    file.write_bytes(b"%PDF-1.7\ngarbage")
    result = runner.invoke(app, ["scan", str(file), "--tier", "fast"])
    assert result.exit_code == 1, result.output
    assert "parse failure" in result.output


def test_scan_json_and_out(tmp_path: pathlib.Path) -> None:
    out = tmp_path / "report.json"
    result = runner.invoke(
        app,
        ["scan", str(positive("pdf.render.mode")), "--tier", "fast", "--json", "--out", str(out)],
    )
    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["verdict"] == "malicious" and payload["schema_version"] == 2
    assert json.loads(out.read_text())["verdict"] == "malicious"


def test_directory_scan_returns_the_worst_code(tmp_path: pathlib.Path) -> None:
    (tmp_path / "a.pdf").write_bytes(simple("Hello"))
    (tmp_path / "b.pdf").write_bytes(positive("pdf.text.tiny").read_bytes())
    (tmp_path / "ignored.bin").write_bytes(b"\x00")
    result = runner.invoke(app, ["scan", str(tmp_path), "--tier", "fast"])
    assert result.exit_code == 2
    assert "a.pdf: CLEAN" in result.output and "b.pdf: MALICIOUS" in result.output


def test_bad_tier_and_bad_profile_exit_three(tmp_path: pathlib.Path) -> None:
    file = tmp_path / "x.pdf"
    file.write_bytes(simple("Hello"))
    assert runner.invoke(app, ["scan", str(file), "--tier", "warp"]).exit_code == 3
    assert runner.invoke(app, ["scan", str(file), "--profile", "nope"]).exit_code == 3


def test_fingerprint_table() -> None:
    result = runner.invoke(app, ["fingerprint", str(positive("pdf.text.low_contrast"))])
    assert result.exit_code == 0, result.output
    assert "fooled" in result.output and "pypdfium2" in result.output
    as_json = runner.invoke(app, ["fingerprint", str(positive("pdf.text.low_contrast")), "--json"])
    assert json.loads(as_json.output)["rows"][0]["technique_id"] == "pdf.text.low_contrast"


@pytest.mark.parametrize(
    ("technique_id", "args", "expect"),
    [
        ("pdf.render.mode", ["--page", "1", "--instruction", "9"], "Tr"),
        ("pdf.render.mode", ["--object", "4"], "object 4 0"),
        ("pdf.font.tounicode_mismatch", ["--page", "1", "--font", "F2"], "ToUnicode"),
        ("pdf.annotation.hidden", ["--page", "1", "--annotation", "0"], "/Contents"),
        ("pdf.metadata.payload", ["--info"], "Keywords"),
        ("pdf.active.content", ["--actions"], "/OpenAction"),
        ("pdf.text.covered", ["--page", "1", "--run", "1", "--ink"], "invisible"),
        ("text.unicode.invisible", ["--run", "1", "--codepoints"], "U+E0072"),
        (
            "docx.run.vanish",
            ["--part", "word/document.xml", "--paragraph", "1", "--run", "0"],
            "w:vanish",
        ),
    ],
)
def test_show_targets(technique_id: str, args: list[str], expect: str) -> None:
    result = runner.invoke(app, ["show", str(positive(technique_id)), *args])
    assert result.exit_code == 0, result.output
    assert expect in result.output


def test_show_without_a_target_exits_three() -> None:
    assert runner.invoke(app, ["show", str(positive("pdf.render.mode"))]).exit_code == 3


def test_version_and_profiles() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0 and "pdf.render.mode rule 1" in result.output
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0 and "default" in result.output


def test_scan_writes_the_html_report_and_report_command_does_too(tmp_path: pathlib.Path) -> None:
    target = tmp_path / "out.html"
    result = runner.invoke(
        app,
        ["scan", str(positive("pdf.text.low_contrast")), "--tier", "fast", "--report", str(target)],
    )
    assert result.exit_code == 2
    html = target.read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>") and "MALICIOUS" in html

    other = tmp_path / "report.html"
    result = runner.invoke(
        app,
        ["report", str(positive("pdf.text.low_contrast")), "--tier", "fast", "--out", str(other)],
    )
    assert result.exit_code == 2, result.output
    assert "MALICIOUS" in result.output and other.exists()

    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "a.txt").write_text("hello")
    (folder / "b.txt").write_text("world")
    result = runner.invoke(app, ["scan", str(folder), "--tier", "fast", "--report", str(target)])
    assert result.exit_code == 3
