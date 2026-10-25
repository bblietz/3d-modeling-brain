---
name: feedback-ask-load-case-before-walls
description: "Ask where a storage part lives and what it carries before choosing wall count and material; default to the printer-minimum wall and PLA for light duty, and put the grams on the sign-off page as a decision"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 57f36788-c5ae-4c4a-b01f-4b0e50546282
  modified: 2026-10-25T21:00:00.000Z
---

On the cable bin (2026-10-25) I defaulted a 17 in bin to 3-line walls and
PETG for stiffness: 368 g and 7 h per bin. Brian's first reaction was
"368g for one bin seems like a lot", then: the bins sit in a drawer, three
sides against its walls, no torsional load, use PLA. Two-line walls and PLA
gave 285 g and 4 h 58 min with the same geometry proofs.

**Why:** Brian weighs filament and time per part; stiffness beyond the use
case is waste to him, and a weight he did not choose reads as a mistake.

**How to apply:** for bins, trays, holders and other storage parts, ask the
load case in the brief (where it sits, what it carries, is it lifted loaded)
before fixing the wall count or the material. Light duty means the
printer-minimum wall (2 lines) and PLA unless heat or toughness is named.
State the grams per part and per spool on the options page as a decision
with the lighter alternative beside it, not as a footnote. See
[[feedback-html-visual-companion]], [[project-cable-bin]].
