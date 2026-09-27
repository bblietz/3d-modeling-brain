---
name: project-desk-cable-storage
description: Under-desk cable storage for Brian's closet printer bench; CAD complete 2026-09-26 (wall trough D, 254 x 152 x 152 mm, front wall 4.5 in, two holes 7 in apart), sliced 8 h 42 m / 417 g PETG, measurements waived; awaiting sign-off and print
metadata:
  type: project
---

Brian wants cord slack and a power brick hidden under his closet desk, a 3/4 in plywood slab on
wall cleats with a 9-outlet power strip screwed to its underside. Brainstormed 2026-09-26 in
another session with four to-scale OpenSCAD concepts rendered inside a model of the closet, each
checked in black from 5 ft, 10 ft and an oblique angle for what shows from the room.

PICKED 2026-09-26: D, a trough on the back wall. As first drawn (under the plug heads) it shows
from beyond about 6 ft; a raised variant D+ with its top edge on the underside hides to about
12 ft. Which of the two is the open question. Shared page, private, all renders embedded:
https://claude.ai/artifact/PrhaKebPkxBCo1XxL1EE7z (rebuilt by `pipeline/make_share_page.py`).

Evening 2026-09-26 (desk session): D vs D+ page rebuilt with a to-scale "measure these" drawing (M1 to M10) and a fill-in sheet that composes a paste-back line, published at https://claude.ai/artifact/CmY2ksbUC4nRorCnHt3nxY (files, not data URIs); the same content is on the local companion. Recommendation on record was D+; Brian overruled it the same evening: "The location on the wall will be D" and "the trough should have a higher front wall. It should be 75% of the height." D+ is dropped. Then: "make the box 6\" deep", "make the width of the box the max width of the printer bed", measurements waived ("ignore M1..M10"), "cavity the full width", "only 2 screw holes in the top" (16 in apart wished, not required). Built as `trough.py` (build123d): 254 x 152.4 x 152.4 mm, front wall 114.3, walls 2.4 / back 3.2, holes 5 mm at 7 in apart (1.5 in from each end; 9 in was "too close to the ends"), 3/4 in below the top edge. Sliced by `pipeline/make_print_3mf.py`: fits the bed at x 1..255 with no brim or skirt (the arranger must be pinned to extruder 1 or it rotates the part into the two-nozzle shared area), 8 h 42 m, 417 g. Printer was unreachable, so the installed nozzle is unconfirmed.

**Why:** the closet is used as a printer bench and is open to the room, so anything under the slab
is judged by whether a standing person can see it. Brian is visual and asked to be shown drawings
rather than questions.

Locked: strip stays put; contents are slack plus brick only; open front, reach in, no lid or
drawer; sized for about ten cords, not the strip's 34 in; brick may go on the desk with its lead
through the plywood. Every dimension in the model is photo-derived at about plus or minus
10 percent and NOTHING has been tape-measured; the six measurements are the gating item.

**How to apply:** read `projects/Desk-cable-storage/.claude/context-check/last-handoff.md` first. Next input expected from Brian is a line like "M1 26.5, M2 3/4, ..." from the phone sheet; feed it into `pipeline/concept.scad`, re-render, then enter the /3d-model skill.
The project folder is untracked in git; do not commit it unasked. Related:
[[feedback-html-visual-companion]], [[feedback-openscad-for-complex-designs]], [[project-garmin-helm-panel]].
