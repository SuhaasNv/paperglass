# Accessibility

Colour never carries meaning alone. Every severity and every verdict has a label and a shape.

| Level | Label | Shape |
|-------|-------|-------|
| critical | critical | filled octagon |
| high | high | filled triangle |
| medium | medium | filled diamond |
| low | low | filled circle |
| info | info | outlined circle |
| benign-hidden | benign-hidden | outlined square |
| possible (status) | possible | dashed border on the card |

Verdict words: clean (outlined circle), benign-hidden (outlined square), suspicious (filled diamond), malicious (filled octagon).

Rules: contrast at or above 4.5:1 for text; every overlay region has a text label; the diff is keyboard navigable (tab to a highlighted run, enter opens the card); no information only on hover; print stylesheet renders shapes and labels; no animation. The HTML report declares `lang` and uses semantic headings so a screen reader can read verdict, counts, then findings in order.
