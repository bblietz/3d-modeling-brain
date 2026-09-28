---
name: project-drawer-bench
description: Drawer-bench (maple post-and-panel kitchen bench) CAD built 2026-08-24; overall footprint (40x24 in) and height (19-5/8 in) measured 2026-09-17; top 1-3/4 in and 3 in posts confirmed 2026-09-27; overhang/edge profile still pending; leg design being revisited
metadata: 
  node_type: memory
  type: project
  originSessionId: 78cb6e72-d3a2-471b-85c4-3674d1c3d30b
  modified: 2026-09-27T00:00:00.000Z
---

Drawer-bench (`projects/Drawer-bench/`): build123d model `drawer_bench.py`, cut list, STEP and renders were produced on 2026-08-24 via subagent-driven development (plan in `plan.md`, ledger in `.superpowers/sdd/progress.md`). Every dimension is a provisional named constant; nothing is cut until Brian measures the space, the Boos island (thickness, edge profile, overhang) and the actual plywood, then re-runs `EXPORT=1 .venv/bin/python projects/Drawer-bench/drawer_bench.py`.

**Why:** Brian was away from home during the design; the top must match the family's John Boos island, and the CAD forced seven resolutions of the prose design (listed in `design.md` "Resolutions from the CAD": 4-1/2 in top opening with 3-11/16 / 8-11/16 in boxes at Blum's maximum, three stopped mortises per front post instead of a groove, rear rail in the back groove line over a 15-1/4 in back, rails milled to T18, rabbet for the bottom's front edge, 7 mm ply lip under the bottom groove) that he has not yet approved.

Undermount numbers were verified against the Blum 563H sheet on 2026-08-24 (inside width = opening minus 42, 14 mm bottom / 6 mm top clearance, runner longer than the box); the same correction went into Cabinet-bench.

**How to apply:** When Drawer-bench comes up, ask first whether Brian has reviewed the resolutions and taken the remaining measurements (top thickness/overhang/profile against the Boos island); treat the exported cut list as provisional until then. Viewer sign-off was pending as of 2026-08-24; the model was shown live in the interactive OCP viewer (`scripts/cad-viewer.sh`, a WebGL-capable Chrome routed to the physical GPU - this vault's usual chrome-devtools sandbox cannot create a WebGL context at all, a separate, known limitation) on 2026-09-17 when Brian asked to see it there. Related: [[project-surfboard-shape3d]] (other parked project), [[feedback-agentic-os-conventions]].

First measurement landed 2026-09-17: Brian gave the overall top footprint (40 x 24 in, was 36 x 24) and the floor-to-top-surface height (19-5/8 in, was 20 in). Applying it was not a pure scale - the front zone shrank and had to be re-split ~1:2 the same way the original design did (fronts now 5-5/8 / 11-1/8 in), which surfaced a stale hard-coded constant in `drawer_bench.py` (`BOX_TOP_H`/`BOX_BOT_H`), caught by the model's own clearance assert and fixed there; see vault commit 7499daa for detail. Re-exported and re-pushed to the viewer.

Same day: Brian confirmed the drawer boxes stay rabbeted (not pocket-hole), then set the drawer-box bottoms to 1/4 in (6 mm) plywood, down from 1/2 in (briefly tried 1/8 in first); sides/front/back stay 1/2 in. Then he changed the front 3 rails' post joints from stub-tenon-into-mortise to dowels (two 3/8 in x 1 in dowels per rail); the rear top rail is unaffected. Each change re-exported and re-pushed to the viewer.

2026-09-27: Brian confirmed the top thickness at 1-3/4 in and the post width at 3 in (the Boos island's legs are also 3 in); both already matched the CAD, so no geometry change. Remaining Boos island items: overhang past the posts and edge profile. Same day he asked to revisit the leg design with a 5-10 option visual page: built `projects/Drawer-bench/leg_options.py` (renders from the model's constants) and published `leg-options.html` as a private Artifact, https://claude.ai/artifact/FyJGk4bqsZq3rfTrXQzhbR, with post-edge options E1-E5 and floor options F1-F4 (details in the handoff). Waiting on one E and one F from Brian; the earlier 2026-08 companion screens only covered proud post vs wrap vs plinth, post thickness, and square/chamfer/taper.
