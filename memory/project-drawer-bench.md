---
name: project-drawer-bench
description: Drawer-bench (maple post-and-panel kitchen bench) CAD built and reviewed 2026-08-24; all dimensions provisional; seven CAD resolutions await Brian's review and site/island measurements
metadata:
  type: project
---

Drawer-bench (`projects/Drawer-bench/`): build123d model `drawer_bench.py`, cut list, STEP and renders were produced on 2026-08-24 via subagent-driven development (plan in `plan.md`, ledger in `.superpowers/sdd/progress.md`). Every dimension is a provisional named constant; nothing is cut until Brian measures the space, the Boos island (thickness, edge profile, overhang) and the actual plywood, then re-runs `EXPORT=1 .venv/bin/python projects/Drawer-bench/drawer_bench.py`.

**Why:** Brian was away from home during the design; the top must match the family's John Boos island, and the CAD forced seven resolutions of the prose design (listed in `design.md` "Resolutions from the CAD": 4-1/2 in top opening with 3-11/16 / 8-11/16 in boxes at Blum's maximum, three stopped mortises per front post instead of a groove, rear rail in the back groove line over a 15-1/4 in back, rails milled to T18, rabbet for the bottom's front edge, 7 mm ply lip under the bottom groove) that he has not yet approved.

Undermount numbers were verified against the Blum 563H sheet on 2026-08-24 (inside width = opening minus 42, 14 mm bottom / 6 mm top clearance, runner longer than the box); the same correction went into Cabinet-bench.

**How to apply:** When Drawer-bench comes up, ask first whether Brian has reviewed the resolutions and taken the measurements; treat the exported cut list as provisional until then. Viewer sign-off was pending as of 2026-08-24. Related: [[project-surfboard-shape3d]] (other parked project), [[feedback-agentic-os-conventions]].
