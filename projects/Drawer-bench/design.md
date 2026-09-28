---
name: drawer-bench-design
description: Approved design for the maple post-and-panel drawer bench (kitchen bench); overall footprint and height measured 2026-09-17, top thickness confirmed 2026-09-27, overhang/edge profile still pending the Boos island measurement
created: 2026-08-24
status: cad-built, provisional dimensions, resolutions pending Brian's review
---

# Drawer Bench - design

Approved section by section with Brian on 2026-08-24 (brainstorm with the
visual companion, then terminal). Companion to [[drawer-bench-brief]];
the plywood sibling is [[cabinet-bench-brief]]. Kitchen bench that lives
with the family's John Boos block island.

## Provisional inputs (named constants in the CAD; nothing is cut from them)

| Input | Provisional value | Becomes final when |
|---|---|---|
| Overall top size | **40 x 24 in (1016 x 609.6 mm), measured (Brian, 2026-09-17)** | done |
| Overall height (floor to top surface) | **19-5/8 in (498.475 mm), measured (Brian, 2026-09-17)** | done |
| Top thickness | **1-3/4 in (44.45 mm), confirmed against the Boos island (Brian, 2026-09-27)** | done |
| Top overhang past the posts | 1-1/4 in (31.75 mm) per side | still to measure |
| Top edge profile | unknown (square / eased / bullnose / chamfer) | still to measure |
| 3/4 ply actual thickness | 18.0 mm | measured at cut time |
| 1/2 ply actual thickness | 12.0 mm | measured at cut time |
| Undermount slide | 18 in drawer class, Blum 563H4570B (471 mm runner) | purchased slide's sheet |

Convention locked: 40 x 24 is the TOP; the posts sit inside the top by
the overhang (footprint 37-1/2 x 21-1/2 in, drawer opening between posts
31-1/2 in at the current numbers; overhang is still provisional, so the
footprint and opening will move slightly once it is measured, but the
overall 40 x 24 x 19-5/8 envelope will not). Top thickness is now
confirmed at 1-3/4 in (matches the provisional CAD value exactly, so
`TOP_T` did not change); leg width (post size, 3 in) is likewise
confirmed against the locked `POST` constant.

## Structure (load path: top -> posts -> floor)

- **Corner posts (4)**: 3 x 3 in soft maple, glued from two 8/4 pieces
  milled to 1-1/2 in; height = overall height minus top thickness
  (18-1/4 in provisional). 3/8 in chamfer on all four vertical edges,
  full length, no foot taper. Chamfer 3/8 < groove setback 1/2, so no
  chamfer reaches a groove.
- **Side panels (2) and back panel (1)**: 3/4 in plywood, housed in
  grooves in the posts, outer face 1/2 in behind the post face
  (frame-and-panel shadow). Grooves 3/4 in wide (cut to measured ply),
  3/8 in deep, stopped 3/4 in above the floor (the same line as the
  bottom drawer front; Brian, 2026-09-27, was 1-1/2 in), open at the
  top. Provisional blanks: sides 16-1/4 x 17-1/8 in, back 32-1/4 x
  17-1/8 in (each includes 3/8 in per housed edge; height runs from the
  groove stop to the top of the posts).
- **Front frame (hidden)**: soft maple 3/4 in thick, dowel-jointed into
  the front posts (two 3/8 in dowels per rail, one at each end, 1 in
  deep into post and rail; Brian, 2026-09-18, was stub-tenoned 3/8 in
  into post mortises) set 1 in + 1.5 mm behind the post front face
  (behind the drawer fronts, which occupy 1/4 to 1 in, plus the Blum
  front gap; see resolution 8). Top rail 1 in tall under the top, mid
  rail 1 in tall centered on the reveal between the fronts, bottom rail
  1-1/2 in tall from the floor gap up; rail length = opening exactly
  (was opening + 3/4 in for the old tenon reach). There is no rear rail
  (Brian, 2026-09-27; it was a 1-1/2 in tenoned rail until then): the
  back runs full height, and a 3/4 x 1-1/2 in soft maple cleat glued and
  screwed to its inside face along the top edge, between the posts,
  takes the rear figure-8 fasteners.
- **Bottom**: 1/2 in plywood in 1/4 in deep grooves in the side and back
  panels and the front bottom rail; top face 2-1/4 in above the floor.
  Dust panel and slide-bracket landing, not structural.

## Front

- Two continuous soft-maple **drawer fronts**, 3/4 in thick, 1/4 in
  behind the post faces, 1/8 in reveal to each post, 1/4 in reveal
  between them, 3/4 in shadow gap at the floor.
- Front zone = post height minus 1/8 in under the top minus the floor
  gap = 17 in exactly at the measured 19-5/8 in overall height (was
  17-3/8 in at the original 20 in); split ~1:2 after the mid reveal:
  top front 5-5/8 in, bottom front 11-1/8 in (was 5-3/4 / 11-3/8 - same
  ~1.98:1 ratio, re-rounded to the nearest 1/8 in for the smaller zone;
  see "Resolutions from the CAD," 2026-09-17). Width = opening minus
  1/4 in (31-1/4 in at the measured 40 in top width, was 27-1/4 in).
  Grain along the length.
- Pulls undecided; fronts are modeled blank (routed finger pull or
  hardware later, no other part changes).

## Drawers

- **Boxes (2)**: 1/2 in plywood sides, front and back, rabbeted corners;
  1/4 in (6 mm) plywood bottom in a 1/4 in groove (Brian, 2026-09-17;
  was 1/2 in, briefly 1/8 in); bottom underside recessed 1/2 in
  (12.7 mm) above the side bottom edge for the undermount slide, as in
  [[cabinet-bench-brief]].
- **Slides**: undermount soft-close, Blum TANDEM plus BLUMOTION 563H,
  face-frame application (563H/563 installation sheet, 2016 ed.): the
  runner's front section screws sideways into the post's inner face (the
  post is the stile; holes 25 and 37 mm above the opening's bottom, 7 to
  34 mm behind the runner front), the rear end hooks into rear mounting
  bracket 295.3750.02 on the back panel. The rails are not slide
  supports. Fronts are inset, so the runner setback from the post face is
  sub-front + front - 11.5 + the 1/4 in reveal = 25.9 mm. Depth rule:
  inside depth from the post face to the back = runner + setback + 6 to
  48 mm; the 18 in class (471 mm runner, 457 mm box) needs 503 to 545 mm
  and the provisional footprint gives 515 mm, so **18 in slides**. The
  21 in class (548 mm runner) needs 580 mm; re-check once measured.
- Box inside width = opening minus 42 mm (Blum), so with 12 mm sides the
  outer width is opening minus 18 mm (680.5 mm provisional). Vertical:
  box side bottom edge 14 mm above the rail top (Blum bottom clearance),
  at least 6 mm free above the box, maximum box height = opening minus
  20 mm: top box 3-11/16 in in the 4-1/2 in opening between the mid and
  top rails, bottom box 8-11/16 in in the 9-1/2 in opening between the
  bottom and mid rails (both at Blum's maximum, 6.6 mm free above).
- Fronts screwed to the boxes from inside through slotted holes so the
  11-3/8 in solid front can move across the grain.

## Top

- Maple butcherblock matched to the Boos island (thickness, edge profile,
  overhang to be measured). Fastened with six figure-8 fasteners, three
  into the front top rail and three into the cleat inside the back's top
  edge (5/8 in forstner recesses 1/8 in deep, centered 1/4 in from the
  inner face so each opens 1/16 in through it and the fastener hangs
  over into the cabinet and sits flush, 3.7 mm of wall left outside; at
  4, 15-3/4 and 27-1/2 in from either end of the rail and of the cleat,
  modeled and volume-checked; #8 x 5/8 in screws both ends;
  the top's holes are marked from the fasteners at assembly; the cleat is
  glued to the back and clamped with #8 x 1-1/4 in screws from inside);
  no glue, no rigid cross-grain screws, so the
  top moves across its 24 in width.

## Wood movement

- Plywood panels and bottom: stable. Posts and rails: along-grain in
  their long direction. Cross-grain spans over 150 mm: the top (figure-8
  fasteners) and the bottom drawer front (slotted screws). Nothing else.

## What the CAD asserts (self-checking model, one named solid per part)

- Overall envelope equals the overall constants.
- Every panel and rail edge sits inside its groove, measured from the
  solids (probe booleans), including the stopped groove height.
- Opening between posts; box outer width = opening minus (42 minus two
  side thicknesses); runner + inset setback + 6..48 mm equals the inside
  depth from the post face; the runner's front screw zone (7 to 34 mm
  behind the runner front, 25 to 37 mm above the opening bottom) lands on
  solid post on both sides.
- Fronts plus reveals exactly fill the front zone; bottom front clears
  the floor by the shadow gap; fronts sit 1/4 in behind the post faces.
- Box side bottom edge exactly 14 mm above its rail, at least 6 mm free
  above, box height at most opening minus 20; 12.7 mm bottom recess
  probed from the box solids.
- Chamfers stop short of every groove; no post edge breaks into a panel.
- Exactly one solid per registry part; no cross-part overlaps.

## Deliverables

- `projects/Drawer-bench/drawer_bench.py` (build123d, parametric;
  env `EXPORT=1` regenerates cut list + STEP, `TMP_STL` for renders,
  `SHOW=1` pushes to the OCP viewer).
- `cutlist.md` and `cutlist.csv` (mm and inches), `drawer_bench.step`,
  `images/final-4view.png`, viewer sign-off before the cut list is final.
- Re-run after measuring: overall size, top thickness/overhang/edge,
  plywood actuals, purchased slide spec.

## Out of scope for this design

- Pull hardware and finish (decide before the build, no geometry impact
  except a routed finger pull).
- Sheet nesting and lumber yield beyond the cut list totals.

## Resolutions from the CAD (2026-08-24)

Places where the section text above did not close numerically or
mechanically once the model forced a value. The CAD uses these; each is
open for Brian's review (change the constant, re-run the file).

- **Top drawer opening is 4-1/2 in, not 4-5/8** (18-1/4 post minus the
  1 in top rail minus the mid rail top at 12-3/4). With the 8 mm slide
  standoff and 20 mm tilt clearance the boxes are **3-1/4 in (top) and
  8-1/4 in (bottom)** tall, not 3-3/4 / 8-1/2. SUPERSEDED 2026-08-24
  (evening) by the Blum sheet: bottom clearance 14, top clearance 6, max
  box = opening minus 20, so the boxes are **3-11/16 in and 8-11/16 in**
  and sit 14 mm above their rails. The bottom opening is 9-1/2 in (not
  9-3/8). Top box interior height is about 69 mm; if that is too
  shallow, drop the mid rail to 3/4 in or move the reveal up.
- **Front-frame joinery is three stopped mortises per front post**, not
  a continuous groove: T18 x 3/8 on the inner face 1 in behind the front
  face, at the rail heights (bottom rail 3/4 to 2-1/4; mid rail centred
  on the reveal; top rail open at the post top). A continuous groove
  would leave an open 18 mm slot on the post face between the rails,
  visible with a drawer open and exactly where the undermount slide's
  front tab screws into the "stile". Same router setup as the panel
  grooves, three short passes with stops. Post blanks unchanged.
  SUPERSEDED 2026-09-18: the front rails changed from stub-tenons to
  dowel joints (Brian); see the next resolution. The stile stays solid
  between the rails either way.
- **Front rails are dowel-jointed, not stub-tenoned into mortises**
  (Brian, 2026-09-18): two 3/8 in (9.525 mm) dowels per rail, one at
  each end, 1 in (25.4 mm) deep into both the post and the rail. Rails
  now butt flush against the post inner face (length = opening exactly,
  was opening + 3/4 in for the tenon reach). The post's three stopped
  box mortises become three round bores at the same rail-centerline
  heights, on the same inner face, 1 in behind the front face - solid
  post stays between the rails either way, so the slide's front-tab
  screw-zone probe (already checked against solid post) is unaffected.
  The rear top rail was untouched by this change (and dropped on
  2026-09-27). `drawer_bench.py`'s volume-identity asserts were updated
  to subtract cylinder volumes instead of box-mortise volumes, which
  passed cleanly on the first re-run - no other constant moved.
- **The rear top rail (1-1/2 in tall) is tenoned into the back groove
  line** and the back panel runs from the groove stop to the rail's
  underside (15-1/4 in tall, not 16-3/4). SUPERSEDED 2026-09-27, next
  bullet.
- **No rear rail; the back runs full height with a cleat** (Brian,
  2026-09-27: "isn't the plywood back sufficient?"). It is: the sides
  already ran to the post tops with no rail, and the rail existed only
  to give the top's figure-8 fasteners solid wood. The back is now
  32-1/4 x 17-1/8 in like the sides, and `cleat_rear`, soft maple from
  3/4 in rail stock x 1-1/2 in, opening length, is glued and screwed
  to the back's inside face flush with the post tops; the figure-8s go
  into it and into the front top rail. Its front face is 15 mm behind
  the top drawer box's back and it sits above the rear slide brackets
  (the pairwise no-overlap check covers it). Alternative not taken:
  Z-clips in a kerf in the back. The cleat was the recommended landing;
  Brian only asked to drop the rail.
- **Rails are milled to the measured ply thickness (T18)** so their stub
  tenons are the full section in the same 3/8 in grooves and mortises;
  the cut list therefore prints 11/16 in, which is a consequence, not a
  target. SUPERSEDED 2026-09-27: with the front rails on dowels and the
  rear rail replaced by a glued cleat, nothing about them sits in a
  ply-sized groove any more, so rails and cleat are plain 3/4 in stock
  (`RAIL_T = 3/4 in`; Brian asked why the cut list said 11/16). Knock-ons:
  the bottom rail's rabbet and the bottom's front notch move 1 mm, the
  figure-8 recesses keep 4.8 mm of wall, the cleat clears the top drawer
  box by about 14 mm.
- **Bottom panel front edge sits in a rabbet, not a groove**: its top
  face and the bottom rail's top face are both 2-1/4 in above the floor,
  so the rail gets a 1/4 x 1/2 rabbet on its rear-top edge, run THROUGH
  the tenons (a stopped rabbet makes the rail's full-section tenon sweep
  through the bottom's front tab at glue-up; the tenon corner it loses
  is 1/4 x 1/2). Glue and screw the bottom's front edge down (no lip
  above it). Sides and back carry a 1/4 x 1/2 groove on the inner face,
  run THROUGH full length (Brian, 2026-09-27; was stopped 3/8 in from
  each end: the groove ends land inside the post grooves, above their
  stop, so they never show); the panel is notched 51.85 x 39.15 (front)
  / 51.85 x 51.85 (rear) around the posts. The back groove is what the
  bottom is pre-joined into, see the assembly order.
- **Design values leave a 7 mm ply lip** under the bottom groove in the
  sides and back (groove stop 1-1/2 in, bottom top face 2-1/4 in, 1/2 in
  ply): supported only at the post ends, fine as a dust-panel detail but
  fragile to machine. Lowering the groove stop to 1 in would give a
  20 mm lip; owner's call. SUPERSEDED 2026-09-27: the groove stop is
  now 3/4 in (below), so the lip is 26 mm.
- **Side and back panels end on the drawer-front line, 3/4 in above the
  floor** (Brian, 2026-09-27, after the rendered leg options page: he
  kept the 3/8 in chamfer, E1, with the posts straight to the floor, but
  wanted the panel bottoms level with the bottom drawer front instead of
  3/4 in higher). In the CAD `GROOVE_STOP = FLOOR_GAP`, one tie, so the
  post grooves, the panel heights and the bottom-groove lip all follow;
  the panels grow 3/4 in and nothing else moves. Options considered and
  passed on: square, 3/8 roundover, 3/4 outer-corner chamfer or
  roundover, a stopped edge with a square foot, and 3 or 4-1/2 in of
  leg showing (`leg_options.py`, `leg-options.html`).
- **Drawer-box bottoms are 1/4 in (6 mm) plywood, not 1/2 in** (Brian,
  2026-09-17; landed on 1/4 in after a brief 1/8 in): only the bottom
  panel's own thickness changed. The groove that houses it in the
  sides, front and back keeps the same 1/4 in reach (`DADO`, unchanged
  router setup) - it just now holds a thinner panel, sized by the
  constant `T6`. `UM_RECESS` (12.7 mm, the Blum-specified rise from the
  bottom's underside to the box side's bottom edge) is a hardware
  distance, not tied to the bottom's own thickness, so it is
  unaffected. Sides, front and back stay 1/2 in ply.
- **`BOX_TOP_H`/`BOX_BOT_H` were hard-coded, not derived** (2026-09-17,
  found when the measured overall height shrank the front zone and, with
  it, both drawer-box openings): their own comments already claimed
  "Blum maximum (opening minus 20 mm)," but the values were locked
  constants computed once for the original 20 in height, not a formula.
  Re-running after the height change left only 0.29 mm of the required
  6 mm top clearance on the bottom box - the model's own assert caught
  it immediately. Fixed by computing both from the rail positions
  (`RAIL_TOP_Z0`/`RAIL_MID_Z0`/`RAIL_BOT_Z0`, already derived above them)
  minus `UM_BOTTOM_CLEAR + UM_TOP_CLEAR`, so any future change to the
  overall height or the front-zone split keeps the box heights correct
  automatically instead of needing a matching manual fix every time.

## Assembly order (walked in the CAD; every part enters by a straight sideways move)

1. Glue each side panel into its front and rear posts (two side
   sub-assemblies).
2. Off the bench, glue and screw the cleat inside the back's top edge,
   then pre-join the bottom to the back: the bottom's rear tab goes into
   the back's groove (through since 2026-09-27, so the tab can also
   slide in from an end; the pair still goes in together).
3. Stand the left sub-assembly; slide the back + bottom pair in sideways:
   the back's edge into the rear post groove, the bottom's edge into the
   side panel's groove face-on. (No rear rail since 2026-09-27.)
4. Dowel the three front rails into the left front post; the bottom
   rail's through rabbet passes over the bottom's front tab (rails can
   also go in before the back + bottom pair).
5. Close the right sub-assembly over the back's edge, the bottom's edge
   and the three rails' dowels at once.
6. Drawers on their slides, fronts screwed from inside, then the top on
   figure-8 fasteners.

## Undermount slide check against the Blum sheet (2026-08-24, evening)

Brian asked how the top drawer's slides fit. Checked against the Blum
563H/563 installation instructions (2016 ed., d2.blum.com). Corrections
applied to the CAD (and to Cabinet-bench, which had the same errors):

- Inside drawer width = opening minus 42; outside = opening minus 18 with
  12 mm sides (the model had minus 10, the 5/8 in side value).
- Bottom clearance 14 mm (model had an 8 mm "standoff"); minimum top
  clearance 6 mm (model had 20); max box height = opening minus 20, so the
  boxes grew to 3-11/16 and 8-11/16 in.
- The 18 in class runner is 471 mm, 14 mm longer than the 457 mm box;
  depth rule for inset fronts: inside depth = runner + setback + 6..48 mm,
  setback = sub-front + front thickness minus 11.5 plus the reveal.
- Runner front screws go into the post's inner face (the stile), 25 and
  37 mm above the opening bottom, 33 to 60 mm behind the post face: solid
  post between the mortises, now asserted with a probe.
- **Front gap (resolution 8):** Blum wants 1.5 mm between the fronts'
  back faces and the frame so the runner stop, not wood, closes the
  drawer. The front frame plane is therefore derived: post face + 1/4 in
  reveal + 3/4 in front + 1.5 mm = 26.9 mm (was the locked 1 in). Mortises
  and rails move with it; the boxes still start on the fronts' back faces.
- **Drawer backs (Blum p.2 "drawer back preparation"):** the rear hooks
  need 35 x 13 mm notches at both bottom corners of the back and 6 x 10 mm
  bores centred 7 mm from the side's inner face and 24 mm above the bottom
  edge. In a 12 mm back that bore breaks into a full-length bottom groove,
  so the back's groove is stopped 35 mm from each side and the bottom's
  rear corners are notched 41 x 6.35 to match. The back is now its own
  registry part (`drawer_back_*`, 20 parts in the file) and a probe asserts
  the bore volume is solid ply and clear of the bottom. The cut list
  now lists front and back (and each rail and post type) on their own
  rows; `scripts/cutlist.py` merges only blanks whose notes also agree.
- Cabinet-bench got the same width, clearance and front-gap corrections
  plus a note about the rear-hook prep (its drawer backs were not
  remodeled); its upper drawer moved up 2 mm so the lower box keeps 6 mm
  under the upper runner.
