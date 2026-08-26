# Task 1 Report: Skeleton, constants, helpers, four chamfered and grooved posts

## What I implemented

Created `projects/Drawer-bench/drawer_bench.py` from scratch, following Steps 2-4 of
the task brief verbatim: file header docstring, provisional-input constants, locked
design constants, undermount-slide constants, derived constants, `PARTS`/`INST`
registries, helpers (`_box`, `vol`, `part`, `assert_housed`, `mirror_x`), the
`make_post` factory and the four post instances (`post_fl`, `post_rl`, mirrored to
`post_fr`, `post_rr`), the post-level asserts, the assembly line, global checks
(single-solid-per-part, pairwise no-overlap), the exports block (`TMP_STL`, `EXPORT`,
`SHOW`), and the final `print("OK  parts: ...")` line.

A diff of the brief's three fenced code blocks (Steps 2-4) concatenated together
against the written file shows exactly one difference in the whole ~230-line file: one
extra blank line between the end of the Step 2 block (after `mirror_x`) and the start
of the Step 3 block (the `# --- Parts: posts` comment) — a PEP8 double-blank-line
separator I added between the helpers section and the posts section. No constant,
name, comment, or code line differs from the brief.

## Step 1 probe output (verbatim)

Command run exactly as given in the brief:

```
disjoint 0 touching 0 overlap 499.9999999999999
chamfer solids 1 vol 920.0 expect 920.0
```

Interpretation: `a & b` on disjoint solids did **not** raise — it returned an empty
`Compound` (0 children) whose `.volume` is `0` (int, hence "disjoint 0" not "0.0"; the
probe script's local `vol()` prints `s.volume` directly for a non-`None` result, and an
empty `Compound`'s `.volume` is the int `0`). I confirmed this with a follow-up check:

```python
r = a & b
print(type(r), r, "volume=", r.volume if r is not None else None)
# <class 'build123d.topology.composite.Compound'> Compound at 0x..., #children(0) volume= 0
```

So the conditional in the "Before You Begin" instructions ("if `a & b` raises...")
does not apply here — no exception path was needed. I kept the brief's `vol()` exactly
as written (it already wraps the boolean in try/except as a defensive no-op), per the
"Create the file exactly as the brief's Steps 2-4 specify" instruction, which does not
depend on the probe outcome. The chamfer probe matched the expected value exactly:
`vol 920.0 expect 920.0`.

## Run command and output (verbatim)

```
$ SCRATCH=/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad
$ TMP_STL=$SCRATCH/db.stl .venv/bin/python projects/Drawer-bench/drawer_bench.py && .venv/bin/python scripts/render_stl.py $SCRATCH/db.stl $SCRATCH/db-t1-posts.png
OK  parts: ['post_front', 'post_rear']
rendered 4 views -> /tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/db-t1-posts.png
```

No traceback; matches the brief's expected `OK  parts: ['post_front', 'post_rear']`.

Post volumes (printed in a separate ad hoc check for the report, not part of the
script): `post_fl.volume = 2458310.607562499`, `post_rl.volume = 2461576.7300624973`
(front has two grooves cut, rear has two grooves cut but at a different stop height on
the frame-groove side — matches the file's own `_front_vol`/`_rear_vol` asserts, which
passed).

## PNG review

Viewed `$SCRATCH/db-t1-posts.png` (4-view render: iso/front/top/right of the full
4-post assembly). At the whole-assembly scale (850.9 x 546.1 mm footprint, posts only
76.2 mm square), I confirmed:
- Four posts sit at the four corners of the expected footprint (top view: corners near
  X in [~32, ~880], Y in [~32, ~580], matching X0/XR/Y0/YB).
- Chamfers are visible in the top view as clipped/octagonal corners on each post.
- Front/right orthogonal views show correct post height (POST_H) and no unexpected
  extra geometry.

Because the grooves (9.525 mm deep, on interior faces) are small relative to the
850x546mm assembly render, I could not confidently eyeball groove placement at that
scale, so I did a second, closer verification: exported `post_fl + post_rl` alone and
`post_fl` alone to separate STLs and re-rendered them
(`$SCRATCH/left_posts.png`, `$SCRATCH/post_fl_only.png`). The top view of `post_fl`
alone shows a chamfered square with two visible notches cut into the top face (the
grooves are "open at the top" per the brief, so at the topmost Z the pocket floors are
visible in a top-down view) — one on the rear (+Y) face and one on the right (+X)
face, consistent with post_fl's side groove (toward post_rl, the other post of the
left side, at +Y) and front-frame groove (toward post_fr, the other front post, at
+X).

I cross-checked this visual read against the code's face-selection logic line by line
against the design-intent comment in the brief:
- Side-panel groove `gy = y + POST - GROOVE_D if front else y - 1`: for the front post
  this is near the +Y (rear) face — correct, since the "other post of that side"
  (post_rl) is at higher Y.
- Front-frame groove cuts at `x + POST - GROOVE_D` — the +X (inner, toward post_fr)
  face — correct.
- Rear-post back-panel groove cuts at `x + POST - GROOVE_D`, Y-band ending at
  `y + POST - SETBACK` (SETBACK behind the rear/outer face) — correct per the "SETBACK
  behind the rear face" comment.
- `FLOOR_GAP (19.05mm) < GROOVE_STOP (38.1mm)`, so the front-frame groove indeed
  reaches lower than the side/panel grooves, as the brief's expected description
  requires.

This matches the brief's expected description. No doubts about correctness beyond the
inherent resolution limits of a coarse STL-mesh matplotlib render for small features
— I consider the volume/bbox/no-overlap asserts (which passed) a stronger proof of
correctness than pixel-level PNG inspection for the groove geometry, and used the PNG
review to confirm overall placement, proportions, and chamfers as the brief asks.

## Files changed

- Created: `/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench/drawer_bench.py`

No other files were modified. Scratch STL/PNG files used only for verification, in
`/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad/`
(`db.stl`, `db-t1-posts.png`, `left_posts.stl`/`.png`, `post_fl_only.stl`/`.png`,
`brief_combined.py`) — none of these are part of the deliverable.

## Self-review findings

- All names in the brief's Interfaces block are present and spelled exactly as
  specified: `_box`, `vol`, `part`, `assert_housed`, `PARTS`, `INST`, `post_fl`,
  `post_fr`, `post_rl`, `post_rr`, `X0`, `Y0`, `XR`, `YB`, `FOOT_W`, `FOOT_D`,
  `POST_H`, `OPEN_W`, `PANEL_H`, `BACK_H`, `RAIL_L`. (`mirror_x` is also present, as
  the brief's Step 2 code defines it, for later tasks' use.)
- No extra features, no additional asserts, no reordering — block order matches the
  brief exactly (header/constants/helpers, posts, assembly, global checks,
  exports/SHOW tail, final print), so later tasks can insert code before the
  `# --- assembly` marker as intended.
- The `# --- assembly` marker line is present verbatim for later tasks to locate.
- Print line (`OK  parts: ...`) is the last line of the file.
- One cosmetic-only diff from a byte-for-byte concatenation of the brief's three code
  blocks: an extra blank line between the helpers section and the posts section
  (PEP8 double-blank-line separator). No functional or content difference.
- No concerns about correctness. Step 1's conditional (try/except needed only if `a &
  b` raises) did not trigger, and I left `vol()` as specified.
