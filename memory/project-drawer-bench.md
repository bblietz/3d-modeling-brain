---
name: project-drawer-bench
description: Drawer-bench (maple post-and-panel kitchen bench) CAD built 2026-08-24; overall footprint (40x24 in) and height (19-5/8 in) measured and applied 2026-09-17; top thickness/overhang/profile still pending the Boos island measurement
metadata: 
  node_type: memory
  type: project
  originSessionId: 78cb6e72-d3a2-471b-85c4-3674d1c3d30b
  modified: 2026-09-18T05:45:03.294Z
---

Drawer-bench (`projects/Drawer-bench/`): build123d model `drawer_bench.py`, cut list, STEP and renders were produced on 2026-08-24 via subagent-driven development (plan in `plan.md`, ledger in `.superpowers/sdd/progress.md`). Every dimension is a provisional named constant; nothing is cut until Brian measures the space, the Boos island (thickness, edge profile, overhang) and the actual plywood, then re-runs `EXPORT=1 .venv/bin/python projects/Drawer-bench/drawer_bench.py`.

**Why:** Brian was away from home during the design; the top must match the family's John Boos island, and the CAD forced seven resolutions of the prose design (listed in `design.md` "Resolutions from the CAD": 4-1/2 in top opening with 3-11/16 / 8-11/16 in boxes at Blum's maximum, three stopped mortises per front post instead of a groove, rear rail in the back groove line over a 15-1/4 in back, rails milled to T18, rabbet for the bottom's front edge, 7 mm ply lip under the bottom groove) that he has not yet approved.

Undermount numbers were verified against the Blum 563H sheet on 2026-08-24 (inside width = opening minus 42, 14 mm bottom / 6 mm top clearance, runner longer than the box); the same correction went into Cabinet-bench.

**How to apply:** When Drawer-bench comes up, ask first whether Brian has reviewed the resolutions and taken the remaining measurements (top thickness/overhang/profile against the Boos island); treat the exported cut list as provisional until then. Viewer sign-off was pending as of 2026-08-24; the model was shown live in the interactive OCP viewer (`scripts/cad-viewer.sh`, a WebGL-capable Chrome routed to the physical GPU - this vault's usual chrome-devtools sandbox cannot create a WebGL context at all, a separate, known limitation) on 2026-09-17 when Brian asked to see it there. Related: [[project-surfboard-shape3d]] (other parked project), [[feedback-agentic-os-conventions]].

First measurement landed 2026-09-17: Brian gave the overall top footprint (40 x 24 in, was 36 x 24) and the floor-to-top-surface height (19-5/8 in, was 20 in). Applying it was not a pure scale - the front zone shrank and had to be re-split ~1:2 the same way the original design did (fronts now 5-5/8 / 11-1/8 in), which surfaced a stale hard-coded constant in `drawer_bench.py` (`BOX_TOP_H`/`BOX_BOT_H`), caught by the model's own clearance assert and fixed there; see vault commit 7499daa for detail. Re-exported and re-pushed to the viewer.

Same day: Brian confirmed the drawer boxes stay rabbeted (not pocket-hole) and set the drawer-box bottoms to 1/8 in (3 mm) plywood, down from 1/2 in; sides/front/back stay 1/2 in. Re-exported and re-pushed to the viewer.
