---
type: handoff
project: NACS-wall-holder
date: 2026-10-08
---

# NACS wall holder handoff (2026-10-08, revision built, not printed)

## State
The 2026-09-19 holder is on the wall and working. Brian asked for a revision on 2026-10-08; its CAD
(`holder.scad`), `holder.stl` and `holder-print.3mf` (8 h 37 min, 438 g) are built and checked, not
printed. Options were picked from rendered pages (https://claude.ai/artifact/5u3wgRBUTWngnCdjFuPzKB);
the plan page (https://claude.ai/artifact/D2zPQ4v2W97wuq1hMqpYa6) is updated. Full record in brief.md
"Revision of 2026-10-08".

## Decisions already locked (Brian, 2026-10-08)
- Drum 1 in deeper (`drum_l` 100.4), not 2 in. Drum diameter 90 (`drum_r` 45) for the deeper cavity;
  flange stays 104 with 7 mm blends.
- Cavity 1/2 in deeper: `cleat_depth` 44.45 (1.75 in). Wand at the far end, mouth top 3.6 mm under the
  flange (`mouth_z` 61.48, `cut_top` 93.8).
- Lip: full width (B), 1.5 in rise (3 in was too tall), `tab_style = "crest"` (shield sides + arched
  top), frame line yes.
- Face: Tesla T back (after generic emblems were shown and "bolt" briefly picked), TESLA wordmark bent
  along the crest's arc. Generic emblems remain as `emblem` options.
- Top screws: plain holes (`top_mount = "none"`); keyhole and driver-hole variants stay in the file.
  Brian knows the driver goes in at a 6 degree tilt past the lip.
- Everything from 2026-09-19 stays locked: v7 cavity and cleat, grip-up docking, 45 / 15 degree wand,
  4 in base and hole pattern, 1/16 in roundovers.

## Open
- Print `holder-print.3mf` (plate down, face up; supports in the cavity, under the flange ring and
  under the lip). Not sent to the printer.
- Grip fit in the extra 1/2 in of opening is unproven (Tesla's CAD ends at 48 mm from the tip). Ask
  for the handle's width and height 1/2 in and 1 in behind the glossy housing, plus the button height;
  adjust `grip_flare` if needed, then rerun zbudget.py, rim_round.py, insertion.py, the export and
  make_coupon_3mf.py (that order).
- If driving the top screws at a tilt proves awkward, switch `top_mount` to "keyhole" and rebuild.
- Retrospective to finish after the print: knowledge/learnings/nacs-wall-holder.md has the revision's
  lessons already.
