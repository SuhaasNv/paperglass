"""Recursion guard for object references, XObjects, nested fields and nested parts."""

from __future__ import annotations

from paperglass.models import ParseFailure


class DepthExceededError(Exception):
    """Raised inside a probe when nesting passes the limit; the sandbox turns it into a failure."""


class DepthGuard:
    """Count nesting; raise DepthExceededError past the cap. Use as `with guard: ...` per level."""

    def __init__(self, max_depth: int) -> None:
        self.max_depth = max_depth
        self.depth = 0

    def __enter__(self) -> DepthGuard:
        if self.depth >= self.max_depth:
            msg = f"nesting deeper than {self.max_depth}"
            raise DepthExceededError(msg)
        self.depth += 1
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.depth -= 1

    @staticmethod
    def failure(parser: str, *, stage: int = 0) -> ParseFailure:
        return ParseFailure(stage=stage, parser=parser, reason="recursion", message="depth cap")
