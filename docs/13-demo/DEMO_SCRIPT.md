# The 30-second demo

Rewritten 22 Sep 2026 (US-045) to what exists on `dev`: the web app at the development URL and the CLI. Recorded by the owner; captions only, no narration. Documents: `documents/resume-clean.pdf`, `documents/resume-poisoned.pdf` (one white-on-white paragraph). One browser window at 1280 px wide, one terminal beside it.

| Time | Screen | Caption | What it proves |
|------|--------|---------|----------------|
| 0 to 3 s | the landing page; the cursor moves onto the resume and the glass opens: outside the ring a normal CV, inside it the extractor's text with the hidden sentence outlined | A resume. Looks fine. | the human view, and the lens in one motion |
| 3 to 8 s | Scan: `resume-poisoned.pdf` dropped on the sheet, tier standard, profile resume, Scan document; the scanning hairline sweeps | This is what the model reads. | the gap |
| 8 to 14 s | Results: MALICIOUS with the octagon, "hidden text found", counts; "Under the glass": the page thumbnail, the hidden run outlined, the glass over it shows the sentence in place; the reading-order column beside it | Hidden text found. Page 1. | evidence, in ten seconds |
| 14 to 19 s | scroll to Finding F-1: the sentence, the crop, `fill colour '1 1 1 rg' (grey 1.000) at instruction 9`, the reproduce command; Copy | The bytes. The reason. | mechanism and reproduce |
| 19 to 24 s | terminal: `paperglass show --page 1 --instruction 9 resume-poisoned.pdf` prints the content stream line; then `paperglass fingerprint resume-poisoned.pdf`: pypdfium2 fooled, pdfplumber fooled, pypdf fooled, pdfminer.six fooled | Which parsers read it. | the RAG developer's question |
| 24 to 28 s | Download HTML report; the file opens from disk with the browser offline, the same page under the glass | One file. Opens offline. | UC2 |
| 28 to 30 s | end card on paper: "Would a human reviewer have seen everything the model is about to read?" github.com/SuhaasNv/paperglass, Apache-2.0, runs offline | | |

The glass at 2 s is the shot that makes everyone care; the fingerprint table at 20 s is the shot that makes RAG developers care. `clean()` and the LangChain snippet return to the demo at v0.4.0.

Recording notes: 1280 by 800 window, system cursor hidden inside the document (the ring replaces it), `prefers-reduced-motion` off so the rule draws and the sections rise, no notifications. Export at 30 fps, MP4 and GIF; the GIF goes in the README at v0.2.0 (US-042).
