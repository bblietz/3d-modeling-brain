# Task 8 report - Buildability check, exports, renders, viewer

Run 2026-08-24 from the vault root. `drawer_bench.py`, `scripts/`, and
`knowledge/woodworking-stock.md` were not modified. All probe scripts live in
`$SCRATCH` (`build_check.py`, `build_check2.py`, `dims.py`, `step_check.py`).

**Status: DONE_WITH_CONCERNS.** All four deliverables exist and every cut-list
dimension matches the design constants exactly. Two blocking *assembly-order*
interferences were found by an insertion walk (they are invisible to the
model's seated-position asserts) and both have verified fixes. They are
reported here, not fixed, because both change text in design.md.

---

## Step 1 - Export

Command (verbatim):

```bash
SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad && EXPORT=1 TMP_STL=$SCRATCH/db.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py && cat projects/Drawer-bench/cutlist.md && ls -la projects/Drawer-bench/drawer_bench.step
```

Output:

```
exported cutlist + step
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom', 'front_bot', 'front_top', 'drawer_side_bot', 'drawer_end_bot', 'drawer_bottom_bot', 'drawer_side_top', 'drawer_end_top', 'drawer_bottom_top', 'top']
```

No assertion fired; runtime about 4 s.

### Deliverables

| File | Present | Size |
|---|---|---|
| `projects/Drawer-bench/cutlist.md` | yes | 4603 B |
| `projects/Drawer-bench/cutlist.csv` | yes | 3586 B |
| `projects/Drawer-bench/drawer_bench.step` | yes | 428863 B |
| `projects/Drawer-bench/images/final-4view.png` | yes | 174025 B |

STEP round-trip check (`import_step` back into build123d): 1 solid, 123 faces,
volume 72598 cm3, bbox 914.4 x 609.6 x 508.0 at origin - identical to the
in-memory assembly and to the sum of all registry parts x qty (72598 cm3), so
nothing was lost in the export. Note it is one *fused* body (the `+` operator
unified the coplanar faces of touching parts), not a per-part assembly tree: a
downstream tool cannot pick individual parts out of this file. Fine as a shape
reference; if Brian wants per-part STEP for a shop or CNC that is a separate
export.

### Cut list as emitted (verbatim)

```
---
type: cutlist
project: Drawer Bench 36x24x20 (provisional)
---

# Cut list - Drawer Bench 36x24x20 (provisional)

| Qty | Part | T x W x L (mm) | T x W x L (in) | Material | Notes |
|---|---|---|---|---|---|
| 1 | top | 44.4 x 609.6 x 914.4 | 1-3/4 x 24 x 36 | maple butcherblock (Boos match) | provisional 1-3/4 thick, 1-1/4 overhang all round; edge profile to match the island; figure-8 fasteners into rail_top and rail_rear, no glue |
| 1 | bottom | 12 x 484.7 x 802.2 | 1/2 x 19-1/16 x 31-9/16 | ply 12mm | notch the four corners 51.85 wide x 39.15 (front) / 51.85 (rear) for the posts; edges in the side/back grooves and the rail_bot rabbet (glue and screw the front edge) ; not a plain rectangular blank (98% of bounding box); needs a drawing or template |
| 2 | drawer_bottom_bot/drawer_bottom_top | 12 x 445.9 x 677.2 | 1/2 x 17-9/16 x 26-11/16 | ply 12mm |  |
| 2 | drawer_end_bot | 12 x 209.5 x 677.2 | 1/2 x 8-1/4 x 26-11/16 | ply 12mm | 1/4 bottom groove at 1/2 up ; not a plain rectangular blank (97% of bounding box); needs a drawing or template |
| 2 | drawer_end_top | 12 x 82.6 x 677.2 | 1/2 x 3-1/4 x 26-11/16 | ply 12mm | 1/4 bottom groove at 1/2 up ; not a plain rectangular blank (92% of bounding box); needs a drawing or template |
| 2 | drawer_side_bot | 12 x 209.5 x 457.2 | 1/2 x 8-1/4 x 18 | ply 12mm | 1/4 end rabbets, 1/4 bottom groove at 1/2 up ; not a plain rectangular blank (94% of bounding box); needs a drawing or template |
| 2 | drawer_side_top | 12 x 82.6 x 457.2 | 1/2 x 3-1/4 x 18 | ply 12mm | 1/4 end rabbets, 1/4 bottom groove at 1/2 up ; not a plain rectangular blank (90% of bounding box); needs a drawing or template |
| 1 | back | 18 x 387.4 x 717.5 | 11/16 x 15-1/4 x 28-1/4 | ply 18mm | housed 3/8 in each post; top edge under the rear rail; stopped groove 6.35 deep x 12 (T12) on the inner face for the bottom, lower wall 7.05 above the bottom edge, stopped 9.525 from each end |
| 2 | side | 18 x 412.8 x 425.5 | 11/16 x 16-1/4 x 16-3/4 | ply 18mm | face grain vertical on the show face; housed 3/8 in each post; stopped groove 6.35 deep x 12 (T12) on the inner face for the bottom, lower wall 7.05 above the bottom edge, stopped 9.525 from each end |
| 2 | rail_rear/rail_bot | 18 x 38.1 x 717.5 | 11/16 x 1-1/2 x 28-1/4 | soft maple | REAR top rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; figure-8 fasteners on top ; FRONT bottom rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; rabbet 6.35 x 12 (T12) on the rear-top edge between the shoulders; glue and screw the bottom into it (no lip above) ; not a plain rectangular blank (89% of bounding box); needs a drawing or template |
| 2 | rail_top/rail_mid | 18 x 25.4 x 717.5 | 11/16 x 1 x 28-1/4 | soft maple | FRONT top rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; figure-8 fasteners on top ; FRONT mid rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; carries the top drawer slides |
| 1 | front_bot | 19 x 288.9 x 692.1 | 3/4 x 11-3/8 x 27-1/4 | soft maple | grain along the length; screwed to the box from inside through slotted holes (cross-grain 11-3/8 wide); pull undecided |
| 1 | front_top | 19 x 146 x 692.1 | 3/4 x 5-3/4 x 27-1/4 | soft maple | grain along the length; screwed to the box from inside; pull undecided |
| 4 | post_front/post_rear | 76.2 x 76.2 x 463.6 | 3 x 3 x 18-1/4 | soft maple | one of 2 FRONT posts, left/right mirrored, grooves on the inner faces; glue-up of two 8/4 pieces milled to 1-1/2; 3/8 chamfer x4 edges full length; side groove T18 (measured ply) x 3/8 at 1/2 from the outer face, stopped 1-1/2 above the floor, open at top; three mortises T18 x 3/8 on the inner face 1 in behind the front face at Z 19.05-57.15, 298.45-323.85, 438.15-top for the rail tenons ; not a plain rectangular blank (94% of bounding box); needs a drawing or template ; one of 2 REAR posts, left/right mirrored, grooves on the inner faces; same blank and chamfer as post_front; side groove as post_front; back groove T18 x 3/8 on the inner face at 1/2 from the rear face, stopped 1-1/2 above the floor, open at top; no mortises ; not a plain rectangular blank (91% of bounding box); needs a drawing or template |

Inches rounded to the nearest 1/16.

## Totals by material

- maple butcherblock (Boos match): 1 part, 0.56 m2 face area (no kerf/waste allowance)
- ply 12mm: 11 parts, 1.66 m2 face area (no kerf/waste allowance)
- ply 18mm: 3 parts, 0.63 m2 face area (no kerf/waste allowance)
- soft maple: 10 parts, 0.53 m2 face area (no kerf/waste allowance)
```

### Row-by-row comparison against the brief's table

14 rows expected, 14 rows emitted. Every part name, every quantity and every
**inch** value matches the brief exactly. Six rows differ in the last printed
digit of the **mm** column. I dumped the bounding boxes at full precision
(`$SCRATCH/dims.py`) before judging them.

| Qty | Part | Brief mm | Emitted mm | Model value (exact) | Verdict |
|---|---|---|---|---|---|
| 4 | post_front/post_rear | 76.2 x 76.2 x 463.6 | 76.2 x 76.2 x 463.6 | 76.2 / 76.2 / 463.55 | match |
| 2 | side | 18 x 412.8 x 425.5 | 18 x 412.8 x 425.5 | 18 / 412.75 / 425.45 | match |
| 1 | back | 18 x 387.4 x 717.6 | 18 x 387.4 x **717.5** | 18 / 387.35 / 717.55 | print rounding only |
| 2 | rail_rear/rail_bot | 18 x 38.1 x 717.6 | 18 x 38.1 x **717.5** | 18 / 38.1 / 717.55 | print rounding only |
| 2 | rail_top/rail_mid | 18 x 25.4 x 717.6 | 18 x 25.4 x **717.5** | 18 / 25.4 / 717.55 | print rounding only |
| 1 | front_bot | 19.1 x 288.9 x 692.2 | **19** x 288.9 x **692.1** | 19.05 / 288.925 / 692.15 | print rounding only |
| 1 | front_top | 19.1 x 146.1 x 692.2 | **19** x **146** x **692.1** | 19.05 / 146.05 / 692.15 | print rounding only |
| 1 | bottom | 12 x 484.7 x 802.2 | 12 x 484.7 x 802.2 | exact | match |
| 2 | drawer_side_bot | 12 x 209.6 x 457.2 | 12 x **209.5** x 457.2 | 12 / 209.55 / 457.2 | print rounding only |
| 2 | drawer_end_bot | 12 x 209.6 x 677.2 | 12 x **209.5** x 677.2 | 12 / 209.55 / 677.2 | print rounding only |
| 2 | drawer_bottom_bot/_top | 12 x 445.9 x 677.2 | 12 x 445.9 x 677.2 | exact | match |
| 2 | drawer_side_top | 12 x 82.6 x 457.2 | 12 x 82.6 x 457.2 | 12 / 82.55 / 457.2 | match |
| 2 | drawer_end_top | 12 x 82.6 x 677.2 | 12 x 82.6 x 677.2 | 12 / 82.55 / 677.2 | match |
| 1 | top | 44.5 x 609.6 x 914.4 | **44.4** x 609.6 x 914.4 | 44.45 / 609.6 / 914.4 | print rounding only |

**No geometry problem.** Every flagged cell is an exact-half value (x.x5) whose
IEEE-754 product falls a hair below the midpoint, so `cutlist._fmt`'s
`round(mm, 1)` rounds it down while the brief's hand table rounded it up:
`1.75 * 25.4 = 44.449999999999996` -> 44.4, whereas the literal `44.45` ->
44.5. The underlying solids measure 44.45 / 19.05 / 146.05 / 692.15 / 209.55 /
717.55 mm, i.e. exactly the design constants. Where the product lands just
*above* the midpoint (82.55 from `3.25 * 25.4`) the same code prints 82.6 and
agrees with the brief - which is the tell that this is float rounding, not
geometry.

Impact 0.05 mm, and the inch column (what gets used at the lumber yard) is
correct in every row. Not fixed here: `scripts/` is off limits for this task.
For the controller: `cutlist._fmt` would print these correctly with
`Decimal(str(mm)).quantize(Decimal("0.1"), ROUND_HALF_UP)`. Low priority.

---

## Step 2 - Buildability check (furniture skill Phase 4)

| Check | Verdict | Detail |
|---|---|---|
| Stock thickness | **PASS, conditional** | 18 mm and 12 mm ply are stock sizes (`woodworking-stock.md`: actual 17.5-18.2 and 11.5-12.2). Model uses nominal 18.0 / 12.0. Maple milling sizes have **no entry** in the stock note (it covers sheet goods and 1x/2x softwood only), so 8/4 and 4/4 rough hardwood is a purchase spec to confirm at the yard, not a checked stock size. |
| Rectangularity | **PASS, one notes gap** | 8 of 18 registry parts flagged under 98% of their bounding box, in 6 cut-list rows. Post/bottom/rail/panel notes carry every dimension needed; the four drawer rows do not. |
| Grain / show face | **PASS, 4 gaps** | Sides and both fronts state grain in the notes. Posts, back, top and the post glue-up seam do not. |
| Joinery fit | **PASS, 3 must-dos** | All housed edges are probe-verified inside their grooves. Every joint is modeled at zero clearance; three shop allowances must be added. |
| Stock yield | **PASS** | One 18 mm sheet (23% used), one 12 mm sheet (56% used), about 10 bf of 8/4 and 8 bf of 4/4 soft maple. |
| Wood movement | **PASS, one watch item** | Only two cross-grain spans over 150 mm: the top (4.0 to 8.6 mm) and front_bot (3.0 mm). Both already have movement hardware. |
| Transport | **PASS** | 914.4 x 609.6 x 508 mm, 48.8 kg; smallest cross-section 609.6 x 508 clears a 750 mm doorway with 140 mm to spare. |
| Assembly order | **FAIL as written in design.md** | Two blocking interferences, both verified by an insertion walk, both with verified fixes. See below. |

### Stock thickness

Six different joint widths and one part thickness are all driven by the
measured ply, so **both sheets must be measured and the constants re-run
before any joinery is cut**: post side grooves and mortises T18 wide; rail
thickness `RAIL_T = T18`; side/back bottom grooves 12 wide x 6.35 deep;
rail_bot rabbet 6.35 x 12; drawer end rabbets 12 wide x 6.35 deep; drawer
bottom grooves 12 wide. A 17.5 mm sheet moves all of them. The file is already
parameterised for this (`T18`, `T12`).

Maple: posts 3 x 3 in net as a glue-up of two 1-1/2 in halves -> 8/4 rough
(3 in cannot come out of 8/4 in one piece; 12/4 would avoid the glue line).
Fronts 19.05 mm net -> 4/4 rough (buy rough, not S4S 3/4, which leaves nothing
for flattening). Rails 18.0 mm net -> 4/4. Top 44.45 mm purchased butcherblock,
thickness and edge profile to be measured off the Boos island.

### Rectangularity - flagged parts and whether the notes carry the dims

| Part | Ratio | Notes carry the dims? |
|---|---|---|
| post_front | 94% | **Yes.** 3/8 chamfer x 4 edges full length; side groove T18 x 3/8 at 1/2 from the outer face, stopped 1-1/2 above the floor, open at top; three mortises T18 x 3/8 on the inner face 1 in behind the front face at Z 19.05-57.15, 298.45-323.85, 438.15-top. Position, width, depth and extent all present. |
| post_rear | 91% | **Yes.** Same blank/chamfer/side groove; back groove T18 x 3/8 at 1/2 from the rear face, stopped 1-1/2, open at top; no mortises. |
| rail_bot | 89% | **Yes.** Rabbet 6.35 x 12 (T12) on the rear-top edge between the shoulders. (But see assembly finding B - "between the shoulders" is the thing that has to change.) |
| bottom | 98% | **Yes.** Four corner notches 51.85 wide x 39.15 (front) / 51.85 (rear). |
| drawer_side_bot | 94% | **No.** "1/4 end rabbets, 1/4 bottom groove at 1/2 up" gives the two depths and nothing else. |
| drawer_side_top | 90% | **No.** Same text. |
| drawer_end_bot | 97% | **No.** "1/4 bottom groove at 1/2 up". |
| drawer_end_top | 92% | **No.** Same text. |

Not flagged but not plain blanks either: `side` and `back` carry the bottom
groove and still measure over 98%; their notes give it in full anyway (6.35
deep x 12 wide, lower wall 7.05 above the bottom edge, stopped 9.525 from each
end), so the notes are better than the flag. Plain blanks: rail_rear,
rail_top, rail_mid, front_bot, front_top, both drawer bottoms, top.

**Gap to fix (drawer rows):** the end rabbet is 6.35 deep x **12 wide** and the
bottom groove is 6.35 deep x **12 wide**, both cut to the *measured* 12 mm ply,
and "1/2 up" means the groove's lower wall sits 12.7 mm above the box side's
bottom edge - that 12.7 is the undermount bottom recess, not a free choice.
None of that is in the notes. Every other flagged part says "T18 (measured
ply)" or "12 (T12)"; these four should too.

Readability caveat: the merged rows put two parts on one line
(`rail_rear/rail_bot` qty 2, `post_front/post_rear` qty 4) with the geometry
flags concatenated, so only the order of the note fragments says which flag
belongs to which part. Traceable, but the drawing set has to disambiguate.

### Grain / show face

Stated: `side` "face grain vertical on the show face"; `front_bot` and
`front_top` "grain along the length" (correct - the fronts' long dimension is
the bench width).

Not stated, worth adding:
- **posts** - grain along the 463.55 mm length (obvious, but the drawing needs it).
- **post glue-up seam** - each post is two 1-1/2 in halves, which leaves a glue
  line on two opposite faces of a 3 in post. Decide where it lands: put the
  seam in the front-to-back plane so it reads on the side faces rather than
  the drawer-front face, and cut both halves off one board so the seam reads
  as a grain line.
- **back** - face grain direction unspecified; not a show face, but run it
  vertical for consistency with the sides.
- **top** - design.md says the grain runs along the 36 in length (Boos style);
  the cut-list note only says "match the island".
- **front continuity** - cut `front_top` and `front_bot` in sequence from one
  board so the grain runs continuously across the two drawer faces (and the
  11-3/8 in front's two-board glue-up gets matched at the same time).

### Joinery fit

Probed from the solids: 23.75 mm free above each drawer box (need 20 to tilt it
onto undermounts), 32.8 mm rear clearance (need 9), 12.7 mm bottom recess,
box outer width = opening - 10.0 mm, box depth = slide length exactly
(457.2 mm). Openings 114.30 mm (4-1/2 in) top and 241.30 mm (9-1/2 in) bottom,
matching design.md's resolutions. Chamfer 9.525 < setback 12.7 and < frame
setback 25.4, so no chamfer breaks into a groove or mortise (asserted by
volume in the model).

Three must-dos:
1. **Test cut every groove, mortise and rabbet in scrap against the measured
   ply.** The skill's rule; nominal 18.0/12.0 is what the model assumes.
2. **Add shop clearance where the model has none.** Mortises about 1 mm deeper
   than the 9.525 mm tenon for glue relief; the bottom's corner notches about
   1 mm oversize around the posts (as modeled they hug the posts at zero
   clearance in *both* axes - that exactness is what makes assembly finding A
   below bite); the stopped bottom grooves in the sides are exactly as long as
   the tab that fills them (393.7 mm each, likewise 698.5 mm in the back), so
   run them through as design.md already permits.
3. **The undermount numbers are unverified.** Box width = opening - 10, 12.7
   recess, 20 tilt clearance, 9 rear clearance, 8 standoff are the Blum Tandem
   563H class values carried over from `knowledge/learnings/cabinet-bench.md`,
   flagged there as "UNVERIFIED vendor values". Check them against the spec
   sheet of the slides actually bought before cutting boxes. Note the vault's
   generic "1 mm gap per side" drawer rule is a wooden-runner value and does
   **not** apply here.

### Stock yield

Standard sheet 2440 x 1220, 3 mm kerf, all lengths run along the sheet length.

- **18 mm ply, 3 parts, 0.63 m2.** Band 1 (387.35 wide): `back` 717.55 long.
  Band 2 (412.75 wide): both `side` panels end to end, 425.45 + 425.45 =
  850.9 mm, with their 425.45 dimension along the sheet length so the show-face
  grain runs vertical. Bands total 800 mm of the 1220 width and 851 mm of the
  2440 length: the whole lot fits in one corner, **23% of one sheet**. One sheet
  as the brief says, but a 1220 x 1220 half panel would do it.
- **12 mm ply, 11 parts, 1.66 m2 of 2.98.** Band 1 (484.7 wide): `bottom` 802.2
  + two `drawer_bottom` 677.2 = 2156.6 mm. Band 2 (209.55 wide): two
  `drawer_end_bot` 677.2 + two `drawer_side_bot` 457.2 = 2268.8 mm. Band 3
  (82.55 wide): the four top-drawer parts, 2268.8 mm. Bands + 3 kerfs =
  789 mm of the 1220 width, longest run 2269 of 2440. **One sheet with 431 mm
  of width to spare** - matches the brief.
- **Soft maple.** 8/4 for the posts: 8 blanks 1-1/2 x 3 x 18-1/4 net (rough
  2 x 3-1/4 x 20-1/4) = 7.3 bf, buy about 10 bf for selection. 4/4 for the
  fronts: 11-3/8 (two glued boards) + 5-3/4 wide at 27-1/4 long = about 4 bf
  rough, buy 6 bf so the three pieces come off one board in sequence. 4/4 for
  the rails: four rails, 5 in of total width at 28-1/4 long = 1.25 bf, buy 2 bf.
  Mill the rails **after** measuring the ply (`RAIL_T = T18`).
- **Top** purchased, not cut from stock.

### Wood movement

Only two cross-grain spans exceed the 150 mm rule. At a 4% MC swing:

| Part | Cross-grain span | Movement | Hardware |
|---|---|---|---|
| top, edge-grain (Boos style) | 609.6 mm (24 in) | 4.0 mm | figure-8s into rail_top and rail_rear |
| top, if a flatsawn slab | 609.6 mm | 8.6 mm | see watch item |
| front_bot | 288.925 mm (11-3/8 in) | 3.0 mm | slotted screws from inside |
| front_top | 146.05 mm | 1.5 mm | screws from inside |
| post | 76.2 mm | 0.8 mm | none needed |

The vault's rule of thumb (1% of width seasonally) gives 6.1 mm for the top and
2.9 mm for the bottom front, bracketed by the numbers above.

- Front reveals absorb it: the bottom front growing 3.0 mm in height, fixed at
  its centre, moves each edge 1.5 mm into a 6.35 mm mid reveal and a 19.05 mm
  floor gap. The 3.175 mm side reveals are along the grain and do not change.
- Ply panels, bottom and drawer boxes: stable. The bottom glued and screwed
  into the rail rabbet is ply-to-maple over 6.35 mm - fine.
- Panels glued into post grooves: 18 mm glue line, far under the 150 mm rule.
- **Watch item:** figure-8 fasteners give roughly 3 mm of travel each. Front
  and rear pairs with the top's centre effectively fixed cover about +/- 2 mm
  per edge = 4 mm total, adequate for an edge-grain top and marginal for a
  flatsawn slab (8.6 mm). Once the Boos top is measured: if it is not
  edge-grain, elongate the slots in rail_top and rail_rear or use Z-clips, and
  fix the top at the front edge so all the movement goes to the back.

### Transport

Assembled 914.4 x 609.6 x 508 mm. Mass estimate from the solid volumes
(soft maple 610, butcherblock 705, ply 680 kg/m3): **48.8 kg total, 31.3 kg
carcase + 17.5 kg top**. The top is on figure-8s and not glued, so it comes off
for the carry. The smallest cross-section is 609.6 x 508, so it clears a
750 mm doorway upright with 140 mm to spare; on its side the 546.1 mm carcase
width also clears. Not knock-down, so it has to be glued up somewhere it can be
walked out of; the 914 mm length is the limit on stair turns.

### Assembly order walk - FAIL as written, two fixes verified

Method (`$SCRATCH/build_check.py`, `build_check2.py`): every part is driven back
out along its insertion axis from the seated position and checked for solid
overlap against everything already placed, at 0 / 25 / 50 / 75 / 100% of the
travel. Zero-clearance seating gives a zero-volume touch, so any non-zero
overlap is a real jam. This is the check the model's asserts cannot make: they
only prove the parts do not overlap once seated.

Walking design.md's "Assembly order" section:

| Step | Move | Result |
|---|---|---|
| 1 | side panel dropped into both post grooves, 425.45 mm in -Z | **PASS** (and it is the only route: the panel is 412.75 mm deep, the gap between the posts is 393.7) |
| 2 | back + rail_rear into the rear post groove, 9.525 mm in -X | **PASS** |
| 3a | bottom's rear tab into the back's groove, 6.35 mm in +Y | **FAIL** - 2983 mm3 into post_fl, plus 484 mm3 into the back |
| 3b | bottom sideways into the side's groove, 6.35 mm in -X | **FAIL** - 484 mm3 into the back's stopped groove end |
| 4 | rail_top into the post mortise, 9.525 mm in -X | **PASS** |
| 4 | rail_mid, same | **PASS** |
| 4 | rail_bot, same | **FAIL** - 725.8 mm3 into the bottom panel |
| 5 | right sub-assembly closes over four tenons, the back edge and the bottom's edge, 9.525 mm in -X | **PASS** |
| 6 | drawers, fronts, top | no housed joints |

**Finding A - design.md steps 2 and 3 cannot both be done in that order.**
Once the back is seated in the rear post groove, there is no way to bring the
bottom to it. The bottom cannot move in Y, because its corner notches hug the
posts at zero clearance in Y as well as X (the 6.35 mm forward move buries
2983 mm3 of panel in the front post); and it cannot move in X either, because
the bottom groove in the back is stopped at exactly the tab length (groove
698.5, tab 698.5), so the 6.35 mm sideways move jams 484 mm3 into the groove
end. Two fixes, both verified clash-free:

- **(i) Reorder.** Pre-join the bottom into the back's groove *off the bench*
  (a free +Y move while the back is loose), then bring back + rail_rear +
  bottom on as **one unit** with a single 9.525 mm move in -X: the back edge
  and the rear rail's tenons enter the rear post groove while the bottom's
  left edge enters the side panel's bottom groove (3.175 mm of approach, then
  6.35 mm of engagement). Verified: no overlap at any point of the travel.
- **(ii) Run the bottom groove through the back panel** (design.md already
  permits this: "The grooves may be run through in the shop; their ends are
  hidden inside the post grooves") and slide the bottom in from the still-open
  right side. Verified clash-free over a 250 mm slide.

Recommend both: (i) costs nothing and (ii) also removes the zero-clearance
stopped groove. The same argument applies to the side panels' stopped bottom
grooves (393.7 mm groove, 393.7 mm tab) - insertion there is face-on so it does
not jam, but there is no room for a shop error; run them through too.

**Finding B - the bottom rail's rabbet, as design.md specifies it, traps the
bottom panel.** design.md says the rabbet runs "between the tenon shoulders".
That leaves the rail full section for the 9.525 mm of each tenon, exactly at
the height and depth the bottom's front tab occupies. The rail has to translate
9.525 mm along X relative to the bottom to enter its closed mortise, and that
full-section shoulder sweeps straight through the tab: **725.8 mm3 of
interference**. It is symmetric and unavoidable by resequencing - the same
725.8 mm3 appears whether the rail arrives with the bottom in place (step 4),
the bottom arrives with the rail in place, or the rail arrives with the right
sub-assembly at step 5. Fixes:

- **Run the 6.35 x 12 rabbet through both tenons** (a stepped tenon). Verified
  clash-free. Cost: 1452 mm3, 0.3% of the rail's volume; the tenon keeps its
  full 18 mm section over the lower 26.1 mm of its 38.1 mm height, and the
  small void left in the mortise is hidden. Same router setup, one pass instead
  of a stopped one.
- Or **shorten the bottom's front tab** by at least 9.525 mm at each end (the
  two front corner notches go from 51.85 to about 61.4 mm wide). It is a dust
  panel, so nothing is lost - but it changes the `bottom` geometry and its
  cut-list note.

Either way design.md's "Resolutions from the CAD" text has to change, which is
why nothing was edited here.

Also confirmed by the walk, consistent with the task context: the mid and
bottom mortises are closed top and bottom, so **rail_mid and rail_bot must be
tenoned in during glue-up** - there is no way to add them later. The top rail's
mortise is open at the post top, but its tenons still enter axially.

Unchanged open items from design.md, both confirmed numerically:
- **7.05 mm ply lip** under the bottom groove in the sides and back
  (`BOT_Z0 - GROOVE_STOP = 45.15 - 38.1`). Supported only at the post ends;
  fragile to machine. Lowering the groove stop from 1-1/2 to 1 in gives about
  20 mm. Owner's call.
- **Top drawer interior height 57.9 mm** (bottom drawer 184.8 mm). design.md's
  own note said "about 58 mm; if that is too shallow, drop the mid rail to
  3/4 in or move the reveal up". Owner's call.

Nothing here requires changing a user-specified dimension. No dimension was
altered.

---

## Step 3 - Renders

- `projects/Drawer-bench/images/final-4view.png` - iso (30, -60), front (0, -90),
  top (90, -90), right (0, 0). The front elevation reads cleanly: two drawer
  fronts with the mid reveal, the posts standing proud at each end, the top
  overhanging both sides, the floor shadow gap under the bottom front. The
  right elevation shows the side panel set back between the posts with the
  post feet clear below it. The top view is the 914.4 x 609.6 slab, as
  expected. The iso pane has the matplotlib depth-sort artifacts noted in the
  brief: interior faces punch through the top and the drawer region.
- `projects/Drawer-bench/images/final-iso-front.png` - extra views (25, -35) and
  (15, -75) for the drawer/front region.
- `projects/Drawer-bench/images/final-iso-rear.png` - extra views (20, -120) and
  (25, 120).

The most readable of the six is `final-iso-rear.png` view0 (elev 20, azim
-120): right side plus front, showing both drawer fronts, the mid reveal, the
floor gap, the chamfered posts proud of the fronts and the top's overhang all
round. (25, 120) shows the rear three-quarter with the back panel set back
between the rear posts. Artifacts remain on every iso pane - the renderer
z-sorts facets and the bench has real interior geometry (drawer boxes, bottom
panel) behind its faces. Proportions, reveals and the overall form are
verifiable; interior detail is not. The OCP viewer (step 4) is the check for
that.

---

## Step 4 - Viewer push

```
$ scripts/cad-viewer.sh
viewer: http://localhost:3939/viewer (push models with SHOW=reset first, SHOW=1 for iterations)

$ curl -sf -o /dev/null http://localhost:3939/viewer   ->  OK (first try)

$ SHOW=reset .venv/bin/python projects/Drawer-bench/drawer_bench.py
+++++++++++++++++++++++++
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom', 'front_bot', 'front_top', 'drawer_side_bot', 'drawer_end_bot', 'drawer_bottom_bot', 'drawer_side_top', 'drawer_end_top', 'drawer_bottom_top', 'top']
exit=0
```

Server running (`.venv/bin/python -m ocp_vscode --port 3939`, pid 1365933) and
the WebGL Chrome window opened on Brian's desktop (pid 1367211,
`--use-angle=vulkan`). All 25 named instances transmitted with the camera
reset. `/tmp/ocp-viewer.log` is empty (no errors).

**Brian is not present, so no sign-off was collected. The model is pushed and
viewer sign-off is pending.** Re-push with `SHOW=1` after any later edit.

---

## Concerns

1. **Blocking, needs a decision: rail_bot's rabbet must run through its
   tenons** (or the bottom's front tab must lose 9.525 mm at each end). As
   design.md specifies it ("between the tenon shoulders") the bench cannot be
   assembled: 725.8 mm3 of interference, unavoidable by resequencing.
2. **Blocking, needs a decision: design.md's assembly steps 2 and 3 are not
   executable in that order.** Fix by pre-joining the bottom to the back off
   the bench and bringing them on as one unit, and/or by running the bottom
   groove through the back panel. Both verified.
3. Drawer cut-list notes are missing the rabbet and groove widths (both = the
   measured 12 mm ply) and the meaning of "1/2 up" (the 12.7 mm undermount
   recess). Every other flagged part carries its dims.
4. Grain direction is unstated for the posts, the back and the top, and the
   post glue-up seam orientation is an unmade show-face decision.
5. Undermount slide numbers are still the unverified Blum 563H class values
   from cabinet-bench; verify against the purchased spec before cutting boxes.
6. Top fastening: figure-8s cover an edge-grain top's 4.0 mm of movement but
   not a flatsawn slab's 8.6 mm. Decide once the Boos top is measured.
7. design.md's own two open items stand, with the numbers confirmed: the
   7.05 mm ply lip and the 57.9 mm top-drawer interior.
8. Cosmetic: `cutlist._fmt` rounds x.x5 mm values down (44.4 for a 44.45 mm
   top). Inch column unaffected. `scripts/` was out of scope for this task.
9. The STEP is a single fused solid (123 faces after coplanar-face unification),
   not a per-part assembly tree. Correct volume and envelope; not usable for
   picking individual parts out.
