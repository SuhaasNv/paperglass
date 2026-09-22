"""What View B produces: page rasters and per-region ink checks."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from paperglass.models.schema import BBox

InkClass = Literal["visible", "invisible", "uncertain"]


class PageRaster(BaseModel):
    """One rendered page as PNG bytes. Picklable, so it crosses the sandbox boundary."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    number: int = Field(ge=1)
    dpi: int = Field(ge=1)
    width_px: int = Field(ge=1)
    height_px: int = Field(ge=1)
    width_pt: float = Field(gt=0)
    height_pt: float = Field(gt=0)
    png: bytes


class InkResult(BaseModel):
    """Stage 1: what the raster says about one region."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    bbox: BBox
    ink_fraction: float = Field(ge=0.0, le=1.0)
    """Share of pixels differing from the local background by more than the contrast threshold."""
    contrast: float = Field(ge=0.0, le=1.0)
    """Largest luminance difference between a pixel in the region and the background, 0 to 1."""
    variance: float = Field(ge=0.0)
    background: float = Field(ge=0.0, le=1.0)
    classification: InkClass
    pixels: int = Field(ge=0)


class OcrResult(BaseModel):
    """Stage 2: what OCR read in a crop."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    engine: str
