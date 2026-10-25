---
name: feedback-small-perimeter-threshold-radius
description: "Bambu's small_perimeter_threshold is a radius (loops under 2*pi*threshold are slowed); the copied PETG override of 10 / 30 mm/s cost the slotted cable bin 1 h 43 min; profile surprising times by layer band with projects/Cable-bin/pipeline/layer_times.py before touching geometry"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 57f36788-c5ae-4c4a-b01f-4b0e50546282
  modified: 2026-10-25T22:00:00.000Z
---

On the cable bin (2026-10-25) adding 13 wall slots per side took a 4 h 58 min
bin to 6 h 41 min. I first blamed the island count and sliced wider slots
(25 min back). The real cause: the `small_perimeter_threshold 10` /
`small_perimeter_speed 30` pair copied from the PETG recipe. In Bambu Studio
the threshold is a RADIUS, so every closed loop shorter than 63 mm printed
at 30 mm/s, and every web between slots is an 18 mm loop: 1147 mm per layer
at 30 mm/s. Stock X2D presets have threshold 0 (off) and 50 %.

**Why:** copied speed overrides are invisible in a slice summary; they only
show up as time, and the time is easy to blame on the geometry.

**How to apply:** when a slice time jumps after a geometry change, run
`projects/Cable-bin/pipeline/layer_times.py <3mf> <plate> <outdir> [z edges]`
(per-layer-band minutes from the M73 marks of a real slice) and compare the
bands before and after, then histogram the feedrates of one layer in the
slow band. Never carry `small_perimeter_*` overrides onto a part with many
small closed loops (slots, grilles, lattices, lettering, pegs). See
[[project-cable-bin]], [[feedback-bounded-fanout]].
