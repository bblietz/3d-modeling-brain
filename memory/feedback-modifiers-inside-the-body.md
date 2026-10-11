---
name: feedback-modifiers-inside-the-body
description: Every infill modifier in a print 3MF stays wholly inside the body it modifies; Bambu Studio draws modifiers translucent over the part, so anything outside reads as added geometry (Brian, 2026-10-11)
metadata:
  type: feedback
---

Brian opened the NACS wall holder's print 3MF in Bambu Studio and saw the solid-base modifier's squared-off ring
sitting on the plate round the drum: "the added ring is squared off, it should round into the wall plate, like the
device rounds into the front plate". The ring was never plastic, only the slicer's 100% infill region, but Studio
draws a modifier translucent over the part, so the part of it outside the body (10.4 cm3: the collar above the
blend, the slab showing through the screw holes, a coplanar top face over the plate) looked like geometry.

**Why:** Brian judges a print file by what Studio shows; a modifier that pokes out of the body misreads as a design
change and costs a round trip. A modifier outside the part can also grow the object's outline and the skirt.

**How to apply:** build every modifier so no part of it lies outside the body: offset it inward from any surface it
follows (one line width, 0.6 mm, keeps the solid region reaching the walls in every layer), stop it a layer under any
face it would otherwise share with the body, and clear holes by the inset. Prove it with an OpenSCAD boolean:
difference(modifier, body) must be empty (`projects/NACS-wall-holder/pipeline/modifier_views.py` measures it and draws
the Studio view before and after). Still prove the solid region itself in the sliced G-code, per
[[feedback-solid-infill-at-screw-holes]]. See also [[project-nacs-wall-holder]].
