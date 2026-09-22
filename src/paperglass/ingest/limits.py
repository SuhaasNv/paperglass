"""Sandbox budgets. Defaults per docs/03-architecture/SANDBOX.md; env overrides per .env.example."""

from __future__ import annotations

import os
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

ENV_PREFIX: Final = "PAPERGLASS_"


class Limits(BaseModel):
    """Every cap the sandbox enforces. A limit hit is a ParseFailure, never an exception."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    wall_seconds: float = Field(default=5.0, gt=0)
    cpu_seconds: int = Field(default=5, gt=0)
    memory_mb: int = Field(default=512, gt=0)
    max_file_mb: int = Field(default=50, gt=0)
    max_pages: int = Field(default=500, gt=0)
    max_zip_ratio: float = Field(default=100.0, gt=0)
    max_zip_entries: int = Field(default=10_000, gt=0)
    max_depth: int = Field(default=32, gt=0)

    @property
    def max_file_bytes(self) -> int:
        return self.max_file_mb * 1024 * 1024

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Limits:
        """Read the PAPERGLASS_SANDBOX_* and PAPERGLASS_MAX_* variables from .env.example."""
        env = os.environ if environ is None else environ
        values: dict[str, float | int] = {}
        if (seconds := env.get(f"{ENV_PREFIX}SANDBOX_SECONDS")) is not None:
            values["wall_seconds"] = float(seconds)
            values["cpu_seconds"] = max(1, int(float(seconds)))
        if (memory := env.get(f"{ENV_PREFIX}SANDBOX_MEMORY_MB")) is not None:
            values["memory_mb"] = int(memory)
        if (file_mb := env.get(f"{ENV_PREFIX}MAX_FILE_MB")) is not None:
            values["max_file_mb"] = int(file_mb)
        if (pages := env.get(f"{ENV_PREFIX}MAX_PAGES")) is not None:
            values["max_pages"] = int(pages)
        return cls(**values)  # type: ignore[arg-type]  # keys are the field names above
