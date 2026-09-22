"""Corpus fetchers: one module per external source (docs/08-benchmark/CORPUS_INDEX.md). They
live under adapters because they are the one place the benchmark touches the network, and
only when `paperglass bench fetch` is run by hand. Each exposes
`fetch(root, *, limit, seed) -> FetchResult`: the samples it produced under `root/files/<source>/`,
and a sentence when it could not run (a toolkit not installed, a licence that forbids
redistribution). Fetching is the one place the benchmark touches the network, and only when
`paperglass bench fetch` is run by hand."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from paperglass.bench.index import Sample


@dataclass(frozen=True)
class FetchResult:
    source: str
    samples: tuple[Sample, ...] = ()
    skipped: str | None = None
    """Why nothing was fetched, in one sentence."""
    notes: tuple[str, ...] = field(default_factory=tuple)


Fetcher = Callable[..., FetchResult]


def sources() -> dict[str, Fetcher]:
    from paperglass.adapters.corpus import crackedpdfs, phantomlint, phantomtext  # noqa: PLC0415

    return {
        "crackedpdfs": crackedpdfs.fetch,
        "phantomlint": phantomlint.fetch,
        "phantomtext": phantomtext.fetch,
    }


def fetch_all(
    root: Path, *, limit: int | None, seed: int, only: tuple[str, ...] = ()
) -> list[FetchResult]:
    results: list[FetchResult] = []
    for name, fetcher in sources().items():
        if only and name not in only:
            continue
        results.append(fetcher(root, limit=limit, seed=seed))
    return results
