# Task 4 report: Bottom panel and its grooves

## What I implemented

Made three insertions into existing Task 2/3 code and added one new block, per the brief, in `projects/Drawer-bench/drawer_bench.py`:

1. **Step 1** (lines 71-73): appended the three derived constants to the end of the `# --- Derived` block, right after `RAIL_L = OPEN_W + 2 * GROOVE_D`:
   ```python
   BOT_Z0 = BOT_TOP_Z - T12                     # 45.15 bottom panel underside
   BOT_X0 = X0 + SETBACK + T18 - BOT_GROOVE     # into the side-panel groove
   BOT_W = FOOT_W - 2 * (SETBACK + T18 - BOT_GROOVE)   # 802.2
   ```

2. **Step 2** (lines 168 and 172): inserted groove cuts directly after `side_l = _box(...)` and directly after `back = _box(...)`, both before `rail_rear = _box(...)`/`side_r = mirror_x(side_l)` and before any registry append:
   - Line 168: `side_l -= _box(BOT_X0, Y0 + POST, BOT_Z0, BOT_GROOVE + 1, FOOT_D - 2 * POST, T12)`
   - Line 172: `back -= _box(X0 + POST, BACK_Y0 - 1, BOT_Z0, OPEN_W, BOT_GROOVE + 1, T12)`

3. **Step 3** (line 207): inserted the rabbet cut directly after `rail_bot = _box(...)`:
   `rail_bot -= _box(X0 + POST, RAIL_Y0 + RAIL_T - BOT_GROOVE, BOT_Z0, OPEN_W, BOT_GROOVE + 1, T12 + 1)`
   and updated the `rail_bot` registry `notes` (lines 213-215) to: `"stub tenons 3/8 each end, full section; 1/4 x 1/2 rabbet on the rear-top edge between the shoulders for the bottom panel"`.

4. **Step 4** (lines 228-247): added the new bottom-panel block after the Task 3 block (rail asserts) and before `# --- assembly`, verbatim from the brief, including the plain-number `notes` string ("notch the four corners 51.85 wide x 39.15 (front) / 51.85 (rear) for the posts; ...").

5. **Step 5** (line 252): extended the assembly line to add `+ bottom`.

## Run commands and outputs (verbatim)

```
$ SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad && TMP_STL=$SCRATCH/db.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py && .venv/bin/python scripts/render_stl.py $SCRATCH/db.stl $SCRATCH/db-t4-bottom.png
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom']
rendered 4 views -> /tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t4-bottom.png
```

```
$ .venv/bin/python - <<'PY'
import runpy; g = runpy.run_path("projects/Drawer-bench/drawer_bench.py")
print("notch w", g["X0"] + g["POST"] - g["BOT_X0"], "front d", g["Y0"] + g["POST"] - g["BOT_Y0"], "rear d", g["BOT_Y1"] - (g["YB"] - g["POST"]))
PY
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom']
notch w 51.84999999999999 front d 39.14999999999998 rear d 51.849999999999966
```

Matches the expected `notch w 51.85 front d 39.15 rear d 51.85` (differences are float noise) and `OK  parts: [..., 'bottom']`.

## PNG

`/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t4-bottom.png`

Viewed all four panels (iso, front, top, right). Top view: a rectangular bottom panel fills the interior footprint between the side/back panels, with square notches cut at the four post corners, matching the brief's expected description exactly. Front/right/iso views: the bottom panel sits as a floor-like slab just under the bottom rail (consistent with BOT_TOP_Z = 57.15, BOT_Z0 = 45.15), does not protrude past the side or back panels, and shows no visible interference with posts or rails. The diagonal lines visible on some faces are STL box-triangulation artifacts from the renderer, not geometry defects.

## Files changed

- `/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench/drawer_bench.py` (283 lines total after edit)

## Self-review

- Interface names all present exactly as required: `bottom` (variable and PARTS/INST entries), `BOT_Z0`, `BOT_X0`, `BOT_W`, `BOT_Y0`, `BOT_Y1` — confirmed via grep.
- Three cuts sit exactly where specified: `side_l -=` right after `side_l = _box(...)` (line 168); `back -=` right after `back = _box(...)` and before `rail_rear = _box(...)` (line 172); `rail_bot -=` right after `rail_bot = _box(...)` and before the `PARTS.append` for rail_top (line 207).
- No extraneous code added beyond the brief's exact snippets.
- Only other change to pre-existing code: the `rail_bot` registry `notes` string (as instructed) and the assembly line's `+ bottom` addition. No other earlier lines were touched.
- All asserts (Task 1-3 existing asserts, plus the five new asserts in the Task 4 block: `len(bottom.solids()) == 1`, top-Z bounding box, and three `assert_housed` calls for side/back/rail_bot) passed — the script printed `OK` with no traceback.
- Global checks at the end of the file (one-solid-per-part, no pairwise INST overlaps) also passed since the run completed with `OK  parts: [...]` and no assertion errors.

## Concerns

None. All asserts passed on the first run, the notch-number probe matched the brief's expected values, and the PNG geometry matches the expected top-view description.
