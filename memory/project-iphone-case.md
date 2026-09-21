---
name: project-iphone-case
description: iPhone 15 Pro Max TPU 95A HF case - CAD complete 2026-09-20 (slim snug bevelled glue-on camera guard, MagSafe pocket to Apple's nominal array); waiting on Brian's MagSafe piece sizes and sign-off; not printed yet
metadata:
  type: project
---

Slim case for Brian's iPhone 15 Pro Max in Bambu TPU 95A HF, X2D 0.4 nozzle: `projects/iPhone-15-Pro-Max-case/` (brief.md has every locked decision with Brian's words; source `iphone-15-pro-max-case.py`, build123d; retrospective [[iphone-15-pro-max-case]]; materials seed `knowledge/tpu-x2d.md`).

Locked by Brian on 2026-09-20: 1.5 mm walls (his "~5mm" was a slip), open cutout windows with no button covers, a camera guard as a SEPARATE ring printed flat and bonded with flexible CA (chosen over printing screen-side down on supports), the guard SNUG around the raised camera island, SLIM (2.5 mm), PLAIN (he rejected dished cutaways for Apple's flash and LiDAR keepout cones) with a 1.5 mm bevel on the inside. He then asked for a MagSafe ring pocket "so I can insert the metal pieces": built in the phone side of the back to Apple's nominal case array (ring 54.10/46.00 x 0.55 centred on the product centre, clocking magnet 6.00 x 19.31 toward the bottom; 0.8 deep, 0.8 mm of back behind it). The size of his own pieces was asked and is still unanswered; the `MAG_*` constants take them.

All phone geometry comes from Apple's own dimensional drawing (developer.apple.com/accessories/dimensional-drawings/); Apple's PDFs and sheet renders are gitignored (title block: do not reproduce). Real slice: 53 min, 29 g, no supports. Next: his MagSafe piece sizes, his sign-off in the viewer, first print, then measured fit into the retrospective. See [[feedback-cosmetic-parts-viewer-first]], [[reference-x2d-preset-includes]].
