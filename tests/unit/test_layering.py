"""The layering rule from docs/03-architecture/ARCHITECTURE.md, enforced.

adapters -> engine -> views / detectors -> parsers

A package may import from itself, from the packages below it, and from the
shared data packages (report models, profiles). Nothing below adapters may
import a network client.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "paperglass"

# Which top-level paperglass packages each package may import from.
ALLOWED: dict[str, frozenset[str]] = {
    "adapters": frozenset(
        {
            "adapters",
            "engine",
            "views",
            "detectors",
            "report",
            "profiles",
            "ingest",
            "bench",
            "redkit",
        }
    ),
    "engine": frozenset({"engine", "views", "detectors", "profiles", "ingest"}),
    "views": frozenset({"views", "parsers", "ingest", "profiles"}),
    "detectors": frozenset({"detectors", "views", "parsers", "profiles"}),
    "parsers": frozenset({"parsers"}),
    "ingest": frozenset({"ingest", "parsers"}),
    "report": frozenset({"report", "profiles"}),
    "bench": frozenset({"bench", "adapters", "engine", "report", "profiles"}),
    "redkit": frozenset({"redkit"}),
    "profiles": frozenset({"profiles"}),
}

# Modules that talk to the network. Importable only from adapters.
NETWORK_MODULES = frozenset(
    {"httpx", "requests", "urllib.request", "aiohttp", "socket", "huggingface_hub"}
)


def _package_of(path: Path) -> str:
    return path.relative_to(SRC).parts[0] if path.parent != SRC else "__root__"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module)
    return found


def _paperglass_package(module: str) -> str | None:
    parts = module.split(".")
    if parts[0] != "paperglass" or len(parts) == 1:
        return None
    return parts[1]


def test_every_package_is_listed() -> None:
    packages = {p.name for p in SRC.iterdir() if p.is_dir() and (p / "__init__.py").exists()}
    assert packages == set(ALLOWED), f"add new packages to ALLOWED: {packages ^ set(ALLOWED)}"


def test_no_forbidden_import_edges() -> None:
    violations: list[str] = []
    for path in SRC.rglob("*.py"):
        package = _package_of(path)
        if package == "__root__":
            continue
        for module in _imports(path):
            target = _paperglass_package(module)
            if target is not None and target not in ALLOWED[package]:
                violations.append(f"{path.relative_to(SRC)} imports paperglass.{target}")
    assert not violations, "\n".join(violations)


def test_only_adapters_import_network_clients() -> None:
    violations: list[str] = []
    for path in SRC.rglob("*.py"):
        package = _package_of(path)
        if package == "adapters":
            continue
        for module in _imports(path):
            root = module.split(".")[0]
            if module in NETWORK_MODULES or root in NETWORK_MODULES:
                violations.append(f"{path.relative_to(SRC)} imports {module}")
    assert not violations, "\n".join(violations)
