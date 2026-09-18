---
name: drawer-bench-brief
description: Brief and locked decisions for the drawer bench (face frame, maple butcherblock top, bulky maple legs)
created: 2026-08-23
status: cad-built-provisional
---

# Drawer Bench - brief

Face-frame bench with drawers. Furniture-grade sibling of
[[cabinet-bench-brief]] (same starting footprint, different construction).

## Specs from user (2026-08-23)

- Face frame construction.
- Sides and back: 3/4" plywood.
- Bottom: 1/4" (material open to suggestions).
- Drawer fronts: soft maple, continuous faces; face frame NOT visible
  (full-overlay fronts cover the frame).
- Legs/corners: soft maple, bulky. Style under discussion.
- Top: maple butcherblock.
- Starting size 36" W x 24" D x 20" T; sizes NOT final (provenance:
  stated in request, not measured against a site).

## Open questions

- Leg/corner style (visual companion session in progress).
- Top thickness, overhang and edge profile: still pending the Boos
  island measurement (overall top footprint and height are now locked,
  see Decisions locked 2026-09-17).
- Drawer count/layout, slide hardware.
- Seating load, what the drawers hold.

## Design

Approved design (2026-08-24, sections 1-3): [[drawer-bench-design]]
(`projects/Drawer-bench/design.md`). Two numbers in the written design
differ from the section text as read out and are flagged for Brian's
spec review: top and mid frame rails 1 in tall (not 1-1/2) to give the
top drawer box a 4-5/8 in opening, and 18 in undermount slides (not 21)
because option (a) leaves 19-1/4 in of interior depth.

## Decisions locked

- Leg/corner style: proud corner posts (post and panel), soft maple,
  floor to underside of top; drawer fronts run between the posts
  (user picked option A in visual companion, 2026-08-23).
- Post size: 3" square, glued up from two pieces of 8/4 soft maple
  milled to 1-1/2" each; ~30" drawer opening at 36" overall width
  (user picked option B, 2026-08-24).
- Post details: 3/8" chamfer on all four vertical edges, full length;
  no foot taper (user picked option B, 2026-08-24).
- Drawer front plane: 1/4" setback behind the post faces
  (user picked option B, 2026-08-24; the companion's click log for that
  screen shows a stray click on A, user re-confirmed B 2026-08-24).
- Assumption (stated, not objected to yet): plywood side/back panels
  set back ~1/2" from post faces, frame-and-panel shadow.
- Top: maple butcherblock to MATCH the family's John Boos block island
  (user, 2026-08-24). PROVISIONAL until measured at home: 1-3/4" thick,
  1-1/4" overhang past the posts (the Boos prefab class, companion
  option B). Measure on the island: thickness, edge profile (square /
  eased / bullnose / chamfer), overhang past its base. Nothing is cut
  from the placeholder.
- Panel-to-post joinery: 3/4" plywood sides and back HOUSED IN GROOVES
  in the posts (3/4" wide nominal, ~3/8" deep, sized to measured ply),
  glued; no fasteners; the panels are the shear bracing
  (user picked option A, 2026-08-24).
- Bottom: 1/2" plywood housed in grooves (same construction as the
  sides), a dust panel and slide-bracket landing, not structural
  (user picked option B, 2026-08-24).
- Overall size convention: 36 x 24 is the TOP; the posts sit inside it
  by the top overhang (footprint 33-1/2 x 21-1/2 at the provisional
  1-1/4" overhang; drawer opening between posts 27-1/2")
  (user picked option (a), 2026-08-24). Section 2 dimensions/joinery
  approved as presented (grooves 3/4 x 3/8 stopped 1-1/2" above the
  floor, 3/4 x 1-1/2 maple rails stub-tenoned into the same grooves,
  1/2" bottom in 1/4" grooves 2-1/4" above the floor, fronts fill the
  zone from a 3/4" floor gap to 1/8" under the top split 1:2 with a
  1/4" reveal, undermount slides mounted face-frame style).
- Drawer layout: graduated, shallow over deep; ~5" top face,
  ~10.5" bottom face, full width between posts
  (user picked option B, 2026-08-24). Contents/location not stated;
  assuming general household storage, bench is sat on (~300 lb),
  undermount soft-close slides per [[cabinet-bench-brief]].
- Overall size measured (Brian, 2026-09-17): top 40 x 24 in (was the
  36 x 24 provisional footprint), top surface 19-5/8 in above the floor
  (was 20 in overall height). Top thickness/overhang stay provisional
  (1-3/4 in / 1-1/4 in) until the Boos island is measured, so post
  height is still `H - TOP_T`, not yet independently fixed.
  Consequences worked through in the CAD, not just scaled: the front
  zone (post height minus the 1/8 in top reveal minus the 3/4 in floor
  gap) shrank from 17-3/8 to 17 in exactly; re-split ~1:2 the same way
  as the original design (design.md, "Front") gives drawer fronts
  5-5/8 in (top) and 11-1/8 in (bottom), the same ~1.98:1 ratio as the
  original 5-3/4 / 11-3/8. That re-split moves the mid rail, which
  shrinks both drawer-box openings slightly; `BOX_TOP_H`/`BOX_BOT_H`
  were hard-coded "Blum maximum" constants left over from the old
  opening sizes, so the first re-run failed a clearance assert (0.29 mm
  of the required 6 mm left above the bottom box) - fixed by turning
  them into a formula (opening minus the 14 mm/6 mm Blum clearances),
  the same rule their own comments already claimed. New box heights:
  3.588 in (top), 8.463 in (bottom) - not rounded to a nice fraction,
  since (unlike the fronts) these were never a show-face/aesthetic
  dimension, just whatever the opening allows. Width change (36 to
  40 in) only widens everything between the posts; it does not touch
  the front-to-back slide-depth fit, still 515.4 mm inside 18 in slides'
  502.9-544.9 mm window. Re-exported and re-pushed to the viewer.

## Build log (2026-08-24)

- CAD: `projects/Drawer-bench/drawer_bench.py` (build123d, parametric;
  `EXPORT=1` regenerates `cutlist.md` / `cutlist.csv` /
  `drawer_bench.step`; `TMP_STL=<path>` for renders; `SHOW=reset|1`
  pushes to the OCP viewer on port 3939). Design and the seven CAD
  resolutions in [[drawer-bench-design]], plan in [[drawer-bench-plan]],
  retrospective in [[drawer-bench-learnings]]. Built with
  subagent-driven development (ledger and per-task reports in
  `.superpowers/sdd/`).
- Deliverables: `cutlist.md`, `cutlist.csv`, `drawer_bench.step` (one
  fused solid, 72.6 dm3), `images/final-4view.png`,
  `images/final-iso-front.png`, `images/final-iso-rear.png`. All
  PROVISIONAL: nothing is cut until the space, the Boos island and the
  plywood are measured and the file is re-run.
- Self-checks in the file: 46 asserts and 12 housed-edge probes from the
  solids (both ends), 300 pairwise no-overlap intersections, post volume
  identity (chamfers vs grooves vs mortises). Mutation-tested during
  review: a rail 5 mm short, a box 20 mm narrow, a shifted top front, a
  narrow bottom, short drawer ends and a moved mortise all fail the run.
- Buildability (furniture skill Phase 4):
  - Stock thickness: PASS conditional. 18 / 12 mm ply are stock sizes but
    the model uses nominal 18.0 / 12.0; measure both sheets and re-run
    before cutting any groove, mortise or rabbet. Maple (8/4 for posts,
    4/4 for rails and fronts) is a yard purchase spec, not a checked size.
  - Rectangularity: PASS. Flagged rows (posts 94/91%, rail_bot 89%,
    bottom 98%, drawer sides 94%) carry their groove, mortise, rabbet and
    notch dimensions in the notes; posts still want a drawing.
  - Grain / show face: posts and rails along their length, fronts along
    the length and cut in sequence from one board so the figure runs
    through the reveal, side ply face grain vertical, top along the 36 in.
  - Joinery fit: every housed edge is probe-verified but modeled at zero
    clearance. Must-dos: test-cut every groove, mortise and rabbet in
    scrap against the measured ply; cut mortises about 1 mm deeper than
    the tenons; the undermount numbers (opening minus 10, 12.7 recess,
    20 mm tilt, 9 mm rear) are the unverified Blum 563H class values
    from [[cabinet-bench-learnings]], verify against the purchased spec.
  - Stock yield: one 18 mm sheet (23% used), one 12 mm sheet (56%),
    about 10 bf of 8/4 and 8 bf of 4/4 soft maple; top purchased.
  - Wood movement: two cross-grain spans over 150 mm, both with hardware
    (top on figure-8s, bottom front on slotted screws). Watch item:
    figure-8s give about 4 mm total travel, enough for an edge-grain Boos
    top (4 mm seasonal) and marginal for a flatsawn slab (8.6 mm); decide
    once the island top is identified.
  - Transport: 914 x 610 x 508 mm, about 49 kg with the top; clears a
    750 mm doorway upright with 140 mm to spare.
  - Assembly order: the first walk FAILED (stopped rail rabbet swept
    through the bottom's front tab; bottom could not enter after the
    back). Fixed in the CAD (rabbet run through the tenons) and in the
    design.md assembly order (bottom pre-joined to the back off the
    bench); insertion walk re-verified clash-free.
- Viewer: OCP viewer started and the model pushed (`SHOW=reset`, 25
  instances) on 2026-08-24; Brian was away, so **viewer sign-off is
  pending**.
- Open for Brian's review: the seven CAD resolutions in design.md
  (especially the 58 mm interior height of the top drawer and the 7 mm
  ply lip under the bottom groove), then the measurements listed under
  "Provisional inputs".
- 2026-08-24 (evening): Brian asked how the top drawer's slides fit.
  Checked the Blum 563H sheet: the box width rule, bottom clearance and
  top clearance in the model were wrong (inherited from Cabinet-bench).
  Corrected constants (`UM_WIDTH_LOSS = 42 - 2*T12`, `UM_BOTTOM_CLEAR =
  14`, `UM_TOP_CLEAR = 6`, `RUNNER_LEN = 471`, inset `RUNNER_SETBACK`),
  boxes now 3-11/16 / 8-11/16 in at Blum's maximum, a probe asserts the
  runner's front screws land on solid post, cut list / STEP / renders
  regenerated, viewer re-pushed. Details in design.md "Undermount slide
  check". Cabinet-bench corrected and re-exported the same way.
  Follow-up from the sheet review: 1.5 mm Blum front gap (frame plane
  now 26.9 mm behind the post face), drawer backs split into their own
  part with the 35 x 13 rear-hook notches, stopped bottom groove and
  bore probes; registry is 20 parts; everything re-exported.
