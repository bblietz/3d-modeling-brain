### Task 7: Top and envelope

**Files:**
- Modify: `projects/Drawer-bench/drawer_bench.py` (insert after the Task 6 block; replace the `assembly` line)

**Interfaces:**
- Consumes: `_box, PARTS, INST, TOP_W, TOP_D, TOP_T, POST_H, H, OH, X0`.
- Produces: `top`; final `assembly`.

- [ ] **Step 1: Add the top**

```python
# --- Part: top (maple butcherblock matched to the Boos island) --------------
# Provisional thickness and overhang; edge profile copied from the island
# once measured. Figure-8 fasteners into rail_top and rail_rear, no glue.
top = _box(0, 0, POST_H, TOP_W, TOP_D, TOP_T)
PARTS.append({"name": "top", "solid": top, "qty": 1, "material": "maple butcherblock (Boos match)",
              "notes": "provisional 1-3/4 thick, 1-1/4 overhang all round; edge profile to match "
                       "the island; figure-8 fasteners into rail_top and rail_rear, no glue"})
INST.append(("top", top))
assert abs(top.bounding_box().min.X + OH - X0) < 1e-6
assert abs(top.bounding_box().max.Z - H) < 1e-6
```

- [ ] **Step 2: Final assembly and envelope asserts**

Replace the `assembly = ...` line with:
```python
assembly = (post_fl + post_fr + post_rl + post_rr
            + side_l + side_r + back + rail_rear
            + rail_top + rail_mid + rail_bot + bottom
            + front_bot + front_top + drawer_bot + drawer_top + top)
bb = assembly.bounding_box()
assert abs(bb.size.X - TOP_W) < 1e-6, bb.size
assert abs(bb.size.Y - TOP_D) < 1e-6, bb.size
assert abs(bb.size.Z - H) < 1e-6, bb.size
assert abs(bb.min.Z) < 1e-6
assert len(INST) == 25, len(INST)
```

- [ ] **Step 3: Run, render, time it**

Run `time TMP_STL=$SCRATCH/db.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py` then render to `$SCRATCH/db-t7-full.png`. Expected: `OK  parts: [...]` with 18 registry names, no assert failure, runtime well under a minute (the 300 pairwise overlap intersections dominate). View the PNG: complete bench, top overhanging the posts equally on all sides, nothing poking through the top or below the floor.

---

