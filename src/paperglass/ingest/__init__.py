"""Ingest: magic-byte sniffing, size and page caps, the sandbox.

See docs/03-architecture/SANDBOX.md.
"""

from paperglass.ingest.depth import DepthExceededError, DepthGuard
from paperglass.ingest.limits import Limits
from paperglass.ingest.sandbox import SandboxResult, run_sandboxed
from paperglass.ingest.sniff import InputType, guard_pages, guard_size, guard_zip, sniff

__all__ = [
    "DepthExceededError",
    "DepthGuard",
    "InputType",
    "Limits",
    "SandboxResult",
    "guard_pages",
    "guard_size",
    "guard_zip",
    "run_sandboxed",
    "sniff",
]
