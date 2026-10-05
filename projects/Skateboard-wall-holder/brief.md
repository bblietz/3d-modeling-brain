---
type: project
project: Skateboard-wall-holder
date: 2026-10-04
status: DONE for print 2026-10-04: cradle with a dipped lip, 40 mm wide; skateboard-holder.3mf sliced 59 min 30 s / 48.4 g PETG; not printed; truck numbers still estimates
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

## Build (2026-10-04)

- Brian pasted the tool's prompt (concept A, default numbers), then in the viewer: "the tongue should have a curved shape, so the board doesnt slide off if it is bumped" and "make the tongue wider and teh curve deeper". Built in build123d: `skateboard_holder.py` (constants at the top, self-checks, exports), STL `skateboard-holder.stl` in print orientation.
- Cradle: R20 arc (hanger half-round R18 + 2 mm) centered 2 mm above the hanger's half-round center; room rim 65 deg of arc (11.5 mm lift to leave toward the room), wall rim 45 deg (5.9 mm; 50 deg put the shelf 1.5 mm from the washer, eased); R27 bowl across the 40 mm width (rims 8.9 mm up). Reach 74 (2 mm from the baseplate, 8 from the deck). Plate 6 x 110, 30 mm above the tongue root, #8 countersunk screws 90 mm apart. 3 mm roundovers, 0.6 side chamfer. Volume 76 cm3.
- Dish construction that worked: side-view cradle extruded across the width INTERSECTED with the width-wise saddle cylinder (floor = max of the two arcs). A loft of saddle arcs along the cradle carved the sides higher than the hanger proxy and collided (0.6 cm3).
- Hold check (`pipeline/hold_check.py`, 0.5 mm slices, frictionless): rest 0.0, drop-in free with the truck grown 0.2, bump slack 0.5 mm, lift to leave 11.5 toward the room, 8.25 sideways. Sections: `pipeline/section_fig.py` (true slices, matplotlib; OpenSCAD section previews lose per-part colors).
- Build report: https://claude.ai/artifact/Q9SgmT5dGhR47c1FfW84SQ
- Tool fix: the tool's contact point had a sign error (tangent point is on the room side of the hanger's lowest point); fixed and republished with a build note.

## Lip dip and 3MF (2026-10-04, later)

- Brian: "the front lip of the holder should also have a rounded dip, to cradle the truck". The dish became the saddle arc carried along the cradle (a ruled loft of R27 arcs through stations along x; a smooth loft overshot the rim by 1.1 mm). The lip toward the room now dips 8.9 mm at its center. Volume 81.9 cm3.
- Hanger proxies: a dome (rounded both ways at once, the shape the dish is cut for; ruled loft of half-discs along the half-round) and the earlier rounded block. Hold check, dome: rest 0.0, drop-in free, slack 0.5, lift 11.5 toward the room, 8.5 sideways. Block: rests 6.5 mm higher on the bowl's shoulders, lift 5.0 toward the room, 2.0 sideways. The real hanger is between the two.
- `skateboard-holder.3mf` (`pipeline/make_print_3mf.py`, from the Desk-cable-storage recipe plus wall_loops 3, 20% gyroid, 2-loop skirt, and a recenter step because the CLI stored this mesh uncentred): PETG Basic, 0.6 nozzle, 0.30 mm, 59 min 30 s, 48.4 g, 133 layers, 250/70 C, centred on the bed, floor on z 0, CLI round trip and a real slice passed. Brian: "make the 3mf" then "go".

## Decisions already locked

- 2026-10-04: concept A (hang from the top truck's hanger center body), curved cradle tongue, 40 mm wide, deeper curve. Trucks face the wall, grip side out. My assumptions: trucks face the wall (grip out); PETG, printed on its side, 3 walls; two #8 countersunk screws (NACS holder convention, 5 mm holes, 90 deg countersink to 10 mm); 0.6 mm high-flow nozzle (printer-verified 2026-10-04).

## Open

1. Print `skateboard-holder.3mf` (open in Bambu Studio, do not reselect the printer preset: it resets the process). Then measure the fit and write the result into the retrospective.
2. Still unmeasured: deck to wheel face (82), deck to the hanger's far face (46), hanger body reach inboard and width (42, 53), deck to washer bottom and nut top (49, 55). The cradle has 2 mm radial clearance and the washer 2.8 mm over the shelf, so these decide the drop-on.

## Files

- `hook-studio.html`: the design tool (single file, no dependencies).
- `skateboard_holder.py`, `skateboard-holder.stl`, `skateboard-holder.3mf`, `skateboard-holder-slice.json`, `pipeline/make_print_3mf.py`, `build/` (regenerated scene STLs, ignored), `images/` (renders and sections), `build-report.html`.
- `pipeline/render_scene.py` (OpenSCAD colored renders), `pipeline/renders.py`, `pipeline/section_fig.py`, `pipeline/hold_check.py`.
