---
name: feedback-solid-infill-at-screw-holes
description: Every printed part with screw holes gets 100% infill around the holes (a modifier part in the 3MF), and the slice must prove it; Brian's standing rule from 2026-10-04
metadata:
  type: feedback
---

Any part with screw holes ships with 100% infill around every hole: a modifier part in the project 3MF (a cylinder through the wall at each hole, about 25 mm across, `sparse_infill_density` 100%), never just the global infill. The 3MF is not done until a real slice shows the pads solid.

**Why:** Brian, 2026-10-04, on the skateboard wall holder after the 3MF was already sliced: "always use 100% infill around screw holes. chekc to make sure this model has it". It did not; the plate core around the countersinks was 20% gyroid. The NACS wall holder had the pads (85 to 92% plastic in the pads against 18 to 19% in the plain plate, checked in the G-code) and this one skipped them as "simple enough".

**How to apply:** build the modifier the way `projects/NACS-wall-holder/pipeline/make_coupon_3mf.py` does (a new object in the object's `3D/Objects/*.model`, a `<component>`, a `<part subtype="modifier_part">` carrying `sparse_infill_density` 100%); the same step now lives in `projects/Skateboard-wall-holder/pipeline/make_print_3mf.py`. Verify with the G-code density check, not a round trip. Add it to every pre-flight checklist for wall mounts and brackets. Related: [[project-nacs-wall-holder]], [[feedback-stl-to-bambu-3mf]].

Checking it in the G-code (NACS holder, 2026-10-11): set each check window out in the model's frame and map it through
the object's item transform read from the sliced 3MF. The CLI's arrange turns the part on the bed (88 degrees that
day), and a window on the model's axes at the bed centre read 0.0 plastic in solid material. See
[[feedback-modifiers-inside-the-body]].
