### Task 9: Documentation and handoff

**Files:**
- Modify: `projects/Drawer-bench/design.md` (add a "Resolutions from the CAD" section, update status)
- Modify: `projects/Drawer-bench/brief.md` (add a "Build log" section with paths and the buildability verdicts, update status)
- Create: `knowledge/learnings/drawer-bench.md` (design-phase retrospective, Obsidian frontmatter, wikilinks)
- Modify: `projects/Drawer-bench/plan.md` status to `done`
- Create: `projects/Drawer-bench/.claude/context-check/last-handoff.md`

- [ ] **Step 1: design.md**

Append this section and change `status:` to `cad-built, provisional dimensions`:
```markdown
## Resolutions from the CAD (2026-08-24)

Three places where the section text did not close numerically; the model
uses these and they are open for Brian's review:

- Top drawer opening is 4-1/2 in, not 4-5/8 (18-1/4 post minus 1 in top
  rail minus mid rail top at 12-3/4). With the 8 mm slide standoff and
  20 mm tilt clearance the boxes are 3-1/4 in (top) and 8-1/4 in
  (bottom) tall, not 3-3/4 / 8-1/2. Top box interior height is about
  58 mm; if that is too shallow, drop the mid rail to 3/4 in or move
  the reveal up.
- The front-frame groove line in the front posts stops at the floor gap
  (3/4 in), not 1-1/2 in, so the bottom rail's tenon is housed; the rail
  sits on the groove's stopped end. Panel grooves keep the 1-1/2 in stop.
- The rear top rail (1-1/2 in tall) is tenoned into the back groove line
  and the back panel runs from the groove stop to the rail's underside
  (15-1/4 in tall, not 16-3/4).
- Rails are milled to the measured ply thickness so their stub tenons
  are the full section in the same 3/8 in grooves.
- Bottom panel: the rail "groove" is a 1/4 x 1/2 rabbet on the rail's
  rear-top edge (its top coincides with the rail top); the panel is
  notched 51.85 x 39.15 (front) / 51.85 x 51.85 (rear) around the posts.
```

- [ ] **Step 2: brief.md**

Change `status:` to `cad-built-provisional` and append:
```markdown
## Build log (2026-08-24)

- CAD: `projects/Drawer-bench/drawer_bench.py` (build123d, parametric;
  `EXPORT=1` regenerates `cutlist.md` / `cutlist.csv` /
  `drawer_bench.step`; `TMP_STL=<path>` for renders; `SHOW=reset|1`
  pushes to the OCP viewer on port 3939). Design in
  [[drawer-bench-design]], plan in [[drawer-bench-plan]].
- Deliverables: `cutlist.md`, `cutlist.csv`, `drawer_bench.step`,
  `images/final-4view.png`. All provisional: nothing is cut until the
  space, the Boos island and the plywood are measured.
- Buildability (furniture skill Phase 4): [paste the Task 8 Step 2
  verdicts, one bullet each].
- Viewer sign-off: [signed off by Brian on <date> | pending].
- Open for review: the CAD resolutions listed in design.md.
```

- [ ] **Step 3: knowledge/learnings/drawer-bench.md**

```markdown
---
name: drawer-bench-learnings
description: Design-phase retrospective for the maple post-and-panel drawer bench (CAD built, provisional dimensions)
date: 2026-08-24
status: design-only
---

# Drawer bench - retrospective (design phase)

Project: [[drawer-bench-brief]] / [[drawer-bench-design]] in
`projects/Drawer-bench/`. Designed and modeled, not built; update with
measured fits after the build.

## What worked

- Post-and-panel in build123d: chamfer the post's four vertical edges
  first, then cut the grooves; assert the post volume equals box minus
  chamfer prisms minus grooves. That one number proves the chamfers never
  reach a groove and the grooves are stopped where the constants say.
- `assert_housed(guest, host, probe)`: a probe box the size of the housed
  slice must be fully inside the guest, fully outside the host, and the
  two must not overlap. Reused for every panel, rail tenon and the bottom.
- A pairwise-intersection loop over every placed instance (25 solids,
  300 pairs) as the global no-overlap check; cheap enough to run every time.
- Writing the design as prose first exposed three numeric inconsistencies
  only when the CAD forced a value (drawer opening height, groove stop
  vs bottom rail tenon, rear rail vs back panel height). Record such
  resolutions in design.md, not only in the code.

## Decisions locked (promoted from the handoff)

- 36 x 24 is the TOP; posts inset by the overhang (footprint 33-1/2 x
  21-1/2, opening 27-1/2).
- 3 in posts, 3/8 chamfer, no taper; panels 1/2 in behind the post faces
  in 3/4 x 3/8 grooves stopped 1-1/2 in above the floor; front frame 1 in
  behind the post faces with 1 / 1 / 1-1/2 in rails; fronts 1/4 in behind
  the post faces, 5-3/4 over 11-3/8; 18 in undermount slides; 1/2 ply
  bottom with its top face 2-1/4 in above the floor.
- Pulls and finish out of scope until the build.

## Open items for the build

- Measure: the space, the Boos island (thickness, edge profile, overhang),
  actual 3/4 and 1/2 ply, the purchased slide spec. Re-run the file.
- Top drawer box is only about 58 mm deep inside; confirm that is useful.
- Decide pulls (routed finger pull vs hardware) and finish.
- After the build: promote measured kerf, ply thickness and undermount
  clearances into [[woodworking-stock]].
```

- [ ] **Step 4: Handoff**

Write `projects/Drawer-bench/.claude/context-check/last-handoff.md` with goal, current state (CAD built, exports written, review items), the "Decisions already locked" block from design.md plus the CAD resolutions, and the next action (Brian reviews the resolutions and measures; then re-run with `EXPORT=1`).

---

## Self-review

- Spec coverage: Structure (Tasks 1-4), Front (5), Drawers (6), Top (7), Wood movement (notes + Task 8 check), every assert in design.md's "What the CAD asserts" list maps to a Task 1-7 assert, Deliverables (8), docs (9). Chamfer-vs-groove is proven by the post volume assert rather than a per-edge probe.
- Placeholders: none; the only bracketed text is in brief.md templates that Task 9 fills from Task 8 output.
- Type consistency: `assert_housed(guest, host, probe)`, `part(name)`, `vol(shape)`, `mirror_x(solid)`, `INST` as `(name, solid)` tuples, `make_drawer(box_h, z0, sfx)` are used with the same signatures throughout.
