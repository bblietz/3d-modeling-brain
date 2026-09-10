---
title: Garmin 943xsv helm panel
type: project-brief
status: DECIDED 1/2 in Starboard, routed one piece. Template printed-ready. Awaiting Brian's measurements and photos
created: 2026-09-08
tags: [boat, helm, garmin, starboard, router-template]
---

# Garmin GPSMAP 943xsv helm panel

Flat black King Starboard panel that replaces the hinged clear cover over the helm compartment directly behind the steering wheel. The 943xsv flush mounts through it. The old clear cover is the router pattern for the panel outline, so the only designed part is one 3D printed router template that locates the cutout and the four mounting holes.

## Locked decisions

- Panel replaces the hinged cover and is fixed in place. Hinges come off. Compartment access is by unmounting the unit.
- Material: black or charcoal King Starboard (HDPE). 3/8" (9.5 mm) unless the opening spans more than 450 mm, then 1/2" (12.7 mm).
- Mount style: Garmin flush mount, screws through the bezel edge into the HDPE. No printed bezel frame.
- Nothing else on the panel. One cutout only.
- Panel outline and perimeter fastening are copied from the old clear cover with a bearing bit. Not designed here.
- Exposure: under a hardtop. Stainless perimeter hardware.
- Compartment depth exceeds 110 mm everywhere, so the cutout position is free.
- Cutting: table saw or track saw for the perimeter, jigsaw rough cut inside the window, router with a bearing-guided flush-trim or pattern bit against the printed template.

## Garmin data (from Garmin install manual and 1:1 template, see [[#Sources]])

| Item | Value |
|---|---|
| Unit outside, bezel | 233.0 x 162.3 x 75.8 mm |
| Flush cutout | 222.4 x 139.0 mm labeled; drawn line 222.7 x 139.15 on center, 222.0 x 138.4 inside the 0.7 mm stroke |
| Mounting holes | four, on a 190.9 x 150.5 mm rectangle, NOT centered on the cutout: the pattern sits 1.24 mm toward the unit's bottom, so the top holes are 4.5 mm above the cutout edge and the bottom holes 7.0 mm below it (measured from the template vectors 2026-09-09) |
| Nut plate pin holes | 3 mm, 10.0 mm inboard of each screw hole in the same rows (171.1 x 150.5 mm pattern), only for the nut plate option |
| Screw pilot in plastic or wood | 2.3 mm |
| Bezel overlap past the cutout, as drawn with trim caps | 5.6 mm each side, 12.4 mm top, 14.9 mm bottom (bezel is centered on the hole pattern, not the cutout) |
| Cutout corners as drawn | 3.7 mm radius; the template calls for a 7.4 mm (5/16 in) relief drill, the manual says 8 mm |
| Rear clearance | 75.8 mm housing plus 33.2 mm cables, about 110 mm |
| Gasket | foam gasket on the back of the bezel, supplied |
| Flush kit | in the box; spare is Garmin 010-12991-01 |

## Panel

- Outline: rout from the old cover. Roundover the outside edges to taste.
- Cutout: 222.4 x 139.0 mm, centered left to right on the outline. Vertical position: centered unless the wheel rim blocks the lower screen from the seat, then shifted up. Brian decides at layout with the unit held in place.
- Corner radius left by the router equals the bit radius. Garmin's drawn cutout corners are 3.7 mm radius, so a 1/4" (6.35 mm) bit leaves 3.2 mm corners that need no squaring. A 5/16" bit would be 0.3 mm proud in the corners; avoid it.
- The cutout is not symmetric top to bottom because the screw holes sit 1.24 mm toward the unit's bottom. Lay out with the unit's top up and the template's TOP mark up.
- Mounting holes: 2.3 mm pilots drilled through the template guides, then the Garmin flat-head screws go straight into the HDPE. If the screws strip or feel soft in 3/8" stock, switch to Garmin's nut-plate option (3.5 mm clearance holes and M3 nut plates behind).

## Printed router template

- One part, PLA, 0.6 high-flow nozzle, 3 perimeters, 30 percent infill, textured PEI at 65 C.
- Window: exactly 222.4 x 139.0 mm, sharp corners. No offset, because the bearing rides on the template edge.
- Frame: 15 mm on the sides, 25 mm top and bottom, so the outside is 252.4 x 189.0 mm. Fits the 256 x 256 bed with the long edge on X.
- Thickness 12 mm, so a bearing up to about 10 mm tall rides fully on the template.
- Four drill guides for the mounting holes on the 190.9 x 150.5 mm pattern, shifted 1.24 mm toward the unit's bottom exactly as Garmin draws it (4.5 mm above the window at the top, 7.0 mm below it at the bottom). Modeled 2.8 mm so they print about 2.5 mm and clear a 2.3 to 2.4 mm bit. Each has a 6 mm counterbore 6 mm deep from the top face, so the guide is 6 mm long and a standard jobber bit reaches through the panel. A 7 mm counterbore would leave only 1.0 mm to the window at the top row.
- Registration: V notches on the outside edges at the four centerline points, to line up with centerlines drawn on the panel.
- Fixing: double-sided tape plus edge clamps. Two optional 4 mm screw holes on the vertical centerline, 6 mm outside the top and bottom window edges, land under the bezel overlap if screws are preferred.
- 0.6 mm chamfer on the bed-side window edge so elephant foot cannot narrow the window.
- TOP is debossed 0.8 mm into the counterbored face. The template is symmetric left to right only, so it still works on the front face with a top-bearing pattern bit or on the back face with a bottom-bearing flush-trim bit, as long as TOP points to the unit's top. Drill the pilots from the counterbored face.

## Process

1. Print the template. Measure the window with calipers. Expected 222.4 x 139.0 mm within 0.3 mm. Adjust slicer XY compensation if outside that, never rescale.
2. Rout the panel blank from the old cover. Roundover the outside edges.
3. Draw the cutout centerlines on the panel. Register the template notches on them with TOP toward the unit's top, fix it with tape and clamps.
4. Drill the four 2.3 mm pilots through the guides.
5. Drill an 8 mm relief hole inside each window corner, rough cut the window with a jigsaw leaving about 2 mm.
6. Rout the window flush to the template.
7. Test fit the 943xsv without screws. Bezel must sit flat on all four sides with the gasket compressed and the four bezel screw holes over the pilots.
8. Mount the panel, mount the unit, fit the trim caps.

Rout a scrap of the same stock first if any scrap is available.

## Deliverables (this folder)

- `brief.md` (this file).
- `garmin_9x3.py` (shared Garmin dimensions, imported by both models so they cannot drift).
- `router-template.py` (build123d source, self-checking), `router-template.stl`, `router-template.3mf`, `images/router-template-4view.png`.
- `helm-panel.py` (build123d source, self-checking), `helm-panel.stl`, `helm-panel.step`, `images/helm-panel-4view.png`.
- Retrospective in `knowledge/learnings/garmin-943-helm-panel.md` after the install.

## Open inputs from Brian

- Vertical placement of the cutout, decided at layout.
- Whether to add 3 mm pin guides for the nut plate option. Not in the template; add only if the wood screws fail.

## Sources

- Garmin install instructions, GPSMAP 7x3/9x3/12x3/16x3: https://www8.garmin.com/manuals/webhelp/GUID-BF2FF273-008A-482A-A96F-362ADA8996BA/EN-US/GPSMAP_7x3_9x3_12x3_16x3_Install_EN-US.pdf
- Garmin 9x3 flush mount template, 1:1: https://static.garmin.com/pumac/GPSMAP_9x3_flush_template.pdf
- Amped Up Marine KB article (hosts the same Garmin PDF, 190-02761-05_0D, July 2022, checked 2026-09-09): https://ampedupmarine.zohodesk.com/portal/en/kb/articles/garmin-gpsmap-9x3-mounting-template
- Note: the Garmin FAQ page lists "190.9 x 150.5 x 139.0 mm" as a cutout size. That is the hole pitch and cutout height run together, not a cutout. The template governs.

## Build results, 2026-09-09

Built with build123d from `router-template.py`. Every run re-checks the geometry: bounding box 252.4 x 189.0 x 12.0 mm, one solid, window probes prove the opening is 222.4 x 139.0 within 0.05 mm, all four guides clear, counterbores open, notches 2 mm deep, watertight STL, 3MF mesh matches the STL.

| Item | Value |
|---|---|
| Outside | 252.4 x 189.0 x 12.0 mm |
| Window | 222.4 x 139.0 mm, sharp corners, 0.6 mm chamfer on the bed side |
| Guides | 2.8 mm modeled, 6 x 6 mm counterbore, rows at +74.0 and -76.5 mm from the window center, wall to window edge 1.51 mm at the top row |
| TOP mark | 8 mm letters debossed 0.8 mm in the top band at x = 40 |
| Fixing holes | 4.0 mm at (0, +75.5) and (0, -75.5) |
| Notches | 90 degree V, 2 mm deep, at the four outer edge midpoints |
| Volume | 200 cm3 |

Print settings, 0.6 high-flow nozzle, Bambu PLA Basic, textured PEI at 65 C, brim off (the part leaves only 1.8 mm to the bed edge on X, so a brim would not fit). Center the part on the plate after import. Counterbored face up. Times from a real CLI slice with grafted Studio settings:

| Preset | Time | Filament |
|---|---|---|
| 0.18mm Balanced Quality, ironing off | 1 h 37 min (rev A slice) | 93 g |
| 0.30mm Standard | 1h 27m 33s (rev B re-slice) | 96 g |

Either works. Layer height does not change the window accuracy, so 0.30mm Standard is the sensible choice.

Slicer note for future sessions: `bambu-studio --arrange 1` placed this 252 mm part off the plate at y = -145.7, and the slice failed with "no object fully inside the print volume". Rewriting the build item transform to 128, 128, 0 in `3D/3dmodel.model` before `graft_slice.py` fixed it.

Revision B, 2026-09-09: checked against the template hosted by Amped Up Marine (Garmin's own 190-02761-05_0D PDF, unchanged). Found that the hole pattern is offset 1.24 mm toward the unit's bottom; revision A had it centered, which put every guide 1.24 mm too high. Guides moved, counterbore reduced to 6 mm, TOP deboss added. The check() function now also asserts that a pin at the old centered position hits material.

Next: print, measure the window with calipers, test the drill guides, rout the panel from the old cover, rough cut and rout the window, test fit the unit, install. Then the retrospective.

## Dimensions in inches

Decimal inches from the mm values, fractions rounded to the nearest 1/64. The mm values govern; Garmin's own template labels the cutout 8 3/4 x 5 1/2, but 139.0 mm is 5.472 in, so the 5 1/2 label is rounded by about 0.7 mm.

| Item | mm | Decimal in | Nearest fraction |
|---|---|---|---|
| Unit outside, bezel | 233.0 x 162.3 x 75.8 | 9.173 x 6.390 x 2.984 | 9 11/64 x 6 25/64 x 2 63/64 |
| Flush cutout | 222.4 x 139.0 | 8.756 x 5.472 | 8 3/4 x 5 15/32 |
| Mounting hole pattern | 190.9 x 150.5 | 7.516 x 5.925 | 7 33/64 x 5 59/64 |
| Hole offset from cutout edge, top row | 4.51 | 0.178 | 11/64 |
| Hole offset from cutout edge, bottom row | 6.99 | 0.275 | 9/32 |
| Hole pattern shift toward the unit's bottom | 1.24 | 0.049 | 3/64 |
| Hole offset from cutout edge, sides | 15.75 | 0.620 | 5/8 |
| Bezel overlap, each side | 5.6 | 0.220 | 7/32 |
| Bezel overlap, top | 12.4 | 0.488 | 31/64 |
| Bezel overlap, bottom | 14.9 | 0.587 | 19/32 |
| Cutout corner radius as drawn | 3.7 | 0.146 | 9/64 |
| Rear clearance, housing plus cables | 109.0 | 4.291 | 4 19/64 |
| Pilot drill | 2.3 | 0.091 | 3/32 |
| Corner relief drill, template label | 7.4 | 0.291 | 19/64 |
| Template outside | 252.4 x 189.0 x 12.0 | 9.937 x 7.441 x 0.472 | 9 15/16 x 7 7/16 x 15/32 |
| Template frame, sides | 15.0 | 0.591 | 19/32 |
| Template frame, top and bottom | 25.0 | 0.984 | 63/64 |
| Drill guide as printed | 2.5 | 0.098 | 3/32 |
| Guide counterbore, dia x depth | 6.0 x 6.0 | 0.236 x 0.236 | 15/64 x 15/64 |
| Fixing holes, dia | 4.0 | 0.157 | 5/32 |
| Fixing holes, from center | 75.5 | 2.972 | 2 31/32 |
| V notch, deep x wide | 2.0 x 4.0 | 0.079 x 0.157 | 5/64 x 5/32 |
| Corner radius from a 1/4 in bit | 3.2 | 0.126 | 1/8 |
| Jigsaw allowance | 2.0 | 0.079 | 5/64 |
| Panel span for 1/2 in stock | 450 | 17.717 | 17 23/32 |

## Panel model, 2026-09-09

Built from `helm-panel.py`. PROVISIONAL: the outline is Brian's estimate of 18.5 x 11.5 in. He will supply exact measurements and photos. Changing `PANEL_W` and `PANEL_H` regenerates the whole model, so nothing below is hand-fitted.

| Item | mm | in |
|---|---|---|
| Panel | 469.9 x 292.1 x 9.525 | 18.5 x 11.5 x 3/8 |
| Corner radius | 12.7 | 1/2 |
| Edge roundover, outside face only | 3.175 | 1/8 |
| Window | 222.4 x 139.0, R3.175 corners | Garmin cutout |
| Window vertical offset | 0.0, centered | set at layout |
| Pilots | 2.3 mm, 7 mm deep, blind | 3/32 |
| Volume | 1008 cm3 | about 0.60 kg printed in ASA |

Thickness is 3/8 in, set 2026-09-09 after Brian questioned the 1/2 in. The 1/2 in came from a rule written for HDPE sheet and should not have survived the switch to printing.

Clearances the model checks on every run:

| Measure | Side | Top | Bottom |
|---|---|---|---|
| Panel material between window and edge | 123.7 | 76.5 | 76.5 |
| Panel beyond the bezel trim caps | 118.1 | 64.1 | 61.6 |

At 469.9 mm the panel is 1.8x the X2D bed, so printing it means splitting it. See the tiles section below. The one-piece `helm-panel.stl` and `.step` remain the design intent and the reference for routing it from sheet instead.

Assumption to confirm against the old cover: the 12.7 mm corner radius. Brian did not specify one, and the old cover sets what looks right.

Open points for a panel this size in black HDPE, worth deciding when the measurements arrive:

- Black HDPE expands about 0.15 mm per metre per degree C. Over 470 mm a 30 C swing moves the panel about 2 mm. Perimeter screws through slightly oversized holes, rather than tight ones, let it move without bowing.
- 1/2 in Starboard unsupported across 470 mm will flex under a hand pressing the touchscreen. If the opening is open-backed, a cleat or two behind the panel near the window is worth adding.

Both depend on what the opening actually looks like, so they wait on the photos.

## Split into printable tiles, 2026-09-09

Brian asked for the panel printed rather than routed, which means splitting it to fit the bed.

**Why four.** 292.1 mm exceeds the 256 mm bed, so a split in Y is forced no matter how the panel is turned; each resulting half is still 469.9 mm wide, so a split in X is forced too. Four is the minimum, and rotating on the bed does not help because 469.9 exceeds even the 362 mm bed diagonal.

**Where the seams go.** Straight cuts at x=0 and y=0. Both seams are interrupted by the window, so the vertical seam exists only in the top and bottom webs and the horizontal seam only in the left and right webs. No four tiles ever meet in solid material, and no Garmin screw lands on a seam: the pilots sit at x = +/-95.45, clear of both.

**Why loose keys and not integral dovetails.** A 2x2 grid cannot be assembled with dovetails cut into the tiles. The top-left tile would have to slide in Y to engage its neighbour across the vertical seam and in X to engage the one below, at the same time. Instead each seam carries bowtie pockets cut into the BACK face, and separate bowtie keys drop straight in along Z after the tiles are laid flat. No over-constraint, and the front face is never broken by the joint.

| Item | Value |
|---|---|
| Tiles | 4, each 234.95 x 146.05 x 12.7 mm |
| Bed margin per tile | 10.5 mm in X, 55 mm in Y |
| Keys | 10 identical bowties, 36 x 20 mm, 12 mm waist, 5.8 mm thick |
| Keys per seam | 2 in the top web, 2 in the bottom, 3 in each side web |
| Pocket | 6 mm deep from the back, leaving 3.5 mm of front skin |
| Key clearance | 0.2 mm per face, a true perpendicular offset |
| Seam chamfer | 0.5 mm on the front edges, so the joint reads as a panel line |

The model verifies the joint rather than assuming it: every key is placed into its actual pocket in the actual tiles and asserted to touch nothing, the four tiles are reconciled against the one-piece panel volume exactly, and the chamfer sliver is predicted and bounded.

**Print settings**, from real slices of each plate:

| Plate | Time | Filament |
|---|---|---|
| Each of the four tiles | 1 h 51 min | 89 g |
| The ten keys together | 30 min | 19 g |
| Total | 7 h 53 min | 375 g |

ASA, not PLA. A dark panel at a helm passes the PLA softening point and would sag. The X2D is enclosed, which is what ASA needs. Textured PEI plate at 100 C, 0.6 nozzle, 0.30 mm layers, 5 mm outer brim because large flat ASA lifts at the corners.

Orient each tile FRONT FACE UP. The perimeter roundover is then a clean top fillet rather than a near-horizontal overhang at the bed, and the presentation face can be ironed. The bowtie pockets end up on the bed side and bridge across at 8 mm, which is well within range.

Assemble face down on a flat surface, drop the keys in from the back, and bond. ASA solvent-welds with acetone, which gives a stronger joint than epoxy on this material.

Files: `helm-panel-tile-{TL,TR,BL,BR}.stl` and `helm-panel-key.stl`, plus five ready-to-print Bambu projects `helm-panel-tile-*.3mf` and `helm-panel-keys.3mf`. Built by `make_plate.py`.

### Slicer findings worth keeping

- `bambu-studio --export-3mf` exits 243 and writes nothing when given an absolute path while `--outputdir` is also set. Pass a bare filename.
- A CLI-made project 3MF still cannot be sliced by the CLI (rc 156, "slicing or export error for partplate 1"); the live X2D extruder and variant keys are only written by the GUI. `projects/Sharks-nametag/pipeline/graft_slice.py` supplies them to a throwaway copy for verification. Studio itself resolves them on open, so the shipped file needs no graft.
- The CLI default `curr_bed_type` of "Cool Plate" resolves to a 0 C bed for ASA, not merely a cold one as with PLA. `make_plate.py` overrides it and lists the override in `different_settings_to_system`, which Studio confirmed by showing the process preset as modified.

## One file, four plates, 2026-09-09

Brian asked for a single 3MF with two plates, one per half. Two plates is not
achievable, and the reason is worth recording.

Two tiles DO fit a 256 mm bed, but only as diagonal pairs. A search over every
rotation and a 1 mm translation grid found TL+BR and TR+BL fitting in
248 x 247 mm; top/bottom and left/right pairs do not fit at all, because each
tile's leg (123.75 mm) is wider than the notch it would have to nest into
(111.2 mm). Even the diagonal pair leaves 4 mm of bed margin and 0.5 mm
between the parts, and ASA on a 235 mm flat part needs a brim. There is
nowhere to put one, so the pairing was rejected.

The deliverable is `helm-panel-all-plates.3mf`: one file, four plates.

| Plate | Contents | Time | Filament |
|---|---|---|---|
| 1 | tile TL | 1 h 51 min | 89 g |
| 2 | tile TR | 1 h 50 min | 89 g |
| 3 | tile BL | 1 h 51 min | 89 g |
| 4 | tile BR plus all ten keys | 2 h 22 min | 109 g |
| Total | | 7 h 54 min | 376 g |

Consolidating the keys onto plate 4 saves a fifth print job. The per-tile
files remain for reprinting a single tile.

Built and verified by `make_multiplate.py`: every plate slices for real, the
layout check refuses any part within 10 mm of another or 5 mm of the bed edge,
and Studio's own reader is asked how many objects it finds on each plate. That
last check is the one that matters, because a mis-authored plate round trips
cleanly and renders blank. Confirmed by opening the file in Studio: four
plates, all populated, ASA on textured PEI, process shown as modified.

### The plate grid, corrected

Studio lays plates in a two-column grid whose rows run in negative Y, not in a
single row along X. Plate p (0-indexed) sits at
`((p % 2) * 307.2, -(p // 2) * 307.2)`. The vault had recorded a single row,
which is indistinguishable for two plates and wrong from the third onward:
plates 3 and 4 came back empty until this was fixed. Now in
[[printer-x2d]].

## Thickness, settled 2026-09-09

Brian asked whether 1/8 in would do. It will not, in printed plastic. Stiffness
goes as the cube of thickness, so 1/8 in is 64 times floppier than the 1/2 in
the model started at. Deflection at the Garmin screws, from the 1.6 kg unit
plus a firm 30 N screen press, modelling the web between the Garmin screws and
the perimeter fixings as a 65 mm cantilever over a 50 mm tributary width, ASA
at 2000 MPa with a 30 percent knockdown for sparse infill:

| Thickness | Printed ASA | Note |
|---|---|---|
| 1/8 in | 5.60 mm | panel visibly flexes, gasket stops sealing |
| 3/16 in | 1.66 mm | still spongy |
| 1/4 in | 0.70 mm | acceptable, but too thin for a 6 mm bowtie pocket |
| 3/8 in | 0.21 mm | CHOSEN |
| 1/2 in | 0.09 mm | the old value, over-built for a printed part |

1/8 in also breaks two things outright: the bowtie pockets cannot exist in a
3.2 mm panel, and the Garmin screws would have 3.2 mm of thread engagement,
forcing the nut plate option. 1/8 in is fine in ALUMINIUM, which deflects
0.11 mm at that thickness because it is 35 times stiffer than ASA; that is
probably where the number came from.

If the panel is ever cut from Starboard instead, HDPE is softer than printed
ASA AND creeps under sustained load, so it needs one size up:

| Starboard | Press now | Long-term sag | Total |
|---|---|---|---|
| 1/4 in | 1.09 mm | 0.75 mm | 1.84 mm, too much |
| 3/8 in | 0.32 mm | 0.22 mm | 0.54 mm, minimum |
| 1/2 in | 0.14 mm | 0.09 mm | 0.23 mm, matches 3/8 in printed ASA |

A thin ribbed panel (1/8 in skin plus 12 mm ribs on the hidden back) would beat
solid 3/8 in for less material, and is the right answer if weight ever matters.
Not built; the flat 3/8 in panel is stiff enough.

## Material verdict, 2026-09-09

Starboard is the better material for this part; the full comparison is in
[[marine-materials]]. ASA is stiffer, creeps less and takes more heat, but all
three are cured by thicker sheet, which is nearly free. Starboard's advantages
(impervious to water, tough, immune to sunscreen and solvents, one piece with
no bonded seams) cannot be engineered into a printed panel.

Both paths are built and ready: rout 1/2 in Starboard using the printed
template, or print the four ASA tiles. The printed route stays worthwhile if
features a router cannot make are ever wanted.

## DECISION, 2026-09-09: 1/2 in black King Starboard, routed in one piece

Brian chose Starboard over the printed ASA tiles. Rationale is in
[[marine-materials]]: ASA's advantages (stiffness, creep, heat) are all cured
by thicker sheet, which is nearly free, while Starboard's (impervious to water,
tough, immune to sunscreen and solvents, seamless) cannot be engineered into a
printed part. 1/2 in because HDPE is softer than printed ASA and creeps, so it
needs one size up; it lands at 0.23 mm total deflection, matching 3/8 in ASA.

An HDPE filament was considered and rejected. The only seriously engineered PE
filament, Braskem FL300PE, died when Braskem shut down Xtellar (announced June
2024, wound down 2025); what remains is white-label stock with no datasheets.
Printed unfilled polyolefin measures about 380 to 575 MPa flexural, roughly
HALF of HDPE sheet, and polyethylene cannot be glued, which would leave the
tile seams permanently unbonded. Bambu Studio does ship Generic PE and PP
profiles compatible with the X2D 0.6 nozzle (PE at 210 C, bed 55 C, 8 mm3/s),
but Bambu sells no such filament and there are no credible reports of anyone
printing HDPE on these machines. If a polyolefin part is ever genuinely needed,
mill it from sheet or print PP-GF.

### The part

One piece of 1/2 in (12.7 mm) black King Starboard, 469.9 x 292.1 mm
provisional. Model is `helm-panel.stl` / `.step`, 1346 cm3, about 1.29 kg.
The window, its R3.175 corners and the four blind 2.3 mm pilots are unchanged;
only the thickness and the one-piece construction differ from the ASA version.

### Shop process

1. Pattern the outline from the old clear cover. Corner radius comes from the
   cover, not from the model's assumed 1/2 in.
2. Lay out the cutout centrelines. Register the printed template on its notches
   with TOP toward the unit's top. Tape and clamp.
3. Drill the four 2.3 mm pilots through the template guides.
4. Drill an 8 mm relief hole inside each window corner, jigsaw the window out
   leaving about 2 mm.
5. Rout the window to the template. Bit reach: the BEARING rides the template
   and the CUTTER only has to span the workpiece, so any pattern or flush-trim
   bit with at least 5/8 in of cutting length works; a common 1 in bit clears
   12.7 mm stock by 12.7 mm. Use a 1/4 in bit so the corners come out at
   R3.175, matching Garmin's drawn R3.7 without needing to be squared.
6. Roundover the front face perimeter, 1/8 in.
7. Test fit the unit dry before any screws.

Routing HDPE: use a SHARP carbide spiral, ideally a single-flute or O-flute
ground for plastics, and keep the feed rate up. A dull bit or a slow feed melts
HDPE and re-welds the chips into the cut. Do not let the bit dwell.

### Fastening

- Garmin's four screws take a 2.3 mm pilot and get 10 mm of engagement in
  12.7 mm stock, which is ample. Do NOT overtighten: HDPE creeps and the
  threads will strip or slowly loosen.
- Perimeter screws must be free to move. Black HDPE grows about 2.5 mm across
  469.9 mm over a 30 C swing, so drill oversized clearance holes (about 6.5 mm
  for a #10 shank) and fit finishing washers. Tight holes will bow the panel.
- Nothing bonds to HDPE. All fastening is mechanical; do not plan on adhesive.

### Materials

Black King Starboard, 1/2 in, at least 19 x 12 in. A 24 x 27 in cut piece is
the usual smallest practical purchase. Stainless #10 oval-head screws and
finishing washers for the perimeter.

### The printed alternative, kept

`helm-panel.py` still builds the four-tile ASA version under `TILES=1`, and
`helm-panel-all-plates.3mf` (four plates, 7 h 54 min, 376 g) is still valid at
3/8 in ASA. That path stays worthwhile only if features a router cannot cut are
ever wanted: a recessed pocket, a cable channel, integrated ribs. Note it is
self-consistent at 3/8 in ASA and is NOT derived from the 1/2 in Starboard
panel.
