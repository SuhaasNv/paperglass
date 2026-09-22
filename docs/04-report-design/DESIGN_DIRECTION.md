# Design direction for the web app (brief for the design pass)

Written 22 Sep 2026 as input for the owner's design session. It states what the product is, who reads it, and what to avoid. It does not draw the screens; that is the design pass. The one rule that carries into code: nothing in the palette or the type carries meaning that a label plus a shape does not also carry (`ACCESSIBILITY.md`).

## What it is

A magnifying glass over paper. The product shows a page and the text a machine reads off it, side by side, and marks every place the two disagree. It is closer to a proof-reading desk or a forensics bench than to a dashboard. The reader is a recruiter, an editor, a loan officer or a developer checking a file before a pipeline eats it. They want calm, density and evidence, not a product tour.

## Tone

Editorial and forensic. Dense text, real tables, hairline rules, generous margins, a page that looks like it could be printed. The verdict is a word and a set of counts, never a gauge or a score ring. Evidence is shown, not dramatised.

## Avoid (the tells of generated interfaces)

- Purple-to-blue or pink-to-orange gradients, gradient text, glowing borders, glassmorphism, frosted cards floating on a dark radial background.
- One accent colour used for everything: buttons, links, badges, charts, hero text.
- Cards for everything; rounded-everything; drop shadows as decoration; oversized hero headline with a three-word tagline and an emoji.
- Default AI-adjacent type pairing (a geometric sans for everything at 700 weight) and default Tailwind blue.
- Score rings, gauges, confetti, skeleton shimmer as a feature, dark mode as the only mode.
- Marketing voice ("supercharge", "seamless", "AI-powered"), exclamation marks, emoji, em dashes.

## Palette: paper and ink, one signal colour

Light mode is the default (documents are read on paper-white). Suggested tokens for the design pass to accept or replace:

| Token | Suggestion | Role |
|-------|------------|------|
| paper | `#F5F2EB` (warm off-white) | page background |
| paper-2 | `#ECE7DC` | panels, table stripes |
| ink | `#17160F` | text |
| ink-2 | `#5B5850` | secondary text, rules |
| rule | `#CFC9BA` | hairlines, borders |
| glass | `#2F5D7C` (muted steel blue) | the one signal colour: links, focus rings, the diff highlight outline |
| glass-2 | `#D9E6EE` | highlight fill for unmatched runs in the diff |

Severity is a label plus a shape first; colour is a secondary cue and is muted, drawn from the same warm family, never neon:

| Level | Shape | Colour cue |
|-------|-------|------------|
| critical | filled octagon | `#7A2E1F` (oxblood) |
| high | filled triangle | `#9A4A1C` (rust) |
| medium | filled diamond | `#8A6A1E` (ochre) |
| low | filled circle | `#4F6A3A` (moss) |
| info | outlined circle | ink-2 |
| benign-hidden | outlined square | ink-2 |

A dark mode may come later; if it does, it is ink on paper inverted (deep warm grey, not pure black), never a neon-on-black theme.

## Type

Three faces, each with a job: a text serif for headings and long copy (a document voice: for example Source Serif 4 or Newsreader), a humanist sans for interface labels and tables (for example Public Sans), and a monospace for mechanism strings, reproduce commands and code points (for example IBM Plex Mono). Body at 16 px, line length 60 to 75 characters, headings one or two sizes up, weight 400 to 600, never 800. Fonts are self-hosted; the app makes no external requests.

## Layout notes for the screens

- Upload: one page, one action, the drop zone is a dashed hairline rectangle on paper, the tier and profile are plain selects; the privacy sentence ("your file is scanned in memory and not stored; the report is kept 7 days under an unguessable link") sits under the button, not in a modal.
- Results: verdict line first (word, shape, counts); then the diff in two columns with the unmatched runs outlined in glass; then finding cards as a list with a hairline between them, not floating cards; the crop is an image with a caption, the mechanism and the reproduce command in monospace with a copy control; tabs for pages and fingerprint are text tabs with an underline, not pills.
- History: a table (date, file name, verdict with shape, link); nothing else.
- Techniques: `THREATS.md` rendered as a readable reference, one section per format, plain sentences first, thresholds in a second column.
- About: what the three views are, what the product does not do, the licence, the disclosure link.

## Motion

Almost none. No animated gradients, no parallax, no reveal-on-scroll. Focus and hover states are visible; state changes are instant or a 150 ms fade. Respect `prefers-reduced-motion` by having nothing to reduce.
