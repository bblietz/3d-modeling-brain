# Handoff: iPhone 15 Pro Max case (2026-09-20)

## Decisions already locked (Brian)
- iPhone 15 Pro Max; 1.5 mm walls; open cutout windows, no button covers; X2D 0.4 nozzle; case in Bambu TPU 95A HF.
- Camera guard required, as a SEPARATE ring. "the guard should be petg and snap into place": rigid PETG, no glue (supersedes the flexible CA bond), the TPU case does the flexing.
- Guard snug around the raised camera island, slim (rim 3.0 mm), plain (NO cutaways for Apple's flash/LiDAR cones), 1.5 mm 45 degree bevel on the inside of the rim.
- NO bevel inside the case around the camera: from inside, a plain square-edged cutout. The barb's groove is buried in the cutout's wall under a 45 degree roof.
- MagSafe pocket: Brian's ring is "the standard size. .4mm thick". Pocket in the phone side of the back, centred on the product centre, locates the ring by its 46 ID, takes 54 to 56.5 OD, 0.8 deep with 0.8 mm of back behind it; alignment-piece pocket at Apple's position.
- "The 3mf file should be 2 plates, one for the guard and one for the case": plate 1 case (TPU 95A HF, filament 1), plate 2 ring (Bambu PETG Basic, filament 2), both on extruder 1.

## State
- CAD complete and self-checking: `iphone-15-pro-max-case.py` (run with the vault .venv; SHOW=reset / SHOW=1 for the viewer on port 3939, one client only). Snap constants `SNAP_*`; the snap is asserted on the real solids (seated clear, held when pulled, stopped when pushed, meets only the flap on the way in).
- Print file: `iphone-15-pro-max-case-print.3mf`, two plates, real slices: case 54 min 27.5 g, ring 11 min 2.0 g, no supports. NOT yet opened in the Bambu Studio GUI (ground truth for authored plates). Brian had the old one-plate file open in Studio on 2026-09-20: it must be reopened.
- After any geometry change: the model, then `pipeline/sections.py`, `pipeline/renders.py`, `pipeline/make_print_3mf.py`, `review_page.py`.
- Notes: brief.md (full decision log), knowledge/learnings/iphone-15-pro-max-case.md, knowledge/tpu-x2d.md (seed, unvalidated).

## Next
1. Brian's sign-off in the viewer and a look at the 3MF in Studio (two plates, right filament on each), then the first print.
2. Record in the retrospective and tpu-x2d.md: cavity fit, bridge sag, stringing, and the snap (insertion effort, hold, the barb's overhang steps, neck fit). There is no snap-fit data in the vault yet: these will be the first numbers.
