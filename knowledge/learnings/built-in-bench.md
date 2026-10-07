---
type: learning
project: Built-in-bench
created: 2026-10-07
status: designed, not built
tags: [furniture, bench, built-in, undermount, blum, frameless, tongue-and-groove]
---

# Built-in alcove bench: retrospective (design phase)

Links: [[Built-in-bench]] brief in `projects/Built-in-bench/brief.md`, model `built_in_bench.py`, shop page `cutlist.html`. Related: [[drawer-bench]], [[feedback-cutlist-inches-only]], [[feedback-cutlist-hero-image]], [[feedback-figure8-recess-offset]].

## What worked

- Options tool before CAD. Brian's picks came back as one pasted block and two follow-up sentences; no design churn in the model.
- A research subagent on Blum's own PDFs before the asserts were written. It caught that Blum's 2022 and 2025 sheets changed the 563H box height to opening minus 21 mm (7 mm top gap), that the rear notch is measured from the inside face of the drawer side, that the 13 mm recess runs to the underside of the bottom, and that the 563H locking devices are the T51.1901 family (T51.1700.04 is for 554H).
- Probe asserts caught my own mistake: the "wood between bore and groove" probe failed because I had the box x origin sign flipped in the probe, not because the geometry was wrong. Compute probe positions from the solids' bounding boxes, not from re-derived arithmetic.
- SUBSET env var in the model to export partial STLs (case, one front, one drawer, no cushion) made the matplotlib renders readable at this size.

## Decisions worth reusing

- Undermount drawer back in 3/4 stock with a 3/16 bottom groove: Blum's hook bore is 10 mm deep into the rear face at 24 mm up, right behind a 1/2 in bottom's groove. 18 mm minus 4.76 leaves 3.2 mm of wood past the bore; with a 1/4 groove it is 1.65 mm, too thin.
- 3/4 box front too: the T51.1901 locking devices screw into the box front below the bottom, and Blum names sub-front splitting as a failure mode.
- Frame-and-panel drawer front with a tongue-and-groove bit set: stiles grooved through, rails grooved plus stub tenons from the same cutter, plywood panel with a tongue all round glued in. The tenon end shows on the stile top; Brian accepted that.
- When the drawer box top sits above where a front stretcher would go, use a nailer on edge at the top back (figure-8s for the top, wall screws through it) and pocket screws into the top at the front. No front stretcher.
- Scribe strips wide enough to cover the end panels' front edges (1 in scribe plus the ply) are easier to attach than a 1 in strip hanging past the panel.

## Tooling notes

- Assembly steps as viewer screenshots: keep one STEPS list (file stem, title, instance prefixes, text) in `assembly_shots.py` and import it in the page builder, so the pictures and the words cannot drift. Parts already in place go pale grey, new parts keep their wood colors. Park the mouse with `xdotool mousemove 2 2` before each capture; the viewer tints the face under the pointer blue.

- The OCP viewer screenshot only works with the GPU Chrome tab open; `scripts/cad-viewer.sh` opens it. `pgrep -f cad-viewer-chrome` matches the pgrep command's own shell line, so check with `curl` plus a look at the screenshot result instead.
- `cutlist.csv` rounds mm to 0.1, so a part at a 1/32 rounding edge can print differently in `cutlist.md` and the page. Set nominal constants (the 1/4 back is 6.35 in the model) so derived lengths land on clean fractions.

- PDF of the shop page: headless Chrome `--print-to-pdf --no-pdf-header-footer` with an `@media print` block in the page. Wrap each group heading and its first row in one `break-inside: avoid` block, or a page break strands the heading; cap drawing heights (3.6 in) so two rows fit a page; hide the tick boxes and tap captions.

## Not yet measured

Nothing is cut. Record actual ply thicknesses, the alcove's three widths, and the drawer fit against Blum's rules here when the bench is built.
