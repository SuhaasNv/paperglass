# Sandbox

Every parser call runs inside `paperglass.ingest.sandbox`, a context manager that launches the parse in a subprocess with limits and turns any failure into a finding.

## Limits (defaults; `.env.example`)

| Limit | Default | Enforced by |
|-------|---------|-------------|
| Wall clock per parser call | 5 s | parent process timeout, child killed |
| CPU time | 5 s | `RLIMIT_CPU` (POSIX); job object on Windows |
| Memory | 512 MB | `RLIMIT_AS` (POSIX); job object on Windows |
| File size | 50 MB | checked before launch |
| Page count | 500 | checked at open; pages beyond the cap are not parsed and the report says so |
| Zip ratio (OOXML) | 100:1 | entry sizes checked before extraction; no nested archives followed |
| Recursion (object references, XObjects, nested fields) | 32 | depth counter in the probes |
| Network | none | no socket use in parsers; `allow_network` only reaches adapters |

## Failure is a finding

A crash, a timeout or a limit hit produces a `parse.failure` finding with the stage, the parser and a redacted message, and the scan continues with the other views where possible. The caller never receives an exception from a parser. A `parse.failure` alone yields the verdict `suspicious` in the default profile, because a file the scanner cannot read is a file a person could not review.

## What is never executed

PDF JavaScript, open actions, form calculations; Office macros; external references and remote XObjects; font programs outside the renderer's own sandboxed rasteriser (pdfium). `pdf.active.content` flags the presence and the carrier is not parsed further.

## Fuzzing

`tests/fuzz/` holds a corpus of malformed PDF, DOCX (and later PPTX, HTML) files plus hypothesis strategies; CI runs it with the limits above and fails on any crash or hang. Adding a crasher: `../06-security/FUZZING.md`.

## Known limits

A subprocess with rlimits does not stop a memory-safety exploit in a native parser from reading the host. The recommended deployment for untrusted volume is the REST image with `--network none`, a read-only filesystem and a non-root user (`../11-integrations/REST.md`); the fast tier's dependency list is kept under ten packages; `pip-audit` blocks CI; a library with an unpatched critical CVE is dropped or pinned within 30 days.
