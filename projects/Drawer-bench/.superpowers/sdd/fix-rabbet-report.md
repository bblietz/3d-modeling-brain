---
title: Fix - rail_bot rabbet run through the tenons
date: 2026-08-24
project: "[[Drawer-bench]]"
status: done
---

# Fix: rail_bot rabbet run THROUGH the tenons

Follow-up to the Task 8 insertion walk ([[task-8-report]], assembly section), which
found that `rail_bot`'s rabbet, stopped at the tenon shoulders, left a full-section
tenon that sweeps through the bottom panel's front tab when the rail slides sideways
into its mortise. Resolution: run the rabbet through the tenons. The tenon loses a
`BOT_GROOVE x T12` corner; the mortise still houses the rest. The bottom's front tab
keeps its full `OPEN_W` length, and the small void the through-rabbet leaves inside
the mortise is hidden.

No dimension constant changed. No tolerance loosened, no assert removed.
Only `projects/Drawer-bench/drawer_bench.py` was edited; the four deliverables
(`cutlist.md`, `cutlist.csv`, `drawer_bench.step`, `images/*.png`) were regenerated.

## Changes (line numbers are post-edit)

**1. Through rabbet on `rail_bot` (line 233) plus the block comment above it (lines 220-226)**

Comment, extended (new text from "The bottom rail's rear-top edge"):

```
# --- Parts: front frame rails (hidden behind the drawer fronts) ------------
# Front face FRAME_SETBACK behind the post faces; stub tenons GROOVE_D each
# end into the front-post grooves. Top rail under the top, mid rail centered
# on the reveal between the fronts, bottom rail from the floor gap up (its
# top face is the bottom panel's top face). The bottom rail's rear-top edge is
# rabbeted for the bottom panel; the rabbet runs THROUGH the tenons (the tenon
# loses a BOT_GROOVE x T12 corner, the mortise still houses the rest) so the
# bottom's front tab can slide past the tenons when the rail goes into its
# mortise at glue-up.
```

Cutter, line 233:

```python
# was
rail_bot -= _box(X0 + POST, RAIL_Y0 + RAIL_T - BOT_GROOVE, BOT_Z0, OPEN_W, BOT_GROOVE + 1, T12 + 1)
# now
rail_bot -= _box(RAIL_X0 - 1, RAIL_Y0 + RAIL_T - BOT_GROOVE, BOT_Z0, RAIL_L + 2, BOT_GROOVE + 1, T12 + 1)
```

**2. Rails housed-probe loop (lines 248-253)**

`rail_bot` no longer fills a full-section tenon slice, so its probe is `BOT_GROOVE`
thinner in Y. The other two rails keep the full `RAIL_T` probe.

```python
# rail_bot's tenon is the full section minus the through-rabbet corner, so its
# probe is BOT_GROOVE thinner in Y; the other two tenons are full section.
for _r, (_z, _h), _t in zip((rail_bot, rail_mid, rail_top), RAIL_ZH,
                            (RAIL_T - BOT_GROOVE, RAIL_T, RAIL_T)):
    assert_housed(_r, post_fl, _box(RAIL_X0, RAIL_Y0, _z, GROOVE_D, _t, _h))
    assert_housed(_r, post_fr, _box(XR - POST, RAIL_Y0, _z, GROOVE_D, _t, _h))
```

The bottom-in-`rail_bot` housed probe (line 283,
`assert_housed(bottom, rail_bot, _box(X0 + POST, BOT_Y0, BOT_Z0, OPEN_W, BOT_GROOVE, T12))`)
is untouched and still passes.

**3. `rail_bot` note (lines 241-245)**

```python
PARTS.append({"name": "rail_bot", "solid": rail_bot, "qty": 1, "material": "soft maple",
              "notes": "FRONT bottom rail, thickness = measured ply (T18): stub tenons 3/8 each "
                       f"end, full section; rabbet {BOT_GROOVE:g} x {T12:g} (T12) on the rear-top "
                       "edge, run THROUGH the tenons so the bottom can slide past them at "
                       "glue-up; glue and screw the bottom into it (no lip above)"})
```

**4. Drawer and post notes**

Drawer side, lines 341-344:

```python
PARTS.append({"name": f"drawer_side_{sfx}", "solid": s, "qty": 2, "material": "ply 12mm",
              "notes": f"end rabbets {DADO:g} deep x {T12:g} (T12); bottom groove {DADO:g} "
                       f"deep x {T12:g} (T12) with its top at {UM_RECESS + T12:g} above the "
                       "bottom edge"})
```

Drawer end, lines 345-347:

```python
PARTS.append({"name": f"drawer_end_{sfx}", "solid": end, "qty": 2, "material": "ply 12mm",
              "notes": f"bottom groove {DADO:g} deep x {T12:g} (T12) with its top at "
                       f"{UM_RECESS + T12:g} above the bottom edge"})
```

`post_front`, line 149, inserted before the mortise sentence:

```python
                       "stopped 1-1/2 above the floor, open at top"
                       "; grain vertical, glue-up seam on a side face; "
                       "three mortises T18 x 3/8 on the inner face 1 in behind the front face at Z "
```

`post_rear`, line 159, appended at the end of the note:

```python
                       "stopped 1-1/2 above the floor, open at top; no mortises"
                       "; grain vertical"})
```

No other note was touched.

**5.** No tolerance loosened, no assert removed. The only assert edit is the probe
Y-size in change 2; every comparison stays at `1e-3` / `1e-6`.

## Verification (outputs verbatim)

### 1. Plain run

```
$ .venv/bin/python projects/Drawer-bench/drawer_bench.py
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom', 'front_bot', 'front_top', 'drawer_side_bot', 'drawer_end_bot', 'drawer_bottom_bot', 'drawer_side_top', 'drawer_end_top', 'drawer_bottom_top', 'top']
```

18 names, every assert in the file passed (including the global pairwise
no-overlap sweep over all 25 placed instances).

### 2 and 3. Probe script ($SCRATCH/probe.py, loaded with runpy)

```
--- 2. rail_bot volume ---
actual   = 437418.480000
expected = 437418.480000   (RAIL_T*RAIL_BOT_H*RAIL_L - BOT_GROOVE*T12*RAIL_L)
delta    = 1.746e-10   pass=True
--- 2b. rabbet cavity extent ---
cavity volume = 54677.310000  solids=1
cavity min.X = 98.425000  RAIL_X0            = 98.425000  pass=True
cavity max.X = 815.975000  RAIL_X0 + RAIL_L   = 815.975000  pass=True
cavity size  = X 717.5500  Y 6.3500  Z 12.0000
--- 3. insertion walk (+X into the left mortise) ---
in place dx=0.000  vol(rail_bot & bottom) = 0.000e+00
dx= 0.000  vol = 0.000e+00  pass=True
dx= 1.000  vol = 0.000e+00  pass=True
dx= 2.000  vol = 0.000e+00  pass=True
dx= 3.000  vol = 0.000e+00  pass=True
dx= 4.000  vol = 0.000e+00  pass=True
dx= 5.000  vol = 0.000e+00  pass=True
dx= 6.000  vol = 0.000e+00  pass=True
dx= 7.000  vol = 0.000e+00  pass=True
dx= 8.000  vol = 0.000e+00  pass=True
dx= 9.000  vol = 0.000e+00  pass=True
dx= 9.525  vol = 0.000e+00  pass=True
GROOVE_D = 9.524999999999999; worst overlap = 0.000e+00; all pass = True
```

The rabbet cavity is one solid spanning the rail end to end
(717.55 = RAIL_L in X, BOT_GROOVE in Y, T12 in Z), and the rail slides its full
GROOVE_D tenon travel into the left mortise without ever touching the bottom panel.

### 4. Deliverables regenerated (from the vault root)

```
$ EXPORT=1 TMP_STL=$SCRATCH/db-final.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py
exported cutlist + step
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom', 'front_bot', 'front_top', 'drawer_side_bot', 'drawer_end_bot', 'drawer_bottom_bot', 'drawer_side_top', 'drawer_end_top', 'drawer_bottom_top', 'top']

$ .venv/bin/python scripts/render_stl.py $SCRATCH/db-final.stl projects/Drawer-bench/images/final-4view.png
rendered 4 views -> projects/Drawer-bench/images/final-4view.png
$ .venv/bin/python scripts/render_stl.py $SCRATCH/db-final.stl projects/Drawer-bench/images/final-iso-front.png 25,-35
rendered 1 views -> projects/Drawer-bench/images/final-iso-front.png
$ .venv/bin/python scripts/render_stl.py $SCRATCH/db-final.stl projects/Drawer-bench/images/final-iso-rear.png 20,-120
rendered 1 views -> projects/Drawer-bench/images/final-iso-rear.png
```

Overwritten: `cutlist.md`, `cutlist.csv`, `drawer_bench.step`,
`images/final-4view.png`, `images/final-iso-front.png`, `images/final-iso-rear.png`.

`final-4view.png` viewed: the bench reads as before, 36 x 24 x 20 in envelope,
overhanging top, two graduated fronts with their reveals, chamfered posts, shadow
gap at the floor. Nothing changed visually, which is expected: the rabbet extension
is a 6.35 x 12 mm corner buried inside the two front-post mortises.

Cut list, `rail_bot` row (line 19 of `cutlist.md`), dimensions unchanged and still
merged with `rail_rear` at qty 2:

```
| 2 | rail_rear/rail_bot | 18 x 38.1 x 717.5 | 11/16 x 1-1/2 x 28-1/4 | soft maple | REAR top rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; figure-8 fasteners on top ; FRONT bottom rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; rabbet 6.35 x 12 (T12) on the rear-top edge, run THROUGH the tenons so the bottom can slide past them at glue-up; glue and screw the bottom into it (no lip above) ; not a plain rectangular blank (89% of bounding box); needs a drawing or template |
```

Compare with the pre-edit row, which was identical except for
"rabbet 6.35 x 12 (T12) on the rear-top edge between the shoulders". Same
`18 x 38.1 x 717.5` / `11/16 x 1-1/2 x 28-1/4`, same qty 2, same 89% blank warning.

The other regenerated note rows:

```
| 2 | drawer_side_bot | 12 x 209.5 x 457.2 | 1/2 x 8-1/4 x 18 | ply 12mm | end rabbets 6.35 deep x 12 (T12); bottom groove 6.35 deep x 12 (T12) with its top at 24.7 above the bottom edge ; ...
| 2 | drawer_end_bot | 12 x 209.5 x 677.2 | 1/2 x 8-1/4 x 26-11/16 | ply 12mm | bottom groove 6.35 deep x 12 (T12) with its top at 24.7 above the bottom edge ; ...
| 4 | post_front/post_rear | 76.2 x 76.2 x 463.6 | 3 x 3 x 18-1/4 | soft maple | ... stopped 1-1/2 above the floor, open at top; grain vertical, glue-up seam on a side face; three mortises T18 x 3/8 ... ; ... no mortises; grain vertical ; ...
```

### 5. OCP viewer

```
$ SHOW=1 .venv/bin/python projects/Drawer-bench/drawer_bench.py
+++++++++++++++++++++++++CameraKeepWarning: reset_camera is set to KEEP. If shown objects are not visible use the 'resize' and a 'view' button
OK  parts: [...18 names...]
EXIT=0
```

Server on port 3939 was up; the re-push succeeded (exit status 0). The camera-keep
warning is the normal `Camera.KEEP` notice, not an error.

## Concerns

- **Shop note, not a CAD problem.** The rabbet is now a single through cut on the
  rail's rear-top edge, which is actually easier to make than the stopped version
  (one pass on the table saw or router table, no stop blocks, no chisel work at the
  shoulders). The cut list note says so explicitly.
- **The void inside the mortise.** Each front-post mortise now has a
  6.35 x 12 x 9.525 mm gap above the tenon's rabbeted corner, at the rear-top of the
  tenon. It is fully enclosed by the post and invisible. Glue surface lost per tenon
  is small (the tenon cheek loses 6.35 mm of its 18 mm height over the 12 mm rabbet
  depth); the bottom rail is also glued and screwed to the bottom panel along its
  whole length, so the joint is not carrying much alone.
- **`bottom` unchanged.** Its front tab is still `OPEN_W` long, so the tab still
  bottoms out in the rabbet across the full opening and the "glue and screw the front
  edge" instruction is unaffected.
- **The insertion walk models one direction only.** It walks `rail_bot` +X, the
  reverse of the -X entry into the left mortise, which is the motion the Task 8 report
  flagged. The bench is symmetric about X, so the right mortise is the mirror of the
  same result. A real glue-up also has the side panels and back in place; those were
  not walked, only the rail-versus-bottom conflict that was the reported defect.
- **Provisional dimensions.** Everything still rests on the design.md provisional
  inputs. Nothing is cut until the stock, the ply, and the Boos top are measured.
