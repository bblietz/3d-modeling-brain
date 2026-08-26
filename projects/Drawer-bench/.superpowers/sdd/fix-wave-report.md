---
type: report
project: Drawer-bench
stage: fix wave after the final whole-file review
date: 2026-08-24
---

# Fix wave report - drawer_bench.py

File: `/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench/drawer_bench.py`
(388 -> 420 lines; original preserved at
`$SCRATCH/fixwave/drawer_bench.orig.py`, patch script at `$SCRATCH/fixwave/patch.py`).
No other file was modified. No dimension changed: every new number is derived
from existing named constants.

Assert budget: 44 -> 46 bare `assert` statements, 8 -> 12 `assert_housed` call
sites. Nothing was removed and no tolerance was loosened.

## What changed

### F1 - front-frame joinery: three stopped mortises (design resolution)

- **lines 71-75** (Derived block, after `RAIL_L`): added `REV_MID_Z0`,
  `RAIL_BOT_Z0`, `RAIL_MID_Z0`, `RAIL_TOP_Z0`, `RAIL_ZH`. The rail Z values now
  exist before `make_post` runs.
- **lines 115-122**: rewrote the comment above `make_post` - front posts get
  three stopped mortises at the rail heights, so the inner face stays solid
  between the rails (slide front tab lands there, and an open groove would show
  with a drawer open).
- **lines 129-132**: `if front:` now loops `RAIL_ZH` and cuts one mortise per
  rail; the cutter gets +1 in Z only for the mortise that reaches `POST_H`
  (`_z + _h >= POST_H`), so the top mortise is open at the top and the other two
  are closed.
- **line 164**: `_front_vol` now subtracts
  `T18 * GROOVE_D * (RAIL_BOT_H + RAIL_MID_H + RAIL_TOP_H)` instead of
  `T18 * GROOVE_D * (POST_H - FLOOR_GAP)`. Removed material per front post drops
  from 76209.525 mm3 to 15241.905 mm3; the equality assert is still exact
  (`post_fl.volume 2519278.228 == _front_vol 2519278.228`), which is only true
  because the chamfers never reach a mortise.
- **lines 222-227** (rails block): deleted the duplicate `REV_MID_Z0` /
  `RAIL_MID_Z0`; `rail_top` / `rail_bot` now use `RAIL_TOP_Z0` / `RAIL_BOT_Z0`.
- **line 242**: the housed-probe loop is now
  `for _r, (_z, _h) in zip((rail_bot, rail_mid, rail_top), RAIL_ZH):`.

### F2 (C1) - bottom-panel groove note on side and back

- **lines 191-198**: added `_BOT_GROOVE_NOTE` (f-string, measured from
  `BOT_GROOVE`, `T12`, `BOT_Z0 - GROOVE_STOP`, `GROOVE_D`) and appended
  `"; " + _BOT_GROOVE_NOTE` to both the `side` and the `back` note.

### F3 (I1) - right-hand and mirror engagement asserts

- **lines 209-210**: `back` and `rail_rear` housed in `post_rr`.
- **line 244**: second probe inside the rails loop against `post_fr`
  (3 rails x right post).
- **lines 270-272**: `_bp` extracted; `bottom` now probed into `side_l` and into
  `side_r` via `mirror_x(_bp)`.
- **lines 303-304**: loop asserting `front_top` is aligned over `front_bot` in
  X and Y.
- **lines 363-365**: `_eb` / `_rabbet_floor_r` - the drawer end and the drawer
  bottom must both land on the mirrored right-hand rabbet floor.

### F4 (I2, I3, I4) - registry notes

Rewritten as f-strings so a measured re-run regenerates them:
`post_front` (line 143), `post_rear` (line 153), `rail_rear` (line 199),
`rail_top` (line 229), `rail_mid` (line 232), `rail_bot` (line 235),
`bottom` (line 261). The bottom note's `51.85 / 39.15 / 51.85` are now computed
from `X0 + POST - BOT_X0`, `Y0 + POST - BOT_Y0`, `BOT_Y1 - (YB - POST)` and print
identically. Other notes untouched.

### F5 - kept

`_front_vol` / `_rear_vol` asserts stay exact equalities at 1e-3; every existing
assert survives; no tolerance widened.

### F6 - shadowing

- **lines 356, 361-362**: the drawer loop's front bbox renamed `_fb` -> `_frb`,
  so the fronts block's `_fb` / `_ft` (used by the new F3 alignment loop at 303,
  which runs before the drawer block) is no longer shadowed.

### F7 - duplicate expression

- **line 222**: `RAIL_X0 = BACK_X0   # same tenon line as the back groove`.

## Verification

### 1. Full run + render

```
$ time TMP_STL=$SCRATCH/db-fix.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py
OK  parts: ['post_front', 'post_rear', 'side', 'back', 'rail_rear', 'rail_top', 'rail_mid', 'rail_bot', 'bottom', 'front_bot', 'front_top', 'drawer_side_bot', 'drawer_end_bot', 'drawer_bottom_bot', 'drawer_side_top', 'drawer_end_top', 'drawer_bottom_top', 'top']

real	0m4.349s
user	0m6.804s
sys	0m0.299s

$ .venv/bin/python scripts/render_stl.py $SCRATCH/db-fix.stl $SCRATCH/db-fix.png
rendered 4 views -> /tmp/.../scratchpad/db-fix.png
```

18 names, no traceback, 4.3 s. PNG viewed (iso / front / top / right): envelope
unchanged - 36 x 24 x 20 in bench, top overhanging all round, four posts with the
floor gap under the bottom drawer front, two graduated fronts with the mid
reveal. Assembly bbox measured `[0.0, 0.0, -0.0, 914.4, 609.6, 508.0]`
(= TOP_W x TOP_D x H). The mortise change is entirely on hidden inner faces, so
the silhouette is identical to the pre-fix render.

### 2. Front-post probe (`$SCRATCH/fixwave/probe_post.py`, runpy, model unedited)

```
solids removed: 8
  chamfer      X    0.000..   9.525  Y    0.000..   9.525  Z    0.000.. 463.550  vol    21027.932
  chamfer      X   -0.000..   9.525  Y   66.675..  76.200  Z   -0.000.. 463.550  vol    21027.932
  chamfer      X   66.675..  76.200  Y    0.000..   9.525  Z    0.000.. 463.550  vol    21027.932
  chamfer      X   66.675..  76.200  Y   66.675..  76.200  Z    0.000.. 463.550  vol    21027.932
  mortise      X   66.675..  76.200  Y   25.400..  43.400  Z   19.050..  57.150  vol     6532.245
  side groove  X   12.700..  30.700  Y   66.675..  76.200  Z   38.100.. 463.550  vol    72943.403
  mortise      X   66.675..  76.200  Y   25.400..  43.400  Z  298.450.. 323.850  vol     4354.830
  mortise      X   66.675..  76.200  Y   25.400..  43.400  Z  438.150.. 463.550  vol     4354.830
mortise (z0, h): [(19.05, 38.1), (298.45, 25.4), (438.15, 25.4)]
RAIL_ZH        : [(19.05, 38.1), (298.45, 25.4), (438.15, 25.4)]
  inner face below bottom rail          Z   0.000.. 19.050  solid fraction 1.000000
  inner face bottom rail to mid rail    Z  57.150..298.450  solid fraction 1.000000
  inner face mid rail to top rail       Z 323.850..438.150  solid fraction 1.000000
PROBE OK
```

Exactly 8 solids: 4 full-length chamfer prisms + 1 side groove (stopped at 38.1,
open to 463.55) + 3 mortises whose (z0, h) pairs equal `RAIL_ZH`, the top one
reaching `POST_H` exactly. The full-width inner-face band is 100 % solid in all
three gaps between the rails - no leftover groove.

### 3. Mutation tests (scratch copies only)

```
=== a RAIL_L -5: CAUGHT (fails)
  File ".../mut_0.py", line 209, in <module>
    assert_housed(back, post_rr, _box(XR - POST, BACK_Y0, GROOVE_STOP, GROOVE_D, T18, BACK_H))
  File ".../mut_0.py", line 104, in assert_housed
    assert abs(vol(probe & guest) - probe.volume) < 1e-3, "guest does not fill the groove"
AssertionError: guest does not fill the groove
=== b BOX_W -20: CAUGHT (fails)
  File ".../mut_1.py", line 365, in <module>
    assert abs(_eb.max.X - _rabbet_floor_r) < 1e-6 and abs(_bb.max.X - _rabbet_floor_r) < 1e-6, _sfx
AssertionError: bot
=== c front_top +2X: CAUGHT (fails)
  File ".../mut_2.py", line 304, in <module>
    assert abs(_a - _b) < 1e-6          # top front aligned over the bottom front
AssertionError
=== d BOT_W -5: CAUGHT (fails)
  File ".../mut_3.py", line 272, in <module>
    assert_housed(bottom, side_r, mirror_x(_bp))
  File ".../mut_3.py", line 104, in assert_housed
    assert abs(vol(probe & guest) - probe.volume) < 1e-3, "guest does not fill the groove"
AssertionError: guest does not fill the groove
=== e END_LEN -4: CAUGHT (fails)
  File ".../mut_4.py", line 365, in <module>
    assert abs(_eb.max.X - _rabbet_floor_r) < 1e-6 and abs(_bb.max.X - _rabbet_floor_r) < 1e-6, _sfx
AssertionError: bot
```

5 / 5 caught, and every one of them by an assert this fix wave added: (a) and (d)
by the new right-hand / mirrored `assert_housed` probes, (c) by the front
alignment loop, (b) and (e) by the mirrored rabbet-floor assert. That is the
direct evidence that the I1 additions close the "left side only" blind spot.

### 4. Emitted cut list (scratch copy, `PROJ` -> `$SCRATCH/fixwave/out`, `EXPORT=1`)

Relevant rows verbatim:

```
| 1 | back | 18 x 387.4 x 717.5 | 11/16 x 15-1/4 x 28-1/4 | ply 18mm | housed 3/8 in each post; top edge under the rear rail; stopped groove 6.35 deep x 12 (T12) on the inner face for the bottom, lower wall 7.05 above the bottom edge, stopped 9.525 from each end |
| 2 | side | 18 x 412.8 x 425.5 | 11/16 x 16-1/4 x 16-3/4 | ply 18mm | face grain vertical on the show face; housed 3/8 in each post; stopped groove 6.35 deep x 12 (T12) on the inner face for the bottom, lower wall 7.05 above the bottom edge, stopped 9.525 from each end |
| 2 | rail_rear/rail_bot | 18 x 38.1 x 717.5 | 11/16 x 1-1/2 x 28-1/4 | soft maple | REAR top rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; figure-8 fasteners on top ; FRONT bottom rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; rabbet 6.35 x 12 (T12) on the rear-top edge between the shoulders; glue and screw the bottom into it (no lip above) ; not a plain rectangular blank (89% of bounding box); needs a drawing or template |
| 2 | rail_top/rail_mid | 18 x 25.4 x 717.5 | 11/16 x 1 x 28-1/4 | soft maple | FRONT top rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; figure-8 fasteners on top ; FRONT mid rail, thickness = measured ply (T18): stub tenons 3/8 each end, full section; carries the top drawer slides |
| 1 | bottom | 12 x 484.7 x 802.2 | 1/2 x 19-1/16 x 31-9/16 | ply 12mm | notch the four corners 51.85 wide x 39.15 (front) / 51.85 (rear) for the posts; edges in the side/back grooves and the rail_bot rabbet (glue and screw the front edge) ; not a plain rectangular blank (98% of bounding box); needs a drawing or template |
| 4 | post_front/post_rear | 76.2 x 76.2 x 463.6 | 3 x 3 x 18-1/4 | soft maple | one of 2 FRONT posts, left/right mirrored, grooves on the inner faces; glue-up of two 8/4 pieces milled to 1-1/2; 0.375 chamfer x4 edges full length; side groove T18 (measured ply) x 3/8 at 1/2 from the outer face, stopped 1-1/2 above the floor, open at top; three mortises T18 x 3/8 on the inner face 1 in behind the front face at Z 19.05-57.15, 298.45-323.85, 438.15-top for the rail tenons ; not a plain rectangular blank (94% of bounding box); needs a drawing or template ; one of 2 REAR posts, left/right mirrored, grooves on the inner faces; same blank and chamfer as post_front; side groove as post_front; back groove T18 x 3/8 on the inner face at 1/2 from the rear face, stopped 1-1/2 above the floor, open at top; no mortises ; not a plain rectangular blank (91% of bounding box); needs a drawing or template |
```

Side and back carry the groove note; every rail row names FRONT or REAR and its
position; the post row says FRONT / REAR, "left/right mirrored, grooves on the
inner faces", and lists the three mortise Z ranges. Nothing was written into
`projects/Drawer-bench/` (output went to `$SCRATCH/fixwave/out/`).

## Concerns

1. **Assembly order changed by F1 (design consequence, worth recording in
   design.md).** With a continuous groove all three front rails could be dropped
   in from the top. With stopped mortises only the top rail can - the mid and
   bottom rails must be tenoned in during the front-frame glue-up. That is
   normal post-and-rail practice and is the price of the solid inner face, but
   it is a real change to the build sequence.
2. **Mixed units inside the post note.** `{CHAMFER / IN:g}` prints `0.375`
   (inches) in the same sentence as mortise heights printed in mm
   (`19.05-57.15`). The wording came from the fix wave spec, so I left it, but a
   shop reader could misread the chamfer as 0.375 mm. Cheap fix if wanted:
   `3/8 chamfer` as literal text, or append `in` after the value.
3. **Merged cut-list rows.** `cutlist.py` merges rail_rear+rail_bot and
   rail_top+rail_mid (identical blank + material) into one Qty 2 row carrying
   both notes joined by " ; ". Now that the notes are self-identifying this reads
   correctly, which is exactly what I3 was after - but the row header still shows
   a combined qty for two different parts. Unchanged behavior, flagged only.
4. **One remaining spelled-out rail Z.** Line 353, in the drawer clearance loop,
   still reads `("top", POST_H - RAIL_TOP_H, front_top)` where `RAIL_TOP_Z0`
   would now say the same thing. Outside the scope named in the fix wave (rails
   block and its asserts), so I left it; a one-token follow-up if consistency is
   wanted.
5. **Volume assert is load-bearing and still exact.** `_front_vol` only closes
   because no chamfer prism touches a mortise or the side groove (the probe in
   section 2 shows the X/Y bands are disjoint). If FRAME_SETBACK or CHAMFER ever
   changes, that assert will trip first - which is the intent, and
   `assert CHAMFER < SETBACK and CHAMFER < FRAME_SETBACK` still guards it.
