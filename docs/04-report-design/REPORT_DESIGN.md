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

| Profile | What changes (built at US-044) |
|---------|--------------|
| `default` | thresholds as in `THREATS.md` |
| `resume` | hidden data is high (one hidden skill list makes the verdict malicious); any ActualText is a finding (a resume has no ligature override); alt text and properties benign only under 100 characters; hiring phrases ("top candidate", "years of experience", "shortlist") count as instructions and "hire", "shortlist", "interview" reach critical |
| `peer-review` | ligature and short-symbol ActualText benign up to 6 characters; figure alt text benign up to 600 characters; review phrases ("strong accept", "recommend acceptance", "overall score") count as instructions and "accept", "reject", "rate" reach critical |
| `rag-ingest` | OCR text layers on scans benign at 0.7 agreement instead of 0.8; phrases addressed to the assistant ("when asked", "tell the user", "respond with", "the following link") count as instructions and "respond", "tell", "visit" reach critical |

Deferred from the original plan: the resume `--job-description` duplicate check and the date contradiction check (a later story), and the `rag-ingest` Policy default (v0.4.0 with `clean()`).

Profiles are TOML files under `src/paperglass/profiles/`; a profile `extends = "default"` and states only what it changes (tables merge key by key, phrase and verb lists extend the base). Detectors read their thresholds and allowlist limits from the profile on the page context, so no threshold lives in code. The profile name is in the report header; `paperglass profiles` and `GET /api/v1/profiles` list them.

## Tested before Done

Opened offline at 375, 768 and 1280 px: no horizontal scroll, overlays aligned to thumbnails, hidden text readable beside each region, verdict visible without scrolling, print to PDF renders the diff and the cards. Golden HTML tests in `tests/report/`.
