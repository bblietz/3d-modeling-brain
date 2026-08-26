---
name: feedback-raised-letters-recipe
description: "How to print small raised or inlaid lettering cleanly on the X2D (one-wall fill-core modifier, object key, parity, thin coupons) and which dead ends never to repeat; Brian said the Sharks letters took far too many prints"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 744ff3b5-47ea-4284-a4c0-57fb6e3fdbcb
  modified: 2026-08-26T20:00:14.670Z
---

Small lettering (strokes 1.5-2.5 mm at a 0.4 nozzle, 1-1.5 mm at 0.2) shows junction marks because the wall stack eats the whole stroke: 2 walls x 0.42 mm x 2 sides = 1.68 mm, so arachne beads collide at every crossbar/stem join and Studio patches the slivers with gap fill. No wall-side setting fixes that. The fix is structural and it is now proven (Sharks nametag gate print, 2026-08-25):

**The recipe (0.4 nozzle, 0.12 mm layers, PETG on textured PEI 70C)**
1. A modifier part over the letters only (outlines buffered 0.3 mm, z from just below the letter tier to just above it) carrying region keys: `wall_loops 1`, `top_one_wall_type all top`, `top_surface_line_width 0.3`, `internal_solid_infill_line_width 0.3`, `infill_direction 90` (fill lines along the stems). Fill line width about 0.7x nozzle: 0.30 at 0.4, 0.22 at 0.2 (at 0.2 the width keys are unnecessary).
2. Object key `detect_narrow_internal_solid_infill 0` (object-level, not a region key; without it the letter cores revert to concentric beads and the marks return).
3. Parity: solid/top fill alternates 90 degrees per layer, so the direction on the top layer depends on the object's layer count. Verify on the real part's layer count (or a coupon with the same parity) that the top-layer lines run along the stems; a coupon with the wrong parity flips the verdict.
4. Side effect of the object key: every narrow internal-solid island in the object goes rectilinear (it hit the navy back inlay). Counter it with a second modifier over that region with `internal_solid_infill_pattern concentric`.
5. Per-part 3MF metadata must hold only region keys and sit before `<mesh_stat/>`; object keys go through the CLI assemble list `print_params`. Tools: `projects/Sharks-nametag/pipeline/fillcore_mod.py`, `graft_slice.py`, `toolpath_voids.py`.

**Dead ends, do not retry**: ironing on PETG (pits and smears), seam gap / speed / flow tweaks, min_feature_size and min_bead_width alone, outline micro-fillets (voids sit on the medial axis, not the corner), 2 walls + fill (worst), wider top lines, the connected monotonic pattern (plate-position sensitive), scaling the tag up, and swapping to the 0.2 nozzle as the first move (it works but costs 2.3x time plus a stringing tune; not needed once the fill-core recipe exists).

**Process rules that would have saved most of the loop**
- Go structural first: when a defect sits at wall junctions, test one-wall fill-core variants before touching speeds, seams or flow.
- Test on thin letters-only coupons: the feature plus 0.24 mm of its substrate on a 0.3-0.4 mm slab, control plus two variants per plate (15 min at 0.4, 38 min at 0.2), never the whole part.
- The toolpath void metric rejects variants with stacked voids; the eye ranks the survivors (it keys on fill-line starts and dimples, not sub-0.15 mm slivers). Brian's eye reversed the metric's top two.
- PETG stays: the 3-color tags face sun and hot cars; PLA Basic softens at 57C.

**Why:** Brian: "It took way too long and too many prints to get a quality result" (prints 4 to 9 plus six coupon plates between 2026-08-20 and 2026-08-25 before the recipe landed).

**How to apply:** For any part with lettering or thin raised graphics, start from this recipe and a thin coupon on day one; full write-up in `knowledge/learnings/sharks-nametag.md` ("Print recipe (locked)" and "Fill-core letters" sections). Related: [[feedback-minimal-test-coupons]], [[user-printer-hardware]], [[project-keep-tools-in-vault]].
