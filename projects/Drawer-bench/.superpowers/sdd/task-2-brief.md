### Task 2: Side panels, back panel, rear top rail

**Files:**
- Modify: `projects/Drawer-bench/drawer_bench.py` (insert before `# --- assembly`)

**Interfaces:**
- Consumes: `_box, mirror_x, assert_housed, PARTS, INST, post_fl, post_rl, X0, Y0, YB, POST, GROOVE_D, SETBACK, T18, GROOVE_STOP, PANEL_H, BACK_H, RAIL_L, RAIL_T, RAIL_REAR_H, POST_H, FOOT_D`.
- Produces: `side_l, side_r, back, rail_rear, SIDE_Y0, SIDE_L, BACK_X0, BACK_Y0`. Task 4 later inserts groove cuts on `side_l` and `back` immediately after they are created, so keep their creation lines and the `mirror_x`/registry lines separate.

- [ ] **Step 1: Add the panels and rear rail**

Insert before `# --- assembly`:
```python
# --- Parts: side panels (qty 2), back panel, rear top rail -----------------
# Sides: outer face SETBACK behind the post face, housed GROOVE_D in each
# post, bottom edge on the groove stop, top edge flush with the post tops.
# Back: same, but stops under the rear top rail, which is tenoned into the
# same groove line and takes the figure-8 fasteners for the top.
SIDE_Y0 = Y0 + POST - GROOVE_D
SIDE_L = FOOT_D - 2 * POST + 2 * GROOVE_D            # 412.75
side_l = _box(X0 + SETBACK, SIDE_Y0, GROOVE_STOP, T18, SIDE_L, PANEL_H)
BACK_X0 = X0 + POST - GROOVE_D
BACK_Y0 = YB - SETBACK - T18
back = _box(BACK_X0, BACK_Y0, GROOVE_STOP, RAIL_L, T18, BACK_H)
rail_rear = _box(BACK_X0, BACK_Y0, POST_H - RAIL_REAR_H, RAIL_L, RAIL_T, RAIL_REAR_H)

side_r = mirror_x(side_l)
PARTS.append({"name": "side", "solid": side_l, "qty": 2, "material": "ply 18mm",
              "notes": "face grain vertical on the show face; housed 3/8 in each post"})
PARTS.append({"name": "back", "solid": back, "qty": 1, "material": "ply 18mm",
              "notes": "housed 3/8 in each post; top edge under the rear rail"})
PARTS.append({"name": "rail_rear", "solid": rail_rear, "qty": 1, "material": "soft maple",
              "notes": "stub tenons 3/8 each end are the full section; figure-8 fasteners on top"})
INST += [("side_l", side_l), ("side_r", side_r), ("back", back), ("rail_rear", rail_rear)]

# Housed edges probed from the solids
assert_housed(side_l, post_fl, _box(X0 + SETBACK, SIDE_Y0, GROOVE_STOP, T18, GROOVE_D, PANEL_H))
assert_housed(side_l, post_rl, _box(X0 + SETBACK, YB - POST, GROOVE_STOP, T18, GROOVE_D, PANEL_H))
assert_housed(back, post_rl, _box(BACK_X0, BACK_Y0, GROOVE_STOP, GROOVE_D, T18, BACK_H))
assert_housed(rail_rear, post_rl, _box(BACK_X0, BACK_Y0, POST_H - RAIL_REAR_H, GROOVE_D, RAIL_T, RAIL_REAR_H))
assert abs(side_l.bounding_box().min.X - X0 - SETBACK) < 1e-6
assert abs(YB - back.bounding_box().max.Y - SETBACK) < 1e-6
assert abs(side_l.bounding_box().max.Z - POST_H) < 1e-6
assert abs(back.bounding_box().max.Z - rail_rear.bounding_box().min.Z) < 1e-6
assert abs(rail_rear.bounding_box().max.Z - POST_H) < 1e-6
```

- [ ] **Step 2: Extend the assembly line**

Change `assembly = post_fl + post_fr + post_rl + post_rr` to:
```python
assembly = (post_fl + post_fr + post_rl + post_rr
            + side_l + side_r + back + rail_rear)
```

- [ ] **Step 3: Run and render**

Run the same command as Task 1 Step 5 with output `$SCRATCH/db-t2-panels.png`.
Expected: `OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear']`. View the PNG: three panels between the posts, each recessed 12.7 from the post faces, sides full height, back panel shorter with the rail on top of it, the front open, a 38.1 mm gap under every panel.

---

