---
name: feedback-cutlist-hero-image
description: Every cut-list / shop page starts with a full image of the whole piece, captured from the OCP CAD viewer (save_screenshot), never the matplotlib STL render
metadata:
  node_type: memory
  type: feedback
  originSessionId: 78cb6e72-d3a2-471b-85c4-3674d1c3d30b
  modified: 2026-09-28T00:00:00.000Z
---

A published cut list (shop page) always opens with a full image of the whole piece, above the title. The image comes from the OCP CAD viewer, not from `scripts/render_stl.py`.

**Why:** Brian (2026-09-28, Drawer-bench): "for the cutlist, always put a full image of the item at the top of the page", and when shown the matplotlib STL render (axes, one flat blue, painter's-algorithm streaks): "take a screenshot from the OCP CAD viewer or export a view." The viewer's shaded, edged image is what he recognises as the piece.

**How to apply:** Keep a `hero_shot.py` per project (Drawer-bench has the template): pop the SHOW/EXPORT env, import the model, push every placed instance with `ocp_vscode.show(...)` in wood tones by material, grid and axes off, `reset_camera=Camera.RESET` with a fixed `position`/`target`, then `save_screenshot(images/hero.png)`. It needs the viewer open in the GPU Chrome (`scripts/cad-viewer.sh`); the screenshot is the canvas at the window's size. The page builder asserts the file exists, and the publish includes it in `files`. Related: [[feedback-cutlist-inches-only]], [[feedback-html-visual-companion]], [[project-drawer-bench]].
