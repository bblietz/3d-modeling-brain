# Task 3 Report: Front frame rails (top, mid, bottom)

## What was implemented

Inserted the brief's Step 1 block verbatim into `projects/Drawer-bench/drawer_bench.py`,
immediately after the Task 2 block (side panels / back panel / rear rail) and immediately
before the `# --- assembly` marker. The block:

- Defines `RAIL_X0`, `RAIL_Y0`, `REV_MID_Z0`, `RAIL_MID_Z0`.
- Creates `rail_top`, `rail_mid`, `rail_bot` via `_box(...)` (the `rail_bot = _box(...)` line
  kept separate from the registry lines, per instructions, for Task 4's rabbet cut).
- Appends the three parts to `PARTS` and their instances to `INST`.
- Runs `assert_housed` for each rail against `post_fl`'s front-frame groove, plus four
  geometric asserts (bottom rail top face at `BOT_TOP_Z`, top rail top flush with `POST_H`,
  top rail set back `FRAME_SETBACK`, mid rail centered on the reveal).

Applied Step 2: extended the `assembly = (...)` expression to add
`+ rail_top + rail_mid + rail_bot`.

No other lines in the file were touched.

## Exact run command and full output (verbatim)

```
SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad
TMP_STL=$SCRATCH/db.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py && .venv/bin/python scripts/render_stl.py $SCRATCH/db.stl $SCRATCH/db-t3-rails.png
```

Output:

```
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot']
rendered 4 views -> /tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t3-rails.png
```

No traceback. Matches the brief's expected `OK  parts: [... 'rail_top', 'rail_mid', 'rail_bot']`.

## PNG and what was seen

Primary PNG: `/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t3-rails.png`
(4-view: iso, front, top, right).

The default 4-view render is small enough that the thin rail bands are hard to confirm by
eye alone, so I additionally rendered two zoomed custom views (same STL, not part of the
required workflow, purely for my own verification) to confirm the geometry precisely:

- `$SCRATCH/db-t3-zoom-top.png` (zoomed top view of the front-left post/rail corner): shows
  the front-left post's chamfered square footprint, the side panel running back in Y, and a
  horizontal band (the front rail) starting right at the post's inner edge and running off to
  the right at Y ~57 to ~75 -- confirming the rail is set back exactly `FRAME_SETBACK` = 25.4 mm
  behind the post's front face (post front face at Y=31.75, rail front face at Y=57.15).
- `$SCRATCH/db-t3-zoom-front.png` (zoomed front elevation): shows three horizontal rails
  spanning the full width between the two front posts:
  - bottom rail from Z~19 to Z~57 (matches `FLOOR_GAP` = 19.05 mm above the floor, height
    `RAIL_BOT_H` = 38.1 mm, top face at `BOT_TOP_Z` = 57.15 mm),
  - mid rail from Z~298 to Z~324 (matches `RAIL_MID_Z0` = 298.45, height 25.4 mm, centered on
    the reveal between the two drawer fronts),
  - top rail from Z~438 to Z~463.55, flush with the post tops (`POST_H` = 463.55).

This matches the brief's expected description exactly: three horizontal rails between the
front posts, bottom one starting 19.05 above the floor, mid one below the top third, top one
flush with the post tops, all set back 25.4 from the post faces in plan view.

The `assert_housed` and geometric asserts in the inserted block also passed (no AssertionError),
which independently confirms the numeric placement (tenon housing, `BOT_TOP_Z`, `POST_H` flush,
`FRAME_SETBACK`, reveal centering) beyond the visual check.

## Files changed

- `/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench/drawer_bench.py`
  (only change: inserted Task 3 block before `# --- assembly`; extended the `assembly = (...)`
  expression with `+ rail_top + rail_mid + rail_bot`).

## Self-review

- Interfaces block names all present and exact: `rail_top`, `rail_mid`, `rail_bot`,
  `RAIL_X0`, `RAIL_Y0`, `REV_MID_Z0`, `RAIL_MID_Z0`. Confirmed by grep and by the passing
  run (no `NameError`).
- Nothing extra added beyond the brief's Step 1 block and the Step 2 assembly edit.
- Earlier code (posts, side panels, back panel, rear rail, helpers, constants) untouched --
  the edit was applied as two exact string replacements (the assembly marker and the assembly
  expression), so no other line could have been altered. Diff is limited to the insertion plus
  the one-line assembly change.
- `rail_bot = _box(...)` left as a standalone statement, separate from the `PARTS.append` /
  `INST +=` lines, as required so Task 4 can insert a rabbet cut right after it.
- `PARTS` now has 8 entries, `INST` has 11 placed instances; the global overlap check
  (`vol(a & b) < 1e-3` for every pair in `INST`) passed for all pairs, so `rail_top`,
  `rail_mid`, `rail_bot` do not overlap any other placed part (including the front posts'
  grooves and each other).

## Concerns

None. Run is clean, all asserts pass, PNG matches the expected description exactly.
