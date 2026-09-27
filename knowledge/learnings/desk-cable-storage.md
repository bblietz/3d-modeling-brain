---
title: Desk cable storage retrospective
type: learning
project: Desk-cable-storage
created: 2026-09-26
tags: [x2d, petg, cable-management, closet-desk, build123d, visual-companion]
---

# Desk cable storage: wall trough under the printer bench

**CAD complete 2026-09-26.** Not printed yet. Brief: [[brief]] in `projects/Desk-cable-storage/`. One-piece PETG trough, 254 x 152.4 x 152.4 mm, screwed to the back wall under the power strip's plug heads.

## What worked

- **A to-scale scene of the room, not just the part.** Modelling the closet, slab, strip, PC and shredder in OpenSCAD and rendering every concept from real eye positions (5 ft, 10 ft, oblique, crouched) let Brian judge "hidden" from pictures instead of arguments. Rendering the new part in black for the hidden checks and in orange for the design views kept both honest.
- **High-resolution photos with zoomed crops.** The first 1183 px photo put the strip at the back wall; the 5712 px versions, cropped and re-read, put it 12 in behind the front edge and showed the closet is 45 in wide behind a 32 in opening. Both facts changed the design space.
- **Draw first, ask against the drawing.** After three text questions Brian said to stop asking and start drawing. The rest of the decisions came in minutes off the pages.
- **A phone page for decisions away from the desk.** Brian picked the concept from his phone; a second session continued the work from the artifact. Every render embedded or published as files, no data URIs in the second version.
- **build123d for a prism with self-checks.** Bounding box, single solid, cavity clear, front wall height, back wall height, both holes through, watertight STL. The first run caught my own square-cornered probe overlapping the cavity fillets, not the part.
- **Real slice before handing over.** The Bambu CLI accepted the 254 mm part at x 1 to 255 with brim and skirt forced off. `--arrange 1` had rotated it 90 degrees into the two-nozzle shared area (extruder 2 starts at x 20.5); pinning the object to extruder 1 and writing the whole item transform fixed it.

## What failed

- **The measurement sheet was wasted.** Ten tape-measure callouts and a fill-in phone sheet were built before Brian said to ignore all of them. The part is free-standing geometry; the closet numbers only affect the install height, which is set by eye. Ask whether a dimension changes the part before asking for it.
- **My recommendation (D+) lost to the pictures.** Brian chose the visible-from-10-ft position because loading from above matters more to him than the sliver that shows. State the tradeoff once, then build what he picks.
- **Two sessions, one folder.** The phone session and this one both wrote to the project; brief.md was nearly overwritten. Read the handoff before writing anything when a project may have moved elsewhere.

## Measured fits

| Feature | Modelled | Result |
|---|---|---|
| Screw holes | 5.0 mm for #8 in drywall anchors, 7 in apart | not printed yet |
| Bed fit | 254 mm in 256, no brim or skirt | slicer accepted; print pending |

## Settings used

Bambu Lab X2D 0.6 nozzle (assumed installed; printer unreachable), 0.30mm Standard, Bambu PETG Basic black, Textured PEI at 70 C, no brim, no skirt, floor down. Slice: 8 h 42 m, 417 g, 508 layers.

## Open

- Print outcome, elephant foot on a 254 x 152 first layer, whether the 2.4 mm walls feel stiff enough over 10 in.
- Anchor pull-out under a loaded trough (a few pounds of cord and one brick).
- Whether cords from the outer outlets drape into a 10 in box cleanly or want a second box.
