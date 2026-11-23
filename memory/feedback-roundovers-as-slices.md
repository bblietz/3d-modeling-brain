---
name: feedback-roundovers-as-slices
description: "Mixed-radius roundovers on a part printed on its side: model it as slices along the print axis joined by hulls in OpenSCAD, not kernel fillets; one chain of slices, binary STL"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 61ead13b-5621-4652-9a82-a98acabf295e
  modified: 2026-11-23T18:13:06.659Z
---

When a part needs a large roundover on some edges and a small one on the edges that meet them (guitar neck rest, 2026-11-23: 1/4 in cradle ends meeting 1/16 in rims), build it in OpenSCAD as slices along the print axis: each slice is the 2D outline with its own corner radius and height, the small roundover is carried in the height curve and in a quarter-circle inset at the two faces, and chained `hull()` joins neighbouring slices.

**Why:** a rolling-ball fillet cannot carry a 1/4 in ball round an edge that already has a 1/16 in round, so the kernel fails or leaves a crease. The slice construction is smooth everywhere, renders in seconds, and is exactly what the nozzle draws layer by layer. Working code: `projects/Guitar-neck-rest/neck_rest.scad`.

**How to apply:** each slice must be convex for `hull()` (cut holes afterwards). Build ONE chain of slices from face to face; mirroring a half onto itself puts two centre slices 0.02 mm apart and the STL comes out open. Export with `--export-format binstl` (the ASCII default was 53 MB). Check the result with rays on the mesh, not on section vertices. A roundover on the plate-side face starts as an overhang: flag it and offer a bevel there. See also [[feedback-openscad-for-complex-designs]].
