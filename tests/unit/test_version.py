"""paperglass version prints the installed version."""

from __future__ import annotations

from typer.testing import CliRunner

from paperglass import __version__
from paperglass.adapters.cli import app


def test_version_command_prints_the_package_version() -> None:
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.splitlines()[0] == f"paperglass {__version__}"


def test_version_is_pep440_like() -> None:
    assert __version__[0].isdigit()
