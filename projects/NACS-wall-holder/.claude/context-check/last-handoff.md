---
type: handoff
project: NACS-wall-holder
date: 2026-10-10
---

# NACS wall holder handoff (2026-10-10, revision plus plate fix built, not printed)

## State
The 2026-09-19 holder was on the wall and working until Brian dropped it on 2026-10-10 and a plate corner broke
off along the drum blend. The 2026-10-08 revision (deeper, 90 drum, crest lip, wordmark, two-colour face, wider
cleat catch window) now also has the plate fix: `plate_t` 6.35 (1/4 in) and a solid-base modifier in the print
3MF (whole plate plus the drum blend ring at 100% monotonic; "rectilinear" is not a Bambu pattern name). Since
2026-10-11 the modifier sits wholly inside the body (the ring follows the blend's arc 0.6 mm inside it, the slab stops
a layer under the plate's top and clears the screw holes): Brian saw the first, squared-off ring in Studio and asked
for it to round into the plate. The same day the face went solid too (Brian: "it will also break if dropped"): a second
modifier from holder.scad's own `part = "facemod"` (flange, lip and the blend behind the flange, `mod_skin` 0.6 inside
every surface, recesses and mouth cleared). `holder.stl` (622.7 cm3, watertight), `holder-inlay.stl` and
`holder-print.3mf` (10 h 11 min, 574.7 g: 558.7 body PETG, 12.4 support interface, 3.5 inlay colour) are built and
checked (solid windows 0.95 to 1.01, sparse ones 0.18 and 0.19), not printed. OPEN AND BLOCKING THE PRINT: Brian's
"the center cylinder extends past the edge of the base on all 4 sides" (the 90 drum's blend foot at 52 and the 104
flange against the 4 in plate's edge at 50.8, since 2026-10-08); options page
https://claude.ai/artifact/5YuDCMozLvJvJUdhwWxwJk (A plate 4.5 in recommended, B 4.25 in, C 4 in with 4 mm blends and
a 98 face; all keep the screw pattern). Evidence page for the break (before and after plate layers, the modifiers):
https://claude.ai/artifact/QCeo4UdoVNbcSQv3je5xm4; plan page https://claude.ai/artifact/D2zPQ4v2W97wuq1hMqpYa6.
Full record in brief.md "Revision of 2026-10-08", "Later the same day", "Dropped, 2026-10-10" and "The fix".

## Decisions already locked (Brian)
- 2026-10-11: the face (flange, lip, blend behind the flange) solid like the base; every modifier wholly inside the body.
- 2026-10-10: plate 1/4 in AND solid ("do 1 and 2"). The break ran "along the contour of the main cylinder".
- `mouth_z` 61.43 and `cut_top` 93.8 stay with the thicker plate: the wand keeps its place off the wall; the flange,
  lip and inlay move out 1.35 mm (holder 106.75 off the wall, mouth top 4.95 under the flange).
- 2026-10-08: drum 1 in deeper (`drum_l` 100.4), `drum_r` 45, flange 104; `cleat_depth` 44.45; `tip_gap` 5,
  `undercut` 20; crest lip 1.5 in full width with the frame line; Tesla T, curved TESLA wordmark and frame inlaid
  flush in filament 3; plain top screw holes (driver at a 6 degree tilt); skirt kept.
- Everything from 2026-09-19 stays locked: v7 cavity and cleat shape, grip-up docking, 45 / 15 degree wand, 4 in
  base and hole pattern, 1/16 in roundovers.

## Pipeline notes
- Order after a cavity, drum or plate change: zbudget.py, rim_round.py, insertion.py, both exports, make_coupon_3mf.py
  holder, render.sh, renders_page.py, republish plan.html to its URL.
- Body export: `openscad -D display=false -D show_nose=false -D show_wall=false -D show_inlay=false -o holder.stl
  holder.scad` (without show_inlay=false the inlay is fused into the body; check that inlay volume samples inside
  the body are 0). Inlay: same with `-D 'part="inlay"'`.
- `pipeline/corner_check.py [sliced.3mf|""] [tag] [body.stl]` draws the mid-plate toolpaths and a screw-hole section;
  `pipeline/corner_page.py` builds the evidence page from the before and after images.
- `pipeline/modifier_views.py [body.stl]` draws the solid-base modifier over the body the way Studio shows it and in a
  true section, before and after, and prints its volume outside the body (must be 0). Any modifier change: run it,
  then `make_coupon_3mf.py holder` (the check has a window at the blend's foot where the modifier's arc meets the walls).
- Regex-parsed constants stay literal numbers. Do not `pkill -f` a pattern that appears in your own command line.

- The G-code check's windows are set out in the model's frame and mapped through the object's item transform from the
  sliced 3MF: the CLI's arrange turns the part on the bed (88 degrees in this build).
- `pipeline/render_plate_options.sh` and `pipeline/plate_options_page.py` made the base options page; after Brian's pick
  set `plate_w`, `hole_in`, `plate_r` (A: 114.3, 16.35, 16.35; B: 107.95, 13.175, 13.175) or `fillet_plate`,
  `fillet_flange` 4 with `tab_w` 98 and `logo_h` 56 (C), turn holder.scad's foot warning into an assert, and run the
  whole pipeline (the plate's size does not move the cavity, but every export, the 3MF, the checks, renders and pages
  follow).

## Open
- Brian's pick of the base (A, B or C above). Nothing prints before that.
- Then print `holder-print.3mf` (plate down, face up; supports in the cavity, under the flange ring and under the lip;
  a second PETG colour in the AMS slot for filament 3). Not sent to the printer.
- Grip fit in the extra 1/2 in of opening is unproven (Tesla's CAD ends 48 mm from the tip). Ask for the handle's
  width and height 1/2 in and 1 in behind the glossy housing, plus the button height; adjust `grip_flare` if needed
  and rerun the pipeline.
- If driving the top screws at a tilt proves awkward, switch `top_mount` to "keyhole" and rebuild.
