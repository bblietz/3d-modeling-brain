### Task 8: Buildability check, exports, renders, viewer

**Files:**
- Generate: `projects/Drawer-bench/cutlist.md`, `cutlist.csv`, `drawer_bench.step`, `images/final-4view.png`

- [ ] **Step 1: Export**

Run:
```bash
SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad && EXPORT=1 TMP_STL=$SCRATCH/db.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py && cat projects/Drawer-bench/cutlist.md && ls -la projects/Drawer-bench/drawer_bench.step
```
Expected: `exported cutlist + step`, then the cut list with these rows (mm, T x W x L; inches nearest 1/16):

| Qty | Part | mm | in |
|---|---|---|---|
| 4 | post_front/post_rear | 76.2 x 76.2 x 463.6 | 3 x 3 x 18-1/4 (flagged: chamfers + grooves need a drawing) |
| 2 | side | 18 x 412.8 x 425.5 | 11/16 x 16-1/4 x 16-3/4 |
| 1 | back | 18 x 387.4 x 717.6 | 11/16 x 15-1/4 x 28-1/4 |
| 2 | rail_rear/rail_bot | 18 x 38.1 x 717.6 | 11/16 x 1-1/2 x 28-1/4 (rail_bot flagged: rabbet) |
| 2 | rail_top/rail_mid | 18 x 25.4 x 717.6 | 11/16 x 1 x 28-1/4 |
| 1 | front_bot | 19.1 x 288.9 x 692.2 | 3/4 x 11-3/8 x 27-1/4 |
| 1 | front_top | 19.1 x 146.1 x 692.2 | 3/4 x 5-3/4 x 27-1/4 |
| 1 | bottom | 12 x 484.7 x 802.2 | 1/2 x 19-1/16 x 31-9/16 (flagged: notched) |
| 2 | drawer_side_bot | 12 x 209.6 x 457.2 | 1/2 x 8-1/4 x 18 (flagged: rabbets) |
| 2 | drawer_end_bot | 12 x 209.6 x 677.2 | 1/2 x 8-1/4 x 26-11/16 |
| 2 | drawer_bottom_bot/drawer_bottom_top | 12 x 445.9 x 677.2 | 1/2 x 17-9/16 x 26-11/16 |
| 2 | drawer_side_top | 12 x 82.6 x 457.2 | 1/2 x 3-1/4 x 18 |
| 2 | drawer_end_top | 12 x 82.6 x 677.2 | 1/2 x 3-1/4 x 26-11/16 |
| 1 | top | 44.5 x 609.6 x 914.4 | 1-3/4 x 24 x 36 |

If any row differs, the geometry is wrong, not the table: go back to the task that owns that part.

- [ ] **Step 2: Buildability check (furniture skill Phase 4), written into brief.md in Task 9**

Walk every row and record the verdicts:
- Stock thickness: 18 / 12 mm ply are stock; maple parts are milled (posts from 8/4, fronts and rails from 4/4). Rails are milled to the MEASURED ply thickness.
- Rectangularity: flagged parts are the posts (chamfer + two stopped grooves: needs a drawing; groove positions are in the registry notes), rail_bot (rabbet), bottom (four corner notches, dims in the notes), drawer sides (end rabbets + bottom groove, standard). Everything else is a plain blank.
- Grain / show face: posts, rails, fronts along the length; side ply face grain vertical; the top's grain runs along its 36 in length (Boos style).
- Joinery fit: post grooves and drawer rabbets/grooves cut to measured ply after a test cut; slide numbers are the unverified Blum class values (see cabinet-bench learnings).
- Stock yield: 18 mm ply 0.35 + 0.28 = about 0.63 m2 plus rails-worth if ply were used (they are maple): one sheet. 12 mm ply: bottom 0.39 + drawer parts about 1.1 m2: one 2440 x 1220 sheet with room. Maple: posts 4 x 18-1/4 in from 8/4 (8 pieces 3-1/4 x 19 rough), fronts 27-1/4 and rails 28-1/4 from 4/4; the 11-3/8 bottom front is a glue-up of two boards.
- Wood movement: top on figure-8s; bottom front on slotted screws; posts and rails along-grain; ply stable.
- Transport: footprint 850.9 x 546.1, height 508: passes a 750 mm doorway on its side (546 wide).
- Assembly order (walk it): (1) glue each side panel into its front and rear posts (two side assemblies). (2) Stand side A, enter the back panel and rear rail tenons into its rear post groove. (3) Slide the bottom panel forward into the back-panel groove, then sideways into side A's groove (the back groove runs along X so the sideways move is free). (4) Enter the three front rails into side A's front post groove; the bottom rail's rabbet slides along the bottom's front tab. (5) Close side B onto all tenons and the bottom's far edge. (6) Drawers and fronts, then the top on figure-8s. Every part can be inserted in this order without interference.

- [ ] **Step 3: Final 4-view render**

Run: `.venv/bin/python scripts/render_stl.py $SCRATCH/db.stl projects/Drawer-bench/images/final-4view.png` and view it. Expected: iso, front, top, right views of the complete bench.

- [ ] **Step 4: Viewer push for Brian's sign-off**

Run `scripts/cad-viewer.sh` (starts the server on port 3939 if needed and opens the WebGL-capable Chrome), then `SHOW=reset .venv/bin/python projects/Drawer-bench/drawer_bench.py`. Tell Brian the model is in the viewer. If Brian is not present, note "viewer sign-off pending" in brief.md and treat the exports as provisional (they already are; every input is provisional). Re-push with `SHOW=1` after any later edit.

---

