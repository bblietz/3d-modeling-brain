---
name: project-freestanding-bench
description: "Freestanding version of the alcove bench (client 2026-10-26: free standing, Roomba underneath): same case, fronts and top as the built-in on a base with 5 in of clear floor; separate project projects/Freestanding-bench, built-in untouched; three bases modeled, legs recommended; waiting on Brian's picks"
metadata:
  node_type: memory
  type: project
  originSessionId: d3e73073-5ff1-4cf2-8b88-f1fd6660abc7
  modified: 2026-10-26T20:40:00.000Z
---

The client changed the alcove bench to a freestanding piece with room for the Roomba under it on 2026-10-26. It lives in `projects/Freestanding-bench/` (`freestanding_bench.py`, same conventions as the built-in model) and the built-in design in [[project-built-in-bench]] stays untouched in case they go back. Everything above the floor gap carries over (14 in top, 17 in seat, white frame-and-panel fronts, brass pulls, maple top, Blum 563H, Baltic birch boxes, Osmo). New: 5 in of clear floor (tallest Roomba 3.9 in, rug margin), so the drawer boxes are 6-1/2 in instead of 8-1/2; top 64 x 24-1/2 with 1 in of air to each wall and the baseboard left in place; show-face ends painted white; 1/4 back glued in as the shear panel; base is BASE=legs (four 2 x 2 maple legs in a C-frame of 3/4 x 2-1/2 rails, no front rail), blades, or gables (notched for the baseboard).

Status 2026-10-26: all three bases pass the asserts; cut list, 16 drawings, hero, assembly images, shop page https://claude.ai/artifact/K37nFPcZU75QxRSvEAmfLL (legs, Version 1, PDF) and the options page https://claude.ai/artifact/QLCHadrNJZDeDjqka9yond (renders, true-scale room overlays, Roomba table, picks line) are published; `images/bench-in-nook-guided.png` is the checked room picture of the legs version ($0.165), without dogs or props yet. Open: Brian's picks (base, base finish bare maple or white, seat 17/18/19), then the styled pass with Maizy and Franco on the picked base, plus the inherited site items (measurements, baseboard and shoe projection under 1-1/4 in, the receptacle now behind the case).

**Why:** CLEAR 5 in, the 1 in side air, the flush back (a rear overhang breaks Blum's 557 mm inside depth), the legs' insets and the C-frame are my calls; the drawers losing 2 in is the cost of the clearance at a fixed seat height, and raising the seat is the client's call.

**How to apply:** change constants in `freestanding_bench.py`, then `EXPORT=1`, `part_drawings.py` (legs only so far), `hero_shot.py` (CUSHION=0), `assembly_shots.py` (viewer), `make_cutlist_page.py`, `make_pdf.py`, republish `cutlist.html` to its URL with root `projects/Freestanding-bench`; pictures via `photo_match.py` (overlay per base, `check` measures the pulls and the front legs) and `render_in_room.py` (guided, styled with both dogs in one pass, soffit-paint fallback). See [[feedback-photo-composite-cad-overlay]], [[feedback-cutlist-inches-only]], [[feedback-html-visual-companion]].
