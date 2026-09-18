---
name: feedback-openscad-for-complex-designs
description: "Brian asked for OpenSCAD on the NACS wall holder after build123d and hand-drawn SVG plans went badly; render real model views, never hand-draw plans"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 506fbb0a-36a5-4411-bd97-64325ff2c036
  modified: 2026-09-18T03:09:58.092Z
---

On the NACS wall holder (2026-09-17) Brian said "for a complex design like this, use opencad" and "you are not doing very will with simple123" after two rounds of build123d attempts and a hand-drawn shapely/SVG plan page with mislabelled, off-centre drawings.

**Why:** a compound-angle part (wand 45 degrees down and 20 degrees off the wall, cleat in a tilted cavity frame) needs a model he can read as code and renders cut from the real geometry; the SVG plan page had to be redrawn every round and still lied about the geometry, and the build123d loop was slow and error-prone for him to follow.

**How to apply:** for multi-frame or compound-angle parts, start in OpenSCAD (`~/.local/bin/openscad`, Manifold backend, see CLAUDE.md Environment) and show progress as rendered views and section cuts of the actual model, published on an HTML page. Keep build123d for simple prismatic parts. Never present hand-drawn plan drawings as the design. Working example: projects/NACS-wall-holder/holder.scad with render.sh and renders_page.py. Related: [[feedback-html-visual-companion]], [[feedback-stl-to-bambu-3mf]].
