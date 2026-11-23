---
type: handoff
project: Guitar-neck-rest
updated: 2026-11-23
---

# Guitar neck rest handoff

State: BUILT 2026-11-23, not printed. `neck_rest.scad` is the model; `guitar-neck-rest.stl` and `guitar-neck-rest.3mf` (one plate, 167.5 g, 2 h 21 min PLA) are exported and the 3MF is proven by a real slice. Page Version 6 is published at https://claude.ai/artifact/PXoUtoD3EfYz3RtPXSQzkf. Spec, plan, brief and the retrospective (`knowledge/learnings/guitar-neck-rest.md`) are up to date. Committed to main 2026-11-23 (Brian asked); the concept STLs in `concepts/` are ignored because `pipeline/concepts.py` regenerates them.

## Decisions already locked

- Brian 2026-11-22: rocker; open-frame body (round 2's C1); 4-3/8 in cradle, unchanged. Do not reopen.
- Brian 2026-11-23: go on the design; the two cradle ends rounded over (confirmed as the ends, not the long top edges); a slight roundover on every other edge; spec approved ("Yes, build it").
- Brian 2026-11-23: one recessed channel in the bottom for his 2 in wide rubber grip tape, replacing the two tread strips.

## My calls (constants at the top of neck_rest.scad)

- `R_END` 6.35 (1/4 in), `R_EDGE` 1.5875 (1/16 in).
- `TAPE_D` 0.5: the channel is shallower than the tape so the rest stands on rubber. His tape thickness is not known.
- `PAD_T` 1.6 for 1/16 in cork; pad cut 2-3/4 x 4-1/8 in; tape cut 2 x 5-1/2 in.
- PLA, 2 walls, 15% infill, seam back, Textured PEI 65 C.

## Next

1. Brian opens the 3MF in Studio, picks the colour, looks at the preview (plate-side roundover in the first layers, steps on the top face) and prints.
2. If the plate-side roundover looks rough: make that side a small bevel (`inset_at()` for the plate-side slices in `neck_rest.scad`).
3. If his tape is thinner than about 1/32 in: lower `TAPE_D`.
4. Any change: edit the constants, `.venv/bin/python projects/Guitar-neck-rest/pipeline/build.py`, then `pipeline/make_print_3mf.py`, then `pipeline/options_page.py` and republish `options.html` to the same Artifact.
5. After the print: measured fits and the outcome into the retrospective.
