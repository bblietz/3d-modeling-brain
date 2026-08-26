# Task 6 Report: Drawer boxes on undermount slides

## What I implemented

Inserted the brief's Step 1 block verbatim into `projects/Drawer-bench/drawer_bench.py`,
between the end of the Task 5 fronts block (after the last front-zone assert,
`assert abs((XR - POST) - _fb.max.X - REV_SIDE) < 1e-6`) and the
`# --- assembly` comment. The block adds:

- Constants `BOX_W, BOX_D, BOX_X0, BOX_Y0, END_LEN`.
- `make_drawer(box_h, z0, sfx)`: builds one drawer box (side, front/back "end",
  bottom) with DADO end rabbets and a DADO bottom groove at UM_RECESS, mirrors
  the side about X and the end about the box's mid-depth plane, registers five
  `PARTS` entries (`drawer_side_{sfx}` qty 2, `drawer_end_{sfx}` qty 2,
  `drawer_bottom_{sfx}` qty 1) and five `INST` entries via `INST.extend([...])`,
  and returns the visual compound `s + s_r + end + end_r + bot`.
- `BOX_BOT_Z0` (on the bottom rail) and `BOX_TOP_Z0` (on the mid rail);
  `drawer_bot = make_drawer(BOX_BOT_H, BOX_BOT_Z0, "bot")` and
  `drawer_top = make_drawer(BOX_TOP_H, BOX_TOP_Z0, "top")`.
- A probe loop asserting undermount geometry from the built solids (bottom
  recess, outer width, slide-length depth, tilt clearance to the rail above,
  hidden-behind-its-front in Z, box back-face starts at the front's back
  face) plus a rear-clearance assert against the back panel.

Applied Step 2: added `+ drawer_bot + drawer_top` to the `assembly` tuple
(only change to pre-existing code; nothing else touched).

## Exact commands and full output

```
$ SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad
$ TMP_STL="$SCRATCH/db.stl" .venv/bin/python projects/Drawer-bench/drawer_bench.py
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom', 'front_bot', 'front_top', 'drawer_side_bot', 'drawer_end_bot', 'drawer_bottom_bot', 'drawer_side_top', 'drawer_end_top', 'drawer_bottom_top']

$ .venv/bin/python scripts/render_stl.py "$SCRATCH/db.stl" "$SCRATCH/db-t6-drawers.png"
rendered 4 views -> $SCRATCH/db-t6-drawers.png
```

### Clearance probe (throwaway script, removed after use)

Script (`$SCRATCH/probe_t6.py`, deleted after running):

```python
import runpy
g = runpy.run_path(".../drawer_bench.py")
part = g["part"]
RAIL_MID_Z0, POST_H, RAIL_TOP_H = g["RAIL_MID_Z0"], g["POST_H"], g["RAIL_TOP_H"]
BACK_Y0, BOX_Y0, SLIDE_LEN = g["BACK_Y0"], g["BOX_Y0"], g["SLIDE_LEN"]
for sfx, above in (("bot", RAIL_MID_Z0), ("top", POST_H - RAIL_TOP_H)):
    sb = part(f"drawer_side_{sfx}").bounding_box()
    print(f"{sfx}: tilt clearance = {above - sb.max.Z}")
print(f"rear clearance = {BACK_Y0 - BOX_Y0 - SLIDE_LEN}")
```

Output:

```
OK  parts: [... same 17 parts as above ...]
bot: tilt clearance = 23.750000000000057
top: tilt clearance = 23.75
rear clearance = 32.7999999999999
```

Matches the brief's expected 23.75 / 23.75 / 32.8 (within float noise).

### Isolated cutaway render (standard 4-view was unreadable, as expected)

The standard 4-view render of the full assembly showed only the bench's outer
shell (posts/panels occlude the drawer boxes and fronts in matplotlib's
depth-sort), so per the task instructions I exported an isolated STL of
`drawer_bot + drawer_top + front_bot + front_top + rail_mid + rail_top + bottom`
via a throwaway `runpy.run_path` script (`$SCRATCH/isolate_t6.py`, deleted
after use) and rendered it separately.

```
$ .venv/bin/python "$SCRATCH/isolate_t6.py"
OK  parts: [... 17 parts ...]
exported isolated view
$ .venv/bin/python scripts/render_stl.py "$SCRATCH/db-t6-iso.stl" "$SCRATCH/db-t6-iso.png"
rendered 4 views -> $SCRATCH/db-t6-iso.png
```

## PNGs and what I saw

- `$SCRATCH/db-t6-drawers.png` (full assembly, 4-view): only the bench
  exterior (posts, panels, fronts) is legible; drawer boxes are occluded by
  outer panels in every view, as flagged as a known limitation in the task.
- `$SCRATCH/db-t6-iso.png` (isolated cutaway of fronts + drawer boxes + mid
  rail + top rail + bottom panel, 4-view): the iso and right views show two
  stacked boxes behind their fronts — a taller lower box sitting just above
  the bottom panel and a shorter upper box sitting just above where the mid
  rail plane is, both shorter in Z than their respective fronts and both
  terminating well short of the fronts' Y=0 (i.e., extending backward, away
  from the fronts, not through them). This matches the brief's expected
  description. The isolated STL geometry is also confirmed numerically by
  the in-model asserts (all passed) and by the clearance probe above.

## Files changed

- `/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench/drawer_bench.py`
  — inserted the Step 1 block verbatim (lines ~277-334) and added
  `+ drawer_bot + drawer_top` to the `assembly` tuple (line ~341). No other
  lines touched (diffed the pre-existing tail of the file after editing;
  identical apart from the assembly line).

No other files were modified. Cabinet-bench, scripts/, and
knowledge/woodworking-stock.md were not touched.

## Self-review

- Verified the inserted block is byte-identical to the brief's Step 1 code
  (diffed against the brief markdown; only difference was the markdown's
  closing ``` fence, which is not code).
- Confirmed by `grep` that all Interfaces "Produces" names exist exactly:
  `drawer_bot, drawer_top, BOX_W, BOX_D, BOX_X0, BOX_Y0, END_LEN,
  BOX_BOT_Z0, BOX_TOP_Z0`, and registry parts `drawer_side_bot,
  drawer_side_top, drawer_end_bot, drawer_end_top, drawer_bottom_bot,
  drawer_bottom_top`.
- Nothing extra was added beyond the brief's block plus the one assembly
  edit.
- Confirmed all Interfaces "Consumes" names (`_box, mirror_x, part, PARTS,
  INST, X0, POST, OPEN_W, UM_*, SLIDE_LEN, SLIDE_STANDOFF, T12, DADO,
  RAIL_Y0, BOT_TOP_Z, RAIL_MID_Z0, RAIL_MID_H, RAIL_TOP_H, POST_H, BACK_Y0,
  BOX_TOP_H, BOX_BOT_H, front_bot, front_top, TOP_W`) already existed in the
  Task 1-5 code before this edit.
- Read the file's tail (global checks, exports, final print) after editing
  and confirmed it is unchanged apart from the assembly line.
- All in-model asserts pass (probed undermount geometry: bottom recess,
  outer width, slide-length depth, tilt clearance, hidden-behind-front,
  starts-at-front's-back-face, rear clearance) plus the pre-existing global
  checks (one solid per PARTS entry, no INST pairwise overlaps — now
  covering the 10 new drawer-box INST entries added via `INST.extend`).

## Concerns

None. The run is clean (`OK` line, no traceback), clearances match the
brief's expected values exactly, all asserts pass, and the isolated render
matches the expected visual description. The full-assembly 4-view PNG
remains unreadable for the drawer boxes specifically due to matplotlib
depth-sorting against the outer panels (a known, pre-flagged limitation, not
a geometry defect) — the isolated cutaway render and the numeric probe/asserts
are the verification evidence for this task.
