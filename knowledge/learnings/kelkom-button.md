---
tags: [learnings, reverse-engineering, freecad, snap-fit]
source: Kelkom intercom button session, 2026-07-28
---

# Learnings: Kelkom intercom button

Photo-to-STL reverse engineering of a snap-fit part took about 13 minutes including one full rebuild. Project state and dimensions: [[brief]] in projects/Kelkom-button.

## Reverse-engineering from photos

- Snap-leg placement is the top ambiguity in bezel/clip parts. Ask before building: legs on opposite faces or opposite corners? A profile photo cannot disambiguate this (corner legs viewed along the diagonal look identical to face-mounted parallel legs); only a sharp bottom view can. Guessing wrong here cost a complete rebuild.
- Photos give shape; calipers give numbers. Tag every dimension in the build script with provenance (`# user-measured` vs `# estimated from photos`). This made the correction round trivial to apply.
- Ask for one photo with a scale reference (ruler, coin, caliper) alongside the part.
- Report all estimated values back explicitly and invite corrections. That feedback loop is what made the project converge.

## FreeCAD / OCC technique

- After any boolean, fillet, or chamfer the topology changes. Re-select edges by exact expected geometry, never by a loose bounding filter: a loose filter picked up the first chamfer's own new edge and the second `makeChamfer` failed with `OCCError: BRep_API: command not done`.
- `assert len(edges) == N` after every topological selection. Converts silent wrong-geometry into a loud, immediate failure. Most valuable scripting habit in the session.
- `.removeSplitter()` after every fuse/cut keeps face counts sane.
- Arc-section corner leg: annular shell (outer cylinder cut by inner cylinder extended past both ends) intersected with an extruded triangle sector; half-angle from chord `asin((W/2)/Ro)`. Barb: revolve a profile face about the arc axis. Second leg: copy and rotate 180 degrees.
- Rounded-corner square hole: fuse two crossed boxes plus four corner cylinders; extend cutters well past both faces to avoid coincident-face artifacts.
- Print-friendly recess: loft between two square wires (truncated pyramid, 45 degree walls), top wire 0.1 mm above the face for a clean cut.
- When a fundamental assumption changes, rebuild from one consolidated script that re-derives everything from a dimension block, rather than patching incremental steps.

## Workflow

- A 12-line XML-RPC helper (`fc.py`, saved in the model's `scripts/` dir) hitting `http://127.0.0.1:9875` directly allowed `exec build.py && shot Isometric && shot Front && shot Bottom` in one Bash call, then reading the PNGs. Far fewer round trips than per-step MCP calls. Candidate pattern to promote into the `/3d-model` skill.
- Screenshot-verify every feature from more than one view. The bottom view is the one that catches leg-placement errors; the isometric view alone does not.
- Keep build scripts in the model directory, not the session scratchpad. This project's parametric source nearly died with `/tmp`; it is now rescued to `models/kelkom-intercom-button/scripts/`.

## X2D design rules confirmed

- Prefer the 0.4 mm nozzle for any thin flexing feature under about 1.5 mm; a 1.3 mm leg is on the knife edge of the 0.6 nozzle's 1.24 mm two-perimeter minimum.
- Snap-fit legs: PETG, not PLA, and orient so layer lines do not cross the flex axis where avoidable.
- Press/panel fits: correct with slicer XY compensation (-0.1 to -0.2 mm), never by rescaling the model; CAD stays at nominal as the faithful record.

## Related

- [[printer-x2d]]
