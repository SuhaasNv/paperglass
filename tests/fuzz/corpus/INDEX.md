# Fuzz corpus

One line per file: what it breaks, where it came from, when it was added (`docs/06-security/FUZZING.md`).

| File | What it exercises | Source | Added |
|------|-------------------|--------|-------|
| `pdf/truncated.pdf` | file cut in half through an object | minipdf mutation | 22 Sep 2026 |
| `pdf/xref-offsets-wrong.pdf` | xref points past the end of the file | minipdf mutation | 22 Sep 2026 |
| `pdf/no-eof.pdf` | missing %%EOF | minipdf mutation | 22 Sep 2026 |
| `pdf/empty-after-header.pdf` | header only | hand-made | 22 Sep 2026 |
| `pdf/negative-mediabox.pdf` | negative page size | minipdf | 22 Sep 2026 |
| `pdf/deep-nesting.pdf` | 5,000 nested q operators | minipdf | 22 Sep 2026 |
| `pdf/huge-font-size.pdf` | font size 1e12 | minipdf | 22 Sep 2026 |
| `pdf/unterminated-string.pdf` | string operand never closed | minipdf | 22 Sep 2026 |
| `pdf/binary-garbage-stream.pdf` | binary bytes in the content stream | minipdf | 22 Sep 2026 |
| `text/invalid-utf8.txt` | bytes that are not UTF-8 | hand-made | 22 Sep 2026 |
| `text/nul-bytes.txt` | NUL bytes in text | hand-made | 22 Sep 2026 |
| `text/very-long-line.txt` | a 200,000 character line | hand-made | 22 Sep 2026 |
