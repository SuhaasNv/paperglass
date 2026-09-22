# MCP server (v0.4.0, US-065)

Planned. `paperglass-mcp` (stdio and HTTP) exposes:

- `scan_document(path | bytes)` returns the report and a receipt (`input_sha256`, verdict, severity counts, rule versions, tool version, pages render-verified, issued time).
- `read_document(path | bytes)` returns the subtractive clean text only when a receipt for that hash exists with verdict `clean` or `benign-hidden`; otherwise returns the verdict and the findings and no text. An agent host wired to this server cannot read a file it has not scanned.
- `clean_document(path | bytes, policy)` returns the `CleanResult`.

No network unless `allow_network`. Passes the official MCP conformance suite. Setup snippets for Claude Code, Cursor and other hosts in this page when built.
