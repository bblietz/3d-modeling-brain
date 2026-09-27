---
type: project
project: Desk-cable-storage
date: 2026-09-26
status: CAD COMPLETE 2026-09-26 evening, revised twice in the viewer (holes to 7 in apart, side walls to 4.5 in). Sliced 7 h 59 m, 387 g PETG, fits the bed at 254 mm; trough-print.3mf ready. Measurements waived by Brian. Waiting on his sign-off in the viewer, then print.
tags: [x2d, cable-management, closet-desk, petg]
---

# Desk cable storage

Hidden, reach-in storage for the cord slack under Brian's closet desk: a 3/4 in plywood slab on 1x2 cleats along both side walls of a closet, no legs, no apron. A 34 in power strip is screwed flat to the underside about 12 in behind the front edge, outlets facing down. Printed on the [[printer-x2d]]. Retrospective: [[desk-cable-storage]] (to be written).

## Decisions already locked (Brian, 2026-09-26)

- "The strip is screwed to the underside, keep it there." Nothing moves the strip.
- Contents: "A, just the cord slack and the bricks." No second strip, no shelf duty.
- Access: "C", an open trough that is reached into, never opened. Nothing shows from standing in the room.
- Size: "the organizer doesn't need to be as long as the power strip. Just long enough, wide enough and deep enough to house ~10 power cords. If the power brick is too big, then I can place that on top of the desk and feed the power cable down through the desk."
- Concept: D, a trough on the back wall behind the strip, picked from the phone page 2026-09-26. D as first drawn (under the plug heads) shows past about 6 ft; the raised D+ (top edge on the underside) hides to about 12 ft. SUPERSEDED 2026-09-26 evening: "The location on the wall will be D." D+ is dropped.
- Front wall: "the trough should have a higher front wall. It should be 75% of the height." (Brian, 2026-09-26). Cords drop over it into the open top.
- Size (Brian, 2026-09-26): "make the box 6\" deep" and "make the width of the box the max width of the printer bed". Read as: cavity 6 in deep (box height 6 in, front wall 4.5 in), front to back stays 6 in. Length 254 mm (10.00 in): the X2D profile has no bed exclusion zone, the slice placed it at x 1 to 255. Centred on the door opening for now, so it sits under outlets 5 to 7.
- Measurements: "you can ignore M1,2,3,4,5,6" and "also ignore m7,8,9,10" (Brian, 2026-09-26). The part is free-standing geometry; the closet numbers stay photo-derived and only matter for the install height.
- Spec (Brian, 2026-09-26): "Just create D that goes on the wall, max width of the X2D bed, and is 6in deep with a 4.5\" front wall. The cavity should be the full width. There should only be 2 screw holes in the top of the device for mounting. If they can be 16\" apart, that would be great, but not required." Holes were first 9 in apart (1/2 in from the ends); Brian: "move the screw holes over, they are too close to the ends" (2026-09-26), now 7 in apart, 1.5 in from each end. 16 in (stud spacing) would need wings beyond the bed width.
- Attachment may be the desk underside or the wall; Brian's original ask allowed both.
- "Don't over complicate it." No lid, drawer, hinge, latch or magnets.
- Process: "Instead of asking all of these questions in text, start drawing them up and show them to me. I am very much a visual person." Every question goes on the companion page with renders.

## Geometry read from the photos (plus or minus 10 percent; measure before printing)

| Item | Value |
|---|---|
| Closet interior width | 45 in behind a 32 in door opening, so 6.5 in pockets behind each jamb |
| Depth, front edge to back wall | 24 in |
| Top height / underside | 27.5 in / 26.75 in |
| Slab | reads 5/8 in in the photo; nominal 3/4 in |
| Cleats | 1x2 on the flat along both side walls; back cleat unknown |
| Strip | 34 in long, 1.9 in tall, 9 outlets at 3.4 in pitch, front face 12 in behind the front edge, left end 4 in from the left wall |
| Floor | PC front left (7.5 x 17 x 15 in), shredder back right (11 in wide, 11 in tall), basket front right |
| Cords | 5 outlets used today; all AC mains plus one DC lead; one 6 x 2.4 x 1.2 in brick |

## Approaches shown (2026-09-26)

- A. Wedge shelf hung from the slab in the 10 in behind the strip, sloped floor, hidden to about 14 ft.
- B. Box in the pocket behind the left jamb, fed by a raceway behind the strip. Easiest reach; face shows edge-on at an angle.
- C. Rail of coil hooks behind the strip; bricks on the desk through a grommet.
- D. Trough on the back wall under the plugs; visible beyond about 6 ft. PICKED. D+ variant raised to the underside added in the phone session.

## Design as built (trough.py, 2026-09-26)

| Item | Value |
|---|---|
| Outside | 254.0 x 152.4 x 152.4 mm (10.00 x 6 x 6 in) |
| Front and side walls | 114.3 mm (4.5 in), 75 percent of the height; only the back wall is 152.4 (Brian, 2026-09-26: "make the sidewalls the same height as the face") |
| Walls | 2.4 mm floor, front and sides; 3.2 mm back wall |
| Corners | R6 outside, R3.6 inside; 0.8 mm chamfer on the bed edge |
| Screw holes | two, 5.0 mm, 7 in (177.8 mm) apart so 1.5 in from each end, 3/4 in below the top edge, through the back wall; #8 screws in drywall anchors, heads inside |
| Print | floor down, open top up, no supports, no brim, no skirt; X2D 0.6 nozzle, 0.30mm Standard, Bambu PETG Basic, Textured PEI; 508 layers, 7 h 59 m, 387 g |
| Volume | 358 cm3 |

## Open before printing

1. Brian's sign-off in the OCP viewer.
2. Nozzle installed (printer was unreachable 2026-09-26 21:15); the 3MF assumes the 0.6.
3. Drywall anchor pull-out under a loaded trough is unverified; the load is a few pounds.
4. Install height: top edge about 1/2 in below the plug heads, set by eye at the wall.

## Files

- `pipeline/concept.scad`, `pipeline/render_concepts.py`: to-scale closet scene and the four options; renders in `images/concepts/`.
- `images/desk-1.jpg`, `images/desk-2.jpg`: Brian's photos (from the doorway; from below).
- `pipeline/make_share_page.py`, `share.html`: phone page with every render embedded, published at https://claude.ai/artifact/PrhaKebPkxBCo1XxL1EE7z
- `pipeline/measure_diagram.py`: the measure-these drawing, `images/design/measure.png`.
- `trough.py`: the part (build123d), self-checking; `trough.stl`; `images/trough-views.png`.
- `pipeline/make_print_3mf.py`: Bambu print 3MF with a real slice; `trough-print.3mf`, `trough-slice.json`.
- `decision.html`: phone page, now the finished part, published at https://claude.ai/artifact/CmY2ksbUC4nRorCnHt3nxY
- `.superpowers/brainstorm/`: companion pages (gitignored).
