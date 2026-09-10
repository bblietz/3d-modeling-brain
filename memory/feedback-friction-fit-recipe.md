---
name: feedback-friction-fit-recipe
description: "Friction-fit lids need crush ribs plus a designed opening feature, not tighter clearance; read knowledge/friction-fits-x2d.md before any fit job"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5c1de18d-a9c6-4689-9468-bd56351ceced
  modified: 2026-09-10T15:45:45.887Z
---

For a full-perimeter plug fit (lid, cap, cover), do NOT reach for the
[[user-printer-hardware]] "0.2 mm snug" clearance rule. Relax the plug body
to a free 0.15 mm per side and let 8 crush ribs (2 per side, R1
half-embedded cylinders, 0.35 mm proud) own the fit. Always design an
opening feature in from the start - a snug flush lid cannot be opened
barehanded. Full recipe: `knowledge/friction-fits-x2d.md`.

**Why:** the snug rule is for local features with somewhere to deflect. A
closed plug in a closed cavity is stiff in every direction, so it is either
rattling or un-assemblable. Measured on the Build123d-trial box: 0.2 mm per
side rattled, 0.1 mm still had play, and the as-printed gap runs ~0.055 mm
per side looser than designed. Walking the clearance down costs prints and
does not converge.

**How to apply:** read `knowledge/friction-fits-x2d.md` before designing
any friction fit; do not re-derive it. Treat the numbers as one
calibration (0.6 high-flow, classic wall generator, PLA Basic, one spool) -
if the nozzle, wall generator, filament brand or material differs, run a
corner coupon first per [[feedback-minimal-test-coupons]]. Map removal
features into the in-use orientation, since a plug lid flips to install.
See also [[project-keep-tools-in-vault]].
