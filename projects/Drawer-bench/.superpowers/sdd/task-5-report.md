# Task 5 report: Drawer fronts

## What I implemented

Inserted the brief's Step 1 block verbatim into `projects/Drawer-bench/drawer_bench.py`, immediately
after the Task 4 bottom-panel asserts and immediately before `# --- assembly`. Extended the
`assembly = (...)` expression with `+ front_bot + front_top` (Step 2), leaving every other line of
that expression untouched.

New names produced, matching the Interfaces block exactly: `front_bot, front_top, FRONT_X0, FRONT_W,
FRONT_Y0, FRONT_TOP_Z0`. No other names added. All consumed names (`_box, PARTS, INST, X0, XR, Y0,
POST, REV_SIDE, OPEN_W, FRONT_SETBACK, FRONT_T, FLOOR_GAP, FRONT_BOT_H, FRONT_TOP_H, REV_MID, REV_TOP,
REV_MID_Z0, RAIL_Y0, POST_H`) already existed from Tasks 1-4.

## Run command and output (verbatim)

```
SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad
TMP_STL="$SCRATCH/db.stl" .venv/bin/python projects/Drawer-bench/drawer_bench.py && .venv/bin/python scripts/render_stl.py "$SCRATCH/db.stl" "$SCRATCH/db-t5-fronts.png"
```

Output:

```
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom', 'front_bot', 'front_top']
rendered 4 views -> /tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t5-fronts.png
```

No traceback. All in-file asserts (including the five new Step-1 asserts) passed, plus the existing
global per-part single-solid check and the pairwise no-overlap check over `INST` (now including
`front_bot`, `front_top`).

## PNG and what I saw

Primary PNG: `/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t5-fronts.png`
(4-view grid: iso, front, top, right).

In the full-assembly render the fronts are present and correctly located, but `scripts/render_stl.py`
uses matplotlib's `Poly3DCollection`, which has no true depth buffer — with 11 overlapping parts the
front/right views show stray diagonal lines from back-of-assembly faces bleeding through the front
faces. This is a known limitation of the render tool, not a geometry defect (Tasks 1-4's renders have
the same character). To confirm the geometry itself I additionally rendered two isolated views (not
part of the deliverable, scratch-only):

- `$SCRATCH/db-t5-focus2.png` — just `front_bot + front_top + post_fl + post_fr`, front and right
  orthographic views. Front view: both fronts visible between the two posts, with a clean thin
  horizontal reveal line visible at the front_bot/front_top boundary (~Z 308-314). Right view: a
  single vertical slab (the two fronts stacked, offset from the post) confirming they sit behind the
  post face, not flush with it.
- `$SCRATCH/db-t5-zoom-floor.png` — zoomed crop (X 0-250, Z -30 to 350) of the left post + both
  fronts. Clearly shows: a visible floor gap below `front_bot` (post touches Z=0, front starts above
  it), a thin visible reveal between the post and the front's left edge (REV_SIDE), and the thin
  reveal line between `front_bot` and `front_top`.

Numeric spot-checks (from the running module's namespace, matching the brief's expected right-view
description):
- `front_bot` Z-range: 19.05 - 307.975 (= FLOOR_GAP to FLOOR_GAP+FRONT_BOT_H); height 288.925 mm =
  11.375 in, matches `FRONT_BOT_H`.
- `front_top` Z-range: 314.325 - 460.375; height 146.05 mm = 5.75 in, matches `FRONT_TOP_H`; top
  reveal to `POST_H` (463.55) = 3.175 mm = REV_TOP.
- Reveal between fronts: 314.325 - 307.975 = 6.35 mm = REV_MID.
- Post front face at Y=31.75 (`Y0`); fronts' front face at Y=38.1, i.e. 6.35 mm (`FRONT_SETBACK`)
  behind the post face.
- Fronts' back face at Y=57.15, exactly equal to `RAIL_Y0` (57.15) — the front's back lands flush on
  the frame plane, so the rail's front face sits `FRONT_T` = 19.05 mm behind the front's own front
  face. This matches the brief's "rails 19.05 behind the fronts" and the code comment "back face on
  the frame plane."

This satisfies the brief's expected description: two fronts between the posts, top front about half
the height of the bottom (146.05 vs 288.925 mm, ratio ~0.5), thin reveals to the posts and between
the fronts, a visible gap at the floor, fronts 6.35 behind the post faces, rails 19.05 (one front
thickness) further back.

## Files changed

- `/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench/drawer_bench.py` — inserted the
  Step 1 block (drawer-front parts + asserts) after the Task 4 bottom-panel block and before
  `# --- assembly`; extended the `assembly` expression with `+ front_bot + front_top`. No other lines
  changed.

Scratch renders (not part of the deliverable, left in scratch for reference):
- `$SCRATCH/db.stl`, `$SCRATCH/db-t5-fronts.png` (the required deliverable render)
- `$SCRATCH/db-t5-focus.stl`/`.png`, `$SCRATCH/db-t5-focus2.stl`/`.png`, `$SCRATCH/db-t5-focus3.stl`,
  `$SCRATCH/db-t5-zoom-floor.png` (extra isolated/zoomed views used only to verify geometry visually
  given the full-assembly render's depth-sorting artifacts)

## Self-review

- Interfaces block names present exactly: `front_bot, front_top, FRONT_X0, FRONT_W, FRONT_Y0,
  FRONT_TOP_Z0` — all defined, nothing extra added.
- Code block matches the brief verbatim (comments, formula, asserts all copied as given).
- Earlier code (Tasks 1-4, helpers, constants) untouched; the only change outside the new block is the
  `assembly` line, extended exactly as instructed (`+ front_bot + front_top` appended).
- `PARTS` and `INST` updated consistently with the two new parts, following the same pattern as prior
  tasks.
- All asserts passed on the first run; no assert was loosened or removed.

## Concerns

- None regarding the geometry — all in-file asserts pass and my independent numeric/visual checks
  confirm every dimension in the brief. The only caveat is cosmetic: the standard 4-view full-assembly
  PNG (`db-t5-fronts.png`) is visually cluttered by matplotlib's lack of proper depth-sorting once 11
  parts overlap in the same view, so the front/right panes show some stray lines from far-side
  geometry. This is a pre-existing limitation of `scripts/render_stl.py` (present since Task 1-4's
  renders too), not something introduced by this task, and I did not touch that script per the
  constraint not to touch `scripts/`.
