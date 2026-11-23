---
name: guitar-neck-rest-plan
description: Build plan for the printed guitar neck rest, from the approved spec to a verified one-plate Bambu 3MF
type: plan
status: done 2026-11-23 (executed inline; not printed)
created: 2026-11-23
tags: [project, 3d-print, guitar, bench-tool, plan]
---

# Guitar Neck Rest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Turn the approved design ([[2026-11-23-guitar-neck-rest-design]]) into a real model, an STL and one verified Bambu 3MF.

**Architecture:** One standalone OpenSCAD source holds every dimension and builds the body as slices across the neck joined by hulls, the construction already proven in `pipeline/concepts.scad` (`c1r_body()`). A Python build script exports the STL, asserts the geometry on the mesh and draws the check pictures. A second script makes the Bambu project 3MF and proves it with a real slice.

**Tech Stack:** OpenSCAD (Manifold backend), Python 3.12 in the vault `.venv` (trimesh, shapely, matplotlib), Bambu Studio CLI through the vault's flatten and graft-slice recipe.

**Backend note (3d-model skill):** OpenSCAD instead of build123d, because the roundovers are a slice-and-hull construction; a kernel fillet creases where the 1/16 in rim meets the 1/4 in cradle end. The skill's discipline is unchanged: one feature at a time, a render after each, asserts in the build, printability check, STL and 3MF.

## Global Constraints

- Sizes exactly as the spec's body table; mm in the source, inches in anything Brian reads.
- Change of 2026-11-23, after the spec: the two tread strips are replaced by ONE recessed channel for Brian's 2 in wide rubber grip tape, centred on the bottom curve (his words: "Create a 2 in wide recessed channel in the bottom of the stand for me to put the grip tape in").
- PLA, 0.6 nozzle, 0.30 mm layers, 2 walls, 15% infill, no supports, printed on one face.
- 2-loop skirt, no brim, Textured PEI Plate at 65 C, seam at the back (the cradle side), never on the rocking curve.
- One 3MF, one plate, one object. No commit unless Brian asks.
- Heavy jobs (slices) run one at a time inside the memory-capped systemd scope.

## Files

- Create `projects/Guitar-neck-rest/neck_rest.scad`: the model. `MODE="part"` gives the body in print orientation; `MODE="scene"` gives the body standing with pad and tape for pictures.
- Create `projects/Guitar-neck-rest/pipeline/build.py`: STL export, mesh asserts, renders, section drawings, `build-report.json`.
- Create `projects/Guitar-neck-rest/pipeline/make_print_3mf.py`: `guitar-neck-rest.3mf`, round trip, slice, G-code checks, `3mf-report.json`.
- Modify the spec, `brief.md`, the page builder (`pipeline/options_page.py`), the handoff and the memory note.
- Create `knowledge/learnings/guitar-neck-rest.md`.

---

### Task 1: Body outline, cradle and roundovers

**Files:** create `neck_rest.scad`, `pipeline/build.py`.

**Produces:** `guitar-neck-rest.stl` in the print frame: x along the neck, y up the standing rocker (0 at the bench, cradle at the top), z across the neck from 0 (the plate) to 80.

- [x] Port `c_outline`, `c1r_side`, `c1r_slab`, `c1r_half`, the window and its flare into `neck_rest.scad` with their own constants (`HIGH 95.25`, `CW 64`, `CR 45.3`, `PAD_T 1.6`, `RR 130`, `YC 80`, `XC_TOP 110`, `C_HALF 75`, `C_FR 12`, `R_END 6.35`, `R_EDGE 1.5875`).
- [x] `build.py` exports the STL and asserts: watertight, one body, min z 0, size 148.7 x 108.5 x 80.0 mm within 0.2.
- [x] Ray checks on the centre plane (z = 40): cradle floor at 93.65 mm (95.25 less the 1.6 seat); the middle of the 1/4 in arc at the height the formula gives; both within 0.05.
- [x] Render the body and one cradle end; look at both before going on.

### Task 2: Grip tape channel

**Files:** modify `neck_rest.scad`, `pipeline/build.py`.

- [x] Add the channel: centred, 2 in plus 0.4 mm each side wide (51.6 mm), 0.5 mm deep, closed ends, long enough for a 5-1/2 in tape with 1/16 in at each end.
- [x] Ray checks from below: at the middle of the curve the bottom is 0.5 mm up inside the channel and 0 on the lips; the lips are (80 - 51.6) / 2 = 14.2 mm wide.
- [x] Render the underside with the tape drawn in; look at it.

### Task 3: Fit and printability checks

**Files:** modify `pipeline/build.py`.

- [x] Pad: 2-3/4 x 4-1/8 in of 1/16 in cork sits inside the level floor and clear of the rim roundovers (assert both margins are positive, report them).
- [x] Neck clearance: with the bass and guitar stand-in necks lying on the pad, the gap to the printed body is at least the pad thickness everywhere under the neck (rays from the neck's underside).
- [x] Overhangs on the mesh in the print frame: list the area steeper than 47 degrees from upright, split into the plate-side roundover band, the channel's down-facing wall and anything else; assert "anything else" is zero.
- [x] Section drawings from the mesh itself: the cradle end on the centre plane with the pad, and the cross-section across the neck with pad and tape.
- [x] Write `build-report.json`.

### Task 4: 3MF and slice proof

**Files:** create `pipeline/make_print_3mf.py`.

- [x] Flattened presets (machine `Bambu Lab X2D 0.6 nozzle`, process `0.30mm Standard @BBL X2D 0.6 nozzle`, filament `Bambu PLA Basic @BBL X2D 0.6 nozzle`) with the overrides; CLI export; write the overrides into `project_settings.config` and `different_settings_to_system`; name the object.
- [x] CLI round trip keeps the overrides.
- [x] Real slice in the capped scope: rc 0, X2D start G-code present, settings lines present, a skirt and no brim, bed 65 C, top layer at 80 mm, every outer-wall seam in the back strip of the part (never on the curve), grams and time.
- [x] Write `3mf-report.json`.

### Task 5: Records

- [x] Spec: the channel replaces the tread strips; plan status done.
- [x] Page: Version 6 with the final model's pictures and numbers.
- [x] `brief.md`, handoff, memory, `knowledge/learnings/guitar-neck-rest.md`.
