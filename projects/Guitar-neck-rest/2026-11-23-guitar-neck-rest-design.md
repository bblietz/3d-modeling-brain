---
name: guitar-neck-rest-design
description: Design spec for the printed bench neck rest (open-frame rocker, rounded edges, cork pad, grip tape channel), as approved by Brian on 2026-11-23
type: design-spec
status: approved 2026-11-23, built 2026-11-23
created: 2026-11-23
tags: [project, 3d-print, guitar, bass, bench-tool, design]
---

# Guitar neck rest: design

**Goal.** A bench rest that holds the neck of Brian's guitar or bass while the instrument lies on its back for string changes, setups and cleaning. One printed piece plus a stick-on cork pad and a strip of Brian's 2 in rubber grip tape underneath.

**Approach.** A rocker: the bottom is one arc, so the rest rolls until its pad lies along the neck. Chosen over five other shapes in round 1, over two other rocker bodies in round 2, and kept over three longer cradles in round 3. History, pictures and research: [[projects/Guitar-neck-rest/brief|brief]] and the page at https://claude.ai/artifact/PXoUtoD3EfYz3RtPXSQzkf (Version 5). Memory: [[project-guitar-neck-rest]].

## Decisions

| Decision | Value | Whose |
|---|---|---|
| Shape | Rocker | Brian, 2026-11-22 |
| Body | Open frame (round 2's C1), cradle length unchanged | Brian, 2026-11-22 |
| Go on the design | Yes | Brian, 2026-11-23 |
| Cradle ends | Rounded over ("the front and back edges closest to the neck", confirmed as the two cradle ends) | Brian, 2026-11-23 |
| Every other edge | A slight roundover | Brian, 2026-11-23 |
| Roundover sizes | 1/4 in on the cradle ends, 1/16 in elsewhere | Mine, open to change |
| Spec approved | "Yes, build it" | Brian, 2026-11-23 |
| Grip underneath | One recessed channel for his 2 in wide rubber grip tape, replacing the two tread strips ("Create a 2 in wide recessed channel in the bottom of the stand for me to put the grip tape in") | Brian, 2026-11-23 |
| Channel depth | 0.5 mm, shallower than the tape so the rest stands on rubber | Mine, open to change; tape thickness not known |
| Pad | 1/16 in self-adhesive cork | Mine, open to change |
| Duty | Light: PLA, 2 walls, 15% infill | Mine, open to change |
| Neck height | 3-3/4 in | Mine, open to change |

## Words used below

- **Ends:** the two sloping sides the neck passes over, one toward the nut and one toward the body of the guitar.
- **Faces:** the two flat sides with the opening in them. One of them is on the plate while it prints.
- **Cradle:** the groove along the top that the neck lies in. **Rims:** its two long edges. **Shoulders:** the flat strips outside the rims.

## The body

One piece, 5-7/8 in long, 3-1/8 in wide, 4-1/4 in tall (148.7 x 80 x 108.5 mm).

| Feature | Size | Note |
|---|---|---|
| Rocking curve | one arc, radius 5-1/8 in (130 mm), 5-7/8 in from end to end | Its centre is 1-3/8 in above the line the neck bears on, so weight on the pad steadies it |
| Ends | lean in 13.3 degrees, from 5-7/8 in at the curve to 4-3/8 in at the top | |
| Frame | 1/2 in (12 mm) thick around one opening; opening corners 3/8 in (9 mm) radius | The opening is the handle and the hanging hole |
| Cradle | 2-1/2 in wide at the pad surface, radius 45.3 mm, about 1/2 in deep, 4-3/8 in long over the top | Printed on its side the upper rim overhangs about 46 degrees from upright at its worst, so it needs no supports |
| Pad seat | the cradle is cut 1/16 in (1.6 mm) deeper than the pad surface, full length | The concept solid drew 2 mm; the real model uses 1.6 mm so the top of the cork is at 3-3/4 in |
| Neck height | 3-3/4 in (95.25 mm) from the bench to the top of the cork | |
| Cradle ends | 1/4 in (6.35 mm) roundover, across the cradle and both shoulders | Leaves about 4-1/4 in of level floor between the two roundovers |
| Other outside edges | 1/16 in (1.6 mm) roundover: both faces all the way round, the opening's edge on both faces, the two rims | |
| Bottom corners | 5 mm radius where the curve meets the ends, as drawn since round 1 | |
| Grip tape channel | one, centred on the curve, 2 in plus 1/64 in each side wide (51.6 mm), 0.5 mm deep, 5-5/8 in along the curve with closed ends | Edges left square: the tape seats against them. 9/16 in (14.2 mm) of plastic is left either side. Replaces the two tread recesses of the first draft |

**How the roundovers are defined.** The body is described as slices across the neck, which is also how it prints. Each slice is the side outline with its top at the cradle's height there and its two top corners rounded 1/4 in. The 1/16 in roundover on the rims is part of that height curve, and at the two faces the outline shrinks through a 1/16 in quarter circle. The opening widens through the same quarter circle. This construction already exists and is checked in `pipeline/concepts.scad` (`c1r_body()`), with the radii `R_END` and `R_EDGE`.

## Soft parts


| Part | Cut size | Goes |
|---|---|---|
| Pad, 1/16 in self-adhesive cork | 2-3/4 x 4-1/8 in | In the cradle, centred, ending where the end roundovers start |
| Grip tape, Brian's 2 in rubber tape | 2 x 5-1/2 in | In the channel on the bottom; it must stand proud of the plastic either side |

Not cork if the guitar has a nitro finish; felt or a printed TPU pad are the alternatives on the page. The bass is taken to be polyester.

## Printing

- Printer and nozzle: Bambu Lab X2D, 0.6 mm nozzle (the high-flow one is normally in; confirm with `scripts/x2d-status.py` before slicing). See [[printer-x2d]].
- Material: PLA, 2 walls, 15% infill, 0.30 mm layers. Colour is Brian's pick in Studio.
- Orientation: on one face. The nozzle then draws the rocking curve and the two cradle ends as smooth lines on every layer.
- No supports. 2-loop skirt. Textured PEI plate at 65 C.
- Seam on the cradle side, where the pad covers it. No seam on the rocking curve.
- Output: one Bambu 3MF, one plate, one object.
- Final slice (`3mf-report.json`): 167.5 g, 2 h 21 min, 267 layers.

## Proven before anything prints

Each of these gets a picture or a number from the real model.

1. **The solid.** Watertight, one body, flat on the plate, overall size as above.
2. **Cradle ends.** Close-up render of one end with the pad in place, and the centre section measured: level floor, then the 1/4 in arc.
3. **Pad seat and channel.** Section across the neck with the pad and the tape drawn in: cork top at 3-3/4 in, the channel 0.5 mm deep and 51.6 mm wide, the pad clear of the rim roundovers.
4. **The roll.** The solid rolled under the bass and guitar stand-ins: the pad lies along the neck, and the neck clears both end roundovers.
5. **Slice preview.**
   - The cradle's upper rim, about 46 degrees from upright at its worst: it prints clean with no supports.
   - The down-facing side wall of the channel, a 0.5 mm ledge: under one line width, so no bevel.
   - The 1/16 in roundover on the plate-side face in the first layers. If it is rough, that side becomes a small bevel.
   - The same roundover on the top face, which prints as about five steps.
   - Seam position.
6. **G-code.** 2 walls, 15% infill, the skirt and the plate temperature are in the sliced file.
7. **Numbers.** Weight and time from the final slice.

## Not in this design

A second height, ballast, a longer cradle, an acoustic-guitar height, and printed TPU pad parts. Each was looked at and set aside.

## Assumed, not confirmed

- The bass is the 2002 Mexican P-Bass. No guitar is on file; a Strat-size neck stands in.
- The neck lies about 1-1/4 in above the bench with the body flat. It sets how far the rest rolls (4.4 degrees under the bass, about 5.2 under the guitar stand-in), not its shape.
- About 3-1/2 lb on the rest. The statics that put the neck's push within 1/8 in of the middle of the pad depend on it.
- No fret levelling, tapping or pressing on it. That would call for more walls and infill.

## Files

- `neck_rest.scad` (the model), `guitar-neck-rest.stl`, `guitar-neck-rest.3mf` (one plate), `pipeline/build.py` and `build-report.json` (the checks on the mesh), `pipeline/make_print_3mf.py` and `3mf-report.json` (the slice proof), pictures in `images/neck-rest-*.png`. Plan: [[2026-11-23-guitar-neck-rest-plan]].
- Outcome of the checks, 2026-11-23: items 1 to 4, 6 and 7 pass; in item 5 the rim (45.6 degrees), the channel wall and the seam pass from the mesh and the G-code, and the two looks (plate-side roundover, top-face steps) are left for Brian in Studio's preview.
- Notes in the brief; a retrospective in `knowledge/learnings/guitar-neck-rest.md` once it is modelled and again after the print.
