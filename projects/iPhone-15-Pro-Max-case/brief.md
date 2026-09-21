---
type: project
project: iPhone-15-Pro-Max-case
date: 2026-09-20
status: CAD COMPLETE 2026-09-20 (guard ring v4: slim, snug, bevelled rim, square plug into a plain cutout; MagSafe pocket for Brian's standard 0.4 mm ring). Awaiting Brian's sign-off in the viewer, then the first print. Not printed yet.
tags: [x2d, tpu, phone-case, iphone]
---

# iPhone 15 Pro Max case (TPU 95A HF)

A slim, form-fitting case for Brian's iPhone 15 Pro Max with open button windows and a glue-on camera guard ring, printed in Bambu TPU 95A HF on the X2D. First TPU project in the vault ([[tpu-x2d]], [[printer-x2d]]). Retrospective: [[iphone-15-pro-max-case]].

## Decisions already locked (Brian, 2026-09-20)

- Phone: iPhone 15 Pro Max (Brian wrote "iPhone 15 Max Pro"; there is no other 15 Max model).
- Wall thickness: 1.5 mm. The original ask said "thin ~5mm"; Brian confirmed 1.5 mm when asked.
- Buttons: NO button covers. Action button, volume up, volume down and the side button get open cutout windows ("These should be cutout holes").
- Nozzle: 0.4 mm on the X2D.
- Filament: Bambu TPU 95A HF, stock preset `Bambu TPU 95A HF @BBL X2D 0.4 nozzle`.
- Camera guard: REQUIRED ("make sure it has a camera guard built in"). The lenses stand 4.07 mm above the back glass, so the guard stands 3.4 mm proud of the 1.6 mm back; with the back on the bed that would be below the bed plane. Brian chose, from three options: TWO PIECES, a guard ring printed flat and bonded on with flexible CA glue. Rejected: one piece printed screen-side down on TPU supports (double time, rough inside floor); one piece back-down with the whole outside back on supports (rough visible back). Printing on edge is out: a 160 mm tall 1.5 mm TPU channel deflects about 15 mm under nozzle drag.
- Guard fit: SNUG around the camera. Brian, on seeing the first ring in the viewer: "the camera on the phone is correct, but the guard around it is too big. It should be snug around the camera." The first ring followed Apple's "plateau outer boundary", which is the base of the glass ramp, 4 mm off the raised island.
- Guard shape: SLIM, PLAIN, BEVELLED INSIDE. On the second ring (snug, 5.1 mm wide, with Apple's flash and LiDAR keepout cones cut out of it as two dished cutaways): "the ring is too thick and there are cutouts in the top right and bottom right. Not good", then "the guard should also be a bevel on the inside". So no cutaways: the ring crosses Apple's flash-outer and rear-sensor cones, as most commercial cases do (told to Brian: possible slight flash haze with light TPU; dark TPU avoids it).
- Inside of the case: NO bevel around the camera. On the third ring (the case floor sloped in over the glass ramp to carry the snug ring): "the inside of the case, around the camera should not have a bevel, only the guard has a bevel". So the case has a plain square-edged cutout and the ring carries a square plug that drops into it.
- MagSafe: "add a magsafe ring so I can insert the metal pieces"; "the ring is the standard size. .4mm thick".

## Design as built (mine unless marked; all numbers are constants at the top of the source)

- Backend: build123d, canonical source `iphone-15-pro-max-case.py`. Every phone dimension is from Apple's dimensional drawing (`reference/iphone-15-pro-max-dimensions.md`): body 76.73 x 159.86 x 8.25, spline corners traced through Apple's ordinate points, Apple's edge cross-section.
- Case 79.93 x 163.06 x 10.8 mm, 23.8 cm3. Side walls 1.5, back 1.6 (8 layers), cavity 0.10 larger than the phone per side (printed TPU cavities come out a little small, and a case should grip).
- Screen lip: a 45 degree underside that leans in over the phone (a hook, checked in `images/section-lip.png`), 0.05 mm off the phone's shoulder at the point where Apple's edge profile is also at 45 degrees. Tip 0.85 mm in from the housing edge (glass starts at 1.00; Apple's drawing says do not touch the glass). Stands 0.95 mm proud of the screen (Apple: 0.85 min, 1.00 ideal).
- Windows, all centred on the band's mid plane: Action 8.04 long, volume up and down share one 27.4 long window (the buttons are only 3.0 apart), side button 19.7 long; each 5.0 tall inside, flaring 45 degrees to 6.5 outside, top and bottom only. Bottom: USB-C 13.0 x 7.0 (Apple asks 12.45 x 6.60 plus margin) and two acoustic slots 2.0 mm clear of the outermost holes (Apple's thin-case rule). Posts: 2.93 between Action and volume, 2.02 each side of USB-C.
- Camera opening: a plain square-edged cutout, 0.4 mm outside the base of the glass ramp that surrounds the camera island (Apple's plateau outer boundary, 44.18 x 45.50 with spline corners). Nothing inside the case is bevelled. It runs to within 1.04 mm of the top and side-button edges, so a 0.74 mm ledge of floor is left there.
- Guard ring (fourth version): a rim and a plug. Rim 3.0 mm wide, 3.4 mm tall, 1.5 mm 45 degree bevel on its inside, 0.5 chamfer on its outside top edge; inside wall 1.56 mm off the island's flat top; top 5.0 mm above the back glass, so the lens glass (4.07) is 0.93 mm off a table. It overlaps the case's back by 0.5 mm all round the cutout (height stop and glue land). Plug: square, 1.64 mm wall, 0.6 mm tall (3 layers), 0.15 smaller than the cutout all round; it locates the ring for gluing and carries the snug rim over the glass ramp (its inside wall is 0.4 mm off the ramp proxy at its lower face). Prints as it is glued, rim face on the bed, plug on top; the only overhangs are the rim's two 45 degree faces. The model still asserts Apple's three camera cones and the flash inner cone against the ring, and reports the accepted crossings (flash outer 3.4 mm3, rear sensor 58.3 mm3).
- MagSafe pocket: in the phone side of the back, so the phone holds the pieces in and nothing shows. Brian's ring is the standard size, 0.4 mm thick. Position and the alignment piece follow Apple's case array (ADG R30 Fig 42-2 to 42-4; `reference/iphone-15-pro-max-dimensions.md` section 16): ring centred on the product centre (the model origin) within 0.30, 46.00 ID; clocking magnet 6.00 x 19.31 from 31.18 to 50.49 below the ring centre toward the bottom edge. "Standard" metal rings on sale run 54 to 56 mm OD (Apple's own is 54.10) with the same 46 ID, so the pocket locates the ring by its inside edge (45.5) and takes any OD up to 56.5 (pocket 57.0). Depth 0.8 (4 layers), deeper than the 0.4 ring needs on purpose: the ring sits 0.4 below the floor's surface, off the phone's glass (Apple: no metal contact with the product), and 0.8 mm (4 layers) of back stays between the ring and the accessory (Apple allows at most 0.85). 4.0 mm clear of the guard ring. Leave the alignment pocket empty if the kit has no alignment piece. Constants `MAG_*` at the top of the source.
- Print orientation: case back on the bed, ring rim face on the bed (plug up), no supports. Only overhangs: the six window roofs (68 mm2 of bridge in all) and the rounded window ends.

## Open risks for the first print

- The volume window's roof is a 22 mm TPU bridge (side button 15 mm, speaker slot 11 mm). The wall lines run along the bridge, the best case, but some sag is likely; it is cosmetic.
- Fit is unproven: cavity clearance 0.10 per side and the lip's 0.05 gap are my first guesses for TPU 95A HF.
- The plug's inside lower corner is 0.2 mm (normal) off my straight-ramp proxy of the camera glass. The real ramp is a concave fillet (not dimensioned by Apple) and sits lower.
- The plug is 0.15 smaller than the cutout all round: first guess for a TPU-in-TPU drop fit. If it is tight, the first-layer elephant foot on the case's cutout is the likely cause.
- MagSafe ring OD not measured ("standard size"); the pocket takes 54 to 56.5. A steel attach ring (0.4 mm suggests steel, not magnets) is outside Apple's rules (permeability 1.05 max) but common on DIY cases; functional risk only (charging heat, compass).
- The ring crosses Apple's flash-outer and LiDAR cones (Brian's call). Watch for haze in flash photos on the first print; a dark TPU is the fix.

## Files

- `iphone-15-pro-max-case.py`: the model, its checks, STL export, viewer push (`SHOW=reset` first, `SHOW=1` after).
- `iphone-15-pro-max-case.stl`, `camera-guard-ring.stl`: both in print orientation.
- `iphone-15-pro-max-case-print.3mf`: Bambu project, both parts on one plate, X2D 0.4 nozzle, 0.20 mm Standard, Bambu TPU 95A HF, Textured PEI; Arachne, 4 wall loops, 100% infill, avoid crossing walls. Real slice: 51 min, 29.3 g (29.5 g if perfectly solid), 54 layers (`iphone-15-pro-max-case-print-slice.json`).
- `pipeline/make_print_3mf.py`: builds and slice-verifies the 3MF. `pipeline/sections.py`: section close-ups from the real meshes. `review_page.py` writes `review.html`.
- `images/`: section close-ups and renders. `build/` (gitignored): staged STLs, phone proxy, assembly meshes.
- `reference/iphone-15-pro-max-dimensions.md`: the dimension table. Apple's two PDFs and the `adg-*.png` sheet renders stay local (gitignored): Apple's title block says do not reproduce; re-download from the URLs in that note.

## Gluing the ring

Flexible (rubber-toughened) CA, gel if possible. Phone out. The plug under the ring drops into the case's camera cutout from the outside, so the ring locates itself (the cutout is 1.3 mm taller than wide: one way only). Glue on the underside of the rim's overlap and on the plug's outside wall; press the rim flat against the back.

## Printing notes

TPU 95A HF is not an AMS filament: feed from the external spool, and dry it first. Brian slices and sends from Bambu Studio; the GUI opening the 3MF is ground truth for the settings.
