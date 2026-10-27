---
type: handoff
project: Freestanding-bench
updated: 2026-10-26
---

# Freestanding bench handoff

State: the client's 2026-10-26 change (free standing, Roomba underneath) is designed as a separate project next to the untouched built-in one. `freestanding_bench.py` passes all asserts for all three bases (BASE=legs|blades|gables, default legs); cut list, STEP, 16 drawings, hero, assembly images, shop page https://claude.ai/artifact/K37nFPcZU75QxRSvEAmfLL (Version 1, with PDF) and the options page https://claude.ai/artifact/QLCHadrNJZDeDjqka9yond are published; `images/bench-in-nook-guided.png` is the checked room picture of the legs version (no dogs or props yet). Waiting on Brian's picks (base, base finish, seat height).

## Decisions already locked

- Everything above the floor gap from the built-in: 14 in top / 17 in seat, white frame-and-panel fronts (1-1/2 maple frames, 1/2 paint-grade panels inset 1/4, T&G), 8 in brass pulls, solid maple top 3 in back from the pilasters with a 3/4 overhang and 1/8 roundover, one cushion, 21 in Blum 563H, 1/2 Baltic birch boxes, Osmo Natural on bare maple.
- The built-in design stays as is (`projects/Built-in-bench/`, shop page Version 18) in case the client goes back.

## My calls (change via constants if Brian objects)

- CLEAR 5 in (tallest Roomba 3.9 in plus a rug); drawers 6-1/2 tall as the consequence; seat kept at 17.
- Top 64 x 24-1/2 (SIDE_AIR 1 in, WALL_GAP 1/2 in, END_OVERHANG 3/4, flush at the back because of Blum's 557 mm); case 62-1/2 x 23; END_REVEAL 1/16; fronts flush with the case underside.
- Legs base: LEG_SQ 2, LEG_IN_X 2-1/2, LEG_IN_FRONT 2, LEG_IN_BACK 2 (baseboard plus shoe assumed under 1-1/4), RAIL_H 2-1/2, C-frame with no front rail, pocket screws plus two #8 x 2 per leg; bare maple.
- 1/4 back glued in; nailer kept for the figure-8s; ends banded and painted; no plinth, strips or wall screws.

## Next

1. Brian pastes the picks line. If the base changes: `BASE=blades` (or gables) for every script; part_drawings.py asserts BASE == "legs" and needs sheets for the blades or gable notch; assembly_shots.py and make_cutlist_page.py already follow BASE_NAMES. If the seat changes: SEAT_Z and BOX_H (box must stay at or below opening minus 21 mm).
2. Then the picture chain on the picked base: `render_in_room.py guided` (if not legs), `styled` (props plus both dogs in one pass; `dogs` is the fallback), `soffit-paint` only if the underside comes out blue; `photo_match.py check` after each; web jpg at 1300 px wide; set NOOK in make_cutlist_page.py; rebuild page and PDF; republish to the same URL with the files map; report every Gemini cost.
3. Pipeline order: `EXPORT=1 freestanding_bench.py`, `part_drawings.py`, `hero_shot.py` (CUSHION=0), `assembly_shots.py` (viewer via `scripts/cad-viewer.sh`; an identical byte count on a changed scene means a stale tab), `make_cutlist_page.py`, `make_pdf.py`, publish `cutlist.html` with root `projects/Freestanding-bench`.
