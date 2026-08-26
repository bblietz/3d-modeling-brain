### Task 3: Front frame rails (top, mid, bottom)

**Files:**
- Modify: `projects/Drawer-bench/drawer_bench.py` (insert after the Task 2 block)

**Interfaces:**
- Consumes: `_box, assert_housed, PARTS, INST, post_fl, X0, Y0, POST, GROOVE_D, FRAME_SETBACK, RAIL_L, RAIL_T, RAIL_TOP_H, RAIL_MID_H, RAIL_BOT_H, POST_H, FLOOR_GAP, FRONT_BOT_H, REV_MID, BOT_TOP_Z`.
- Produces: `rail_top, rail_mid, rail_bot, RAIL_X0, RAIL_Y0, REV_MID_Z0, RAIL_MID_Z0`. Task 4 inserts a rabbet on `rail_bot` right after its creation.

- [ ] **Step 1: Add the rails**

```python
# --- Parts: front frame rails (hidden behind the drawer fronts) ------------
# Front face FRAME_SETBACK behind the post faces; stub tenons GROOVE_D each
# end into the front-post grooves. Top rail under the top, mid rail centered
# on the reveal between the fronts, bottom rail from the floor gap up (its
# top face is the bottom panel's top face).
RAIL_X0 = X0 + POST - GROOVE_D
RAIL_Y0 = Y0 + FRAME_SETBACK
REV_MID_Z0 = FLOOR_GAP + FRONT_BOT_H                  # 307.975 reveal bottom
RAIL_MID_Z0 = REV_MID_Z0 + REV_MID / 2 - RAIL_MID_H / 2   # 298.45
rail_top = _box(RAIL_X0, RAIL_Y0, POST_H - RAIL_TOP_H, RAIL_L, RAIL_T, RAIL_TOP_H)
rail_mid = _box(RAIL_X0, RAIL_Y0, RAIL_MID_Z0, RAIL_L, RAIL_T, RAIL_MID_H)
rail_bot = _box(RAIL_X0, RAIL_Y0, FLOOR_GAP, RAIL_L, RAIL_T, RAIL_BOT_H)

PARTS.append({"name": "rail_top", "solid": rail_top, "qty": 1, "material": "soft maple",
              "notes": "stub tenons 3/8 each end, full section"})
PARTS.append({"name": "rail_mid", "solid": rail_mid, "qty": 1, "material": "soft maple",
              "notes": "stub tenons 3/8 each end, full section; carries the top drawer slides"})
PARTS.append({"name": "rail_bot", "solid": rail_bot, "qty": 1, "material": "soft maple",
              "notes": "stub tenons 3/8 each end, full section"})
INST += [("rail_top", rail_top), ("rail_mid", rail_mid), ("rail_bot", rail_bot)]

for _r, _z, _h in ((rail_top, POST_H - RAIL_TOP_H, RAIL_TOP_H),
                   (rail_mid, RAIL_MID_Z0, RAIL_MID_H),
                   (rail_bot, FLOOR_GAP, RAIL_BOT_H)):
    assert_housed(_r, post_fl, _box(RAIL_X0, RAIL_Y0, _z, GROOVE_D, RAIL_T, _h))
assert abs(rail_bot.bounding_box().max.Z - BOT_TOP_Z) < 1e-6
assert abs(rail_top.bounding_box().max.Z - POST_H) < 1e-6
assert abs(rail_top.bounding_box().min.Y - Y0 - FRAME_SETBACK) < 1e-6
# mid rail is centered on the reveal
assert abs((RAIL_MID_Z0 + RAIL_MID_H / 2) - (REV_MID_Z0 + REV_MID / 2)) < 1e-6
```

- [ ] **Step 2: Extend the assembly**

```python
assembly = (post_fl + post_fr + post_rl + post_rr
            + side_l + side_r + back + rail_rear
            + rail_top + rail_mid + rail_bot)
```

- [ ] **Step 3: Run and render**

Output `$SCRATCH/db-t3-rails.png`. Expected `OK  parts: [... 'rail_top', 'rail_mid', 'rail_bot']`. View the PNG (front view): three horizontal rails between the front posts, the bottom one starting 19.05 above the floor, the mid one just below 1/3 height, the top one flush with the post tops; all set back 25.4 from the post faces in the top view.

---

