---
type: handoff
project: Freestanding-bench
updated: 2026-11-01
---

# Freestanding bench handoff

State: Version 3 of the post design (2026-11-01). Brian asked for the baseboard notch gone and the top 1/4 in from the walls all round; he picked 18 in runners to pay for the depth the posts lose standing off the baseboard. `freestanding_bench.py` passes all asserts: top 65-1/2 x 24-3/4 at 1/4 in from all three walls, rear posts 2 in off the back wall (no notch, 3/4 in clear of the 1-1/4 in baseboard estimate), overhangs 1-1/2 ends / 3/4 front / 1-3/4 back, boxes 27-11/16 x 6-1/2 x 18 on Blum 563H4570B, inside depth 516.1 mm (Blum 481), post-side bracket gap 44.6 mm (6 to 48). Cut list, STEP, 15 drawing sheets (232 probes), hero, assembly images, page and PDF rebuilt; shop page https://claude.ai/artifact/K37nFPcZU75QxRSvEAmfLL republished. The room picture `images/bench-in-nook-dogs.png` is still Version 1 (notched posts, 64 in top); not rerun. Options page https://claude.ai/artifact/QLCHadrNJZDeDjqka9yond untouched (Version 2, posts decided). Waiting on site measurements and the client.

## Decisions already locked

- Everything above the floor gap from the built-in: 14 in top / 17 in seat, white frame-and-panel fronts (1-1/2 maple frames, 1/2 paint-grade panels inset 1/4, T&G), 8 in brass pulls, solid maple top 3 in back from the pilasters with a 3/4 front overhang and a 1/8 roundover, one cushion, 1/2 Baltic birch boxes, Osmo Natural on bare maple.
- Brian 2026-10-26: the legs are the drawer bench's construction (proud chamfered corner posts, panels housed in them, fronts between them), size A, 2-1/2 in square.
- Brian 2026-11-01: no notch in the rear posts; the top 1/4 in from the walls all round (65-1/2 wide); 18 in Blum 563H instead of 21 in (his pick over pulling the case 1-1/2 in forward or taking the baseboard out).
- The built-in design stays as is (`projects/Built-in-bench/`, shop page Version 18) in case the client goes back.

## My calls (change via constants if Brian objects)

- CLEAR 5 in; drawers 6-1/2 tall; seat kept at 17.
- The posts stayed where they were when the top grew: END_OVERHANG 1-1/2 (X0 unchanged at 1-3/4 from the side walls), OVERHANG 3/4 front.
- BB_CLEAR 3/4: rear posts at 2 in off the wall, set by the Blum rear bracket (1-3/4 left 51 mm, over the 48 mm reach), REAR_OVERHANG 1-3/4 as the consequence. RUNNER_LEN 471 is the drawer bench's measured 563H4570B body.
- WALL_GAP 1/4, SIDE_AIR 1/4, FRONT_SETBACK 1/4, SETBACK 1/2, GROOVE_D 3/8, NOTCH_H 1-1/2, GROOVE_CLR 3/4; 1/2 maple ply back kept.
- Posts and cleat soft maple; ends banded and painted; no plinth, strips or wall screws.

## Next

1. Site measurements (opening at every height, baseboard and shoe projection on all three walls, receptacle), the Blum hook-bore scrap test.
2. If the client should see the new shape in the room: `photo_match.py` (overlay, `check`), `render_in_room.py guided`, then `styled` (concept only), then `dogs`; never the dogs and the props in one pass; `check` after each; web jpg at 1300 px; report every Gemini cost (about $0.50 for the chain).
3. Any change: edit constants, then `EXPORT=1 freestanding_bench.py`, `part_drawings.py`, `hero_shot.py` (CUSHION=0), `assembly_shots.py` (viewer via `scripts/cad-viewer.sh`; an identical byte count on a changed scene means a stale tab), `make_cutlist_page.py`, `make_pdf.py`, publish `cutlist.html` with root `projects/Freestanding-bench` to the same URL with the files map.
