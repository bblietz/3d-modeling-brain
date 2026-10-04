---
type: project
project: Skateboard-wall-holder
date: 2026-10-04
status: design tool published, waiting for Brian to pick the concept and measure his truck
tags: [x2d, petg, wall-mount, skateboard, hook]
---
# Skateboard wall holder

Brian (2026-10-04): "create a wall holder for a skateboard. It should be narrow, and the board should rest on the center circular part of the skate board truck." Then: "provide a visual HTML tool to help guide the design."

## Design tool

- `hook-studio.html` in this folder, published as the Skate Hook Studio artifact: https://claude.ai/artifact/KLEtv2Tq6MH1gkTuoyo6J6
- Side view and room-side x-ray view drawn to scale from the state; chips show the clearances and the lift needed to come off; the prompt box writes the chosen numbers as a build instruction.
- Concept A (default): the board hangs nose-up, trucks toward the wall, grip side to the room. The top truck's hanger center body rests on a narrow tongue; the kingpin nut sits above the tongue as a locator. A lip at the tongue end and a tilt toward the room give the fore-aft hold, a concave saddle across the width gives the side hold. The lower wheels rest on the wall.
- Concept B: the board stands on its bottom truck, axle boss in a U block, top wheels on the wall. Weaker: the hanger body limits the cradle depth and nothing holds sideways.

## Why the hold is on the hanger, not the nut (research 2026-10-04)

- A traditional-kingpin truck's kingpin is nearly perpendicular to the deck (literature about 70 deg to the deck plane; an Indy Stage 11 photo reads 10 to 13 deg from the deck normal) and the nut leans toward the axle, not toward the board center.
- The nut top stands only about 3 mm proud of the hanger on the axle side and about 9 mm proud of the inboard rim; it sits in a roughly 41 mm bowl. Hanging from the nut alone would be a near-level hex prism on a shelf: friction, not a hold.
- Typical numbers used as tool defaults: Indy Stage 11 Standard height 55 mm (139 hanger, 203 axle); wheels 54 x 33; nut 9/16 in = 14.3 AF, jam nut about 6.7 tall; top cone bushing 19.3 x 9.9; cup washer about 23; deck 10.5; completes 2.0 to 2.4 kg. Thunder 147 Hi 50 mm, Venture 5.2 Lo 48.3 mm.
- Hanger center body (bulb) dimensions in the tool (53 wide, 10 to 46 mm from the deck, 42 mm inboard of the axle, half-round inboard end) are photo estimates, plus or minus 3 mm. They must be measured on Brian's truck before CAD.

## Decisions already locked

- None from Brian yet. My assumptions: trucks face the wall (grip out); PETG, printed on its side, 3 walls; two #8 countersunk screws (NACS holder convention, 5 mm holes, 90 deg countersink to 10 mm); 0.6 mm high-flow nozzle (printer-verified 2026-10-04).

## Open

1. Concept A or B, from the pictures.
2. Measure on the board: deck underside to wheel face, deck underside to nut top, hanger body width across the axle, hanger body inboard end from the axle, and where the hanger's far face sits from the deck. Truck make and size.
3. Then the build123d model with a truck proxy from those numbers, docking and hold check with the real mesh per [[feedback-check-docking-and-hold-kinematics]], close-up of the lip per [[feedback-verify-retention-features-closeup]], STL and one 3MF.

## Files

- `hook-studio.html`: the design tool (single file, no dependencies).
- `pipeline/render_scene.py`: headless colored OpenSCAD renders of exported STLs for the later options page.
