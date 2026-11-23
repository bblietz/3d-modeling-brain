---
type: project
project: Guitar-neck-rest
created: 2026-11-22
status: BUILT 2026-11-23, not printed: neck_rest.scad, guitar-neck-rest.stl and guitar-neck-rest.3mf (one plate, 167.5 g, 2 h 21 min PLA), with one recessed channel for Brian's 2 in rubber grip tape in place of the two tread strips (his note the same day; 0.5 mm deep is my call, tape thickness unknown); page Version 6; waiting on his look at the 3MF in Studio; earlier status: design approved 2026-11-23 ("Yes, go") on round 2's C1 (open-frame rocker, 4-3/8 in cradle), with two additions the same day: the two cradle ends rounded over (1/4 in, my size) and a slight roundover on every other edge (1/16 in, my size); page Version 5 shows it; spec written (2026-11-23-guitar-neck-rest-design.md), waiting on Brian's review of it; my unconfirmed defaults stand (1/16 in cork pad and tread, PLA 2 walls 15% for light duty, 3-3/4 in); next is the plan, then the build; concept solids only, no final CAD, nothing printed
printer: Bambu Lab X2D
material: PLA (light duty, assumed)
tags: [3d-print, guitar, bass, bench-tool]
---

# Guitar neck rest

## Request (Brian, 2026-11-22)

"Research and design a guitar neck stand to be used when working on my guitar and bass. Find examples of popular and quality designs already out there. Create an HTML companion that gives at least 5 different base design shapes and then we can iterate from there. Use /superpowers"

Process: superpowers brainstorming. The design was approved on 2026-11-23 and is written up in [[2026-11-23-guitar-neck-rest-design]]; nothing past concept solids is built until Brian has reviewed that spec and the build is planned. Related: [[project-pickup-height-gauge]] (the bass is a 2002 Mexican Fender Standard Precision), [[printer-x2d]].

## Options page

- Page: `options.html`, published as a private Artifact: https://claude.ai/artifact/PXoUtoD3EfYz3RtPXSQzkf. Version 1 (2026-11-22): the six base shapes. Version 2 (2026-11-22): round 2, the rocker. Version 3 (2026-11-22): round 3, the open frame with a longer cradle. Version 4 (2026-11-22): the design Brian kept (round 2's C1) at the top, with rounds 3, 2 and 1 folded away at the bottom of the same page. Version 5 (2026-11-23): the same design with its edges rounded over (solid `c1r`) and a new Edges section.
- Built by `pipeline/concepts.py` (one parameter set, writes `pipeline/params.scad`, exports the concept STLs to `concepts/`, draws `images/concepts/fit.png`, `use.png`, `roll-empty.png`, `roll-bass.png`, `end-section.png` and `side-c1a|b|c.png`, renders every picture through OpenSCAD), `pipeline/concepts.scad` (the six round 1 solids, the three round 2 rocker bodies, the three round 3 long-cradle bodies, the kept body with rounded edges `c1r`, the pad, the tread, the neck stand-in, the 1 in grid mat) and `pipeline/options_page.py` (the page, images inlined).
- Slice quotes: `concepts-slice-pla.json` (round 1), `rocker-slice-pla.json` (round 2), `long-slice-pla.json` (round 3) and `design-slice-pla.json` (the kept body, `c1r`), from `projects/Fishing-rod-holder/pipeline/slice_stls.py --material pla --walls 2 --infill 15` (X2D 0.6 nozzle, 0.30 mm Standard, Bambu PLA Basic).
- Sizes, derived numbers, tilt angles and the rocker statics: `concepts-report.json` (`rocker` block; `long` block for round 3; `roundover` block and `parts.c1r` for the kept body).
- Rebuild: `.venv/bin/python projects/Guitar-neck-rest/pipeline/concepts.py`, slice the changed STLs, then `options_page.py`, then republish `options.html` to the same Artifact.

## The six base shapes (concept solids, all with the same cradle)

| | Shape | Neck height | Follows the neck slope | Pieces | Plastic | Print time | Modeled on |
|---|---|---|---|---|---|---|---|
| A | Two-height block (hollow frame, cradle on top and on one side) | 2-1/2 and 3-3/4 in | No | 1 | 147 g | 2 h 02 | Harley Benton GuitarTech, StewMac Hi-Lo, Bukken (Printables) |
| B | Three-height block (cradle on three faces) | 2-1/2, 3-3/4 and 5 in | No | 1 | 247 g | 3 h 13 | MusicNomad Cradle Cube |
| C | Rocker (curved bottom, R 130 mm) | 3-3/4 in | Yes, rolls | 1 | 225 g | 2 h 58 | StewMac Rock-n-Roller, Widara, Crimson |
| D | Hanging cradle on a yoke (pins just above the neck line) | 3-3/4 in | Yes, swings | 2 | 160 g | 2 h 37 | Dunlop System 65 Neck Cradle, Hosco, G&W |
| E | Long low trough, 9 in, clamp flanges | 1-1/4 in (estimate) | Neck lies level | 1 | 231 g | 3 h 06 | StewMac Neck Support Caul |
| F | Screw pedestal (printed 44 mm thread, 8 mm pitch) | 2-1/2 to 3-3/4 in | No | 2 | 173 g | 2 h 54 | PSG (MakerWorld), Hercules HA206 |

Recommendation put to Brian: start from C (rocker). A level cradle under a neck that slopes 2 to 4 degrees bears on one edge of the pad; the rocker removes that with no moving parts and prints in one piece on its side. D does the same on a steadier base with a second part. E is a second tool for fretwork, not a replacement. Shapes can combine (rocker bottom under a two-height block).

Common cradle: 64 mm (2-1/2 in) wide at the rim, radius 45.3 mm, 13.2 mm deep, 2 mm allowance for a stick-on pad. The 45.3 radius puts the rim tangent at 45 degrees so the groove prints on a vertical wall without supports.

## Round 2: the rocker (Brian's pick, 2026-11-22: "C, the rocker")

What the rocker does, from the model (`concepts-report.json`, `rocker`): bottom arc radius 130 mm (5-1/8 in), neck line 34.75 mm (1-3/8 in) below the arc's centre, so a loaded rocker is stable and an empty one rights itself. At 3-3/4 in it rolls 4.4 degrees under the bass and about 5.2 under a Strat-size guitar (stand-in, 31.5 in tail to nut). A level cradle of the same length would stand 5/16 in clear at one end. Statics, assuming about 1.6 kg on the rest (estimate): the neck's push lands within 1/8 in of the middle of the pad.

Settled by me, open to change: size 5-7/8 x 3-1/8 x 4-1/4 in; cradle unchanged; two recessed tread strips on the curve (14 mm wide, 3 mm in from each edge, 1.2 mm deep for a 1/16 in strip) in the pad's material; printed on its side; PLA, 2 walls, 15% infill.

| | Body | Neck height | Plastic | Print time | Weight in use | Pieces |
|---|---|---|---|---|---|---|
| C1 | Open frame, 12 mm thick around one opening | 3-3/4 in rocking | 170 g | 2 h 27 | 170 g | 1 |
| C2 | Weighted: closed, 132 cm3 ballast pocket under a press-in lid, hang slot above | 3-3/4 in rocking | 255 g (body 245, lid 11) | 3 h 36 | about 1 lb with sand, 2 lb with steel BBs | 2 plus ballast |
| C3 | Two-way: closed, second cradle on one side with a 2.6 degree slope built in | 3-3/4 in rocking, 2-5/8 in fixed lying on its side | 242 g | 3 h 14 | 242 g | 1 |

Recommendation put to Brian: C1 (simplest, least plastic, tread answers the sliding complaint). C3 if a second, lower height is worth 72 g and the handle. C2 for the heft of the wooden ones; its weight pulls the rocker toward level, moving the neck's push to about 1/4 in off the pad middle with a full load of BBs. C3 can also carry ballast; C1 cannot.

Pad and tread, one material for both: cork (my pick unless the guitar is nitro), felt, or printed TPU.

Not proven on any of the three: overhangs in a slice preview, the lid fit, the pad and tread recesses. C3's built-in slope depends on the lying-flat measurement.

## Round 3: a longer cradle (Brian, 2026-11-22)

"C1, open frame. the rocker design should have longer surface area for the neck to sit on, and the bottom rocker can either stay the same or even get smaller"

Carried over from C1: the 130 mm curve, the 3-3/4 in neck line, 80 mm width, the cradle section, the 12 mm frame, the two tread strips, printing on its side. Changed: the cradle is a straight beam with square ends (27 mm deep: groove, pad allowance, frame) and the legs run to its lower corners; the parameter set is `LONG` in `concepts.py`. A long cradle has to clear the headstock and tuners, so it is drawn starting 19 mm (3/4 in) from the nut (`REST_START`); its middle is then further up the neck and the 8 in bodies roll 4.5 degrees under the bass (5.4 under the guitar stand-in).

| | Cradle | Rocker (chord) | Curve each way | Plastic | Print time | Size |
|---|---|---|---|---|---|---|
| C1, round 2 | 4-3/8 in | 5-7/8 in | 35 degrees | 170 g | 2 h 27 | 5-7/8 x 3-1/8 x 4-1/4 in |
| C1a | 6 in | 5-7/8 in | 35 degrees | 188 g | 2 h 36 | 6 x 3-1/8 x 4-1/4 in |
| C1b | 8 in | 5-7/8 in | 35 degrees | 222 g | 3 h 03 | 8 x 3-1/8 x 4-1/4 in |
| C1c | 8 in | 4 in | 23 degrees | 218 g | 2 h 59 | 8 x 3-1/8 x 4-1/4 in |

Findings:
- The smaller rocker saves almost nothing (4 g, 4 minutes): the legs grow by about what the curve loses. It is a looks call, not a plastic one.
- The line of contact moves only 3/8 to 1/2 in from the middle under either instrument, so even the 4 in rocker has far more curve than it uses.
- A level 8 in cradle would stand 5/8 in clear at one end under the bass, so rolling matters more as the cradle grows. Statics, same 1.6 kg assumption: the neck's push lands within 1/8 in of the middle of the 8 in pad.
- On the bass the 8 in cradle runs from 3/4 in past the nut to the 5th fret (the 7th on the guitar stand-in); the 6 in stops short of the 4th.
- Any cradle up to about 9 in fits the bed on its side.

Recommendation put to Brian: C1b (8 in on the whole rocker: nearly twice the surface for 52 g and 36 minutes over round 2, and the extra curve is free reserve). C1c works the same under a neck. C1a if 6 in is enough.

Not proven: overhangs in a slice preview, the pad and tread recesses.

Outcome (Brian, 2026-11-22): "keep design from last step", confirmed by a question as round 2's C1, unchanged. The longer cradles are dropped. Their solids, slices and pictures stay in the pipeline (`LONG` in `concepts.py`) and on the page, folded, for the record.

## The design as it stood at Version 4 (2026-11-22; Brian's go came on 2026-11-23, see the next section)

- Body: C1 from round 2, unchanged: open frame, 12 mm thick, on the 130 mm curve; 5-7/8 x 3-1/8 x 4-1/4 in; cradle 2-1/2 in wide, 4-3/8 in long; neck line at 3-3/4 in; two recessed tread strips; printed on its side; 170 g, 2 h 27 (concept slice).
- My defaults, stated on the page as unconfirmed: pad and tread in 1/16 in self-adhesive cork (felt or printed TPU on request; not cork if the guitar is nitro); PLA, 2 walls, 15% infill for string changes, setups and cleaning (more if he does fret work).
- The lying-flat measurement is no longer needed for the build: the rocker rolls to meet the neck, so the measurement only changes the roll angle, not the shape. Brian was asked for it three times and did not answer; it is dropped from the asks.
- To prove on the real model before any print: overhangs (cradle rim, upper edge of each tread recess) in a slice preview; pad and tread recess depth against a 1/16 in sheet in a close-up section; the roll under both neck stand-ins; final slice weight and time.
- Next, on his go: design spec, his review, the plan, then the build with the 3d-model skill (one-plate 3MF, 2-loop skirt, retrospective).

## Go, and the rounded edges (Brian, 2026-11-23)

"Yes, go" on Version 4. Then two notes while the spec was being written:

1. "the front and back edges closest to the neck should be rounded over". Two readings (the two cradle ends, or the two long top edges beside the neck), so I asked one question; his answer: the two cradle ends.
2. "all edges should have a slight roundover".

What was done:

- New solid `c1r` in `pipeline/concepts.scad`: C1 with a 1/4 in (6.35 mm, `R_END`) roundover on the two cradle ends, across the cradle and both shoulders, and 1/16 in (1.5875 mm, `R_EDGE`) on every other outside edge (both faces all the way round, the opening's edge on both faces, the two cradle rims). Both sizes are mine. The tread recesses stay square because the strips seat against them.
- Construction: slices across the neck, the way it prints. Each slice is the side outline with its top at the cradle's height there and the two top corners rounded `R_END`; the rim roundover is in that height curve; at the faces the outline shrinks through a quarter circle; chained hulls join the slices. A rolling-ball fillet was not used: the 1/16 in rim cannot carry a 1/4 in ball round the end without a crease.
- Checked: `concepts.py` drops a ray on the centre plane of the exported STL and asserts the level floor and the middle of the arc (93.25 and 91.88 mm, both matched); watertight, one body, 414.0 cm3 against 415.6 with square edges.
- Slice (`design-slice-pla.json`): 168.8 g, 2 h 27 min, against 170.3 g and 2 h 27 with square edges.
- The level floor between the two roundovers is 107 mm (about 4-1/4 in); the pad as drawn (104 mm) ends just inside it.
- Page Version 5: `c1r` pictures in The body, a new Edges section (`c1r-end.png`, `end-section.png`), the pad pictures redrawn on `c1r`, and the ask replaced by where it stands.
- Spec: [[2026-11-23-guitar-neck-rest-design]], kept here with the project like the vault's other specs, not in `docs/superpowers/specs/`. Not committed: Brian commits on request.

Flagged to Brian, not yet proven: the 1/16 in roundover on the plate-side face starts on the plate (rough first layers; fallback a small bevel on that side), and on the top face it prints as about five 0.30 mm steps. Found while writing the spec: with the pad seat cut in, the cradle's upper rim overhangs about 46 degrees from upright as it prints, not 45; still support-free, to be confirmed in the slice preview. The real model cuts the pad seat 1.6 mm deep for a 1/16 in sheet (the concept drew 2 mm) and the tread strips become 1/2 in wide with 1/64 in clearance each side (the concept drew 14 mm).

## The build (2026-11-23)

"Yes, build it" on the spec. While the plan was being written: "I have 2 in wide rubber grip tape. Create a 2 in wide recessed channel in the bottom of the stand for me to put the grip tape in". The two tread recesses became one channel.

- Plan: [[2026-11-23-guitar-neck-rest-plan]], executed inline with the 3d-model skill's discipline. Backend OpenSCAD, not build123d: the roundovers are slices joined by hulls, and a kernel fillet creases at the rims.
- Model: `neck_rest.scad` (standalone, every dimension at the top). Print frame of `guitar-neck-rest.stl`: x along the neck, y up the standing rocker with the cradle at the back of the plate, z from the plate. 148.7 x 108.5 x 80.0 mm, 415.5 cm3, watertight, one body.
- Channel: centred, 51.6 mm wide (2 in plus 0.4 each side), 0.5 mm deep (my call: shallower than the tape, so the rest stands on rubber; Brian's tape thickness is not known), 142.9 mm along its floor with closed ends, 14.2 mm of plastic either side. Tape cut 2 x 5-1/2 in.
- Pad seat 1.6 mm; cork cut 2-3/4 x 4-1/8 in fits with 1.1 mm at each end and 2.8 mm each side.
- `pipeline/build.py` checks on the mesh (`build-report.json`): cradle floor 93.65 mm and the 1/4 in arc within 0.05 mm; channel depth and ends; the bass and guitar stand-in necks never closer than 1.6 mm to the plastic; overhangs steeper than 47 degrees only on the plate-side 1/16 in roundover (953 mm2) and the channel's 0.5 mm side wall (72 mm2); cradle upper rim 45.6 degrees.
- `pipeline/make_print_3mf.py` (`3mf-report.json`): X2D 0.6 nozzle, 0.30 mm Standard, Bambu PLA Basic, 2 walls, 15% infill, 2-loop skirt, no brim, no supports, Textured PEI at 65 C, seam "back". Overrides listed in `different_settings_to_system` slots 0 and 1; CLI round trip keeps them; real slice: 167.5 g, 2 h 21 min, 267 layers, top at 80.1 mm, all 533 outer-wall seams on the cradle side (266) or inside the top of the opening (267), none on the rocking curve.
- Pictures: `images/neck-rest-hero|end|under|bare.png`, `neck-rest-section-end.png`, `neck-rest-section-across.png`. Page Version 6.
- Found on the way: two centre slices 0.02 mm apart (the half mirrored onto itself) left the STL open; fixed with one chain of slices. ASCII STLs were 53 MB; both pipelines now export binary.
- Printer on 2026-11-23 (`scripts/x2d-status.py`): 0.6 mm standard-flow hardened steel in both hotends, PLA Basic black in AMS slot 2 at 42%, last job 'Gitarrenstuetze' finished at 233 layers (not this file, which has 267).
- Not proven: the look of the 1/16 in roundover on the plate-side face and the five steps on the top face (Brian, in Studio's preview); the 3MF opened in the GUI; the tape's real thickness against the 0.5 mm channel; nothing printed.

## Assumptions (none confirmed)

- Bass: the 2002 Mexican P-Bass. Guitar: not on file; a Strat-size neck stands in.
- Neck stand-ins: P-Bass nut 1.625 in, depth .94/.99 in ('51 figures), width at the 12th fret 2.20 in interpolated from the nut to a 2.5 in heel; Strat nut 1.650, 2.075 at 12, depth .82/.87.
- Lying flat, the neck back is about 1-1/4 in above the bench (Fender body 1-3/4, neck 3/8 proud of the body top, neck depth about .85 to .94). Not measured.
- Side elevation stand-in: tail of the body to the nut 36.5 in (34 in scale plus an estimated 2.5 behind the bridge); body 20 in and headstock 8.5 in long are for the drawing only.
- Heights 2-1/2 and 3-3/4 in come from the range of rests sold (2.6 to 4.2 in solid body, 5 to 6.2 in acoustic).
- Light duty: PLA, 2 walls, 15% infill. Fretwork would get more.

## Open questions for Brian

Answered: shape C, the rocker (2026-11-22); body C1, the open frame (2026-11-22); cradle length: round 2's 4-3/8 in, unchanged (2026-11-22); go on the design (2026-11-23); the two cradle ends rounded over and a slight roundover on every other edge (2026-11-23).

1. His look at the 3MF in Studio, and his grip tape's thickness (the channel is 0.5 mm deep).
2. Roundover sizes: 1/4 in and 1/16 in are mine; bigger or smaller on request.
3. Pad and tread: cork is the default; felt or printed TPU on request. Whether the guitar is nitro.
4. Whether he does fret work (default: no).

No longer asked: which guitar and the lying-flat measurement (not needed for a rocker; see above).

## Research (2026-11-22, two web surveys by subagents)

### Sold

| Product | Shape | Size and heights | Contact | Price | Notes |
|---|---|---|---|---|---|
| MusicNomad Cradle Cube | Hollow cube, cradle per face, 5 positions | about 4 x 4 x 5.25 in; faces 5 in (acoustic) and 3.5 in (electric) | Gel sleeve | $20 | Stable, grippy; corners obstruct fretwork |
| StewMac Rock-n-Roller | Hardwood rocker | 3-3/4 in solid body, 5 in acoustic | Cork | $52 to $89 | Self-levels |
| StewMac Neck Support Caul, Tall | Long clampable trough | 12 x 2-3/4 x 3-1/2 in (standard 1 in high) | Cork | $59 | For fret pressing |
| StewMac Hi-Lo Featherweight | Two-height foam block | 8-1/2 x 5-3/4 x 3 in, cradle 2-3/8 | Foam, sold as nitro safe | $43 | |
| Benedetto Neck Rest | Two-tier plywood tower | cradles 4-3/16 and 6-3/16 in | Felt | $115 | |
| Dunlop System 65 Neck Cradle | Pivoting cradle, one side flat | about 4.5 x 5 x 5.5 in | Neoprene (not for permanent nitro contact) | $42 | Flips flat when unloaded |
| D'Addario Headstand | Folding stand | 5 x 4.25 in standing | Rubber | $13 | Not firm, can collapse |
| Harley Benton GuitarTech | Two-height cork block | 115 x 97 x 82 mm, heights 65 and 100 mm | Cork | $10 | 4.9 of 5 from 2,318 |
| Widara ServiceCradle | Semicircular wood rocker | 180 x 90 x 90 mm | Thin cork | $18 | Nitro caution from reviewers |
| Fender Arch Work Station | Arch block plus base | package 5 x 5.25 x 7.5 in | TPE, sold as nitro safe | $30 | |

Unverified (search snippets only): Hosco (pivoting beech cradle, 85 to 110 mm), Crimson Rockin' Neck Rest (nested rockers).

### Printable

- Bukken (Printables, 3,330 downloads): curved two-height block, 15% infill, 4 walls; everyone adds leather, cork or foam.
- heapstar (MakerWorld, 1,366 prints): small U block; too small and too low, makers scale 130 to 170%.
- Doppelgang311 (MakerWorld, 633 prints): upright block with glued TPU pads; many use foam tape instead.
- vidision 3-position (MakerWorld, 712 prints, 4.97 stars): tall, short or rocker in one piece; needs supports.
- PSG (MakerWorld, 248 prints, 5.0 stars): rotating adjustable head on an M5 x 105 bolt.
- TroyDL rocker (Thingiverse): cork top and bottom; too low for acoustics, slides on smooth benches.

Lessons: too low and too small is the top complaint; narrow bases tip; nearly every maker adds padding afterwards; bare plastic slides; acoustics need height, not a bigger cradle; none of the designs surveyed has a weighted base or designed-in non-slip feet.

### Design facts

- Body thickness: Strat about 1.75 in, Les Paul 1.875 to 2 in, dreadnought about 4-5/8 in.
- Headstock pitch: Gibson 17 degrees, Epiphone 14, Fender straight.
- Nitro: Fender warns against vinyl, plastic and surgical rubber tubing. Sellers flag neoprene and vulcanized rubber. TPE, StewMac foam and felt are sold as safe. Cork is contested. No data found for TPU or silicone.
- StewMac's neck jig instructions warn that hammering frets over point supports dents the neck.
