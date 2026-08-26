# Task 2 report: Side panels, back panel, rear top rail

## What I implemented

Inserted the brief's Step 1 block verbatim into `projects/Drawer-bench/drawer_bench.py`, immediately
before the `# --- assembly` marker (after the last post assert, `assert abs(post_rl.bounding_box().max.Y - YB) < 1e-6`).
The block:

- Computes `SIDE_Y0`, `SIDE_L` and creates `side_l` via `_box(...)`.
- Computes `BACK_X0`, `BACK_Y0` and creates `back` and `rail_rear` via `_box(...)`.
- Mirrors `side_l` to `side_r`, appends three `PARTS` entries (`side`, `back`, `rail_rear`), and
  extends `INST` with all four new placed instances.
- Runs four `assert_housed(...)` checks (side into front-left post, side into rear-left post, back
  into rear-left post, rear rail into rear-left post) plus five geometry asserts (side outer face
  setback, back rear-face setback, side top flush with post top, back top flush with rail bottom,
  rail top flush with post top).

Per Step 2, changed the assembly line from:
```python
assembly = post_fl + post_fr + post_rl + post_rr
```
to:
```python
assembly = (post_fl + post_fr + post_rl + post_rr
            + side_l + side_r + back + rail_rear)
```

Kept the `side_l = _box(...)` and `back = _box(...)` creation lines separate from the
`mirror_x`/registry lines, per the brief's note that Task 4 will insert groove cuts right after
each creation line.

No other lines in the file were touched.

## Exact run command and full output (verbatim)

```
SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad
TMP_STL=$SCRATCH/db.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py && .venv/bin/python scripts/render_stl.py $SCRATCH/db.stl $SCRATCH/db-t2-panels.png
```

Output:
```
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear']
rendered 4 views -> /tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t2-panels.png
```

This matches the brief's expected `OK` line exactly. No traceback, no assert failures on the first
run.

## PNG

Path: `/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t2-panels.png`

What I saw (4-view render: iso, front, top, right):

- **iso**: four chamfered posts, a full-height panel on each side (left and right), a shorter panel
  at the rear with a rail sitting directly on top of it flush with the post tops, and the front
  completely open (no panel, no rail) between the two front posts. All three panels sit visibly
  recessed inward from the post outer faces.
- **front** (X-Z, looking along Y): only the front-left and front-right posts are visible; nothing
  spans between them, confirming the front is open. (The diagonal line across the frame is the STL
  triangulation diagonal of the flat side panel behind, not a real feature.)
- **right** (Y-Z, looking along X): shows a side panel running from just above the floor to the top
  of the posts, with a visible gap between the panel's bottom edge and the floor (Z=0 to
  Z=GROOVE_STOP=38.1), matching the "38.1 mm gap under every panel" expectation.
- **top** (X-Y, looking down): shows the four post corners connected across the back by the rear
  rail (topmost solid at that Z), and nothing across the front, matching "front open."

This matches the brief's expected description: three panels recessed 12.7 mm from the post faces,
sides full height, back shorter with the rail on top, front open, 38.1 mm gap under every panel.
No geometry fixes were needed.

## Files changed

- `/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench/drawer_bench.py` (only file
  touched; Task 1 content otherwise unmodified except the `assembly = ...` line per Step 2).

## Self-review

- All Interfaces "Produces" names present exactly: `side_l, side_r, back, rail_rear, SIDE_Y0,
  SIDE_L, BACK_X0, BACK_Y0` (verified by regex search of the file).
- Nothing extra added beyond the brief's Step 1 block and the Step 2 assembly-line edit.
- Task 1 code (constants, helpers, posts, post asserts, global checks, exports, SHOW tail, final
  `print`) is byte-for-byte unchanged apart from the `assembly = ...` expression.
- `side_l = _box(...)` and `back = _box(...)` creation lines are kept separate from the
  `mirror_x`/`PARTS.append`/`INST +=` lines, as required for Task 4's later groove-cut insertion.
- All four `assert_housed` calls and all five geometry asserts passed on the first run; none were
  loosened.

## Concerns

None. The run was clean on the first attempt: no assert failures, no traceback, output matched the
brief's expected `OK` line verbatim, and the rendered PNG matched the expected visual description
in every particular (panel recess, side full height, back shorter with rail on top, front open,
38.1 mm floor gap).
