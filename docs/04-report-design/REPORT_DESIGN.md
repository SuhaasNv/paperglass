# Report design (v0.2.0)

One HTML file. No external requests. Opens from `file://` with the browser offline. Everything inline: CSS, the page images as data URIs, the findings as JSON in a script tag.

## Layout, top to bottom

1. **Header**: file name, SHA-256 (short), tool version, profile, tier, extractor, pages checked (render-verified count of page count, dpi). Verdict as a word with its shape (see `ACCESSIBILITY.md`) and the severity counts as labelled chips. No score anywhere.
2. **Diff** (the centrepiece): two columns. Left, "what the model reads": View A text in reading order. Right, "what a person sees": the page thumbnail with the same text aligned. Every unmatched run on the left is highlighted with its severity shape; clicking it scrolls the right column to the crop and opens the finding card. Invisible Unicode is shown as its code point (`U+E0041`). Benign-hidden runs are marked with the info shape and the word "benign-hidden", never as an attack.
3. **Findings**: one card per finding: technique sentence (plain language, from the registry), status (possible or confirmed), page, the crop, the hidden text, the mechanism, the reproduce command in a copyable block, confidence, ATR id if any. Possible findings are grouped under "not confirmed on the page" and visually quieter.
4. **Pages** (tab): thumbnails with overlays; the hidden text beside each region.
5. **Clean text** (tab, v0.4.0): the subtractive result with provenance tags per run and the fidelity line.
6. **Footer**: how to reproduce (`paperglass scan --report`), what Paperglass does not check (DEFERRED list, one line), the disclosure link.

## Copy rules

- Plain language from the registry; no jargon without the sentence beside it.
- "Hidden text found", never "fraud", "cheating", "deceptive". The report describes the document, not the person.
- No em dashes, no emoji, no decorative icons; dates as `22 Sep 2026`.
- The report never describes itself as a grade or an exam of the person.

## Profiles

| Profile | What changes |
|---------|--------------|
| `default` | thresholds as in `THREATS.md` |
| `resume` | ActualText never benign; hidden data that duplicates a supplied job description (optional `--job-description` input) escalates to high; contradiction check between hidden and visible dates and years |
| `peer-review` | ligature ActualText and tagged structure expected (benign-hidden with constraints); instruction phrases about reviews and scores escalate |
| `rag-ingest` | OCR layers expected; `structure-only` findings hidden from the top line; Policy defaults to `clean` |

Profiles are TOML files under `src/paperglass/profiles/`; the profile name is in the report header.

## Tested before Done

Opened offline at 375, 768 and 1280 px: no horizontal scroll, overlays aligned to thumbnails, hidden text readable beside each region, verdict visible without scrolling, print to PDF renders the diff and the cards. Golden HTML tests in `tests/report/`.
