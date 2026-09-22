# Sandbox

Built at US-003 (22 Sep 2026): `paperglass.ingest` provides `sniff` (type from magic bytes), `guard_size`, `guard_zip`, `guard_pages`, `DepthGuard`, `Limits` (defaults below, `Limits.from_env()` reads `.env.example` variables) and `run_sandboxed(func, args, kwargs, limits=, parser=, stage=)`, which runs a module-level callable in a spawned child process under the limits and returns a `SandboxResult` holding either the value or a `ParseFailure`. Parsers (US-006 onward) are always called through it.

## Limits (defaults; `.env.example`)

| Limit | Default | Enforced by |
|-------|---------|-------------|
| Wall clock per parser call | 5 s | parent process timeout, child killed |
| CPU time | 5 s | `RLIMIT_CPU` in the child (POSIX); on Windows best effort until a job-object implementation lands (the wall clock still holds) |
| Memory | 512 MB | `RLIMIT_AS` in the child (Linux reliable; macOS advisory for some allocators; Windows best effort); the wall clock and the size cap are the limits that always hold |
| File size | 50 MB | checked before launch |
| Page count | 500 | checked at open; pages beyond the cap are not parsed and the report says so |
| Zip ratio (OOXML) | 100:1, at most 10,000 entries | central directory only, nothing inflated; nested archives refused (`recursion`) |
| Recursion (object references, XObjects, nested fields) | 32 | `DepthGuard` used per level inside the probes |
| Network | none | no socket use in parsers; `allow_network` only reaches adapters |

## Failure is a finding

A crash, a timeout or a limit hit produces a `parse.failure` finding with the stage, the parser and a redacted message, and the scan continues with the other views where possible. The caller never receives an exception from a parser. A `parse.failure` alone yields the verdict `suspicious` in the default profile, because a file the scanner cannot read is a file a person could not review.

## What is never executed

PDF JavaScript, open actions, form calculations; Office macros; external references and remote XObjects; font programs outside the renderer's own sandboxed rasteriser (pdfium). `pdf.active.content` flags the presence and the carrier is not parsed further.

## Fuzzing

`tests/fuzz/` holds a corpus of malformed PDF, DOCX (and later PPTX, HTML) files plus hypothesis strategies; CI runs it with the limits above and fails on any crash or hang. Adding a crasher: `../06-security/FUZZING.md`.

## Known limits

Each sandboxed call spawns a fresh interpreter (about 0.3 to 1.5 s with the parser imports), which is far above the fast-tier budget of 100 ms per page. The fix is a long-lived worker per parser, reused across calls and restarted on any failure, with the same limits applied at worker start; it is part of the CLI and speed story (US-036) and the budget is measured only after it lands.

A subprocess with rlimits does not stop a memory-safety exploit in a native parser from reading the host. The recommended deployment for untrusted volume is the REST image with `--network none`, a read-only filesystem and a non-root user (`../11-integrations/REST.md`); the fast tier's dependency list is kept under ten packages; `pip-audit` blocks CI; a library with an unpatched critical CVE is dropped or pinned within 30 days.
