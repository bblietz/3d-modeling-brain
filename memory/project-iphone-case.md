---
name: project-iphone-case
description: iPhone 15 Pro Max TPU 95A HF case - CAD complete 2026-09-20 (PETG camera guard v5 that snaps in, MagSafe pocket for a standard 0.4 mm ring, two-plate 3MF); waiting on Brian's sign-off and the first print
metadata:
  type: project
---

Slim case for Brian's iPhone 15 Pro Max in Bambu TPU 95A HF, X2D 0.4 nozzle: `projects/iPhone-15-Pro-Max-case/` (brief.md has every locked decision with Brian's words; source `iphone-15-pro-max-case.py`, build123d; retrospective [[iphone-15-pro-max-case]]; materials seed `knowledge/tpu-x2d.md`).

Locked by Brian on 2026-09-20: 1.5 mm walls (his "~5mm" was a slip), open cutout windows with no button covers, a camera guard as a SEPARATE ring printed flat (chosen over printing screen-side down on supports); first glued TPU, then "the guard should be petg and snap into place" (rigid PETG, no glue: barb on the ring's plug, groove buried in the cutout's wall, a 0.6 mm flap of TPU as the spring; unproven until printed). The guard's shape took four versions, each corrected within minutes of him seeing the viewer: SNUG around the raised camera island, SLIM, PLAIN (he rejected dished cutaways for Apple's flash and LiDAR keepout cones), bevelled on the inside of its rim, and NO bevel inside the case ("only the guard has a bevel"), so from inside the case the cutout is a plain square-edged hole and the ring carries a plug that goes into it. MagSafe: a pocket in the phone side of the back for his ring, "the standard size. .4mm thick" (pocket locates by the 46 ID, takes 54 to 56.5 OD, 0.8 deep, 0.8 mm of back behind it; alignment-piece pocket at Apple's position).

All phone geometry comes from Apple's own dimensional drawing (developer.apple.com/accessories/dimensional-drawings/); Apple's PDFs and sheet renders are gitignored (title block: do not reproduce). Print file: "The 3mf file should be 2 plates, one for the guard and one for the case": plate 1 case in TPU 95A HF (54 min, 27.5 g), plate 2 ring in Bambu PETG Basic (11 min, 2.0 g), no supports, both on extruder 1. Next: his sign-off in the viewer, his opening the two-plate 3MF in Studio (GUI is ground truth), first print, then measured fit and the vault's first snap-fit numbers into the retrospective. See [[feedback-cosmetic-parts-viewer-first]], [[reference-x2d-preset-includes]], [[reference-two-material-two-plate-3mf]].
