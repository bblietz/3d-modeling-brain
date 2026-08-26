### Task 4: Bottom panel and its grooves

**Files:**
- Modify: `projects/Drawer-bench/drawer_bench.py` (three insertions into Task 2/3 code, one new block)

**Interfaces:**
- Consumes: everything above plus `T12, BOT_GROOVE, BOT_TOP_Z, OPEN_W, FOOT_W, FOOT_D, SIDE_Y0, SIDE_L, BACK_X0, BACK_Y0, RAIL_X0, RAIL_Y0`.
- Produces: `bottom, BOT_Z0, BOT_X0, BOT_W, BOT_Y0, BOT_Y1`; groove cuts on `side_l`, `back`, `rail_bot`.

- [ ] **Step 1: Define the bottom's Z and groove lines right after the derived constants** (append to the `# --- Derived` block in Task 1):

```python
BOT_Z0 = BOT_TOP_Z - T12                     # 45.15 bottom panel underside
BOT_X0 = X0 + SETBACK + T18 - BOT_GROOVE     # into the side-panel groove
BOT_W = FOOT_W - 2 * (SETBACK + T18 - BOT_GROOVE)   # 802.2
```

- [ ] **Step 2: Cut the bottom grooves into the side panel and back panel** (insert directly after `side_l = _box(...)` and `back = _box(...)` in Task 2; grooves are stopped at the post faces so the housed probes stay full; they may be run through in the shop, the ends hide inside the post grooves):

```python
side_l -= _box(BOT_X0, Y0 + POST, BOT_Z0, BOT_GROOVE + 1, FOOT_D - 2 * POST, T12)
```
```python
back -= _box(X0 + POST, BACK_Y0 - 1, BOT_Z0, OPEN_W, BOT_GROOVE + 1, T12)
```

- [ ] **Step 3: Rabbet the bottom rail** (insert directly after `rail_bot = _box(...)` in Task 3; the groove's top coincides with the rail's top, so it is a rabbet on the rear-top edge, stopped at the tenon shoulders):

```python
rail_bot -= _box(X0 + POST, RAIL_Y0 + RAIL_T - BOT_GROOVE, BOT_Z0, OPEN_W, BOT_GROOVE + 1, T12 + 1)
```
Update the `rail_bot` registry notes to: `"stub tenons 3/8 each end, full section; 1/4 x 1/2 rabbet on the rear-top edge between the shoulders for the bottom panel"`.

- [ ] **Step 4: Add the bottom panel block** (after the Task 3 block):

```python
# --- Part: bottom (1/2 ply dust panel / slide-bracket landing) ---------------
# Between the posts it spans into the side-panel grooves; ahead of and behind
# the posts it narrows to the opening width and runs into the bottom-rail
# rabbet and the back-panel groove. So: a rectangle with four corner notches
# the size of the post footprint minus the groove reach.
BOT_Y0 = RAIL_Y0 + RAIL_T - BOT_GROOVE       # into the rail rabbet
BOT_Y1 = BACK_Y0 + BOT_GROOVE                # into the back groove
bottom = _box(BOT_X0, Y0 + POST, BOT_Z0, BOT_W, FOOT_D - 2 * POST, T12)
bottom += _box(X0 + POST, BOT_Y0, BOT_Z0, OPEN_W, Y0 + POST - BOT_Y0, T12)
bottom += _box(X0 + POST, YB - POST, BOT_Z0, OPEN_W, BOT_Y1 - (YB - POST), T12)
PARTS.append({"name": "bottom", "solid": bottom, "qty": 1, "material": "ply 12mm",
              "notes": "notch the four corners 51.85 wide x 39.15 (front) / 51.85 (rear) "
                       "for the posts; edges in the side/back grooves and the rail rabbet"})
INST.append(("bottom", bottom))

assert len(bottom.solids()) == 1
assert abs(bottom.bounding_box().max.Z - BOT_TOP_Z) < 1e-6
assert_housed(bottom, side_l, _box(BOT_X0, Y0 + POST, BOT_Z0, BOT_GROOVE, FOOT_D - 2 * POST, T12))
assert_housed(bottom, back, _box(X0 + POST, BACK_Y0, BOT_Z0, OPEN_W, BOT_GROOVE, T12))
assert_housed(bottom, rail_bot, _box(X0 + POST, BOT_Y0, BOT_Z0, OPEN_W, BOT_GROOVE, T12))
```
- [ ] **Step 5: Extend the assembly and run**

Add `+ bottom` to `assembly`. Run with output `$SCRATCH/db-t4-bottom.png`; also print the notch numbers once:
```bash
.venv/bin/python - <<'PY'
import runpy; g = runpy.run_path("projects/Drawer-bench/drawer_bench.py")
print("notch w", g["X0"] + g["POST"] - g["BOT_X0"], "front d", g["Y0"] + g["POST"] - g["BOT_Y0"], "rear d", g["BOT_Y1"] - (g["YB"] - g["POST"]))
PY
```
Expected: `notch w 51.85 front d 39.15 rear d 51.85` and `OK  parts: [..., 'bottom']`. View the PNG (top view): the bottom panel fills the footprint between the panels with square notches at the four posts.

---

