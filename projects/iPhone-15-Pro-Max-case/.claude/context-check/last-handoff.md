# Handoff: iPhone 15 Pro Max case (2026-09-20)

## Decisions already locked (Brian)
- iPhone 15 Pro Max; 1.5 mm walls; open cutout windows, no button covers; X2D 0.4 nozzle; Bambu TPU 95A HF.
- Camera guard required, as a SEPARATE ring printed flat and bonded with flexible CA.
- Guard snug around the raised camera island, slim (rim 3.0 mm), plain (NO cutaways for Apple's flash/LiDAR cones), 1.5 mm 45 degree bevel on the inside of the rim.
- NO bevel inside the case around the camera: plain square cutout; the ring has a square plug that drops into it.
- MagSafe pocket: Brian's ring is "the standard size. .4mm thick". Pocket in the phone side of the back, centred on the product centre, locates the ring by its 46 ID, takes 54 to 56.5 OD, 0.8 deep with 0.8 mm of back behind it; alignment-piece pocket at Apple's position.

## State
- CAD complete and self-checking: `iphone-15-pro-max-case.py` (run with the vault .venv; SHOW=reset / SHOW=1 for the viewer on port 3939, one client only).
- Print file: `iphone-15-pro-max-case-print.3mf`, real slice 51 min, 29.3 g, no supports. Regenerate with `pipeline/make_print_3mf.py` after any geometry change, then `pipeline/sections.py` and `review_page.py`.
- Notes: brief.md (full decision log), knowledge/learnings/iphone-15-pro-max-case.md, knowledge/tpu-x2d.md (seed, unvalidated).

## Next
1. Brian's sign-off in the viewer, then first print; record measured fit, bridge sag, stringing, glue joint in the retrospective and tpu-x2d.md.
