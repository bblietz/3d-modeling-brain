---
type: brief
project: Built-in-bench
status: CAD built 2026-10-07, cut list and shop page written, waiting on Brian's viewer look
created: 2026-10-06
tags: [furniture, bench, built-in, drawers, undermount]
---

# Built-in alcove bench

A built-in bench with two side-by-side, full-width drawers for the alcove that used to be a wet bar. Designed with the [[furniture]] skill; this round is the options tool, not CAD.

## Given by Brian, 2026-10-06

- Opening 66 in wide by 28 in deep. Three walls: two pilasters about 5 in thick and the back wall; open above to an 8 ft ceiling, no sill or soffit. Re-measure at the floor, 16 in and 36 in, at the back wall and at the pilaster faces, before any cut list (the photo's scale references disagree with 66 in by several percent).
- Two drawers side by side, full width, on undermount slides.
- Top is 3/4 in maple with a 3 in cushion on it.
- Baseboard (about 4 in) inside the alcove comes out; the pilaster faces keep theirs, so a 4 in base continues that line.
- Capped plumbing on the left is inside the wall; nothing protrudes into the opening.
- Outlet: Brian says it is above bench height (it served the old countertop). The space photo shows a duplex receptacle low on the back wall, roughly 12 to 17 in off the floor and left of center. Confirm on site before the back panel is cut.
- Ignore the dog-bowl cubby in the concept picture.

## Reference images

- `images/space-photo.png` and `images/space-photo-web.jpg`: the empty alcove. Cream walls, white 4 in baseboard, dark hand-scraped plank floor running parallel to the bench front, a six-panel door tight to the left pilaster, a passage past the right pilaster, a switch at about 48 in on the right return wall.
- `images/concept-ai-bench.png` and `images/concept-ai-bench-web.jpg`: AI concept. Painted cream body a shade deeper than the walls, slim-shaker inset-look fronts, brass bar pulls, flush base with no toe kick, one long oatmeal boxed cushion, floating white-oak shelves above (shelves and lighting out of scope for this bench).

## Options tool

`bench-options.html`, titled Alcove Bench Studio, published as a private artifact (link in the chat and in [[project-built-in-bench]]). Groups A to J, each drawn to scale from a shared parametric model in the page's script, with a live elevation and section, derived dimensions, flags, and a Copy picks button.

My recommendations (defaults in the tool): A2 wood top at 16 in, B2 flush base, C1 face frame with inset fronts, D2 slim shaker, E1 brass bar (flagged for shin height), F2 3/4 in overhang with an eased edge, G1 maple plywood with a 1-1/2 in solid nosing, H1 one full-depth cushion, I1 21 in Blum TANDEM 563H, J1 painted body.

## Undermount slide rules (web research 2026-10-06, primary Blum sheets)

- Blum TANDEM plus BLUMOTION 563H: 9 to 21 in only. Inside box width = opening minus 42 mm. Max box height = opening minus 20 mm (14 mm bottom, 6 mm top). Bottom recess 13 mm. 21 in needs at least 557 mm inside cabinet depth. Rear brackets allowed on a face frame. 90 lb dynamic. No push-to-open. About $21 to $22 a pair plus locking devices.
- Blum MOVENTO 769 heavy duty: 18 to 30 in. Same width rule. Max box height = opening minus 23 mm (16 mm bottom, 7 mm top). Bottom recess 13 mm. 24 in needs 630 mm inside depth (643 mm with the lateral stabilizer). No rear brackets: cabinet sides blocked out flush with the inside of the face frame. 24 in and longer runners raised 1/8 in for inset fronts. TIP-ON BLUMOTION exists; the set that spans 24 in is rated for 88 to 155 lb drawers. 155 lb dynamic. About $52 to $64 a pair, stabilizer about $41 per drawer. Blum recommends the stabilizer on openings 24 in and wider.
- Knape and Vogt MuV is gone from the 2026 catalog; Salice Futura stops at 21 in.
- Unpublished by every maker: bottom panel thickness, minimum side height, any allowance for a box shorter than the slide.

## Open

- The three on-site measurements (floor, 16 in, 36 in; back wall and pilaster faces). The model assumes a square 66 x 28 opening; the top, plinth and scribe strips are cut long and scribed.
- The low receptacle in the photo, before the back panel is cut.
- Brian's look at the fronts in the viewer: the maple frame is 1-1/2 in wide (STILE_W); 1 in or 2 in is a one-constant change.

## Brian's picks, 2026-10-06 (from the tool's Copy button)

A2 wood top at 16 in; B2 flush base; C2 frameless, full-overlay fronts; D1 flat slab fronts; E1 brass bar pull 8 in; F2 3/4 in overhang, eased edge; G2 solid maple top, glued up; H1 one cushion, full depth; I1 21 in Blum TANDEM 563H; J2 clear maple body. Measurements kept at 66 x 28 in; fronts set back 3 in from the pilaster faces (tool default was 3/4; confirmation asked).

Derived by the tool: fronts 2 x 31-13/16 x 11-1/8 in; boxes 30-3/16 x 9-1/2 x 21 in; 2-15/16 in behind the box; top 66 x 25-3/4 in.

Plan proposed 2026-10-06: frameless maple-ply carcass on a 4 in ladder base with a solid maple plinth board flush with the fronts, 1 in scribe strips, 1/4 in back in through grooves, flat top-back stretcher for the top's slotted screws and the wall screws, solid top on figure-8s with a 3/8 in gap at the wall, drawer boxes with 1/2 in bottoms and 3/4 in backs (keeps Blum's 10 mm hook bores clear of the through groove), fronts recommended as 3/4 maple ply with 1/4 in solid edging because an 11 in solid slab moves about 1/8 in.

## Decisions 2026-10-07 and the built model

Brian: drawer fronts are 3/4 walnut veneer ply with maple around the outside, joined with his tongue-and-groove router bit set; the rail tenon showing on the top end of the stiles is fine. The cabinet top sits 3 in back from the pilaster faces.

Model: `built_in_bench.py` (build123d, mm inside, inch constants). One solid per part in PARTS, every placed copy in INST, hardware and cushion in HW for the viewer only. Asserts cover one-solid-per-part, no overlaps (wood and hardware), the 3 in setback, the 1/8 reveals, every Blum 563H rule, the hook bore staying in wood, and every housed joint by probe.

Layout from the back wall: case front edge 23-1/2, front faces 23-1/2 plus the ply, top front edge 25 (overhang 25/32 with 18 mm ply). Case 64 wide between 1 in scribe spaces; scribe strips 1-23/32 wide cover the end panels' front edges, so the fronts are 31-3/32 x 11-1/8 with 1/8 reveals, 1-1/2 maple stiles and rails, and a 28-1/16 x 8-1/8 walnut field. Plinth 3-7/8 tall, flush with the fronts, 1/8 reveal under them. Opening 30-15/16 x 10-17/32 per bay; boxes 30-7/32 x 9-1/2 x 21 outside (inside width = opening minus 42 mm), sides 1/2 Baltic birch with 1/4 rabbets, box front and back 3/4 maple ply (the 3/4 back keeps the 10 mm hook bores in wood above a 3/16 groove; the 3/4 front takes the locking-device screws), 1/2 Baltic birch bottom with its underside 1/2 above the side edges. Top 66 x 24-5/8 x 3/4 solid maple, 1/8 roundover on the front arrises, 3/8 gap at the wall, pocket screws near the front, figure-8s on a 2-1/2 in solid maple nailer on edge at the top back (notched through the partition). Back 1/4 ply in 1/4 grooves. Base is a 4 in ladder of any 3/4 ply.

Blum 563H numbers re-verified 2026-10-07 from Blum's own sheets: box height = opening minus 21 mm (14 bottom, 7 top; the 2016 sheet said 20), bottom recess 13 mm to the underside of the bottom, rear notch at least 35 x 13 mm starting at the inside face of the drawer side, hook bore 6 mm dia x 10 mm deep into the rear face, 7 mm in from the side's inside face and 24 mm above the bottom edge, min inside depth 557 mm from the case front edge to the inside of the back, locking devices T51.1901 R/L into the box front. Rear brackets are not used in a frameless case.

Deliverables: `cutlist.md`, `cutlist.csv`, `built_in_bench.step`, `images/final-4view.png`, `images/case-4view.png`, `images/drawer-box-4view.png`, `images/hero.png` (viewer), `images/parts/*.png` (via `part_drawings.py`), `cutlist.html` (via `make_cutlist_page.py`, published as a private artifact at https://claude.ai/artifact/YQFcx4g5x64K83yhDHvGMf), `hero_shot.py`, `assembly_shots.py` (exploded view, 11 step images and two sub-assembly explosions from the viewer; its STEPS list is also the text of the page's Assembly section). `cutlist.pdf` (18 pages, letter) comes from `make_pdf.py`, which prints the page with headless Chrome using the page's own print styles. The options tool stays at https://claude.ai/artifact/MtDXsCPZCmjG1xELTh9jPP with a Decided banner.
