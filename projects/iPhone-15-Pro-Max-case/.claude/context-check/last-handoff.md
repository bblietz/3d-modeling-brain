# Handoff: iPhone 15 Pro Max case (2026-09-20)

## Decisions already locked (Brian)
- iPhone 15 Pro Max; 1.5 mm walls; open cutout windows, no button covers; X2D 0.4 nozzle; Bambu TPU 95A HF.
- Camera guard required, as a SEPARATE ring printed flat and bonded with flexible CA.
- Guard snug around the raised camera island, slim (2.5 mm), plain (NO cutaways for Apple's flash/LiDAR cones), 1.5 mm 45 degree bevel on the inside.
- MagSafe ring pocket requested ("add a magsafe ring so I can insert the metal pieces"): IN PROGRESS. Need the dimensions of his pieces (ring OD, ID, thickness; alignment bar size). Apple's array geometry is being appended to reference/iphone-15-pro-max-dimensions.md section 16 by a research agent.

## State
- CAD complete and self-checking: `iphone-15-pro-max-case.py` (run with the vault .venv; SHOW=reset / SHOW=1 for the viewer on port 3939, one client only).
- Print file: `iphone-15-pro-max-case-print.3mf`, real slice 52 min, 30.2 g, no supports. Regenerate with `pipeline/make_print_3mf.py` after any geometry change, then `pipeline/sections.py` and `review_page.py`.
- Notes: brief.md (full decision log), knowledge/learnings/iphone-15-pro-max-case.md, knowledge/tpu-x2d.md (seed, unvalidated).

## Next
1. MagSafe pocket on the INSIDE of the back (captured by the phone), centred on the product centre (model origin), sized to Brian's pieces; keep at least 0.6 mm of TPU behind it.
2. Brian's sign-off in the viewer, then first print; record measured fit, bridge sag, stringing, glue joint in the retrospective and tpu-x2d.md.
