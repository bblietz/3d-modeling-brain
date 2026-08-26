---
name: feedback-logo-recreation-fidelity
description: "For logo/badge recreations Brian expects trace-faithful artwork, not primitive approximations"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 82e96f18-aad3-4512-9490-4e2762835ab5
  modified: 2026-08-08T00:05:49.463Z
---

On the Sharks-nametag project (2026-08-01), Brian rejected a logo tag whose soccer ball, stars, and seams were rebuilt from geometric primitives ("looks like shit") even though every element was individually printable and verified. The one traced element (surfer silhouette) was the only part that looked right.

**Why:** A recognizable logo carries its identity in the exact drawn shapes. Rebuilding elements from circles/polygons produces a clip-art imitation that reads as wrong next to the original, no matter how clean the geometry is.

**How to apply:** When recreating an existing logo/badge/artwork as a 3D model, vector-trace every kept element from the reference image at a fixed 1:1 scale mapping, and keep parametric geometry only for features that must be mathematically crisp (outer disc, mounting holes, frames, new text). Then refit the raw traces into real CAD primitives before extruding - polyline facets become visible walls in 3D. Brian asked for this smoothing explicitly on Sharks-nametag: line/arc refit for geometric shapes, periodic splines for organic silhouettes, with area-preservation asserts (working implementations: `refined_face` / `spline_ring_face` in projects/Sharks-nametag/sharks-nametag.py). Related: [[feedback-agentic-os-conventions]].

**Extension (2026-08-07, Sharks-nametag v3.19 -> v3.20 revert):** the fidelity rule also outranks PRINTABILITY. Brian reverted a full set of printability adaptations (thickened banner frame, badge redesigned as an inlay seal, morphologically widened crescent tips) after one look in the viewer - he prefers the slicer silently dropping sub-printable hairlines (which printed acceptably) over altered artwork. Morphological widening in particular turns long artistic tapers into lumpy hooked blobs; never apply it to visible logo shapes. Any geometry change that alters how artwork LOOKS needs Brian's viewer sign-off BEFORE it reaches exports; measure-and-report (projects/Sharks-nametag/pipeline/audit_widths.py) instead of auto-fixing.
