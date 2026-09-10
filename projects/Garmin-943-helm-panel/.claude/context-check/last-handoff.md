# Handoff: Garmin 943xsv helm panel, 2026-09-09 (revision B)

## State
Router template designed, verified, and exported. Nothing printed yet. The full panel is now modeled too, at Brian's provisional 18.5 x 11.5 in; he will send exact measurements and photos later.

Files in `projects/Garmin-943-helm-panel/`: `brief.md` (spec, Garmin numbers, build results, print settings), `router-template.py` (build123d source with self-checks), `router-template.stl`, `router-template.3mf`, `images/router-template-4view.png`.

## Decisions already locked
- Black King Starboard panel, 3/8" unless the span exceeds 450 mm, replaces the hinged cover and is fixed in place.
- Garmin flush mount, screws through the bezel edge into the HDPE. No printed bezel frame.
- Panel outline and perimeter fastening come from the old cover. Out of scope.
- One printed PLA router template, window exactly 222.4 x 139.0 mm, bearing-guided bit, 12 mm thick, 252.4 x 189.0 mm outside.
- Drill guides 2.8 mm modeled with 6 x 6 mm counterbores, shifted 1.24 mm toward the unit's bottom as Garmin's template draws them (rows at +74.0 and -76.5 from the window center). TOP debossed on the counterbored face. Two optional 4 mm fixing holes on the vertical centerline, four V notches for registration.
- Garmin's drawn cutout corners are R3.7, so a 1/4 in bit needs no corner squaring.
- Vertical cutout placement decided by Brian at layout (`CUTOUT_DY` in helm-panel.py, currently 0).
- Panel modeled at 469.9 x 292.1 x 12.7 mm, R12.7 corners, 1/8 in roundover on the outside face, blind 2.3 mm pilots. 1/2 in stock because the span exceeds the 450 mm rule.
- Garmin dimensions live in garmin_9x3.py, imported by both models. Do not re-inline them.
- Panel is printed, not routed: split into four 234.95 x 146.05 x 12.7 mm tiles at x=0 and y=0, joined by 10 loose bowtie keys dropped in from the back (integral dovetails cannot work on a 2x2 grid).
- ASA, not PLA. Textured PEI 100 C, 0.6 nozzle, 0.30 mm, 5 mm outer brim, each tile FRONT FACE UP. 8 h 55 min and 439 g total across five plates.
- make_plate.py builds and verifies the five Bambu project 3MFs; it slices them via Sharks-nametag/pipeline/graft_slice.py because the CLI cannot slice its own project files.

## Next steps
1. Brian prints the template (0.30mm Standard, 0.6 nozzle, brim off, centered on plate, counterbored face up, about 1 h 28 min).
2. Measure the window with calipers; expected 222.4 x 139.0 within 0.3 mm. If off, adjust slicer XY compensation, never rescale.
3. Rout, test fit the 943xsv, install.
4. Write `knowledge/learnings/garmin-943-helm-panel.md` with measured window, fit result, and screw hold in the HDPE.
