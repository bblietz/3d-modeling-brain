---
type: project
project: Fishing-rod-holder
created: 2026-11-07
status: Options page published 2026-11-07; waiting on Brian's picks (pocket shape, printed comb vs caps on the wood, material, rods per comb, reels) before the CAD build.
printer: Bambu Lab X2D
material: PETG (recommended, not yet picked)
tags: [3d-print, garage, fishing, storage]
---

# Fishing rod holder (garage rafter)

## Request (Brian, 2026-11-07)

"Lets create a new project for a fishing rod holder." "The holder will hang from a rafter in my garage." Then a photo of the current wooden holders: "This is a picture of the wooden ones I have now. They don't work well at all. The longer one is 20 in from the bottom of the rafter, 27 in overall."

What fails (Brian, same day): "rods fall out when minimal force is applied. They stay in at steady state. They fall out when I am trying to get other rods out of the holder. Any bump on another rod makes it fall out."

## What exists today (read from the photo)

- Unfinished garage ceiling: exposed joists with a plywood floor above, looks like 2x8 at 16 in on center (to confirm; the 7 in of board above the joist bottom matches a 7-1/4 in 2x8 almost exactly).
- Two wooden combs, each a flat 1x4 screwed to the side face of a joist and hanging straight down. The near one is 27 in overall, 20 in below the joist bottom, with four semicircular notches cut into one edge; the far one is shorter with three notches. The notches open sideways, about 1-1/4 in across, roughly 5 in apart.
- Rods lie horizontally across the two combs, resting in the notches, running across the joists.
- The open garage door sits below the combs, so the hang below the joist is bounded; the current 20 in is the known-good depth.
- Several rods with foam grips are visible; reels not clearly visible. Count and reel positions to confirm.

## Diagnosis

A half-round notch cut into a vertical edge has its lowest point at the board edge, so the rod rolls down the arc and rests at the mouth with nothing in front of it. Steady state holds by a sliver of slope; a bump on a neighbour frees it. The fix is a pocket whose floor sits inside the plate behind a lip at the mouth (a hook pocket), so a rod has to rise the lip height before it can leave.

## Options page (2026-11-07)

Published: https://claude.ai/artifact/MuJqbgWZjUNzqSTMLFRt4H (source `options.html`, built by `pipeline/options_page.py` from `pipeline/concepts.py` drawings and `concepts-slice-petg.json`).

Drawn concept, option A everywhere: a 2-1/2 x 1/2 in plate on the joist side face, mount 4-1/2 in on the joist with three #8 x 1-1/2 screws, four hook pockets at 4 in pitch starting 4 in below the joist, hang 17 in (now 20). Pocket: lip 3/4 wide and 5/8 tall (the lift to leave), pocket 7/8 wide, mouth 1-1/4 tall, 1/4 in chamfers at the mouth. Three pieces because 256 mm is 10 in: mount 6-1/2, module 9-1/2 (two rods), end module 8-1/2 (two rods, rounded foot), half-laps 1-1/2 in long with two M4 bolts each.

Decisions on the page:
1. Pocket shape: A hook pocket (recommended, 5/8 in lift), B deep hook (1 in lift, sloped mouth, rod rolls in, pocket 3/8 taller), C snap clip (PETG spring, fits 5/16 to 7/16 blanks only).
2. What gets printed: A printed comb in three pieces (recommended), B printed caps screwed over the notches of the existing wood combs (cheapest fix: 2-3/4 x 3-1/4 x 3/8 in, mouth 1 in proud of the board edge).
3. Material: PETG recommended (garage heat, constant load); PLA and ASA shown scaled by density.
4. Rods per comb (2 / 4 / 6) and reels (off at 4 in pitch, or on at 5 in pitch).

Slice quotes (PETG, 2 walls, 15% infill, 0.30mm Standard, 0.6 nozzle; `pipeline/slice_stls.py`): mount 48.0 g / 59 min, module 55.6 g / 1 h 08, end module 50.6 g / 1 h 01; one comb 154 g / 3 h 08, pair 308 g / 6 h 16; cap 19.6 g / 28 min, seven caps 137 g / 3 h 16.

## Constraints known so far

- Load case: a few fishing rods, with or without reels, hanging all year in a garage. Light load, but constant, and the garage gets hot in summer. PLA creeps under a sustained load when warm; PETG is the baseline, ASA if the ceiling bakes. Grams and material are on the options page as a decision.
- Mounting: screws into the joist side face, like the wooden boards. Every screw hole gets a solid-infill pad in the 3MF (Brian's standing rule).
- Build volume 256 x 256 x 260 mm. A 17 to 20 in hang does not fit in one piece: modules with half-laps, or caps on a wooden backbone.
- Retention: the pocket gets a close-up section render with a rod cross-section before export, and a hold check against the way the rod goes in (lift over the lip, then sideways).

## Open

1. Brian's picks from the options page.
2. Rod inventory: how many rods, longest, reels left on and where they hang.
3. Joist size and spacing (assumed 2x8 at 16 in OC), comb spacing along the rods, and the mouth direction.
4. Copy of the photo into `images/` (it exists only in the chat so far).

## Files

- `projects/Fishing-rod-holder/brief.md` (this note)
- `projects/Fishing-rod-holder/options.html` (options page, published above)
- `projects/Fishing-rod-holder/concepts-slice-petg.json` (slice quotes behind the page)
- `projects/Fishing-rod-holder/pipeline/concepts.py` (parameters, 2D drawings, concept solids, OpenSCAD scene renders)
- `projects/Fishing-rod-holder/pipeline/slice_stls.py` (STL to grams and time through the Bambu CLI, memory-capped)
- `projects/Fishing-rod-holder/pipeline/options_page.py` (page generator)
- `projects/Fishing-rod-holder/images/concepts/` (why, scene-a, pockets, build, side, render-comb, render-pocket, render-cap)
