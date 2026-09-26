# Handoff: Garmin 943xsv helm panel, 2026-09-26 (revision D: printing in ASA)

## State
BUILD SWITCHED TO PRINTED ASA. Brian chose to print the panel rather than rout Starboard.
Router template printed and FITS (2026-09-11, Brian confirmed), which validated the whole
cutout chain. Retrospective at knowledge/learnings/garmin-943-helm-panel.md.

Print files rebuilt and re-verified 2026-09-26 on Bambu Studio 02.08.02.61. Every plate
slices for real; Studio's own reader reports 1, 1, 1 and 11 objects across four plates.

Nothing of the panel is printed yet. The panel OUTLINE is still Brian's 18.5 x 11.5 in
estimate.

Files in `projects/Garmin-943-helm-panel/`: `brief.md`, `helm-panel.py`, `garmin_9x3.py`,
`make_plate.py`, `make_multiplate.py`, `helm-panel-all-plates.3mf` (THE print file),
five per-part 3MFs, tile and key STLs, `router-template.*`, `images/`.

## Decisions already locked
- DECIDED 2026-09-26: the panel is PRINTED IN ASA as four interlocking tiles. The routed
  1/2 in Starboard one-piece stays in the repo as the alternative, not the plan.
- ASA thickness is 3/8 in (9.525 mm), NOT the 1/2 in from the Starboard decision. 1/2 in
  was an HDPE allowance for softness and creep; printed ASA reaches the same deflection at
  3/8 in. helm-panel.py now derives thickness from the build so neither path inherits the
  other's number, and TILES=1 no longer overwrites the one-piece STL/STEP.
- Real deflection with 15 percent infill is about 0.33 mm, not the 0.21 mm solid-section
  figure. Still imperceptible. Do NOT raise infill; the solid skins carry the bending.
- Four tiles 234.95 x 146.05 x 9.525 mm, split at x=0 and y=0, joined by 10 loose bowtie
  keys dropped in from the back. Integral dovetails cannot work on a 2x2 grid.
- ASA, not PLA. Textured PEI 100 C, 0.6 nozzle, 0.30 mm layers, 5 mm outer brim, each tile
  FRONT FACE UP. 7 h 55 min and 376 g across four plates.
- Ironing stays OFF. Satin ASA reads matte at the helm; an ironed face would glare.
- helm-panel-all-plates.3mf is THE print file. Two plates is impossible; two tiles fit only
  as diagonal pairs at 248 x 247 with no brim room.
- Studio's plate grid is two columns running in negative Y, not one row along X.
- Garmin dimensions live in garmin_9x3.py, imported by both models. Do not re-inline them.
- Garmin's drawn cutout corners are R3.7, and the four screw holes sit 1.24 mm toward the
  unit's bottom (rows at +74.0 and -76.5 from the window center).
- Vertical cutout placement is Brian's at layout (`CUTOUT_DY`, currently 0).
- Panel outline and perimeter fastening come from the old cover.

## Open, and blocking a good print
1. OUTLINE IS UNCONFIRMED. 18.5 x 11.5 in is an estimate. The template was safe to print
   against it because it only locates the cutout; a printed PANEL bakes it in at a cost of
   8 hours and 376 g. Get the opening measured before starting.
2. NOZZLE. Files are built for the 0.6 high-flow; the 0.4 has been installed since
   2026-08-06. Studio silently re-slices to the installed profile with no warning.
3. Unrecorded from the template print: caliper reading of the window (expect
   222.4 x 139.0 within 0.3 mm) and which of the two presets was actually run.

## Next steps
1. Brian measures the opening and sends photos; update PANEL_W, PANEL_H, CORNER_R.
2. Re-run `TILES=1 helm-panel.py`, then `make_multiplate.py`, then reprint the files.
3. Install the 0.6 high-flow nozzle, load dry black ASA, print plate 1 and check corners.
4. Print the rest, assemble face down with the ten keys, acetone weld.
5. Update the retrospective with measured fit and screw hold in printed ASA.
