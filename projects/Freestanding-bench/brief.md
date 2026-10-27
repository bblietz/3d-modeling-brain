---
type: brief
project: Freestanding-bench
status: CAD, cut list, shop page and a true-scale room picture built 2026-10-26; waiting on Brian's base pick
created: 2026-10-26
tags: [furniture, bench, freestanding, drawers, undermount, robot-vacuum]
---

# Freestanding alcove bench

The second design for the 66 x 28 in former wet-bar alcove. On 2026-10-26 the client asked for the bench to be free standing and high enough for their Roomba to get underneath it. This project is that design; the built-in design in [[Built-in-bench]] (`projects/Built-in-bench/`, shop page https://claude.ai/artifact/YQFcx4g5x64K83yhDHvGMf, Version 18) is untouched in case they go back. Designed with the [[furniture]] skill.

## What carried over from the built-in (Brian's locked picks)

Wood top at 14 in, seat 17 in with the 3 in cushion (kept for Maizy, the senior dog). Frameless case, full-overlay fronts built as a 1-1/2 in maple frame around a 1/2 in paint-grade panel inset 1/4 in on the tongue-and-groove bit set, all painted white. 8 in brass bar pulls. 3/4 in overhang with a 1/8 roundover. Solid glued-up maple top with its front edge 3 in back from the pilaster faces. One full-depth cushion. 21 in Blum TANDEM 563H undermounts with every Blum rule from the built-in brief. Drawer boxes of 1/2 in 9-ply Baltic birch (no groove in the back, bottom butts it). Osmo Natural on the bare maple. The picture-only shelves and dropped soffit stay in the room picture.

## What changed

- **Clear floor, 5 in** (CLEAR): the underside of the case is 5 in off the floor. Roomba heights: j7 and Combo j7+ 3.4 in, i7 and the 600/900 series 3.6 in, the 2025 lidar models (Plus 405/505) about 3.3 to 3.9 in, the Max 705 fits a 4 in gap, other lidar robots 3.8 to 4.0 in. Five inches leaves an inch over the tallest and room for a rug under the bench. Sources: https://www.irobot.com/en_US/roomba-j7-robot-vacuum/J715020.html, https://irobotthailand.com/en/shop/irobot-roomba-i7/, https://www.consumerreports.org/appliances/vacuum-cleaners/irobot-roomba-max-705/m417680/, https://www.sylvane.com/collections/robotic-vacuum-cleaners/products/irobot-roomba-plus-415-combo-vacuum-mop-autowash-dock.
- **The drawers pay for it**: the opening is 7-17/32 tall, so the boxes are 6-1/2 in (Blum: opening minus 21 mm), 5-17/32 inside, instead of 8-1/2. Fronts 31-1/8 x 8-1/8 (panel field 28-1/8 x 5-1/8). Every inch added to the seat would go straight back into the drawers.
- **Size**: top 64 x 24-1/2 x 3/4 with 1 in of air to each wall (SIDE_AIR) and its back edge 1/2 in off the back wall (WALL_GAP); case 62-1/2 x 23 x 8-1/4 under it (3/4 overhang at each end, 25/32 at the front, flush at the back). A rear overhang would have pushed the case forward past Blum's 557 mm inside depth, so the top is flush with the case back. Overall 64 x 24-1/2 x 17 in with the cushion. The alcove's baseboard stays: the case bottom clears it, the legs sit 2 in inside the case back (the model assumes baseboard plus shoe under 1-1/4 in, confirm on site).
- **Case**: ends are show faces now, painted white, front and bottom edges banded; fronts stop 1/16 short of the case ends (END_REVEAL) and are flush with the case underside; the 1/4 back is glued into its grooves (it is the shear panel, no wall screws); the nailer stays for the top's figure-8s and ties the ends. No plinth, no scribe strips, no ladder base.
- **Base, three options** (BASE env var in the model, default legs):
  - A. **Four legs** (recommended): 2 x 2 solid maple, 5 in tall, outer faces 2-1/2 in in from the case ends, front legs 2 in behind the case front edge, back legs 2 in inside the case back. A C-frame of 3/4 x 2-1/2 maple rails on edge between them (an end rail front to back at each end, one back rail, no front rail) with their top edges flush with the leg tops; glue and pocket screws; the case bottom pocket-screwed down onto the rails and two #8 x 2 down into each leg top under the drawer boxes. Bare maple under Osmo like the top.
  - B. **Two blades**: 1-1/2 x 5 solid maple on edge front to back under the ends, same back rail.
  - C. **Gables**: the end panels run to the floor with the bottom in a dado 5 in up, a stretcher at the bottom back, and a 1-1/4 x 4-1/2 notch at each rear bottom corner for the baseboard and shoe (alcove-specific).
- The receptacle low on the back wall (12 to 17 in up, left of center, per the photo) is now simply behind the case; if it is live and used, the back gap has to grow or the back panel gets a cutout. Confirm on site.

## Model and pipeline

`freestanding_bench.py` (build123d, mm inside, inch constants, same axes and conventions as `built_in_bench.py`): PARTS/INST/HW, asserts for one solid per part, no overlaps, the Blum rules, every housed joint by probe, and the new layout rules (the top is the widest part and sits inside the air gaps, nothing but the base reaches below CLEAR, the base meets the case bottom, the rails stay 2-1/2 in up, the back legs clear the baseboard, the leg screw spots are under the boxes and not under the runners, the gable notch is cut). All three bases pass. `EXPORT=1` writes `cutlist.md`/`.csv` (16 part rows, hardware and base screws, edge banding, cushion) and `freestanding_bench.step`.

`hero_shot.py` (viewer, BASE and CUSHION env), `assembly_shots.py` (exploded view, 10 steps, base/drawer/front explosions; the STEPS list is the page's assembly text), `part_drawings.py` (16 sheets in `images/parts/`, every header checked against the cut list), `make_cutlist_page.py` (shop page, links the options page and the built-in page), `make_pdf.py` (19 pages). `photo_match.py` (the built-in's camera match, importing this model; writes `images/alcove-overlay-<base>.png`; `check` measures the brass pulls and the front legs), `render_in_room.py` (jobs guided, styled, dogs, soffit-paint).

## Pictures

- `images/options/`: viewer renders and room-overlay crops of the three bases for the options page.
- `images/bench-in-nook-guided.png` (web copy `-web.jpg`): the legs version photorealized from the true-scale overlay in one Gemini pass ($0.165). `check`: pulls within 0.25 in of the projected height and 0.02 in across, the front legs' maple columns at the projected spots, shelves and soffit on their lines; the soffit's underside came out white on the first try (the built-in chain needed a repaint pass for that). No dogs or props yet: the styled pass (Maizy, Franco, pillows, throw, shelf objects, sign, rug; no bowls, no collar) runs once the base is picked, so nothing is redrawn three times.

## Deliverables

- Options page: https://claude.ai/artifact/QLCHadrNJZDeDjqka9yond (`base-options.html`: three bases with renders and room overlays, the Roomba table, the room picture, a picks line to copy back: base, base finish, seat height).
- Shop page: https://claude.ai/artifact/K37nFPcZU75QxRSvEAmfLL (`cutlist.html`, Version 1, with the PDF, hero, assembly and part images), documenting the legs base.

## Open

- Brian's picks from the options page: base (A, B or C), base finish (bare maple or white), seat height (17 in as drawn, or 18/19 to give the drawers their depth back).
- Inherited from the built-in: on-site measurements (the opening must be at least 66 in at every height for the 64 in top; measure the baseboard and shoe projection), the receptacle, the Blum hook-bore scrap test, Brian's look at the 1-1/2 in frame width.
