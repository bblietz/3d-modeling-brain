---
name: project-iphone-case
description: iPhone 15 Pro Max TPU 95A HF case - CAD complete 2026-09-20 (glue-on camera guard v4 with locating plug, MagSafe pocket for a standard 0.4 mm ring); waiting on Brian's sign-off and the first print
metadata:
  type: project
---

Slim case for Brian's iPhone 15 Pro Max in Bambu TPU 95A HF, X2D 0.4 nozzle: `projects/iPhone-15-Pro-Max-case/` (brief.md has every locked decision with Brian's words; source `iphone-15-pro-max-case.py`, build123d; retrospective [[iphone-15-pro-max-case]]; materials seed `knowledge/tpu-x2d.md`).

Locked by Brian on 2026-09-20: 1.5 mm walls (his "~5mm" was a slip), open cutout windows with no button covers, a camera guard as a SEPARATE ring printed flat and bonded with flexible CA (chosen over printing screen-side down on supports). The guard took four versions, each corrected within minutes of him seeing the viewer: SNUG around the raised camera island, SLIM, PLAIN (he rejected dished cutaways for Apple's flash and LiDAR keepout cones), bevelled on the inside of its rim, and NO bevel inside the case ("only the guard has a bevel"), so the case has a plain square cutout and the ring carries a square plug that drops into it. MagSafe: a pocket in the phone side of the back for his ring, "the standard size. .4mm thick" (pocket locates by the 46 ID, takes 54 to 56.5 OD, 0.8 deep, 0.8 mm of back behind it; alignment-piece pocket at Apple's position).

All phone geometry comes from Apple's own dimensional drawing (developer.apple.com/accessories/dimensional-drawings/); Apple's PDFs and sheet renders are gitignored (title block: do not reproduce). Real slice: 51 min, 29 g, no supports. Next: his sign-off in the viewer, first print, then measured fit into the retrospective. See [[feedback-cosmetic-parts-viewer-first]], [[reference-x2d-preset-includes]].
