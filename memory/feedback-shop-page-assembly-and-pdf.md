---
name: feedback-shop-page-assembly-and-pdf
description: Every shop page (cut list) ends with an assembly section (exploded view, one row per step with a viewer image of the parts going in, sub-assembly explosions) and ships as a PDF printed from the page
metadata:
  node_type: memory
  type: feedback
  originSessionId: 78cb6e72-d3a2-471b-85c4-3674d1c3d30b
  modified: 2026-10-07T00:00:00.000Z
---

A published cut list (shop page) does not stop at the parts and hardware: it ends with the assembly order, one numbered row per step with the shop text and a picture from the OCP CAD viewer of the parts going in (new parts in wood colors, parts already placed in pale grey), an exploded view of the whole piece above the steps, and a pulled-apart picture of any sub-assembly a step builds (a drawer box, a side frame). The page is also printed to a PDF for the shop and links it.

**Why:** Brian asked for it on both benches: the Built-in-bench page got its assembly section and PDF on the morning of 2026-10-07, then for the Drawer-bench the same day: "add assembly steps/diagram to the cutlist. Export the cutlist to pdf". He reads pictures, not paragraphs (see [[feedback-html-visual-companion]]), and the shop copy is paper.

**How to apply:** Per project keep `assembly_shots.py` (template in `projects/Drawer-bench/`): a STEPS list of (file stem, title, placed-instance prefixes, shop text) that the page builder imports so text and pictures cannot drift, `capture()` through `ocp_vscode.show` + `save_screenshot` with the GPU viewer open (`scripts/cad-viewer.sh`), cumulative step images, an EXPLODE offset table per instance prefix, and explicit sub-assembly explosions. Scale each step's zoom by the viewer's fit radius (the larger of the shown parts' bounding-sphere radius and the bbox center's distance from the origin) over the full model's, so every step shares one scale with one target. Then `make_pdf.py` (headless `google-chrome --print-to-pdf`, letter, no header or footer) with `@media print` rules in the page: ticks and captions hidden, each big section on a new page, each row kept together, each group heading in one `break-inside: avoid` block with its first row. Publish the assembly PNGs and the PDF as the artifact's files. Related: [[feedback-cutlist-hero-image]], [[feedback-cutlist-inches-only]], [[project-drawer-bench]], [[project-built-in-bench]].
