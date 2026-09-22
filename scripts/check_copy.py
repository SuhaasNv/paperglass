"""Fail on copy that the project rules forbid in repository documents.

Rules: no em dashes, no emoji, the word "assessment" nowhere. Run from the repository root:
    python scripts/check_copy.py
"""

from __future__ import annotations

import pathlib
import re
import sys

EM_DASH = "—"
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")
FORBIDDEN_WORD = re.compile(r"assessment", re.IGNORECASE)
SKIP_DIRS = {".git", ".venv", "node_modules", "bench", ".ruff_cache", ".mypy_cache"}


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    problems: list[str] = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            rel = path.relative_to(root)
            if EM_DASH in line:
                problems.append(f"{rel}:{number}: em dash")
            if EMOJI.search(line):
                problems.append(f"{rel}:{number}: emoji")
            if FORBIDDEN_WORD.search(line):
                problems.append(f"{rel}:{number}: forbidden word")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
