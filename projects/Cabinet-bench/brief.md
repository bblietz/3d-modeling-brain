---
name: cabinet-bench-brief
description: Brief and locked decisions for the 36x24x20 cabinet bench with 2 drawers
created: 2026-08-04
status: designed-not-built
---

# Cabinet Bench - brief

36" wide x 24" deep x 20" high cabinet bench, two drawers, goal: maximize
storage. Dimensions user-specified (provenance: stated in request, not
measured against a site). Bench is assumed to be sat on; designed for a
~300 lb seated load.

## Decisions locked (user answered 2026-08-04)

- Layout: two stacked full-width drawers.
- Material: 3/4" (18mm) plywood carcass/top/faces, 1/2" (12mm) ply drawer
  boxes and bottoms, 1/8" (3mm) ply back (revised 2026-08-04, user).
- Joinery: dados and rabbets, 6mm deep, widths sized to MEASURED stock
  thickness at cut time (model uses 18.0 / 12.0 nominal).
- Slides: 21" (533mm) undermount soft-close, Blum Tandem 563H class.
  Geometry consequences: box outer width = opening - 10mm, box depth =
  exactly 533mm, drawer bottom underside recessed 12.7mm above the box
  side bottom edge, >= 20mm free space above each box to tilt it onto
  its slides. VERIFY these
  numbers against the purchased slide's spec sheet before cutting.
  Optional upgrade: Blum Movento 550mm gains ~17mm box depth.

## Design assumptions (stated, not asked)

- Frameless / full-overlay (Euro) construction; no toe kick so the bottom
  drawer sits low. Overall depth includes the 18mm proud drawer faces:
  carcass depth = 609.6 - 18 = 591.6mm.
- Seat top is TWO laminated 18mm layers (36mm slab), full 914.4 x 609.6
  footprint, overhanging the carcass front to land flush over the drawer
  faces. The slab replaces a front rail so the entire front is drawers.
- Carcass structure (revised 2026-08-04, user): the bottom is a
  full-width platform (914.4 x 576.6) sitting on the floor; the sides
  (460mm tall) seat in 6mm-deep rabbets in its top face, so seating
  loads bear down through the bottom panel. The 3mm back rides in 6mm
  dados in the sides and the slab underside, inset 12mm from the rear
  edge; the bottom's depth stops exactly at the back's front face so
  the back slides down past it during assembly, then gets glued and
  brad-nailed to the bottom's rear edge. Glued in on all edges it acts
  as the racking shear panel, dresser-style (thinner than the original
  12mm back, but braced on four sides).
- 12mm (not 6mm) drawer bottoms: 844mm-wide drawers will carry weight.
- Reveals: 20mm floor shadow gap (revised 2026-08-04 after viewer
  review: a near-flush face would scrape rugs/uneven floor; boxes
  unchanged, only the bottom face shortened to 257mm), 3mm between
  faces, 2mm under slab, 2mm per side. The carcass bottom's front edge
  shows in the gap; edge-band or paint it dark.
- Drawer face attachment: screws from inside the box front. Pulls not
  specified; add hardware or a routed finger pull later.
- Grain: top and drawer faces run along the 36" length; sides vertical.

## Joinery detail (for cut-list rows flagged non-rectangular)

All flagged parts are rectangular blanks per the cut list with these cuts:

- Carcass sides: 6mm-deep x 3mm-wide groove on the inner face for the
  back, inset 12mm from the rear edge, full height. Widths = measured
  stock, not nominal.
- Carcass bottom: 6mm-deep x 18mm-wide rabbet across each end of the
  top face; the sides seat in these (side lower edge 12mm above floor).
- Slab lower layer: stopped 3mm x 6mm-deep groove in the underside,
  aligned with the side grooves (back's top edge captures when the slab
  goes on). Cut BEFORE laminating the two layers.
- Drawer sides (all 4): 6mm-deep x 12mm-wide rabbet across the inner face
  at BOTH ends (captures drawer front/back); 6mm-deep x 12mm bottom
  groove full length, lower edge 12.7mm above the bottom edge of the side
  (undermount recess).
- Drawer fronts/backs (all 4): same 6 x 12 bottom groove at the same
  height on the inner face.
- Drawer bottoms sit in the grooves; underside at exactly 12.7mm above
  the box bottom edges.

## Sheet shopping

- 18mm: 2.59 m2 of parts. Does NOT nest on one 2440x1220 sheet (the two
  910mm faces are the overflow; verified by manual layout). Buy TWO
  sheets of 3/4"; generous offcuts remain.
- 12mm: 1.98 m2 of parts (back moved to 3mm stock). Fits ONE 1/2" sheet
  with room to spare; parts may be rotated freely (painted ply, grain
  not critical on drawer boxes).
- 3mm: one 890.4 x 466 piece. A 1/8" quarter sheet / project panel
  covers it; measure actual thickness (batches run 2.7-3.2mm) and size
  the grooves to it.

## Outcome (2026-08-04)

Design complete and verified: all geometry asserts pass (envelope
914.4 x 609.6 x 508, undermount recess 12.7 probed from solids, box
width = opening - 10, slide length fits interior with >=9mm rear
clearance, faces + reveals exactly fill the front). Not yet built.
Storage: ~92L bottom drawer + ~54L top drawer interior volume.

## Artifacts

- Canonical CAD: `cabinet_bench.py` (build123d, parametric)
- Cut list: `cutlist.md` / `cutlist.csv`
- STEP: `cabinet_bench.step`
- Renders: `images/final-4view.png`

## Update 2026-08-24

Undermount constants corrected against the Blum 563H sheet (box width
opening minus 18 with 12 mm sides, 14 mm bottom clearance, 6 mm top
clearance, 548 mm runner depth rule); `cabinet_bench.py`, `cutlist.md`,
`cutlist.csv`, `cabinet_bench.step` and `images/final-4view.png`
regenerated. See [[cabinet-bench-learnings]] "Correction 2026-08-24".
