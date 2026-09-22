"""The paperglass command line.

Commands land story by story; see docs/04-report-design/CLI_DESIGN.md.
"""

from __future__ import annotations

import typer

from paperglass import __version__

app = typer.Typer(
    name="paperglass",
    help="See exactly what the model reads.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main() -> None:
    """See exactly what the model reads."""


@app.command()
def version() -> None:
    """Print the tool version and, once they exist, the rule versions."""
    typer.echo(f"paperglass {__version__}")


if __name__ == "__main__":  # pragma: no cover
    app()
