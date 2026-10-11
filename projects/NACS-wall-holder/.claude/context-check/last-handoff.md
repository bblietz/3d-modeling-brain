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
3MF (whole plate plus the drum blend ring at 100% monotonic; "rectilinear" is not a Bambu pattern name). `holder.stl` (622.7 cm3, watertight),
`holder-inlay.stl` and `holder-print.3mf` (9 h 21 min, 499.1 g: 483.2 body PETG, 12.4 support interface, 3.5 inlay
colour) are built and checked, not printed. Evidence page for the break (before and after plate layers):
https://claude.ai/artifact/QCeo4UdoVNbcSQv3je5xm4; plan page https://claude.ai/artifact/D2zPQ4v2W97wuq1hMqpYa6.
Full record in brief.md "Revision of 2026-10-08", "Later the same day", "Dropped, 2026-10-10" and "The fix".

## Decisions already locked (Brian)
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
- Regex-parsed constants stay literal numbers. Do not `pkill -f` a pattern that appears in your own command line.

## Open
- Print `holder-print.3mf` (plate down, face up; supports in the cavity, under the flange ring and under the lip;
  a second PETG colour in the AMS slot for filament 3). Not sent to the printer.
- Grip fit in the extra 1/2 in of opening is unproven (Tesla's CAD ends 48 mm from the tip). Ask for the handle's
  width and height 1/2 in and 1 in behind the glossy housing, plus the button height; adjust `grip_flare` if needed
  and rerun the pipeline.
- If driving the top screws at a tilt proves awkward, switch `top_mount` to "keyhole" and rebuild.
