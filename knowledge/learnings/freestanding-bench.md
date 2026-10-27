---
type: learning
project: Freestanding-bench
created: 2026-10-26
status: designed, not built
tags: [furniture, bench, freestanding, undermount, blum, robot-vacuum]
---

# Freestanding alcove bench: retrospective (design phase)

Links: [[Freestanding-bench]] brief in `projects/Freestanding-bench/brief.md`, model `freestanding_bench.py`; forked from [[built-in-bench]] on 2026-10-26 when the client went from built-in to freestanding with a robot vacuum underneath. Related: [[feedback-photo-composite-cad-overlay]], [[feedback-html-visual-companion]], [[feedback-cutlist-inches-only]].

## What worked

- A redesign that keeps the old one goes in a new project folder with its own model, pipeline and artifact URLs. Copying the model and changing the base left every Blum rule, every housed-joint probe and the drawer code untouched; the new asserts are about the floor gap (nothing but the base below CLEAR, the base meets the case bottom, the back legs clear the baseboard, the leg screws land under the boxes and not under the runners).
- One BASE env var in the model gives three bases from one file. The viewer renders and the true-scale room overlays of all three took minutes, and the options page shows the real model, not sketches. Brian picks against pictures; the shop page documents the recommended one and the others are a rerun.
- Two forks in parallel (drawings; assembly steps plus page builder) while the main thread did the viewer and the picture. Both were told not to touch the viewer and not to call Gemini; the captures ran afterwards from one place. Every number in their output came from the model's constants, checked row by row against the cut list.
- One guided Gemini pass on the recommended base before the pick, not the whole chain: $0.165 for a checked room picture; the dogs and props wait so they are not redrawn three times. The guided prompt describes the piece without a single dimension (the overlay carries the geometry) and it held every edge; the soffit's underside even came out white this time.

## Decisions worth reusing

- Clearance for a robot vacuum: take the tallest current model (the lidar Roombas, about 3.9 in), add an inch, and say what a rug costs (1/4 to 1/2 in). Five inches; four and a half would scrape a lidar model on a rug.
- At a fixed seat height the clearance comes straight out of the drawers (8-1/2 to 6-1/2 in here). Put the seat-height question to the client with the drawer numbers next to it.
- A top with a rear overhang costs case depth: here it would have pushed the case past Blum's 557 mm minimum for a 21 in runner by 3 mm, so the top is flush with the case back. Check the slide's inside-depth rule before giving a freestanding top an overhang all round.
- A base that lets a robot in is a C-frame: end rails and a back rail under the case, no front rail; the legs inset so the back ones clear the baseboard and shoe (2 in inside the case back) and the bench pushes to the wall with the baseboard left in place.
- Gable ends to the floor need a notch for the baseboard and tie the piece to one alcove; legs and blades do not.
- When the case ends become show faces, the fronts overlay them with a small reveal (1/16) instead of scribe strips, and the ends' front and bottom edges get banded.

## Tooling notes

- A hero capture with the same scene as an earlier capture legitimately has the identical byte count (57512 twice here); the stale-tab test is a byte count that does not change when the scene did. Compare against a capture of a different scene.
- `photo_match.py check` measures the front legs as the longest warm, bright run in the leg's projected column; the back legs are hidden behind the case from this camera and are skipped. The pulls remain the height check (within 1/4 in again).
- Crops for an options page: the viewer PNG cropped to its content, and the overlay cropped to the alcove at photo scale, both straight from the files the pipeline already makes.

## 2026-10-26, round two: the legs were wrong

- "Look at the legs for the other bench we designed and let's start there." A base I invented (short legs under a box) lost to the construction Brian already owns: the drawer bench's proud chamfered corner posts with the panels housed in them. Before inventing a base for a second piece, start from the one the first piece has; the vault holds it.
- Five options of one construction (post size and foot) beat three different constructions. Brian picked by size (2-1/2 in for a 14 in piece); the foot details were not the question.
- The superpowers visual companion worked for this: `leg_options.py` built a shell per option, the OCP viewer captured a full view and a foot close-up, the crops went into the companion's content folder as `/files/<name>` and one screen of five cards did it. `Plane.XZ` in build123d has its normal toward -Y, so a mirror "about Y = ymid" needs `Plane(origin=(0, ymid, 0), z_dir=(0, 1, 0))`, or the rear posts land far behind the bench.
- Corner posts in an alcove stand where the baseboard is. With the top held 3 in back from the pilasters the 21 in runners need every millimetre behind the fronts, so the choices were: notch the rear posts over the baseboard (done, 1-1/2 x 4-1/2, skippable), a 1/2 in back instead of 3/4, and 1/4 in to the wall. Standing the bench off the baseboard would have meant 18 in runners. Check the slide depth before the post layout, not after.
- The post-side runners mount the drawer bench's way (front screws into the post, Blum rear bracket on the back), the partition side the frameless way; the case bottom under the runners is notched around the posts. Two mounting styles on one drawer are fine as long as both references are level.
- Gemini: props and the client's dogs in one pass with four input images made it rebuild the scene as the reference picture (cropped, built in, no posts), $0.172 gone; the check caught it (no pulls, no posts found). Two passes, each with one reference set, held every edge. Keep one job per reference set.
- `check` on the styled picture reads the left pull short (5.8 in) because the throw's corner covers its end; the center offset says so (+1 in). Read the measurements against the styling before calling an error.

## Not yet measured

Nothing is cut. Still to confirm on site: the opening at every height (the 64 in top needs 66 in everywhere), the baseboard and shoe projection (the model assumes under 1-1/4 in), the receptacle behind the case.
