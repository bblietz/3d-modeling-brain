---
name: feedback-cutlist-inches-only
description: Brian's cut lists, shop pages, drawings and part notes are inches only (nearest 1/32); no mm anywhere he reads, plywood-sized cuts say "measure" instead of a fraction
metadata:
  node_type: memory
  type: feedback
  originSessionId: 78cb6e72-d3a2-471b-85c4-3674d1c3d30b
  modified: 2026-09-28T00:00:00.000Z
---

Everything Brian reads in the shop is inches only: the cut list markdown, the published shop page, the part drawings and the machining notes on each row. No mm columns, no mm in parentheses, no metric material names ("3/4 ply", not "ply 18mm"), areas in sq ft. Fractions to the nearest 1/32.

**Why:** Brian (2026-09-28, Drawer-bench): "get rid of the metric numbers in the cutlist." His shop works in inches; the mm column was noise. With the mm gone the fraction carries all the precision, and 1/16 was too coarse for blanks derived from metric plywood (a drawer end came out 0.67 mm long at 1/16, 0.12 mm at 1/32).

**How to apply:** `scripts/cutlist.py` `write_cut_list(..., units="in", denom=32)` for his furniture projects (the default stays mm plus inches for the speaker-cab pipeline); part notes format every number through an `inch()` helper (`inch_frac(mm, 32)`), never `:g` on a mm constant. A cut sized to plywood prints "3/4 ply (measure)" instead of a fraction (18 mm would print as 23/32, which reads as a number to hit). Dimension from the datum that is a clean inch (a groove's top wall at 1-1/2, not its lower wall at 1-1/32). The CSV may keep mm as data for page builders. Related: [[project-drawer-bench]], [[feedback-stopped-groove-notched-panel]].
