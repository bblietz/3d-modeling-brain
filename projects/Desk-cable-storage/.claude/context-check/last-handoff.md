# Handoff: Desk cable storage, 2026-09-26 evening (revision B: D vs D+ page and measurement sheet out)

## Evening update 3: CAD COMPLETE
- Brian waived every measurement and fixed the spec: wall trough, max bed width, 6 in deep, 4.5 in front wall,
  full-width cavity, two screw holes in the top of the back wall (16 in apart wished; 9 in was too close to the ends, now 7 in). Side walls then cut to 4.5 in like the front; back wall alone at 6 in. Slice 7 h 59 m, 387 g..
- `trough.py` (build123d, self-checking) -> `trough.stl` 254 x 152.4 x 152.4 mm, 385 cm3.
- `pipeline/make_print_3mf.py` (subagent, adapted from NACS-organizer/make_plate.py + iPhone flattener) ->
  `trough-print.3mf`, `trough-slice.json`: 8 h 42 m, 417 g, 508 layers, no brim/skirt, x 1..255 on the bed.
  Gotcha: --arrange 1 rotates the part into the two-nozzle shared area unless pinned to extruder 1.
- OCP viewer open with the part (scripts/cad-viewer.sh; SHOW=reset trough.py). Companion page `part.html`.
- Waiting on: Brian's sign-off, then he prints. Nozzle unconfirmed (printer unreachable).

## Evening update 2 (later the same evening)
- Brian: "the trough should have a higher front wall. It should be 75% of the height. The location on the wall will be D."
  D+ dropped. concept.scad option D now has D_LIP_FRAC = 0.75 and cords routed over the wall; D re-rendered,
  phone page republished (D+ card and pick control removed), companion page `d-decided.html` pushed.
- Then Brian: "make the box 6\" deep" and "make the width of the box the max width of the printer bed".
  Applied: D_L = 250 mm (one piece on the 256 mm bed), D_D = 6 in, D_H = 6 in (read "deep" as cavity depth;
  front wall 4.5 in). If he meant front-to-back, only D_H changes back to 4.5. Re-rendered, both pages updated,
  phone artifact republished (D+ files removed).
- Still waiting on: M1 to M10, back cleat yes/no, which outlets need slack.

## Evening update 1 (desk session, transcript 7353995d resumed)
- Read revision A. Concept D stands. Built the D vs D+ page with the ten-span measurement drawing
  (`pipeline/measure_diagram.py` -> `images/design/measure.png`) and a fill-in sheet that composes a
  paste-back line ("pick D+, M1 26 3/4, ..."). Published as a NEW artifact (the morning one was too big
  to read back): https://claude.ai/artifact/CmY2ksbUC4nRorCnHt3nxY (deleted 2026-10-02; the local decision.html is the only copy, publish a new artifact if a phone page is wanted again) . Same content on the local companion
  (`.superpowers/brainstorm/1073966-*/content/d-or-dplus.html`, server port 60460).
- Recommendation given: D+ (D shows from 10 ft; the plug heads show before D+ does).
- brief.md now exists (written this evening; the morning session had none).
- Printer unreachable at 21:15 (no route to host), nozzle unconfirmed.
- Waiting on: Brian's pick, M1 to M10, and which outlets' cords need slack. Then: update concept.scad,
  re-render, /3d-model skill (build123d or OpenSCAD part, section checks, split for the bed, STL + 3MF).

## Revision A (morning, kept for history)

## State
CONCEPT PICKED, NOT YET MEASURED OR MODELLED. Brainstormed in session 3d-modeling-brain-f7
this morning (transcript 7353995d), four to-scale concepts rendered in OpenSCAD inside a
model of the closet. Brian picked D, the trough on the back wall, from his phone at 11:40.
A raised variant (D+, top edge on the underside) was added because D as first drawn is
visible from beyond about 6 ft. Both are on the shared page.

Shared page (private, embeds every render): https://claude.ai/artifact/PrhaKebPkxBCo1XxL1EE7z
Rebuilt by `pipeline/make_share_page.py` from `images/concepts/`; republish to the same URL.

No brief.md yet (the brainstorming skill withheld it until a pick). No CAD. Nothing sliced.
The whole project folder is UNTRACKED in git; Brian has not asked for it to be committed.

Files: `images/desk-1.jpg`, `desk-2.jpg` (5712 x 4284, the only copies; Desktop originals
were deleted), `pipeline/concept.scad` (to-scale scene, options today/A/B/C/D, D_TOP override
gives D+), `pipeline/render_concepts.py` (VARIANTS maps Dhigh to D with D_TOP=26.75),
`pipeline/make_share_page.py`, `share.html`, `images/concepts/*.png` (57).

## Decisions already locked
- CONCEPT: D, a trough screwed to the back wall behind the strip. Picked 2026-09-26.
- Whether it sits under the plug heads (D, easy to load, shows past 6 ft) or raised to the
  underside (D+, hidden to about 12 ft, coil gets tucked in) is the open question.
- The power strip stays where it is, screwed to the underside. Brian: "keep it there".
- Contents: cord slack plus the power brick only. Not the floor bundle, not a shelf.
- Open front, reach in. No lid, drawer, hinge, latch or magnets. "Don't over complicate it."
- Sized for about ten cords, NOT the 34 in length of the strip.
- If the brick does not fit it goes on the desk with its lead fed down through the plywood.
- Brian is visual: draw options and ask against the pictures, at most one or two text
  questions. Recorded in memory/feedback-html-visual-companion.md.
- Attachment may be the desk underside or the wall (his original ask allowed both).

## Open, and blocking any CAD
1. NOTHING IS MEASURED. Every dimension is photo-derived, about plus or minus 10 percent.
   Need: closet width, front edge to back wall, underside height, slab thickness (he said
   3/4 in, photo reads 5/8), strip setback behind the front edge, clear depth behind the strip.
2. D vs D+.
3. Cord count: all nine, or are the PC and shredder cords permanent? Sets the trough length.
4. Build method never answered: fully printed in sub-256 mm segments vs hybrid with printed
   end caps. D is 16 in long so it splits in two either way.
5. Material, colour and nozzle never discussed. Page says PETG. Confirm installed nozzle.
6. Drywall anchor pullout with a loaded trough is unverified. Four anchors assumed.

## Next steps
1. Brian answers D vs D+ and sends the six measurements.
2. Update concept.scad numbers, re-render, republish the page, get a visual sign-off.
3. Enter the /3d-model skill for the build: build123d part, verify the lip and mouth against
   real cord and brick sizes in section, printability check, split for the bed, STL + 3MF.
4. Write brief.md, then commit the project if Brian wants it tracked.
