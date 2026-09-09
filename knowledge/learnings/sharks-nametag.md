---
type: learning
project: Sharks-nametag
date: 2026-08-02
status: v3.19 - three test prints diagnosed, full review done, reprint pending
---

# Sharks-nametag retrospective (design phase)

3" logo backpack tag from the SCCYSC club crest, 3 colors, 0.4 nozzle. Design locked at v3.14 after ~15 iteration rounds with Brian. Print results pending.

## What worked

- **Trace everything, 1:1.** The primitive-rebuilt v1 was rejected on sight ("looks like shit"); the moment every element was vector-traced from the club PNG at 679 px = 76.2 mm, each review round became about layout, not likeness. See [[feedback-logo-recreation-fidelity]].
- **Measure, do not eyeball.** Radial scans of the PNG settled the swoosh profile (5.1 mm crescent, non-concentric outer edge), the crest band layering (band / white line / pinstripe that a coarse min/max scan had fused), star positions/rhythm, and ring widths. Every "check the logo" complaint from Brian was resolved by a scan, not squinting.
- **Refit traces into CAD primitives.** Raster traces look fine flat but every polyline facet becomes a visible wall in 3D. Two reusable fixes in the model file: `refined_face` (corner detection + chord-tolerance Lines + least-squares ThreePointArcs) for geometric shapes, `spline_ring_face` (uniform resample, light smoothing passes, periodic Spline) for organic ones. Area-preservation asserts (4%) catch refit damage.
- **Asserts as design memory.** Clearances (hole/stars/swoosh/letters), zero cross-color volume, watertightness, letter-frame gaps - each user decision became an assert, so later edits could not silently regress earlier ones.
- **Subagent trace pipeline.** navy/cyan/white color masks -> morphological cleanup -> subpixel contour (0.5 level) -> Douglas-Peucker; per-layer visual verification mandatory. Five trace JSONs, all reusable. Stencil fonts need an `extra_parts` key for detached glyph pieces.
- **Layer-priority booleans.** Encode overlay order once: white art punches all navy (`- white_t2_2d`), navy trims cyan, banner/pill union over the band bottom. Micro-overlaps between same-color regions are harmless; cross-color ones are caught by the volume asserts.

## What failed / gotchas

- **FreeCAD viewport z-fighting** nearly derailed the project: coincident color faces render as washed-out garbage in the GUI even when the solids are perfect. Verify geometry numerically (probes, volumes) before believing a viewport. The OCP viewer draws the same solids cleanly.
- **Coarse scans lie about thin features.** A 0.5 px radial scan with min/max navy fused a band + white line + pinstripe into one block; only a per-radius color-run profile showed the truth. Brian caught it by eye.
- **Source art encodes constraints invisibly.** T/A/C in SANTA CRUZ are drawn short and the C notched because the CITY oval tucks into that space. We stretched them full-height on request, then had to revert when CITY came back. Lesson: when a source glyph looks wrong, look for what occupied the space next to it.
- **Tiny text estimates were wrong twice** (CITY 4.5 mm not 2.7; YOUTH SOCCER CLUB strokes 0.45-0.8 not 0.34). Measure before declaring something unprintable.
- **Trace winding matters:** clockwise outlines extrude DOWNWARD in build123d (face normal -Z). Normalize with a signed-area ccw() helper before Polygon().

## Print recipe (locked)

FINAL as of 2026-08-26 (gate print MAX 18 on 2026-08-25 passed; batch
files in `projects/Sharks-nametag/final/`, manifest in `final/README.md`):

- Nozzle 0.4 hardened steel; presets `Bambu Lab X2D 0.4 nozzle`,
  `0.12mm High Quality @BBL X2D`, `Bambu PETG Basic @BBL X2D 0.4 nozzle`
  x3 (white #FFFFFF, navy #00395E, cyan #31BAD6); textured PEI 70C;
  vent open, chamber fan on cool (chamber settles at 42-44C).
- Process recipe (flatten_04.py SMOOTH_TOP, pinned in the diff list):
  no ironing, 2 top walls, top speed 60, seam_gap 0%, small perimeters
  30 (threshold 10), gap fill 40, arachne with wall_distribution_count 3,
  wall_transition_filter_deviation 50%, min_feature_size 10%,
  min_bead_width 50%, 50% zig-zag infill, skirt 2 loops / 3 mm / 1 layer,
  first layer 30 / 50 mm/s, prime tower brim 5 + rib wall + fillet wall.
- Letter tier (front SANTA CRUZ letters): modifier part (outlines
  +0.3 mm, z 3.92-4.64) with wall_loops 1, top_one_wall_type all top,
  top_surface_line_width 0.3, internal_solid_infill_line_width 0.3,
  infill_direction 90 (lines along the stems on the 37-layer tag; parity
  asserted), plus object key detect_narrow_internal_solid_infill 0.
- Back inlay (name + number): modifier part (outlines +0.5 mm, z
  0.16-0.56) with internal_solid_infill_pattern concentric, which undoes
  the object key's side effect in layers 2-4.
- Tower rule: free spot closest to the bed center, brim >= 12 mm from
  every disc and >= 15 mm from the edges; singles (30,106.5), plate A
  (106,183.5), plate B (30,183.5).
- Studio: select the 0.4 printer preset BEFORE opening a file; AMS
  mapping white 4 / navy 3 / cyan 2; re-calculate flushing volumes (the
  files carry a 280 placeholder). Single ~1h36m, plate A ~7h05m, plate B
  ~9h19m. Real print time runs ~1.4x the estimate on color-change-heavy
  plates.

## First test print (2026-08-06) - failed, root cause confirmed

The exported 3MFs were verified CORRECT (printer_settings_id "Bambu Lab
X2D 0.4 nozzle", 0.12mm layers, 0.42 line widths). The failure was at
print time: the 0.6 high-flow was physically installed and Bambu Studio's
Prepare machine was set to 0.6mm (main + aux), so Studio adapted the job
to the 0.6 profile and sliced it that way - no warning fired anywhere
because software and hardware agreed with each other, just not with the
design. Result: every fine feature globally fattened - YOUTH SOCCER CLUB
and the SCCYSC arc illegible mush, SANTA CRUZ letters inflated with
ragged edges. Geometry and layout printed correctly. 0.4 nozzle swapped
in 2026-08-06.

- **Lesson (promoted to [[printer-x2d]]): before printing fine-detail
  work, verify BOTH the physically installed nozzle AND Bambu Studio's
  Prepare machine match the design's target nozzle. When Studio's
  machine matches the installed nozzle, it silently re-profiles an
  imported project and no mismatch warning ever fires.**
- Also ran on the Clawd AMS load slot-for-slot (orange/black/purple instead
  of white/navy/cyan); the purple was PLA Matte on a Basic-profile print,
  which underflushes (45 vs 30 prime) and added color smearing. Check the
  filament mapping screen against intended colors at every job start.
- Navy #00395E and cyan #31BAD6 PLA Basic have never appeared in any AMS
  snapshot - likely need purchasing before the real batch.

## Crisp/full variants (2026-08-06)

Per Brian: keep every element printable on the 0.4 nozzle, full design
preserved for the 0.2mm nozzles he ordered.

- `DETAIL=crisp` (default): SCCYSC and YOUTH SOCCER CLUB become FLUSH
  COLOR INLAYS (0.24mm = 2 layers deep) instead of raised/cut relief -
  the same technique as the back name inlay. Raised 0.58mm bars print
  as wobbly free-standing beads, but identical strokes embedded flush
  in a surrounding surface print clean and get ironed. The band stays
  solid navy (SCCYSC inlaid white into its top); YSC is inlaid navy
  into the white disc top. SCCYSC gets a morphological closing
  (offset +0.15/-0.15) so its 0.22mm stencil gaps become solid
  letterforms rather than slice-time pinholes - the stencil style is
  the one casualty at 0.4. Everything else kept as-is, including CITY
  (4.5mm letters) and the 0.47mm pinstripe (continuous single-wall
  rings print cleanly; text does not).
- `DETAIL=full`: the complete traced design; verified to reproduce the
  original STLs to 0.0000 volume difference.
- File layout: crisp is the default everywhere (`sharks-nametag-*.stl`,
  `exports/`); full backups are `sharks-nametag-*-full.stl`,
  `sharks-nametag-max-18-full.3mf`, and `exports-full/` (the original
  13-kid batch). The 0.4 build pipeline (`flatten_04.py`,
  `batch_roster.py`) was rescued from an ephemeral session scratchpad
  into `pipeline/` - scripts/flatten_presets.py remains 0.6-hardcoded.
- For the 0.2 nozzle later: rebuild with `DETAIL=full` and new flat
  presets (machine "Bambu Lab X2D 0.2 nozzle", an 0.2-compatible
  process, e.g. "0.12mm Balanced Quality @BBL X2D 0.2 nozzle", and
  top_surface_line_width sized for 0.2).

## Second test print (2026-08-07) - ball lines missing, root cause confirmed

The 0.4-nozzle crisp test printed, but every line of the soccer ball was
absent: the traced seam/rim lines (measured 0.17-0.45 mm wide) and the
0.65 mm parametric rings.

- **Lesson: Bambu's X2D 0.12mm High Quality preset uses the CLASSIC wall
  generator with `detect_thin_wall` off. Classic prints NOTHING under
  2 perimeters (0.84 mm at 0.42 line width) - no warning, the feature
  is silently skipped at slice time. Raised line art for the 0.4 nozzle
  must be >= 0.9 mm wide, full stop.** This kills the earlier note that
  "continuous single-wall rings print cleanly" - with this preset there
  are no single walls at all.
- Fix (v3.16, crisp only): min-width enforcement on the traced ball web -
  iterative morphological grow of every sub-0.9 member (shapely, on the
  refined lines/arcs sampled at 0.1 mm; OCC 2D offsets return null on
  concave webs), clipped against navy and a 0.42 mm protected halo
  around the surfer. Cyan area +25%, drawing preserved. Rings 0.65 ->
  0.9 grown outward. Widths this small should have been caught at
  design time: 2D-measure every art layer (erosion test or 2*area/
  perimeter) against the printability floor BEFORE the first print.
- Also v3.17: YOUTH SOCCER CLUB at 1.5x never actually fit its arc -
  ink-kerning showed it needs ~110 deg where ~85 exist under the banner;
  it "fit" only because adjacent letters overlapped (gap 0.00). Brian
  chose a wide flat arch (R 72 centers circle, bottom y -21.4, uniform
  0.45 mm ink gaps, word breaks 2.2x). Lesson: bbox kerning lies for
  arched type - kern by INK distance (shapely bisection on arc angle),
  and check gaps numerically, not by eye on a render.

## Third test print (2026-08-07, v3.17) - bottom peeled off the bed

Print of the v3.17 file: top half perfect (widened ball lines, stars,
band, banner, CITY all crisp), but the bottom arc of the disc curled off
the bed mid-print (Brian watched it lift); the nozzle shredded the
lifted region - swoosh bottom, YOUTH SOCCER CLUB inlay zone, and the
disc edge became fuzz and smear.

- **Root cause: the CLI-composed project 3MF defaulted
  `curr_bed_type` to "Cool Plate", so the bed ran the Cool Plate
  profile at 35C on the textured PEI plate. PLA needs ~65C on textured
  PEI. Lesson: bambu-studio CLI exports NEVER set the plate - every
  composed project 3MF must explicitly set `curr_bed_type`
  "Textured PEI Plate" and sane `textured_plate_temp[_initial_layer]`
  values, and the bed temp readout is worth a glance at print start.**
- Note the temp keys are filament-scope: they must be listed in the
  FILAMENT diff slots (different_settings_to_system[1..3]), not slot 0,
  or the GUI silently resets them. Slot layout: [0]=process,
  [1..3]=filaments, [4]=machine.
- Fixed in exports/sharks-nametag-max-18.3mf (patched + round-trip
  verified) and pipeline/batch_roster.py (with round-trip asserts).
- The flattened X2D filament preset carries textured_plate_temp 55C;
  Bambu stock PLA textured is 65C - patched to 65 for adhesion margin
  (100% infill disc = high shrinkage stress at the rim).

## Full review before print 4 (2026-08-07, v3.19)

A four-agent numeric review of the model, STLs, 3MF, and pipeline before
the reprint found that the v3.16 min-width fix had only covered the tier
it was written for (navy/cyan ball art) - the raised WHITE art was still
sub-floor and would have silently vanished: banner border 0.60, CITY
white ring 0.78 + word fragments 0.38-0.78, swoosh tips, a C thin spot,
the surfer neck, plus 0.24/0.46 navy letter-frame channels.

- **Lesson: a printability fix scoped to one feature class WILL miss the
  others. The floor is a property of the whole print, so the check must
  be global** - implemented v3.19 as an in-model gate, demoted v3.20 to
  the standalone report `pipeline/audit_widths.py` when Brian chose to
  accept the drops rather than adapt the artwork. Filters in such checks
  need care: the old 0.30 mm2 residue exemption hid a real 1 mm seam
  break.
- **Lesson: white-on-navy microdetail cannot be widened into
  printability.** Widening the CITY word's surrounding navy was
  geometrically impossible (0.2-0.5 available where 0.9 is needed), and
  fusing the gaps erased the letterforms. The printable rendering flips
  polarity: solid white oval seal + the word as a flush NAVY inlay in
  its top - legible, and consistent with the YSC/back-name technique.
  General rule: at the wall floor, text needs its CONTRAST field to be
  printable, not just its strokes.
- **Lesson: bambu-studio CLI compose leaves the build item at the
  identity transform = part centered on the plate's front-left CORNER,
  3/4 off the bed.** Every composed 3MF must translate the item to
  ~(128,128,0); the GUI blocks slicing until moved, so it fails loud
  but wastes a cycle. Now baked + round-trip-asserted in the pipeline.
- Pipeline hygiene from the same review, all fixed with tests: CLI
  returncodes were unchecked and intermediates only cleaned on success
  (a failed rerun could repackage a STALE kid and report OK - pre-clean
  per kid + returncode asserts now); subprocess env inherited the shell
  (a leaked DETAIL=full/FINAL/SHOW changed the batch - env now pinned
  and "(crisp)" asserted); roster regex silently dropped unparseable
  names (count 13 + uniqueness asserted).
- Banner geometry: making the 0.9 border + printable navy channels fit
  required growing the banner (+0.97/+0.75) and moving the YSC arch down
  0.35; every clearance chain (YSC-banner-swoosh-pill) re-verified by
  bisection prototype in shapely BEFORE touching the CAD - tune in
  seconds, then port once.
- **Lesson: the in-model audit runs on the shapely mirror; the printed
  part is the tessellated STL. Members that pass at 0.88-0.90 in shapely
  can measure 0.80-0.83 on the mesh (tessellation chords + simplify).
  Detect-and-widen at a small margin above the audit radius, and always
  re-audit the exported STLs once** - the v3.19 STL re-audit caught two
  navy pinches and a web neck exactly in that band, plus a diamond the
  stencil closing had fused (the viable closing radius window was 0.01
  mm wide: 0.115-0.125).
- **Outcome (v3.20): Brian reverted every cosmetic adaptation after
  seeing v3.19 in the viewer.** Morphological widening turns long
  artistic tapers into lumpy hooked blobs (the crescent tips), and the
  CITY badge polarity flip read as a different logo. Standing rule:
  SOURCE FIDELITY OUTRANKS PRINTABILITY - sub-floor hairlines are left
  to drop at slice time (print 3 already validated that this looks
  fine), and any printability change that alters artwork must be shown
  in the viewer and approved BEFORE it lands in exports. What survived
  the revert: the web seam-break fix (invisible), plate centering, all
  pipeline hardening, and audit_widths.py as an informational report.

## Fourth test print (2026-08-20, v3.23, first PETG attempt) - cancelled on layer 1

Brian cancelled during the first layer: the M of MAX went to spaghetti and
the X looked melted; the 8, 1 and 2015-2016 on the same layer were
perfect. Printer state afterwards: gcode_state FAILED with fail_reason
0300400C ("task was canceled"), layer 0/44, no HMS, extruder had just
changed from slot 4 to slot 3 (white), so no white was ever laid down.

- **Diagnosis: localized first-layer adhesion failure on plate residue.**
  The photo shows faint ghost outlines of earlier prints on the textured
  PEI running exactly through the MAX region; the other glyphs sit on
  clean plate. PETG lines that do not bond bead up into blobs (the
  "melted" X) and the nozzle then catches and drags the neighboring
  thin M (spaghetti). Small isolated first-layer islands (6 mm letters)
  are the most sensitive features on the plate. Fix: wash the textured
  PEI with dish soap and hot water, dry, no fingers on the print area.
  Optional next lever if clean-plate letters still misbehave: slower
  first layer for the islands (initial_layer_speed 35, initial_layer_infill_speed 50;
  process keys, list them in diff slot 0); keep 245C first layer.
- **Estimate test prints from the real G-code, and crop coupons thin.**
  The first coupon plate (2026-08-21) was quoted as "30 minutes" with no
  slice behind it and took 2h18m: it carried the full 4.2 mm base and the
  back-inlay color changes. The tag's own G-code header says 2h 8m for 44
  layers, 21.1 g white / 5.6 g navy / 1.45 g cyan; three 44 x 28 coupons
  are 81% of the disc area with the same layer count, so ~2 h was
  predictable. Rules: (1) read `; total estimated time` from the last
  sliced G-code under /tmp/bamboo_model and scale by area x layers; (2)
  a top-surface coupon needs only the top ~2 mm (1.0 mm of base under
  the art), which cuts the layer count from 44 to ~18 and the time to
  about an hour (the 10 multi-color art layers dominate, not the area);
  (3) say "unsliced estimate" when it is one, and point to Studio's
  figure before the user commits a long print.
  Calibration from Studio (2026-08-21): full-base 3-coupon plate 2h18m,
  thin 2.2 mm plate 1h34m, whole tag 2h08m. About two thirds of a
  multi-color tag print is the ten art layers (changes, purges, tower),
  one third the base, so cropping a coupon's base saves ~45 min, not
  hours; cutting time further means fewer coupons or a smaller window.
- **Print 5 (clean, flipped plate) failed the M again, so the plate was
  not the cause.** The sliced G-code (Studio keeps the live slice under
  /tmp/bamboo_model/<date>/<id>/Metadata/.<pid>.<n>.gcode) shows the
  job's very first extrusion is the M of MAX: the X2D start gcode ends
  with no purge line, the nozzle travels at 1000 mm/s to the M and starts
  its inner wall, which arachne renders as a 0.38 mm bead in the notch.
  Un-primed nozzle + ooze string + thinnest bead of the layer = the M
  goes to spaghetti; the second island (X) caught the tail of it once.
  Fix baked into the pipeline (2026-08-20, diff slot 0): `skirt_loops`
  2, `skirt_distance` 3, `skirt_height` 1 (the skirt prints first with the
  initial filament and primes/wipes before any letter), `initial_layer_speed`
  30 and `initial_layer_infill_speed` 50 for the small PETG islands.
  Lesson: for multi-color first layers whose first island is tiny text,
  always give the job something sacrificial to prime on (skirt or flow
  calibration lines); read the first 100 lines after `; CHANGE_LAYER`
  of the real G-code when a first-island failure repeats.
- **The job also ran with navy and cyan swapped.** Printer-reported
  ams_mapping [2, 3, 1] (0-based tray ids) = filament 2 -> slot 4 (Lake
  Blue spool), filament 3 -> slot 2 (navy spool); the photo's text color
  (hue 210, bright) matches #0086D6, not #001489. Spools were in slots
  2/3/4 with slot 1 empty. Rule: load slot 1 white / 2 navy / 3 cyan
  before opening the project, and read the Send dialog's mapping table
  row by row before confirming; `scripts/x2d-status.py` shows the
  mapping the printer is actually running (`mapping` field).
- Minor: a PETG ooze string curled off the last letter when the nozzle
  lifted for the filament change (the curl above MAX); it would be
  buried in the white first layer. Watch for stringing generally.

## Print 6 (2026-08-21, v3.24, 1.2x YSC) - first complete PETG tag

Photo: projects/Sharks-nametag/images/print6-v324-first-full-petg.jpg.
The skirt + slow first layer fixed the first-island failure; all three
colors landed where they belong; the white stayed clean after the
navy/cyan changes; arachne printed what classic used to drop: the 0.6 mm
ball seams, the 0.65 mm rings, the banner's thin white border, the CITY
ring and letters; stars, band, surfer and SANTA CRUZ are crisp.

- **Weak spot: the raised YOUTH SOCCER CLUB.** At 1.2x (bars 0.54-0.76
  mm) the letters print as single stacked PETG beads 0.5 mm tall and come
  out blobby; YOUTH is partly filled in, SOCCER CLUB legible but chunky.
  Small raised single-bead text in PETG on the 0.4 nozzle reads rough
  at this scale; the flush inlay technique (back name, v3.15 YSC) prints
  the same letterforms crisp because the surrounding surface anchors
  them and the ironing pass smooths them. Options, in order of
  expected crispness: flush inlay (YSC_RAISE 0); raised + ironing off on
  the navy part (the ironing pass drags the 0.6 mm tops) + 1.3x; raised
  on the 0.2 mm nozzle (two walls at 0.44 mm, 3 to 4x time).
- Raised feature tops (cyan pentagons, surfer, white letters) show faint
  ironing texture; PETG ironing is acceptable, not glassy. Leave as is
  unless Brian objects; per-part ironing off is the lever.
  SUPERSEDED the same day: Brian called the ironing terrible (pits in the
  SANTA CRUZ tops showing navy, scuffed cyan); resolved by the coupon
  plate below (ironing out, two top walls in).

## Top-surface coupons (2026-08-21/22) - ironing out, two top walls in

Plate: `exports/top-surface-coupons.3mf` (full 4.2 mm base, 2h18m), the
real banner/CITY/ball-bottom/surfer window (x -22..22, y -17..11) three
times as one 9-part object with per-part overrides in
model_settings.config (metadata before `<mesh_stat/>`): A no ironing, B
PETG-tuned ironing 15% / 20 mm/s / 0.1, C no ironing + `top_one_wall_type`
"not apply" (two walls on every top surface); all `top_surface_speed` 60,
PETG Basic, textured 70C, skirt, arachne. Photo `~/Desktop/IMG_1527.jpg`
(camera at the printer front, plate +X = photo-right, so left A, middle
B, right C).

- **Winner C.** Deep uniform navy, bright crisp white letter tops with
  essentially no specks, clean pentagons, seams, surfer and CITY ring.
- A (single top wall) prints crisp edges but the monotonic top fill runs
  to every edge and the white tops stay granular with navy pinholes.
- B (ironing, even PETG-tuned) smears: swirl/drag marks on the navy
  surfer and the CITY ring, dark pits in A/C/R and in CITY, wavy letter
  edges, a blob at the surfer tip. **On PETG with this much small raised
  art, ironing of any flavor drags the tops; do not iron PETG here.**
- What makes "no ironing" look clean is the second top wall: it hides
  the fill-line ends around every small top region. Cost is a few
  minutes, not the 5 to 15% of ironing.
- Baked in: `pipeline/flatten_04.py` SMOOTH_TOP (`ironing_type` no
  ironing, `top_one_wall_type` not apply, `top_surface_speed` 60, dead
  ironing keys dropped), `pipeline/batch_roster.py` SMOOTH_KEYS + round
  trip asserts on all three values.
- YSC for the batch: FLUSH inlay (v3.25, `YSC_RAISE` 0). The coupon
  window never covered the YSC arc, so it does not prove raised bars
  clean up without ironing; print 6's blobbiness was single stacked
  beads as much as ironing drag, and a 0.5 mm raised hairline on a
  backpack tag is the first thing to get knocked off. Raised is one
  constant away if Brian prefers it after seeing the flush print.
- Estimate discipline still applies: `--slice` fails on these assembled
  3MFs, so the MAX 18 v3.25 figure is unsliced (print 6 G-code said
  2h08m with ironing; expect about 2 h) until Studio slices it.

## Gaps in the white art (2026-08-23) - toolpath diagnosis, CLI slicing, coupons

Brian: SANTA CRUZ and CITY (and stars, ball patches) still show gaps after
the no-ironing recipe; white text must be completely solid. Also: YSC
back to RAISED, base 20% thinner (v3.26: YSC_RAISE 0.5, BASE_T 3.36).

- **Read the toolpaths before changing settings.** `pipeline/top_coverage.py
  <plate_1.gcode> <out_dir>` rasterizes one layer (FEATURE + LINE_WIDTH
  hints, G2/G3 arcs interpolated, 0.02 mm/px) over the exposed white
  regions from the STLs and paints uncovered pixels red. Finding for the
  letters' top layer (z 5.36 for a 5.4 design: the 0.2 first layer shifts
  the 0.12 grid by 0.08): strokes 0.85 to 1.65 mm wide are ~100% arachne
  wall beads (outer 531 mm, inner 199 mm, top fill 10 mm, gap fill 1 mm),
  98% covered. So the "gaps" are seam gaps (Bambu `seam_gap` default 15%,
  aligned seams land on sharp corners = A apex, crossbar ends, N
  junctions), bead-count transitions, and gap fill at 250 mm/s, not
  missing paths. The star pockets and ball patches are floors of ONE
  continuous top-surface layer of the disc (lines run under the navy
  band, Bambu treats the white's top as "top surface" even under another
  material), so their marks come from the navy pocket walls/seams.
- **CLI slicing: works only on Studio-saved projects.** `bambu-studio
  --slice 1 --export-3mf out.3mf <gui-saved>.3mf` reproduced Studio's
  estimate exactly (1h56m10s) and embeds Metadata/plate_1.gcode. Our
  CLI-raw files fail: without plate `model_instance` entries the slicer
  loads plate 1 as empty ("The supplied file couldn't be read because
  it's empty", -6); with them it fails "No valid nozzle found" / "could
  not found extruder_type Bowden" because the live X2D extruder keys (3
  variants per extruder, filament_map "1 1 1", extruder_nozzle_stats,
  extruder_ams_count...) are only written by the GUI, which also
  re-resolves all presets on open (159 keys differ between a GUI save
  and our flatten; our `different_settings_to_system` overrides are what
  survive, mapped by variant name). `--load-assemble-list` + `--slice`
  aborts with free(): invalid size (xvfb does not help). Practical loop:
  have Brian save the project once in Studio, then CLI-slice that file.
- **Coupon plates are now a script:** `pipeline/coupons.py` crops windows
  of the canonical STLs with trimesh (`slice_mesh_plane`, cap=True, cut
  the flat z plane FIRST or the cap stays open), 1.0 mm slab under the
  art, variants side by side as one object with per-part overrides
  (before `<mesh_stat/>`), CLI round trip verified (percent options come
  back normalized: write "0%" not "0"). 2026-08-23 plate
  `exports/solid-text-coupons.3mf`: P = seam_gap 0% + small perimeters
  (radius < 10 mm) 30 mm/s + gap fill 40; Q = P + wall_distribution_count
  3 + wall_transition_filter_deviation 50%; R = Q + print_flow_ratio
  1.03; windows W1 (S-A-N-T-A, CITY left, ball bottom, surfer) and W2
  (5 top band stars). Small coupon layers can hit the 12 s min layer
  time, so absolute speeds are lower than on the tag; the comparison
  between variants stays fair.
- **The junction holes are geometric, and settings only halve them.** The
  O/P/Q/R coupon print (IMG_1529) + the void metric (rasterize every
  letter layer, stack, keep voids >= 3 layers deep and >= ~0.13 mm wide)
  agree: seam/speed changes fix the loop-start/stop half (Q visibly
  better, R's +3% flow harms: strings, fuzz, blurred sub-mm glyphs), but
  the junction voids are identical across O/P/Q/R. Sweeping 13 settings
  variants offline (assemble-list objects + graft + `--slice`, 20 s per
  round, zero prints): classic is worse, 1 wall + fill no better; only
  `min_feature_size` 10% + `min_bead_width` 50% halves the visible voids
  (dot centers die; walls 0.30/0.32 would cut another 25% but thin-bead
  quality is unproven). Locked solid-text package (process-wide):
  seam_gap 0%, small_perimeter_speed 30 / small_perimeter_threshold 10,
  gap_infill_speed 40, wall_distribution_count 3,
  wall_transition_filter_deviation 50%, min_feature_size 10%,
  min_bead_width 50%. Real-tag verification: visible letter voids
  1.44 -> 0.39 mm2, largest 0.30 -> 0.17. The floor below that is the
  0.4 mm bead itself: a 0.2 mm nozzle is the zero-hole path (3-4x time),
  letterform micro-editing the design-side alternative.
- Photo morphology (IMG_1528, 0.14 mm/px): the letter marks are
  junction/terminal voids 0.15-0.4 mm (A crossbar joins, R join, N join,
  stroke ends) plus dark-center pinholes in the 1.0 mm CITY bullets (two
  perimeters, no third bead); stroke tops are flat with no center
  groove. That is loop start/stop + bead-transition behavior, consistent
  with the toolpaths.
- **Flush matrix must match the extruder count.** The X2D wants
  flush_volumes_matrix as 2 extruders x (n_filaments)^2 (= 18 for 3
  filaments), flush_multiplier/_fast with 2 entries, nozzle_flush_dataset
  with 6. A 16-entry single-nozzle placeholder makes Studio expand it
  by reading uninitialized memory (garbage like 6.85e-310 in Brian's own
  saves) until a NaN kills slicing ('Failed to serialize
  flush_volumes_matrix'). All builders now write the dual-extruder
  block; Studio recalculates real values from the colors on load.
- **Object-level vs region-level keys (PrintConfig.hpp).** seam_gap,
  wall_distribution_count, wall_transition_length/filter_deviation,
  min_bead_width, min_feature_size are PrintObjectConfig: they only work
  as OBJECT settings; per-PART metadata carries PrintRegionConfig keys
  only (speeds, small_perimeter_*, gap_infill_speed, print_flow_ratio,
  line widths, wall_loops, infill_wall_overlap, ironing). A coupon plate
  that compares object-level keys must therefore be several OBJECTS (the
  CLI assembler's `assembled_params[].print_params` does that), not one
  object with per-part overrides. The first 2026-08-23 plate got this
  wrong and was rebuilt with an O control + P/Q/R objects.
- **Offline slicing of our own files: graft Studio's live settings.**
  `pipeline/studio-live-settings.json` = the project_settings.config of
  a project Brian saved in Studio (same printer/filaments/process; refresh
  it whenever the recipe or presets change). Writing it into a CLI-made
  3MF (keep our 3D/, model_settings with plate instance lists) makes
  `bambu-studio --slice 1 --export-3mf` work and match Studio's numbers.
  Used it to prove the coupon objects differ in the G-code: O loops at
  60 mm/s with 0.060 mm seam gaps, P/Q/R at 30 mm/s fully closed, gap
  fill 250 vs 40, R +3.0% extrusion per mm; plate estimate 1h21m.
- Candidate keys verified in PrintConfig.cpp: seam_gap (15%),
  small_perimeter_speed (50%), small_perimeter_threshold (0 = off),
  gap_infill_speed (30 default, X2D 0.12 preset 250), wall_distribution_count
  (1), wall_transition_filter_deviation, wall_transition_length (100%),
  min_bead_width (85%), print_flow_ratio (1).

- **Letterform micro-fillets do NOT fix arachne junction voids
  (2026-08-23, offline).** After the max-18 gate print (IMG_1530) still
  showed junction pinpricks, v3.27 added `fillet_line_sketch`:
  shapely closing+opening at FILLET_R on the banner + CITY white in
  final mm space, with an adaptive ladder (full / close-only / raw) so
  thin pieces (the CITY oval ring loses 35% under opening) fall back to
  closing-only, plus per-piece area/hole asserts and a FILLET_DEBUG
  overlay PNG. The offline sweep (W1 coupons at r 0/0.15/0.25/0.35 as
  four assembled objects, graft + slice + stacked void metric, region
  split banner vs CITY) refuted it: banner visible voids 0.24 control
  vs 0.29-0.37 filleted - the N wedge shrinks but new specks appear
  distributed along the rounded arcs. The voids live where wall beads
  COLLIDE (the stroke-junction medial axis), not at the outline corner;
  rounding the outline just relocates the collision. CITY residuals are
  sub-bead stroke centers, equally untouchable. `FILLET_R` stays 0 in
  the canonical file (r=0 is regression-identical), kept as a
  documented dead end.
- **The 0.2 nozzle really is the zero-void path - provable offline.**
  Patch the grafted live config to 0.2 geometry (`nozzle_diameter`
  ["0.2","0.2"], `layer_height` 0.08, `initial_layer_print_height`
  0.12, every non-percent `*_line_width` 0.22) and the same coupon
  plate slices clean: CITY 0.73 -> 0.04 mm2, banner -> one 0.20 blob
  that is the W1 crop boundary through the S (identical across all
  fillet radii = crop artifact, not a void). 1.6 mm strokes fit ~7
  beads at 0.22 with gentle transitions, so the junction collisions
  vanish below the 0.13 mm visibility floor. Cost from a real full-tag
  re-slice at the 0.2 patch: 3h43m vs 1h36m (2.3x) - and the patch
  keeps the 0.4 profile's speeds, so genuine 0.2 presets will be
  slower still. Caveat: the patched config is a metric vehicle, not a
  printable recipe - build real flattened 0.2 presets before printing.

## Two-plate roster project (2026-08-22) - Bambu CLI multi-plate assembler

Brian: "create a project file with roster using 2 plates, 6 nametags on
one plate and the rest on the other". Result
`exports/sharks-nametag-roster-plates.3mf` from `pipeline/plates.py`
(layout `images/roster-plates-layout.png`): plate A = the first six of
roster.md, plate B = the other seven.

- **Route that works: `bambu-studio --load-assemble-list plates.json`**,
  the CLI's own multi-plate assembler (schema in src/BambuStudio.hpp):
  `{"plates": [{"plate_name", "need_arrange": false, "plate_params":
  {"curr_bed_type": "Textured PEI Plate"}, "objects": [{"path": stl,
  "count": 1, "filaments": [n], "assemble_index": [k], "pos_x": [x],
  "pos_y": [y], "pos_z": [0]}]}]}`. Same `assemble_index` within a plate
  merges STLs into one object (our 3 color parts); `filaments` sets the
  part extruder; with `need_arrange` false the positions are
  plate-relative mm and the CLI adds the plate origin itself (plate 2 at
  x 307.2 = 256 x 1.2). Pass `--load-settings` + `--load-filaments` as
  usual, but NO input files and NO `--load-filament-ids` (that flag is
  per input file and the CLI errors "loaded_filament_ids size 3 should be
  the same with input files size 0"). Loading several 3MFs as inputs is
  not supported (return -4 immediately).
- Gotchas: a ":" in `plate_name` makes the CLI write an empty
  `plater_name` (letters and spaces are safe); the CLI defaults the bed to
  Cool Plate, so PETG validation fails unless `plate_params`
  `curr_bed_type` is given (it lands as per-plate `bed_type`) and the
  global `curr_bed_type` is patched as before; objects come out named
  `assemble_N`, parts `<stl>_1` - rename them (object names are what the
  X2D lists for skip-object, so `NAME NUM`); filament_colour comes out as
  one entry - patch to the three colors as batch_roster does;
  `wipe_tower_x/y` come out as `['165','165'] / ['250','250']` on this
  path - set them explicitly per plate.
- **Geometry vs bookkeeping in a Bambu 3MF:** the volume transformation
  is the `<component transform>` in `3D/3dmodel.model` (bbs_3mf.cpp:
  `volume->set_transformation(comp_transform * ...)`); the
  model_settings.config part `matrix` is only stored as
  `source.transform`, and the exporter writes `volume x source` back, so
  a CLI round trip DOUBLES the matrix (46 -> 92) while the geometry stays
  put. Validate positions from item transform + component transform,
  never from the part matrix.
- Layout rules used: disc 76.2 on the 256 bed -> 3 x 3 grid with centers
  46/128/210 (7.9 mm edge margin for the 3 mm 2-loop skirt, 5.8 mm
  between discs). Keep the back-left slot empty for the wipe tower and
  pin it at (12, 203): Brian's 12:27 Studio slice of one tag shows the
  real 3-color tower footprint is ~43 x 41 mm (prime_tower_width 60, rib
  wall; the tower extrusion bbox is what to measure, the WIPE_TOWER
  comment blocks include travel) and Studio auto-placed it at (35.5,
  197.6), which would collide with a back-left disc. Clearance to every
  disc >= 34.6 mm.
- CLI `--slice 0` on the assemble-list path crashes (`free(): invalid
  size`, rc 134) after the bed-type fix, so plate estimates stay
  unsliced: one tag with the coupon C recipe = 1h56m in Studio; by-layer
  plates pay the color-change/tower overhead once per layer for the
  whole plate, so expect roughly 6.5 to 9 h (6 tags) and 7.5 to 10.5 h
  (7 tags), about 14 to 20 h total vs ~25 h as 13 singles. Read Studio's
  figure before committing.

## Clean ball and hairline seams (2026-08-20, v3.22 / v3.23)

- **Morphological widening is a dead end for line art.** Growing
  hairlines until they pass a width floor leaves lumpy junctions, knobby
  ends and uneven widths (v3.16 ball web, "the soccer ball is messy").
  Rebuild instead: keep the traced solid shapes (pentagons) exactly,
  turn every hairline into a fitted centerline (line or gentle arc
  through cross-section centroids) buffered to ONE uniform width, run
  each end into a hiding region (neighbor shape core, rim ring, clip)
  so no cap shows, trim sub-floor stubs rather than growing them, and
  close tiny acute wedges with a small closing. Layout stays traced,
  only the stroke rendering is synthetic. This is "refit", the same
  principle as v3.11, not "rebuild from primitives".
- **Arachne is the right wall generator for raised line art on the 0.4
  nozzle.** Classic walls need 2 perimeters (0.84 mm) and silently drop
  thinner members; arachne prints a single variable-width bead down to
  ~0.45 mm, so 0.6 mm seams and the 0.65 mm rings can look close to the
  source hairlines. Set `wall_generator` arachne in the process
  overrides AND list it in `different_settings_to_system[0]`. Unvalidated
  on this printer until the PETG test print: judge single-bead lines
  (free-standing 0.6 wide x 0.6 tall) for wobble.
- **Print floor is a property of the slicer setting, not the nozzle
  alone.** MIN_LINE_W 0.9 (classic) vs WEB_FLOOR 0.5 (arachne) in the
  model; `pipeline/audit_widths.py` FLOOR follows the active generator.

## Pre-print audit before the PETG print (2026-08-20)

Full settings audit of the composed 3MF against the stock X2D presets plus
a read-only look at the printer. Lessons, independent of the verdict:

- **CLI-composed project 3MFs carry a placeholder flush matrix** (4x4,
  uniform 280) regardless of filament count or colors. Studio's X2D
  schema is nozzles x filaments^2 (18 entries for 3 filaments); on a
  size mismatch the GUI rebuilds the matrix from `flush_volumes_vector`
  (140 + 140 = 280 everywhere), it does NOT auto-calculate from the
  colors on open. Re-calculate in the Flushing Volumes dialog before
  slicing, or bake an 18-entry matrix in the pipeline; Bambu's calculator
  wants roughly 640 for navy->white and 500 for cyan->white.
- **`filament_map` / `filament_map_mode`** come out of the CLI as ["1"] +
  "Auto For Flush". On a dual-extruder profile with `filament_printable`
  3 the GUI may route a color to the Bowden support nozzle. Bake Manual
  [1,1,1] for single-nozzle multi-color parts and glance at the
  left/right assignment in the GUI.
- **Flatteners must merge the machine preset's `include` templates**
  (start / end / layer-change / filament-change / timelapse gcode);
  without them the embedded gcode is the generic base gcode. The GUI
  masks this (machine diff slot 4 empty = stock X2D templates restored),
  CLI slicing would not. Also read the live bundle
  (`~/.config/BambuStudioBeta/system/BBL`, 02.08.00.04), not the stale
  `~/.config/BambuStudio` one (02.07.00.08).
- The 0.2 mm first layer shifts the 0.12 grid by 0.08: design heights
  that are 0.12 multiples slice 0.04 low (disc top 4.16, part 5.36; back
  inlay 0.6 deep = 4 navy layers; YSC letter tops at 4.70 sit exactly on
  a slice plane). Harmless here; `initial_layer_print_height` 0.24 would
  align the grid if ever needed.
- **Studio's AMS sync overwrites the project's filament list on connect.**
  2026-08-20: the 3MF on disk had white/navy/cyan, but with PETG blue in
  AMS slot 2 and PETG white in slot 3 (slots 1 and 4 empty), Studio
  replaced filament 3 (cyan) with the white from slot 3 and appended the
  two support filaments from the virtual trays, so the preview showed
  two colors. Load the spools in file order (slot 1 white, 2 navy, 3
  cyan) BEFORE opening the project, or after opening set filament 3's
  color back to cyan; the file itself needs no change. The navy spool's
  RFID color is #001489 (Bambu PETG Basic Blue), darker than the design's
  #00395E; that only affects the preview and the flush calculation.

- Printer state is readable from the terminal over LAN MQTT
  (`scripts/x2d-status.py`, [[x2d-printer-control]]): nozzle type and
  diameter per extruder, AMS tray contents, plate id, firmware. Use it
  for the nozzle + filament pre-flight instead of the touchscreen.

## Fill-core letters at 0.2 (2026-08-24) - modifier part, one wall, raster top

Brian's 0.2 coupon verdict: only N and CITY perfect; S, A, T, A still
carry ~0.1 mm marks at crossbar/stem junctions. Those are the letters
where arachne wall beads collide; the control toolpath shows the A
crossbar joins and the N center as gap-fill blobs between walls.

Fix found offline (fillcore sweep, `exports/fillcore-coupons-02.3mf`):
- Letter tier as a `modifier_part` (letter outlines buffered 0.3 mm,
  z 1.60-2.30) carrying `wall_loops 1` + `top_one_wall_type all top`:
  one outer wall, everything else raster top fill, so each junction is
  crossed by continuous lines. Per-part keys must be region keys and
  sit before `<mesh_stat/>`; survives CLI round trip and `--slice`.
- `detect_narrow_internal_solid_infill` is an OBJECT key (ignored in a
  modifier). Set it to 0 on the object (CLI `print_params`), otherwise
  the narrow-region conversion turns the letters' solid core back into
  concentric arachne beads and the junction wedges reappear in every
  layer under the top.
- Metric (stacked >=3/5 top layers, 0.13 mm opening): control 0.03 mm2
  visible + 0.31 mm2 top-interior uncovered; V7o 0.00 + 0.02.
- Dead ends: `infill_wall_overlap` is a sparse-infill key in 2.08 and
  does nothing on solid fill; `top_bottom_infill_wall_overlap` does not
  exist; 2 walls + fill is the worst of the family; 0.25 top lines
  worse; the connected monotonic pattern leaves apex triangles at the A
  tops depending on plate position.
- Trade: 256 line starts per letter top (V7o) vs 48 for the connected
  pattern (V3); V3 is the fallback if starts show as dimples.
- Graft that slices a 0.2 file offline: keep the file's own 0.2
  `project_settings.config` and add only the keys missing/empty vs
  `pipeline/studio-live-settings.json` (host, notes, gcode placeholders,
  bed areas, extruder stats, filament_map/filament_nozzle_map at 3
  entries). Overwriting the live 0.4 config the other way fails (rc 156).
- 0.4 nozzle, same size (2026-08-24 evening, `exports/fillcore-coupons-04.3mf`):
  the 0.2 winner does NOT transplant as-is. One 0.42 wall leaves a
  0.8-1.0 mm channel and 0.42 raster lines at 45 deg leave stacked
  boundary triangles (C1 0.43 mm2, worse than the 2-wall control 0.23).
  Fix at 0.4 = narrower fill lines in the modifier: `top_surface_line_width
  0.3` + `internal_solid_infill_line_width 0.3` (0.01), then
  `infill_direction 90` (C7: 0.00 / 0.00, 185 starts, 10 mm gap fill) or
  `infill_direction 0` (C8: 0.00 / 0.15, 100 starts, 47 mm gap fill along
  the walls). Keep the outer wall at 0.42 (0.3 wall is worse). Letter tier
  at 0.12 layers = 5 letter-only layers 1.76-2.24. Cost: +6 s per tag.
- Rule of thumb from both nozzles: the letters need (a) one wall so the
  offset never pinches, (b) the object key so the core stays raster, and
  (c) fill lines narrow enough relative to the channel (0.22 in a 1.2 mm
  channel at 0.2; 0.30 in a 0.8-1.0 mm channel at 0.4) that the raster
  sawtooth at the wall does not stack.
- PARITY (2026-08-24 late): solid and top fill alternate 90 deg per
  layer, so the direction on the TOP layer depends on the object's layer
  count parity. A coupon must have the same parity as the tag (37 layers
  at 0.12 mm on 0.4; fillcore_coupons.py asserts it) or the C7/C8 verdict
  flips. With the tag's parity the 0.4 bake is `infill_direction 0`
  (lines across the strokes: 0.00 visible / 0.00 top interior); 90 runs
  along the stems and leaves gap-fill slivers at the walls.
- PHYSICAL VERDICT 0.4 (2026-08-25, thin plate): C7 (infill_direction
  90, lines along the stems, 65 starts) beat C8 (lines across, 164
  starts) and the control, reversing the metric's order. The eye keys
  on fill-line starts and dimples; the 0.11-0.14 mm2 wall slivers the
  metric counted against C7 are invisible. Use the metric to reject
  variants with stacked voids, not to rank the survivors; the coupon
  ranks them.

- OBJECT KEY SIDE EFFECT (2026-08-25): `detect_narrow_internal_solid_infill
  0` is object-wide; it turns every narrow internal-solid island (< 6 mm)
  rectilinear, including the navy back-inlay strokes in layers 2-4
  (visible on the camera, hidden in the finished part). The detection is
  read from the object config (Fill.cpp is_narrow_infill_area), so no
  region key restores it; but `internal_solid_infill_pattern` IS a
  region key: a second modifier over the back text (+0.5 mm, z 0.16-0.56,
  pattern concentric) restores the loops without touching layer 1, layer
  5 or the front letters. Baked into batch_roster.py / plates.py.

- Thin letters-only coupons (pipeline/fillcore_coupons.py): SANTA bbox +
  1.5 mm, 0.24 mm navy stub, 0.30-0.40 mm slab; 0.2 plate 38 min,
  0.4 plate 15 min; metric identical to the full W1 coupons. Trade:
  no color changes and shorter layer times in the letter tier (hotter
  cadence than the tag, pessimistic for the tops).
- Tools live in the vault now: pipeline/graft_slice.py (offline slice of
  any CLI export; a single-tag export also needs the plate
  model_instance, filament_map Manual 1/1/1, and a tower clear of the tag)
  and pipeline/toolpath_voids.py (stacked-void metric + renders).

- Physical coupons pending: 0.2 full plate printing 2026-08-24 evening
  (V0/V7o/V3); 0.4 thin plate (C0/C7/C8, 15 min) after the nozzle swap.

## Outcome and experiment catalog (2026-09-08)

Result: all 14 tags printed from `projects/Sharks-nametag/final/` with
clean letters; Brian: "the final print worked. All the kids are happy."
Turnkey version of what follows: [[lettering-x2d]].

What changed between the first PETG attempt (2026-08-20) and the final
files (2026-08-26):

- Model: v3.22 clean ball web + hairline seams (fitted centerlines, no
  free ends); v3.24 YOUTH SOCCER CLUB at 1.2x on the source arc; v3.26
  base 3.36 mm, YSC raised 0.5; v3.27 `FILLET_R` (kept at 0, dead end).
- Process: SMOOTH_TOP in flatten_04.py (no ironing, 2 top walls, top 60,
  seam_gap 0%, small perimeters 30/10, gap fill 40, arachne with
  distribution 3 / transition deviation 50% / min feature 10% / min bead
  50%, 50% zig-zag infill, skirt 2/3/1, first layer 30/50, tower brim 5 +
  rib + fillet), a correct 2 x 3 x 3 flush block.
- Letters: modifier part (1 wall, all-top, 0.3 mm fill lines, direction
  90) + object key detect_narrow_internal_solid_infill 0; back inlay
  counter-modifier (internal_solid_infill_pattern concentric).
- Tower: rule-placed (closest free spot to center, off the edges).
- Pipeline (all in pipeline/): batch_roster.py, plates.py, fillcore_mod.py,
  fillcore_coupons.py, graft_slice.py, toolpath_voids.py,
  gcode_features.py, backfix_probe.py, flatten_04.py / flatten_02.py;
  scripts/x2d-status.py for read-only printer telemetry.

Experiments, in order, with outcome (P = physical print, O = offline):

| date | experiment | outcome |
|---|---|---|
| 08-06/07 | P1-P3 PLA, ironing + classic walls | letters crisp but bed peel, ball lines lost; PLA rejected (57 C HDT) |
| 08-20 | P4, P5 PETG v3.23 | first island (M of MAX) spaghetti: un-primed nozzle; fixed by skirt priming + slow first layer |
| 08-20 | O clean ball + hairline seams (v3.22) | seams 0.6 mm as single arachne beads, kept |
| 08-21 | P6 v3.24, first complete PETG tag | junction marks on letters, CITY dot pinholes, ironing pits |
| 08-21/22 | P top-surface coupons A/B/C (2h18m, thin 1h34m) | ironing on PETG pits/smears; no ironing + 2 top walls wins |
| 08-23 | P solid-text coupons O/P/Q/R | all still holed at junctions; +3% flow worse; marks are geometric |
| 08-23 | O 13-variant sweep + toolpath void metric | classic walls worse; 1 wall + fill "no better" (object key missing); min feature/bead best; baked |
| 08-23 | P gate IMG_1530 | ~15 junction specks, failed the bar |
| 08-23 | O outline micro-fillets r 0.15-0.35 | refuted: voids sit on the medial axis, fillets relocate them |
| 08-23 | O 0.2 nozzle prediction | zero visible voids predicted at 2.3x time |
| 08-24 | P7 0.2 letter coupon (W1) | N and CITY perfect, S/A/T/A still marked; brimless tower peeled at the corner |
| 08-24 | O fill-core sweep at 0.2 (V0-V8o) | 1 wall + all-top + object key = 0.00 mm2; infill_wall_overlap inert; 2 walls worst |
| 08-24 | O fill-core at 0.4 (C0-C8) | direct transplant worse (0.42 lines); 0.3 mm fill lines + direction fix it |
| 08-24 | O thin letters-only coupons | 15 min at 0.4 / 38 min at 0.2; layer-count PARITY flips the fill direction |
| 08-24/25 | P8 0.2 fill-core plate (3h39m) | V7o clean; time and stringing argue against 0.2 |
| 08-25 | P9 0.4 thin plate (15 min) | Brian: C7 (lines along stems) best, reversing the metric's C8 |
| 08-25 | P10 gate MAX 18 at 0.4 | passed; object key made back-inlay layers 2-4 rectilinear (hidden), fixed with the concentric modifier |
| 08-25 | O tower relocation + anti-peel pins | rule encoded; tag toolpaths byte-identical |
| 08-26 | build final/ (14 singles + 2 plates) | all asserts green; MAX 18 identical to the gate |
| 08-26..09 | P batch | success, 14/14 |

Studio's calculated flush volumes for this filament set (as printed):
white->navy 223, white->cyan 260, navy->white 629, navy->cyan 430,
cyan->white 492, cyan->navy 182 mm3.

## Open

- Project complete 2026-09-08. Leftovers from the 2026-08-06 full-detail
  variant (`exports-full/`, `sharks-nametag-max-18-full.3mf`, `-full`
  STLs) still on disk pending Brian's decision.
- TEAM_YEARS=2015-2016 constant.
