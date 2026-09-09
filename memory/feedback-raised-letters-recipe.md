---
name: feedback-raised-letters-recipe
description: "How to print small raised or inlaid lettering cleanly on the X2D (one-wall fill-core modifier, object key, parity, thin coupons) and which dead ends never to repeat; validated by the 14-tag Sharks batch; Brian does not want to redo any of this"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 744ff3b5-47ea-4284-a4c0-57fb6e3fdbcb
  modified: 2026-09-09T04:21:57.273Z
---

Small lettering (strokes 1.5-2.5 mm at a 0.4 nozzle) shows junction marks because the wall stack eats the whole stroke (2 walls x 0.42 mm x 2 sides = 1.68 mm): arachne beads collide at every crossbar/stem join and Studio patches the slivers with gap fill. No wall-side setting fixes that. The structural fix is proven: MAX 18 gate 2026-08-25, then all 14 Sharks tags printed clean (batch finished by 2026-09-08, "all the kids are happy").

**The recipe** (full turnkey write-up in `knowledge/lettering-x2d.md`, tools in `projects/Sharks-nametag/pipeline/`):
1. Modifier part over the letters only (outlines +0.3 mm, z just below to just above the letter tier): `wall_loops 1`, `top_one_wall_type all top`, `top_surface_line_width 0.3`, `internal_solid_infill_line_width 0.3`, `infill_direction 90` (lines along the stems). Fill width ~0.7x nozzle; at 0.2 the width keys are unnecessary.
2. Object key `detect_narrow_internal_solid_infill 0` via the CLI assemble list `print_params` (without it the cores revert to concentric and the marks return).
3. Parity: top-layer fill direction depends on the object's layer count; verify on the real part (37 layers on the tag) or a coupon of the same parity.
4. Object-key side effect: narrow internal-solid islands elsewhere go rectilinear; counter with a region modifier `internal_solid_infill_pattern concentric` (needed on the navy back inlay).
5. Region keys only in per-part metadata, before `<mesh_stat/>`; list every recipe key in `different_settings_to_system` or Studio resets it.

**Dead ends, do not retry**: ironing on PETG, seam/speed/flow tweaks, bead-minimum settings alone, outline micro-fillets, 2 walls + fill, wider top lines, the connected monotonic pattern, scaling the part, the 0.6 nozzle, and the 0.2 nozzle as a first move.

**Process rules that would have saved most of the loop**: go structural first when a defect sits at wall junctions; test on thin letters-only coupons (15 min at 0.4), control + two variants; the void metric rejects, the eye ranks (Brian's eye reversed the metric's top two); offline slice + metric before every print; print one gate part, then the batch. Studio flush volumes for PETG white/navy/cyan are in the knowledge note.

**Why:** Brian: "It took way too long and too many prints to get a quality result" and "Next time I print letters, I do not want to have to redo all of this" (prints 4 to 9 plus six coupon plates and five offline sweeps between 2026-08-20 and 2026-08-25).

**How to apply:** For any part with lettering or thin raised graphics, open `knowledge/lettering-x2d.md` first, build with `fillcore_mod.py`, verify offline, run one thin coupon only if the letters differ in scale/font/nozzle, then gate and batch. Related: [[feedback-minimal-test-coupons]], [[user-printer-hardware]], [[project-keep-tools-in-vault]].
