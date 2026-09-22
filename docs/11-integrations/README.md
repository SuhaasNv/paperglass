# 11-integrations

One page per adapter: what it wraps, the contract, how to install, how it is tested, known limits. All planned for v0.4.0 (week 7 and 8); each page is rewritten as built.

| Page | Adapter |
|------|---------|
| `LANGCHAIN.md` | `PaperglassTransformer` document transformer |
| `LLAMAINDEX.md` | `PaperglassPostprocessor` and `PaperglassReader` |
| `DOCLING.md` | pipeline step, and Docling as a View A extractor |
| `MCP.md` | `paperglass-mcp`: scan receipt and read gate |
| `REST.md` | `paperglass-server` and the hardened image on Railway |
| `GITHUB_ACTION.md` | the Action and the pre-commit hook for repository documents |

Shared contract: metadata keys `paperglass.verdict`, `paperglass.severity_counts`, `paperglass.findings` (ids), `paperglass.provenance` (per run); text replaced by the subtractive clean view when the Policy says `clean`; a `block` verdict raises or drops per adapter convention. Adapters are optional extras with their own pinned CI; a broken adapter is marked unsupported in its page rather than blocking a release.
