---
name: feedback-stopped-groove-notched-panel
description: Brian stops a post/leg groove short and notches the panel's corner to meet it, so the groove end never has to be squared; model the clearance and assert it
metadata:
  node_type: memory
  type: feedback
  originSessionId: 78cb6e72-d3a2-471b-85c4-3674d1c3d30b
  modified: 2026-09-28T00:00:00.000Z
---

When a panel is housed in a stopped groove (post-and-panel legs, a shelf in a stopped dado), do not run the groove to the panel's end and rely on a squared groove end. Stop the groove short, notch the panel's corner (groove depth x a comfortable height, 3/8 x 1-1/2 in on the Drawer-bench) so the housed tongue starts well above the groove's end, and let the panel's un-housed edge butt the post face over the end.

**Why:** Brian (2026-09-28, Drawer-bench): "This will make it much easier to construct if I don't have to have a perfectly clean bottom of the dado." A router leaves a round end, a table saw a ramp; squaring both at every post is chisel work with no visual payoff, since the end hides behind the panel anyway.

**How to apply:** Give the groove a window rather than a line: its end may fall anywhere between the panel's bottom edge (nothing below it shows) and the tongue's start; keep at least the bit radius plus 1/4 in of clearance and make it a named constant that the model asserts. Put the tongue's start on a clean datum (the Drawer-bench uses the bottom panel's top face, so the notch runs up to the bottom groove's top wall) and keep it out of any other groove band, or a sliver is left. Probe the clearance zone as air on both sides and the post as solid below the stop; the drawings show the two lines and say "leave the end as the tool cuts it". Related: [[project-drawer-bench]], [[feedback-cutlist-inches-only]].
