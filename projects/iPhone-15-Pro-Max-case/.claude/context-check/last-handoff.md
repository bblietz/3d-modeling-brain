# Handoff: iPhone 15 Pro Max case (2026-09-20)

## Decisions already locked (Brian)
- iPhone 15 Pro Max; 1.5 mm walls; open cutout windows, no button covers; X2D 0.4 nozzle; Bambu TPU 95A HF.
- Camera guard required, as a SEPARATE ring printed flat and bonded with flexible CA.
- Guard snug around the raised camera island, slim (2.5 mm), plain (NO cutaways for Apple's flash/LiDAR cones), 1.5 mm 45 degree bevel on the inside.
- MagSafe pocket requested ("add a magsafe ring so I can insert the metal pieces"): BUILT to Apple's nominal case array (ring 54.10/46.00 x 0.55, clocking magnet 6.00 x 19.31, reference note section 16), in the phone side of the back, 0.8 deep, 0.8 mm of back behind it. STILL OPEN: the size of Brian's own pieces (asked, not answered); change the five `MAG_*` constants to match.

## State
- CAD complete and self-checking: `iphone-15-pro-max-case.py` (run with the vault .venv; SHOW=reset / SHOW=1 for the viewer on port 3939, one client only).
- Print file: `iphone-15-pro-max-case-print.3mf`, real slice 53 min, 29.4 g, no supports. Regenerate with `pipeline/make_print_3mf.py` after any geometry change, then `pipeline/sections.py` and `review_page.py`.
- Notes: brief.md (full decision log), knowledge/learnings/iphone-15-pro-max-case.md, knowledge/tpu-x2d.md (seed, unvalidated).

## Next
1. Get Brian's MagSafe piece sizes (ring OD, ID, thickness; alignment piece length, width), set `MAG_*`, rerun model, sections, make_print_3mf, review_page.
2. Brian's sign-off in the viewer, then first print; record measured fit, bridge sag, stringing, glue joint in the retrospective and tpu-x2d.md.
