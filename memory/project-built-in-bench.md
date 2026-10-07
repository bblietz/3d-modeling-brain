---
name: project-built-in-bench
description: "Built-in alcove bench (66 x 28 in former wet bar), two drawers on Blum 563H undermounts, maple frame + walnut ply fronts on a T&G bit set, solid maple top 3 in back from the pilasters; CAD, cut list and shop page built 2026-10-07, waiting on Brian's viewer look"
metadata:
  node_type: memory
  type: project
  originSessionId: d3e73073-5ff1-4cf2-8b88-f1fd6660abc7
  modified: 2026-10-07T16:26:14.289Z
---

Built-in bench for the former wet-bar alcove: opening 66 x 28 in, three walls, open above. Picks locked 2026-10-06/07: wood top at 16 in, flush 4 in plinth, frameless with full-overlay fronts, flat fronts built as a 1-1/2 in maple frame around a 3/4 walnut veneer ply panel using Brian's tongue-and-groove router set (rail tenon showing on the stile top is fine), 8 in brass bar pulls, 3/4 overhang with eased edge, solid glued-up maple top whose front edge is 3 in back from the pilaster faces, one full-depth cushion, 21 in Blum TANDEM 563H, clear finish. Project folder `projects/Built-in-bench/`.

Status 2026-10-07: `built_in_bench.py` (build123d) passes all asserts; `cutlist.md/.csv`, STEP, renders, `hero_shot.py`, `part_drawings.py`, `make_cutlist_page.py`, `assembly_shots.py` (exploded view plus 11 step images) `cutlist.html` and `cutlist.pdf` (`make_pdf.py`) exist; shop page artifact https://claude.ai/artifact/YQFcx4g5x64K83yhDHvGMf, options tool https://claude.ai/artifact/MtDXsCPZCmjG1xELTh9jPP. Open: on-site measurements (floor, 16 in, 36 in), the low receptacle in the photo, and Brian's viewer look at the 1-1/2 in frame width (STILE_W is one constant).

**Why:** the frame width and the drawer-back construction (3/4 maple ply back with a 3/16 groove so Blum's 10 mm hook bores stay in wood; 3/4 box front for the locking-device screws) were my calls, not Brian's, so they are the things to confirm first if he wants changes.

**How to apply:** change constants in `built_in_bench.py`, run `EXPORT=1`, then `part_drawings.py`, `hero_shot.py` and `assembly_shots.py` (viewer open via `scripts/cad-viewer.sh`), `make_cutlist_page.py`, and republish the shop page to its artifact URL. Blum 563H rules re-verified from Blum sheets 2026-10-07 are in brief.md (box height = opening minus 21 mm; notch datum is the side's inside face; recess 13 mm to the underside of the bottom). See [[feedback-cutlist-inches-only]], [[feedback-cutlist-hero-image]], [[feedback-figure8-recess-offset]].
