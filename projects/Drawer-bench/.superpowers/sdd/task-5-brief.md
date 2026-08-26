### Task 5: Drawer fronts

**Files:**
- Modify: `projects/Drawer-bench/drawer_bench.py` (insert after the Task 4 block)

**Interfaces:**
- Consumes: `_box, PARTS, INST, X0, XR, Y0, POST, REV_SIDE, OPEN_W, FRONT_SETBACK, FRONT_T, FLOOR_GAP, FRONT_BOT_H, FRONT_TOP_H, REV_MID, REV_TOP, REV_MID_Z0, RAIL_Y0, POST_H`.
- Produces: `front_bot, front_top, FRONT_X0, FRONT_W, FRONT_Y0, FRONT_TOP_Z0`.

- [ ] **Step 1: Add the fronts**

```python
# --- Parts: drawer fronts (continuous soft maple, modeled blank) -------------
# FRONT_SETBACK behind the post faces, REV_SIDE to each post, REV_MID between
# them, FLOOR_GAP below, REV_TOP under the top. Their backs land exactly on
# the frame plane, so the boxes start there.
FRONT_X0 = X0 + POST + REV_SIDE
FRONT_W = OPEN_W - 2 * REV_SIDE                 # 692.15
FRONT_Y0 = Y0 + FRONT_SETBACK
FRONT_TOP_Z0 = REV_MID_Z0 + REV_MID             # 314.325
front_bot = _box(FRONT_X0, FRONT_Y0, FLOOR_GAP, FRONT_W, FRONT_T, FRONT_BOT_H)
front_top = _box(FRONT_X0, FRONT_Y0, FRONT_TOP_Z0, FRONT_W, FRONT_T, FRONT_TOP_H)
PARTS.append({"name": "front_bot", "solid": front_bot, "qty": 1, "material": "soft maple",
              "notes": "grain along the length; screwed to the box from inside through "
                       "slotted holes (cross-grain 11-3/8 wide); pull undecided"})
PARTS.append({"name": "front_top", "solid": front_top, "qty": 1, "material": "soft maple",
              "notes": "grain along the length; screwed to the box from inside; pull undecided"})
INST += [("front_bot", front_bot), ("front_top", front_top)]

# Fronts plus reveals exactly fill the front zone
assert abs(FLOOR_GAP + FRONT_BOT_H + REV_MID + FRONT_TOP_H + REV_TOP - POST_H) < 1e-6
_fb, _ft = front_bot.bounding_box(), front_top.bounding_box()
assert abs(_fb.min.Z - FLOOR_GAP) < 1e-6
assert abs(_ft.min.Z - _fb.max.Z - REV_MID) < 1e-6
assert abs(POST_H - _ft.max.Z - REV_TOP) < 1e-6
assert abs(_fb.min.Y - Y0 - FRONT_SETBACK) < 1e-6
assert abs(_fb.max.Y - RAIL_Y0) < 1e-6                       # back face on the frame plane
assert abs(_fb.min.X - (X0 + POST) - REV_SIDE) < 1e-6
assert abs((XR - POST) - _fb.max.X - REV_SIDE) < 1e-6
```

- [ ] **Step 2: Extend the assembly, run, render**

Add `+ front_bot + front_top` to `assembly`. Run with output `$SCRATCH/db-t5-fronts.png`. Expected `OK  parts: [..., 'front_bot', 'front_top']`. View the PNG (front view): two fronts between the posts, the top one about half the height of the bottom one, thin reveals to the posts and between them, a visible gap at the floor; in the right view the fronts sit 6.35 behind the post faces and the rails 19.05 behind the fronts.

---

