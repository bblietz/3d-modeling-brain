---
type: handoff
project: Freestanding-bench
updated: 2026-10-26
---

# Freestanding bench handoff

State: the client's 2026-10-26 change (free standing, Roomba underneath) is designed as a separate project next to the untouched built-in one, on four proud 2-1/2 in chamfered soft maple corner posts the drawer bench's way (Brian's pick A from five companion options, after rejecting legs under a box). `freestanding_bench.py` passes all asserts; cut list, STEP, drawings, hero, assembly images, shop page https://claude.ai/artifact/K37nFPcZU75QxRSvEAmfLL (with PDF) and the options page https://claude.ai/artifact/QLCHadrNJZDeDjqka9yond (Version 2, decided) are published; `images/bench-in-nook-dogs.png` is the checked sign-off picture (guided -> styled -> dogs, $0.50 this round plus $0.17 wasted on a one-pass styled). Waiting on site measurements and the client.

## Decisions already locked

- Everything above the floor gap from the built-in: 14 in top / 17 in seat, white frame-and-panel fronts (1-1/2 maple frames, 1/2 paint-grade panels inset 1/4, T&G), 8 in brass pulls, solid maple top 3 in back from the pilasters, 3/4 overhang with a 1/8 roundover, one cushion, 21 in Blum 563H, 1/2 Baltic birch boxes, Osmo Natural on bare maple.
- Brian 2026-10-26: the legs are the drawer bench's construction (proud chamfered corner posts, panels housed in them, fronts between them), size A, 2-1/2 in square.
- The built-in design stays as is (`projects/Built-in-bench/`, shop page Version 18) in case the client goes back.

## My calls (change via constants if Brian objects)

- CLEAR 5 in (tallest Roomba 3.9 in plus a rug); drawers 6-1/2 tall as the consequence; seat kept at 17.
- WALL_GAP 1/4 in, SIDE_AIR 1 in, OVERHANG 3/4 past the posts, FRONT_SETBACK 1/4, SETBACK 1/2, GROOVE_D 3/8, NOTCH_H 1-1/2, GROOVE_CLR 3/4 (all the drawer bench's numbers except the wall gap).
- The 1/2 maple ply back (a 3/4 back loses the 21 in runners their 557 mm); the rear posts' baseboard notch 1-1/2 x 4-1/2 (BASEBOARD_NOTCH=0 if the baseboard comes out); RUNNER_LEN 547 assumed for the bracket check, verify.
- Posts soft maple like the drawer bench; the cleat soft maple; ends banded and painted; no plinth, strips or wall screws.

## Next

1. Site measurements (opening at every height, baseboard and shoe projection, receptacle), the Blum hook-bore scrap test, the runner body length.
2. Any change: edit constants, then `EXPORT=1 freestanding_bench.py`, `part_drawings.py`, `hero_shot.py` (CUSHION=0), `assembly_shots.py` (viewer via `scripts/cad-viewer.sh`; an identical byte count on a changed scene means a stale tab), `make_cutlist_page.py`, `make_pdf.py`, publish `cutlist.html` with root `projects/Freestanding-bench` to the same URL with the files map.
3. Picture changes: `photo_match.py` (overlay, `check`), `render_in_room.py guided`, then `styled` (concept only), then `dogs` (the two dog photos); never the dogs and the props in one pass; `check` after each; web jpg at 1300 px; NOOK in make_cutlist_page.py; report every Gemini cost.
4. The companion server for the leg options was started from the vault (`.superpowers/brainstorm/2477357-1793074339`); stop it with the brainstorming skill's `scripts/stop-server.sh` if it is still up.
