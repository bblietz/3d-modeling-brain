# Task 7 report: Top and envelope

## What was implemented

Applied both steps from the brief verbatim to `projects/Drawer-bench/drawer_bench.py`.

**Step 1** — inserted the top block after the Task 6 drawer block (after the
`assert BACK_Y0 - BOX_Y0 - SLIDE_LEN >= UM_REAR_CLEAR` line) and before
`# --- assembly`: defines `top = _box(0, 0, POST_H, TOP_W, TOP_D, TOP_T)`,
appends its `PARTS` entry and `INST` tuple, and the two envelope asserts on
`top` itself (X alignment with `X0 - OH`, top face at `H`).

**Step 2** — replaced the old multi-line `assembly = (...)` expression (which
ended at `drawer_bot + drawer_top`) with the brief's version that folds in
`+ top`, and added the five envelope asserts directly after it (bounding-box
size == `TOP_W`/`TOP_D`/`H`, `bb.min.Z == 0`, `len(INST) == 25`) — all placed
before the untouched `# --- global checks` block.

No other lines were touched: global checks, exports, SHOW tail, and the
final `print("OK  parts:", ...)` are exactly as they were after Task 6.

## Run command and output (verbatim)

```
$ SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad
$ time TMP_STL=$SCRATCH/db.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom', 'front_bot', 'front_top', 'drawer_side_bot', 'drawer_end_bot', 'drawer_bottom_bot', 'drawer_side_top', 'drawer_end_top', 'drawer_bottom_top', 'top']

real	0m4.205s
user	0m6.629s
sys	0m0.324s
```

Render:

```
$ .venv/bin/python scripts/render_stl.py $SCRATCH/db.stl $SCRATCH/db-t7-full.png
rendered 4 views -> $SCRATCH/db-t7-full.png
```

No traceback, no assert failure. Runtime (4.2s wall) is well under a minute,
consistent with the brief's note that the 300 pairwise overlap checks (25
choose 2 = 300 instances now, up from 276) dominate cost.

## PNG

Path: `/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t7-full.png`

What I saw across the four views:
- **iso**: a complete bench — four chamfered posts, side/back panels, front
  frame rails, two drawer fronts, and a slab top sitting on top with a
  visible overhang past the post faces on the near and side edges.
- **front**: top overhangs the front posts symmetrically left/right; legs
  run down to the floor line (Z = 0) with no gap and nothing protruding
  below it.
- **right**: same — top overhangs front and rear posts symmetrically, legs
  flush to the floor.
- **top** (plan view): a clean rectangle (the top slab) with no other
  geometry visible outside its silhouette, i.e. nothing wider than the top.

This matches the brief's expected description: complete bench, top
overhanging the posts equally on all sides, nothing above the top or below
the floor. (The known matplotlib depth-sort artifacts on interior parts —
visible as stray diagonal lines through the drawer/panel area in the iso and
front views — are cosmetic render-only issues, not geometry problems; the
envelope is what was checked here and it is correct.)

## Files changed

- `/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench/drawer_bench.py`
  — only the region between the end of the Task 6 block and
  `# --- global checks`: added the `top` part block, replaced the `assembly`
  expression, added the envelope asserts.

## Self-review

- `top` exists: yes, `_box(0, 0, POST_H, TOP_W, TOP_D, TOP_T)`.
- `assembly` contains all 17 solids as listed: yes —
  `post_fl + post_fr + post_rl + post_rr + side_l + side_r + back +
  rail_rear + rail_top + rail_mid + rail_bot + bottom + front_bot +
  front_top + drawer_bot + drawer_top + top` (17 terms, matches brief
  exactly).
- `len(INST) == 25`: asserted in-file and passed (24 from Tasks 1-6 + 1 for
  `top`).
- OK line lists 18 registry names: confirmed in the run output above
  (17 prior + `top`).
- Nothing extra: no additional parts, asserts, or prints were added beyond
  what Steps 1-2 specify.
- Earlier code untouched apart from the assembly replacement: confirmed by
  reading the file — the Task 6 block, global checks, exports, SHOW tail,
  and final print are byte-identical to their pre-Task-7 form; only the
  `assembly = (...)` line was replaced and the new `top` block plus envelope
  asserts were inserted between it and the Task 6 code.

## Concerns

None. The task ran clean on the first attempt: no failed asserts, no
loosened checks, geometry matches the expected envelope description.
