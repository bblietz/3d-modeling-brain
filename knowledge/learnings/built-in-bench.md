---
type: learning
project: Built-in-bench
created: 2026-10-07
status: designed, not built
tags: [furniture, bench, built-in, undermount, blum, frameless, tongue-and-groove]
---

# Built-in alcove bench: retrospective (design phase)

Links: [[Built-in-bench]] brief in `projects/Built-in-bench/brief.md`, model `built_in_bench.py`, shop page `cutlist.html`. Related: [[drawer-bench]], [[feedback-cutlist-inches-only]], [[feedback-cutlist-hero-image]], [[feedback-figure8-recess-offset]].

## What worked

- Options tool before CAD. Brian's picks came back as one pasted block and two follow-up sentences; no design churn in the model.
- A research subagent on Blum's own PDFs before the asserts were written. It caught that Blum's 2022 and 2025 sheets changed the 563H box height to opening minus 21 mm (7 mm top gap), that the rear notch is measured from the inside face of the drawer side, that the 13 mm recess runs to the underside of the bottom, and that the 563H locking devices are the T51.1901 family (T51.1700.04 is for 554H).
- Probe asserts caught my own mistake: the "wood between bore and groove" probe failed because I had the box x origin sign flipped in the probe, not because the geometry was wrong. Compute probe positions from the solids' bounding boxes, not from re-derived arithmetic.
- SUBSET env var in the model to export partial STLs (case, one front, one drawer, no cushion) made the matplotlib renders readable at this size.

## Decisions worth reusing

- Undermount drawer back in 3/4 stock with a 3/16 bottom groove: Blum's hook bore is 10 mm deep into the rear face at 24 mm up, right behind a 1/2 in bottom's groove. 18 mm minus 4.76 leaves 3.2 mm of wood past the bore; with a 1/4 groove it is 1.65 mm, too thin.
- 3/4 box front too: the T51.1901 locking devices screw into the box front below the bottom, and Blum names sub-front splitting as a failure mode.
- Frame-and-panel drawer front with a tongue-and-groove bit set: stiles grooved through, rails grooved plus stub tenons from the same cutter, plywood panel with a tongue all round glued in. The tenon end shows on the stile top; Brian accepted that.
- When the drawer box top sits above where a front stretcher would go, use a nailer on edge at the top back (figure-8s for the top, wall screws through it) and pocket screws into the top at the front. No front stretcher.
- Scribe strips wide enough to cover the end panels' front edges (1 in scribe plus the ply) are easier to attach than a 1 in strip hanging past the panel.

## Tooling notes

- Assembly steps as viewer screenshots: keep one STEPS list (file stem, title, instance prefixes, text) in `assembly_shots.py` and import it in the page builder, so the pictures and the words cannot drift. Parts already in place go pale grey, new parts keep their wood colors. Park the mouse with `xdotool mousemove 2 2` before each capture; the viewer tints the face under the pointer blue.

- The OCP viewer screenshot only works with the GPU Chrome tab open; `scripts/cad-viewer.sh` opens it. `pgrep -f cad-viewer-chrome` matches the pgrep command's own shell line, so check with `curl` plus a look at the screenshot result instead.
- `cutlist.csv` rounds mm to 0.1, so a part at a 1/32 rounding edge can print differently in `cutlist.md` and the page. Set nominal constants (the 1/4 back is 6.35 in the model) so derived lengths land on clean fractions.

- PDF of the shop page: headless Chrome `--print-to-pdf --no-pdf-header-footer` with an `@media print` block in the page. Wrap each group heading and its first row in one `break-inside: avoid` block, or a page break strands the heading; cap drawing heights (3.6 in) so two rows fit a page; hide the tick boxes and tap captions.

## Not yet measured

Nothing is cut. Record actual ply thicknesses, the alcove's three widths, and the drawer fit against Blum's rules here when the bench is built.

## 2026-10-09 revisions

- An inset panel in a flush-thickness frame needs a thinner panel set back-flush; with only 3/4 walnut ply the options were a 1/4 maple lip on the frame or 1/2 ply. Do not plane plywood (veneer, glue lines, unbalanced).
- The "same thickness" trap: the groove position now comes from the panel thickness (GY0 = back face + panel thickness - tongue), not from centering. Panels of 12 mm ply (nominal 1/2) make the groove front wall 6 mm.
- 1/2 in box backs cannot take a bottom groove and Blum's 10 mm hook bore (12 - 10 = 2 mm skin). Bottom butts the back instead. Unverified against Blum's sheets.
- Painted parts get their own white color in hero_shot.py and assembly_shots.py (PAINTED set); picture composites by Gemini are mood only and predate geometry changes.

## 2026-10-23: a composite the client can sign off on

- Gemini cannot hold a dimension given in words. "The wood top is 14 inches above the floor" produced a bench about 20 in tall (measured against its own 66 in width), twice. Treat any dimension in a prompt as decoration.
- What works: camera-match the photo (`photo_match.py`: the alcove's four floor corners give distance, focal length, camera height and lateral offset in closed form; the 8 ft ceiling checks the fit to 2 in), z-buffer the CAD solids into the photo flat-shaded at true scale, and have Gemini photorealize that overlay with a prompt that forbids moving an edge (`render_in_room.py guided`). One call, $0.17, and the output's edges land on the projection.
- Always verify: `photo_match.py check <image>` draws the projected outline over the output and measures the walnut panels in inches. A detector that looks for "dark" rows catches the overhang's shadow on white paint; it must test for brown (R well above B), not just dark.
- The 4x corner crops with pixel ticks were the reliable way to read the floor corners; a first-dark-pixel column scan was fooled by the baseboard's shoe shadow.
- Styling goes on as a second, separate edit of the verified picture (`styled` job: the verified image plus the client's reference as image 2), never in the same call that photorealizes the overlay. Gemini kept every edge in place while adding a dog, pillows, a throw and shelf objects; the check still passed to 1/4 in. Props can hide a measuring column (the throw covered the left panel's quarter point), so the check measures a quarter in from either end and keeps the column with the longest walnut run; a "found something" fallback is not enough, because a stripe of the throw's fringe reads as a 1 in walnut run.
- Real pets from snapshots: one photo each (lying on a beach, standing with a ball) was enough for Gemini to put faithful likenesses on the cushion in new poses at the right relative size, as a third edit stage on top of the styled picture. Tell it to ignore the people and the setting in the snapshots.
- Gemini keeps the overlay's colors, even when the prompt says they are placeholders. A flat-shaded box face turned away from the light rendered grey, and three passes in a row kept it as a blue-grey ceiling. Render overlay surfaces in roughly their finished color (the soffit is now nearly unshaded paint white), and when a color still comes out wrong, fix it with a separate repaint edit of the output rather than another run from the overlay. Every rerun also re-rolls the details: one rerun corrupted the sign's lettering, so look at the words after each pass.
- Adding geometry to an already photoreal picture: `photo_match.py soffit <picture>` z-buffers just the new solids onto the Gemini output at its own pixel size (the projection scaled by the size ratio), so a new element can join at any stage of the chain without redoing the earlier ones.
- Read a terse note against the reference before acting on it. "The soffit is flush with the front and then extends over the hallway" described the concept picture (a bulkhead in the pilasters' plane, continuous across their tops and on over the hallway opening); I read it as a fault report about a beam, set the box 3 in back, and Brian saw no change. When a note could be either a description of the target or a complaint, open the reference first; the answer was in it.
- Compare the new picture with the old one before claiming a visible change. From this camera a 3 in move at the soffit is 6 to 14 px, and the two versions were indistinguishable. Below about 25 px nothing counts as a change the client can see.
- Measure the ceiling through the solved camera instead of trusting "about 8 ft": the pilaster tops put it at 98.6 in and the back wall's top edge at 98.0. With the band's top drawn at 96 a strip of old ceiling showed above it in three versions and read as the soffit hanging short of the ceiling.
- Where the photo ends matters: the bulkhead runs 36 in past the right pilaster so it leaves the frame, and it stays 28 in deep because the only thing behind the hallway opening is an angled wall 47 to 84 in back (its ceiling line inverted through the camera); a deeper box would have painted over that wall.
- A material change on a finished picture is one repaint edit of the last stage (`walnut-shelves`: maple shelves to walnut, $0.157, every object on them kept, edges still on the projection), not a rerun of the chain, which would re-roll the dogs, the props and the sign. Change the overlay color and the earlier prompts in the same commit so a later rerun from the first stage agrees with the picture on the page.
- A change below the visibility threshold still has to be proven, just not by eye on the full frame: the top's front edge is about 7 px tall from this camera, so the `walnut-top` pass was verified by sampling the strip's pixels through the matched camera (pale 204/157/142 to walnut 130/69/61) and a zoomed before/after crop, and Brian was told up front that the full picture barely shows it. Claiming a visible change there would have earned another "i dont see a change".
- A material change that is in the cut list (the top, unlike the shelves) touches six places: the PARTS material string in `built_in_bench.py`, the color maps in `hero_shot.py` and `assembly_shots.py`, the sheet header in `part_drawings.py`, the material order and labels in `make_cutlist_page.py`, and the overlay color plus prompts in the picture chain. Grep for the old material name across the project before declaring it done.
- Painted panels leave `check` nothing brown to measure, so it falls back to the brass pulls (8 in long, centered on each front). Gemini's brass is a dull antique tone, about 170/119/98: test red over blue by 40, green over blue by only 12, brightness over 100 (walnut fails brightness, white paint and linen fail red over blue). The bar's end pixels drop out, so the measured length undercounts by about an inch; the center position is the number to trust. A short brown run (the throw's fringe) still passes the walnut test, so the panel measurement is skipped when the run is under half the panel height.
- The OCP viewer tab can stop taking pushes while `save_screenshot` keeps answering with the last frame: `hero_shot.py` wrote a file of the identical byte count (58391) after the model changed, and Version 16 of the shop page went out with a walnut hero over a white-and-maple cut list. Compare the byte count with the previous capture (or `git status` the image) before publishing a viewer screenshot; if it did not change, `pkill -f cad-viewer-chrome`, rerun `scripts/cad-viewer.sh`, and capture again.
- Requests that arrive together go into one pass (the bowls went with the panels, one call, one re-roll); a request that arrives after a pass has already been run and checked gets its own pass on that output instead of re-rolling a result that passed.
