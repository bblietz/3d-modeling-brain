---
type: project
project: NACS-wall-holder
date: 2026-09-16
status: REVISION 2026-10-08, CAD and 3MF done, not printed. Drum 1 in deeper and 90 across, crest lip 1.5 in with the TESLA wordmark, frame line, T back, cavity 1/2 in deeper (cleat 1.75 in); cleat catch window 5 mm, face inlays in a second colour; sliced 8 h 47 min, 442 g. The 2026-09-19 holder (v7 cavity, 4 in base, round flange, 1/16 in roundovers) is on the wall and working great.
tags: [x2d, nacs, tesla, wall-mount]
---

# NACS wall holder (Tesla Wall Connector Gen 3, 48A)

Our own design for a wall-mounted dock for Brian's Tesla Gen 3 Wall Connector handle, with a cable wrap hook.

## Revision of 2026-10-08 (CAD and 3MF done, not printed)

Brian asked for a deeper holder, a taller squared-off top lip and a deeper wand cavity. Picked from
rendered options (page: https://claude.ai/artifact/5u3wgRBUTWngnCdjFuPzKB, built by
`pipeline/render_options.sh` + `pipeline/options_page.py`, renders in `images/options-2026-10-08/`):

- Drum `drum_l` 75 to 100.4 (1 in deeper; "2 in" was first asked, then "only be 1 in deeper"). The
  holder stands 105 mm off the wall; 72 mm of straight drum for the loops (was 47).
- Drum `drum_r` 40 to 45 (diameter 90) because the cavity 1/2 in deeper did not fit the 80 drum: the
  cavity crosses the drum at 45 degrees, and `pipeline/depth_limit.py` measured the wall left at its far
  corner at 11.4 / 5.9 / 0.1 mm for cleat depths 1.25 / 1.5 / 1.75 in on the 80 drum; the 90 drum
  leaves 10.3 mm at 1.75 in (first estimated at 5 from the 80 drum's numbers; the mouth moves out with the
  drum, so the far reach grows less than the radius). The flange stays 104, so `fillet_flange` 12 to 7 and `fillet_plate` 8 to 7
  (the plate blend's foot must stay inside the screw countersinks, 52.7 off the axis; it is at 52).
- Cavity: `cleat_depth` 31.75 to 44.45 (1.75 in, "1/2 deeper, 90mm drum"). `mouth_z` 61.48 keeps the
  wand at the far end with the mouth top 3.6 mm under the flange as validated (`cut_top` 93.8 = flange
  underside 97.4 minus 3.6); the deepest corner is now 23 mm off the wall, no longer in the plate.
  Checks: `holder.stl` one watertight body, 612 cm3; docked clash 0 mm3; `insertion.py` (GOAL_TIP
  raised 45 to 72 for the deeper mouth) WAY IN yes at 0 to 9 degrees, HOLD 19.6 mm with 1.87 of 3.57 mm
  engaged, tip 3.20 mm from the end wall at -3.0 degrees: the v7 numbers, because the rounded floor lip
  now sits under the grip, which the tool does not model (the 1.25 in cavity gave 3.37 / -3.5 / 1.75 /
  20.4 with the lip on the housing).
  - NOT PROVEN: the first 1/2 in of the grip (48 to 61 mm from the tip) now sits inside the opening,
    where Tesla's CAD ends. The cavity there is the housing's last section plus the 0.1 per mm flare
    (about 2 mm per side at the rim) and the floor on Tesla's line. If the grip or the top button is
    bigger than that, it will not dock. Ask Brian for the handle's width and height 1/2 in and 1 in
    behind the glossy housing, and the button height, before printing.
- Lip ("the top lip of the holder should be 3 in taller, and have a squared off profile with rounded
  corners"): 3 in "is too tall", so `tab_rise` 38.1 (1.5 in above the flange's top). Width: option B,
  full width 104 (tangent to the flange), over A (72 mm, clearing the top screws) and C (the whole
  flange squared off). Outline: Brian asked to "combine the top of the arch lip with the shield lip"
  after seeing plain / arch / shield / gable: `tab_style = "crest"`, sides tapering to `tab_top_w` 84
  tangent to the circle, top an arc crowned `tab_crown` 10, corners `tab_r` 12.7, 8 mm thick, all edges
  edge_r (sphere minkowski). Trim: `tab_trim = "frame"` (2.5 mm line 1 mm deep, 6 mm in, round the
  whole face outline), yes.
- Face: Brian first asked to "remove the tesla artwork and put something more generic"; four generic
  emblems were built and shown (bolt, plug, the NACS face traced from the housing STEP by
  `pipeline/nacs_face.py` into `nacs_face.scad`, the letters EV; `emblem` parameter), picked "bolt",
  then "actually add the tesla logo back in. keep border. Tesla text at top that follows the curve of
  the lip": `emblem = "tesla"` (the T, 59 mm, as before) and `lip_text = true`: the official wordmark
  (`reference/tesla-wordmark.svg`, the wordmark group of Wikimedia Tesla_Motors.svg with its transform
  shifted so the viewBox starts at 0 0) 62 mm wide, cut into 0.4 mm strips and stood on the crest's own
  arc 2 mm under the frame line (`wordmark_arc()`). The generic emblems stay in the file as options.
- Top screws: the full-width lip hides them from a straight driver. Keyhole slots (`top_mount =
  "keyhole"`, hang on the top screws, drive the bottom two) and driver holes through the lip
  (`"holes"`) were built and shown; Brian: "just keep regular holes, now that the lip is slightly out
  of the way" (`"none"`). Told him: the crest's edge is 6 mm outside the top screw centres at that
  height, so the driver goes in at about a 6 degree tilt, not straight.
- Print (`pipeline/make_coupon_3mf.py holder`, same recipe): 8 h 37 min, 438 g (426 g PETG, 12 g support
  interface), 351 layers, 104 x 142 x 105 mm on the bed. The prime tower moved from (212, 180) to
  (212, 40): the lip's tree supports root further out and left it 13.2 mm from the part (the build
  asserts 15); now 20.2 mm. Screw pads 90% solid, plain plate 18%. Learned on the way: the 3MF item
  transform puts the model's ORIGIN (the plate centre) at BED_CENTRE, not the bounding-box centre; a
  bounding-box correction to the pad check put the windows off the plate (pads 0.0).
- Tools: `pipeline/depth_limit.py` (far-wall thickness vs cleat depth, from the raw cavity:
  `part="cavity"` in holder.scad), `pipeline/render_options.sh` + `pipeline/options_page.py` (the
  options page), `pipeline/nacs_face.py`. Pipeline constants parsed by regex (`insertion.py`,
  `make_coupon_3mf.py`, `renders_page.py`) must stay literal numbers in holder.scad, never
  expressions. OpenSCAD's `import(svg, center = true)` centres on the viewBox origin, not on the
  content, so artwork viewBoxes must start at 0 0.

### Later the same day (2026-10-08)

- Cleat ("the cleat should be a bit bigger. The wand has a tendency to fall off if not seated
  perfectly"). The cleat fills the lock pocket to within 0.45 mm on every side and cannot grow (the
  50% longer cleat of September ran into the nose's underside), so what grew is the catch window:
  `tip_gap` 2.5 to 5 (the pocket's wall lands behind the edge if the nose is pushed to within 5 mm
  of the stop, twice the old window; the wand also slides back 5 mm on release before it catches)
  and `undercut` 15 to 20 degrees (the pull seats the pocket's wall deeper into the hook). Cost: the
  cavity 2.4 mm longer (mouth depth 71.6), far wall 10.3 to about 8.3 mm, `mouth_z` 61.43 (mouth top
  still 3.6 under the flange). `insertion.py` (GOAL_TIP 75): WAY IN yes 0 to 9 degrees, hanging tip
  5.70 mm from the end wall at -3.0 degrees, 1.87 of 3.57 mm engaged, HOLD 19.6 mm. Docked clash 0.
- Face in a second colour ("the tesla logo and the border should be a different filament color
  fill"): the T, the TESLA wordmark and the frame line are now flush inlays, `logo_depth` and
  `frame_depth` 1.2 (four 0.30 mm layers), exported as `holder-inlay.stl` (`part = "inlay"`, the same
  2D shapes that cut the body, 12 bodies, 2.35 cm3) and assembled with `holder.stl` into ONE object
  by `make_coupon_3mf.py` (`PARTS`, `--assemble`, `--load-filament-ids 1,3`): filament 1 body PETG,
  2 support interface on the second nozzle, 3 a second PETG in another AMS slot for the inlay (preview
  colour #D9D9D9; Brian picks the real one in the AMS). The build asserts each part's name and
  extruder in model_settings.config and that filament 3 prints grams. Slice: 8 h 47 min, 442.5 g
  (426.6 body, 12.4 support, 3.5 inlay), 351 layers, tower 19.9 mm, pads 90%. Renders show the
  inlays in gainsboro (`show_inlay`).
- `holder.stl` now has one spot (41, 10.5, 45) where two surfaces touch along an edge (trimesh:
  not watertight, 2 edges in 4 faces, 6 zero-area triangles; Manifold reports NoError). The CLI
  sliced it without complaint; noted, not fixed.

## Decisions already locked (2026-09-17, supersedes the nose-down socket of 09-16)

- Handle: Tesla Wall Connector Gen 3 (AC, 48A), 18 ft (5.5 m) cable.
- Form, to mimic Brian's sample (photos in `images/`): a cylinder (drum) perpendicular to the wall on a square backing plate with four screw holes; a teardrop front flange (round since 2026-09-18, see Round flange below); the cable wraps around the drum.
- The charge wand comes out of the drum's RIGHT side, angled 45 degrees DOWN (front view). It must also lean AWAY from the wall so the grip and cable boot clear the wall (Brian: "the charge wand would hit the wall"); working value 20 degrees out, adjustable; 15 degrees since v5, see the cleat depth decision below.
- The nose cavity is cut to Tesla's connector profile plus 0.5 mm; the sample's opening was "much too large for the adapter".
- Retention: a FIXED cleat in the connector's lock notch, NO spring tab, and the cleat sits on the DOWNWARD (lower) wall of the cavity so gravity seats the nose on it. Not on the back (wall-side) wall. The notch therefore faces down and the button faces up along the wand. Docking and roof: see the v7 decision below (2026-09-18); the v1 to v6 step roof, lifted-over-the-cleat docking, is superseded.
- Tooling: Brian asked for OpenSCAD for this design (2026-09-17), not build123d; render views from the real model, do not hand-draw plans.
- No geometry from the licensed Printables organizer (CC BY-NC-SA, [[NACS-organizer]]); it is a measurement reference only.
- Drum 75 mm long (Brian, 2026-09-17, down from 120); the wand stays at the far end. The cable hangs in loops over the top of the drum as on the sample (39 mm of straight drum between the blends), it is not wound under the wand.
- Tesla T recessed 1 mm into the flange face, 70 mm tall, centred on the drum axis: 57% of the round part, as measured on the sample photos. Official emblem artwork (`reference/tesla-t.svg`, Wikimedia `Tesla_Motors.svg` with the wordmark removed, PD-textlogo), never rebuilt from primitives.

- Cleat depth (Brian, 2026-09-17): the cleat's holding wall is 1.25 in (31.75 mm) from the opening, measured along the cleat's wall. Tesla's CAD agrees with that number: the notch's holding wall to the end of the glossy housing is 31.2 mm, so the whole housing sits inside and the grip starts at the opening, as in the sample photos. The cavity behind the nose shoulder is lofted from Tesla's own housing sections (`bell_sections.scad`, `pipeline/bell_sections.py`); past the end of that CAD (48.4 mm from the tip) the grip is not modelled, so the cavity gets 1.5 mm extra and flares. The roof relief grows from 4 to 6.5 mm toward the mouth.
- Lean 15 degrees, down from 20 (my parameter; Brian's two numbers, drum 75 and cleat 1.25 in, were kept). The deeper cavity is 62 mm tall inside the drum at 15 degrees and 69 mm at 20; the 75 mm drum has 62 mm between 3 mm off the wall and the flange blend. At 15 degrees the cavity's deepest corner leaves 3 mm of the 5 mm plate, the mouth top runs 5 mm up the flange blend (6.7 mm under the flange), and the grip clears the wall by 25 / 36 / 52 mm (start / middle / end). 20 degrees would need a drum of about 83 mm. `pipeline/zbudget.py` measures all of this from the real cavity; rerun it after changing lean, cleat depth or drum length.

- Coupon scope (Brian, 2026-09-17): "we will skip the coupon with this change. If the wand fits this coupon, then extending the opening should be trivial." The printed coupon is the v4 shallow-cavity one (commit cb42b65, lean 20, opening 33 mm deep at the centre). It proves the nose profile and clearance, the cleat in the notch, the tight roof over the tip and the lift over the cleat, all unchanged in v5. Not covered by it, first tried on the full part: lifting the handle over the cleat with the housing under the deeper roof, and the grip past the end of Tesla's CAD (the cavity there is 46.6 mm wide at 48 mm from the tip, flaring to 49 mm at 60 mm).

- Cleat v6 (Brian, 2026-09-17, after the first coupon): "the cleat is too small": wider, taller, and "it should angle upward more and act like a wedge with a sharp edge on the top of the back so it can catch the wand better". Now a wedge cut to the lock pocket: the pocket's own cross-section from Tesla's CAD less 0.45 mm (10.6 mm wide at the floor narrowing to 9.3 at 3 mm up, domed top), 3.57 mm tall at the edge (pocket 4.02 at the centre), a 31 degree ramp from the mouth side up to a sharp edge at the back, and a back face that overhangs 15 degrees so the pocket's wall bears on the edge near the pocket's base. Spec p25: pocket 9.71 +-0.2 wide and 6.2 +-0.2 long AT THE BASE, 4 +-0.2 deep, 3 degree max draft; Tesla's CAD shows 11.56 wide at the mouth with 18 degree side walls across the wand, and a domed base (4.02 at the centre, 3.6 at 4 mm off centre).
- Flaw found in the v1 to v5 cleat: its "10 degree undercut" was built leaning the wrong way (top set back 0.39 mm toward the mouth), a draft, not a hook, so the pocket's mouth edge bore on the cleat's base and the pull tended to cam the nose up. Small (8 x 2.2 mm) and drafted: it did not catch. Fixed in v6; check the sign of any hook angle in the close-up section render (`images/scad/cleat-detail.png`).
- With the taller cleat: nose tip stops 2.5 mm short of the end wall when hanging (was 1.17), which is the over-travel needed to get the pocket past the edge; roof relief 5 mm (was 4) and 3 mm more by the housing end, so the nose can ride over a 3.57 mm edge with its tip already under the tight roof (about 7 degrees of grip-up tilt). Lever-off check: pivoting on the floor lip the tip can rise 1.8 mm before the tight roof stops it, which lifts the pocket 1.2 mm, leaving 2.3 mm of engagement. mouth_z 36.65. SUPERSEDED by Cavity v7 below: that tilt runs the nose's top corner into the end wall, and the lever-off check did not look at the top corner swinging out from under the roof.

- Cleat length (Brian, 2026-09-18): "the cleat is still too small. The width is fine, but it needs to be 50% longer, keeping the same angle." Built as a `cleat_scale = 1.5` variant with its own coupon (commit f0ea071); in Tesla's CAD it overlaps the wand by 31 mm3 (tip 1.3 mm through the pocket's base, ramp 2.4 mm past the far wall). RETIRED the same day on Brian's word ("work on the coupon.stl, not the long version. That one can be version controlled and then removed"): files and the `cleat_scale` parameter removed, recoverable from f0ea071. The cleat stays the pocket-filling wedge, 5.9 x 3.57 mm.

- Cavity v7: docking and hold (2026-09-18). Brian: "the wand fit at the end of the cavity is the correct size. That size should extend further out." Checking how far the snug roof could run (new tool, `pipeline/insertion.py`: side-view path search over slide, lift and tilt, Tesla's real housing sections against the holder's, seven sections across the wand) found the reason the cleat never caught. The hanging load acts far out on the grip and levers the wand about the mouth's floor lip, tip up and pocket up, which is the lift-over-the-cleat docking motion run backwards. With the step roof: snug length under 3.9 mm, the wand gets in and its own weight takes it back out (load has to rise 0.2 mm, no friction assumed); over 3.9 mm it is locked and cannot get in. v6 had 5 mm: no way in, by 1.1 mm. No step-roof length does both, for any tip gap (the snug roof can cover 1.4 mm of nose at most) or relief height.
  - So Brian is right that the snug roof must reach further, and the wand must dock by a motion the load cannot undo: grip raised about 12 degrees, nose in to the stop, grip lowered; the nose pivots on its tip and the pocket comes down over the cleat. Out: push in, raise the grip, pull.
  - The cavity is now the swept room of that pivot: each 2.5 mm piece of the snug cavity hulled with itself tilted 6 and 12 degrees about the tip's lower corner (`dock_tilt = 12`, `dock_top = 0.1` over the tilted nose), never below the floor. Result: roof 0.5 mm over the tip (was 1.0; `roof_extra` gone), opening at 12 degrees (1.6 mm at 10 mm from the end wall, 3.7 at 20, 6.9 at the shoulder; the step was 5.5 from 10 mm on), and the end wall leaning back 12 degrees for the nose's top corner. `roof_relief`, `tight_len`, `bell_extra` are gone.
  - Tool results on the model as built: WAY IN yes with the wand grown 0.2 mm all round (lock pocket kept at its real size), using up to 9 degrees of tilt. HOLD: settles tip-up 3 degrees against the roof with 1.87 of the 3.57 mm edge engaged; the load must be raised 19.6 mm before it can come off. `dock_tilt = 10` leaves no way in; 14 drops the engaged edge to 1.4 mm.
  - Tried and dropped: a floor that falls away past the cleat so the wand rocks next to it (engaged edge 2.25 mm, but a 7.5 degree droop and more shape for 0.4 mm).
  - Cost in the drum: cavity 65.4 mm tall (was 62), `mouth_z` 37.68 (was 36.65) to keep 3 mm behind the deepest corner, mouth top 8.4 mm up the flange blend and 3.6 mm under the flange; grip to wall 26 / 38 / 53 mm. Docked clash 0.000 mm3.
  - Nose geometry note: Tesla's nose is not a prism. At the centre plane its top is 17.0 at 1 mm from the tip against 17.76 at 30 mm, and its underside tapers the same way over the first 16 mm. `handle()` in holder.scad is still the straight 30 mm outline (the safe side for clash checks); the tool uses the real mesh.
  - RESULT (Brian, 2026-09-18, after printing the v7 coupon): "ok the last coupon printed great. This is the one. Now lets create the whole design". The v7 cavity, cleat and grip-up docking are LOCKED.
- Full part (2026-09-18): `holder.stl` (150 x 150 x 80 mm, one watertight body, 663 cm3 solid) and `holder-print.3mf`, same recipe as the coupon plus 3 walls and 20% gyroid: real slice 7 h 47 min, 366 g (356 g PETG, 10 g support interface), 267 layers; part at bed (108, 128), prime tower at (192, 180). Plate down, flange and T up.
  - Base 150 mm square (Brian, 2026-09-18: "increase the width of the base by 125%", read as to 125% of 120; 270 mm would not fit the bed; kept square, holes still 10 mm in from the edges). All four screw holes are now visible from the front; the lower-left hole's centre is 1.9 mm outside the flange's point.
  - Solid screw pads (Brian, 2026-09-18: "the area round the screw holes in the base should be solid infill"): one modifier part in the 3MF, four diameter 25 cylinders through the plate clipped to the plate's outline, `sparse_infill_density` 100%. Verified in the sliced G-code between the skins: 91 to 92% plastic in the pads, 18% in the plain plate. Bambu keeps the "Sparse infill" label at 100%, and gyroid comes as G2/G3 arcs, so the check measures plastic per volume, not labels.
  - Dual-nozzle bed fact: the CLI log gives `shared_printable_size {236, 256, 256}, shared_center {138, 128}`, so both nozzles reach x 20 to 256 only. A modifier that sticks out past the part grows the object's outline and the skirt with it; at part centre x = 100 that put the skirt past x = 20 and the slice failed (rc 152, error_code 4).
  - The cavity cut now stops at the flange's underside (z = 72): the docking room's top corner nicked 1.7 mm into the flange at the rim near the mouth (49 mm2 at z = 72.2). WAY IN and HOLD are unchanged (9 degrees, 19.6 mm, 1.87 mm).
  - First tried on the full part, not covered by the coupon: the housing and the start of the grip in the deep opening.
- Smooth entry (Brian, 2026-09-18: "the entry to the wand holder is rough. It steps in. Make it a smooth entry from the outer edge in."). The step was `grip_clear`: at the end of Tesla's housing CAD (48.2 from the tip, 50.7 from the end wall) the cavity jumped 1.5 mm wider on the sides and floor and 3 mm at the roof, just inside the mouth. `grip_clear` is gone. The sides and roof now open at `grip_flare` = 0.1 per mm from the nose shoulder to the rim (`flare(a)`), which reaches 1.57 mm at the old step and the same size at the rim.
  - The floor is NOT flared. With the floor falling away from the shoulder too, `insertion.py` gives a different hang (tip 4.03 mm from the end wall, tilt -5.5 degrees, overlap 2.00, hold 24.2 mm); with the floor kept it gives the validated numbers exactly (3.20 mm, -3.0 degrees, 1.87 of 3.57 mm, hold 19.6 mm, way in 0 to +9 degrees). Brian called the fit perfect, so the floor keeps Tesla's line to the end of the housing CAD and the old ledge beyond it is a ramp over `floor_knee` = 4 mm (`bell_profile(..., drop)` clips the flared profile at the floor).
  - New cavity against the validated one: 2678 mm3 of room added, 29 mm3 removed, all of it the ramp filling the ledge's corner (50.4 to 54.5 from the end wall, 8.6 mm either side of centre, under the start of the grip). Docked clash 0.000 mm3.
- 4 in base (Brian, 2026-09-18: "reduce the size so the base is 4 x 4 but make sure to preserve the wand holder size, as this is perfect"). Read as: shrink the body round the true-size cavity. `plate_w` 101.6, `drum_r` 40 (was 50), flange diameter 104 (was 124), `flange_point` 70, `logo_h` 59 (still 57% of the round part), `mouth_z` 37.92 from `zbudget.py` (3 mm behind the deepest corner, mouth top 3.6 mm under the flange, grip to wall 26 / 38 / 54 mm). Cavity, cleat, `cleat_depth`, both wand angles and `drum_l` 75 are unchanged; the depth cannot shrink because the cavity is 65.4 mm tall out from the wall.
  - How small the drum can go: the cavity's far roof corner is 10.5 mm from the surface at radius 40 (wall profile, scratch check), 7.3 at 38, 3.2 at 36. Radius 40 also puts the three uncovered screw heads 0.7 mm outside the round flange (hole centres 57.7 mm from the axis).
  - The flange's point covers the lower-left screw on any base this size (the round part alone reaches 52 of the 52.7 mm the head needs), so a diameter 11 hole through the point lets the screw and driver through. Brian has not seen this yet.
  - Print: 108 x 108 x 80 mm on the bed, 6 h 07 min, 275 g (265 g PETG, 10 g support interface), 267 layers; pads 89 to 90% plastic, plain plate 18%.
  - Round flange (Brian, 2026-09-18: "make the face round, removing the pointed bottom left corner"): the flange is a plain circle, diameter 104; `flange_point`, `point_angle` and the driver hole through the point are gone. All four screw heads now clear the flange's edge by 0.7 mm. This supersedes the teardrop flange in the locked decisions above. Cavity untouched, so `insertion.py` was not rerun. Print: 104 x 104 x 80 mm, 5 h 47 min, 252 g (243 g PETG, 9 g support interface), pads 85 to 89%, plain plate 19%.
  - The round flange's tree supports root up to 20 mm outside the part, and one trunk landed 9.3 mm from the prime tower's base, which the new gap check caught. Tower moved from x 192 to 212: gap 26.6 mm.
  - Rounded edges (Brian, 2026-09-18: "all edges should have a minimum of a 1/16 in of a roundover except for the back of the wall plate and the screw holes"). `edge_r = 25.4 / 16`.
    - Plate: top edge rounded (four turned corner posts, hulled). `plate_r` 8 to 10 = `hole_in`, so each countersink is centred in its corner; at 8 the countersink broke through the rounded edge for the top 0.35 mm.
    - Flange: both rims rounded inside `drum_profile()`, which now turns the drum and flange as one profile; the back rim's arc is tangent to the blend (the underside is all blend, no flat).
    - Mouth rim: rolling-ball roundover from `pipeline/rim_round.py`, which writes `rim_round.scad` (251 stations at 0.8 mm; wedge angle 56 to 157 degrees). The ball-centre curve is the rim of "body shrunk by edge_r minus cavity grown by edge_r", cut by OpenSCAD; each centre is then settled at exactly edge_r from both real surfaces. `holder()` cuts the kite edge, touch, centre, touch between stations and puts the balls back. Measured on the finished mesh: the new surface is 1.549 to 1.587 mm from the centre curve all round (ball 1.5875, 20-gon spheres), one body, watertight. RERUN `rim_round.py` after any change to the cavity, the drum, the blends or `edge_r` (order: `zbudget.py`, `rim_round.py`, `insertion.py`).
    - `cut_top = 68.4`: the cavity cut stops where its top reaches inside the drum (was the flange's underside, 72). Above that the docking room's flared top corner ran on outside the drum as a 2 mm wide groove up the blend to the flange's rim; no wand goes there and it could not be rounded cleanly. WAY IN unchanged.
    - Hang with the rounded floor lip (a 67 degree wedge, so the ball touches the floor 2.4 mm in from the lip): tip 3.37 mm from the end wall (was 3.20), tilt -3.5 degrees (was -3.0), 1.75 of 3.57 mm engaged (was 1.87), HOLD 20.4 mm (was 19.6); WAY IN the same (0 to +9 degrees, 3.88 mm). Docked clash 0.000 mm3. Brian has been told this number moved.
    - Left sharp on purpose: the cleat (its holding edge is the function) and the T's outline (1 mm recess, artwork). Trap found on the way: `use <holder.scad>` does not bring `$fn` along, so a scratch file that exports `body()` gets coarse facets unless it sets `$fn` itself.
    - Print: 5 h 32 min, 241 g (233 g PETG, 9 g support interface), pads 89 to 90%, plain plate 19%, tower gap 26.6 mm.
  - Prime tower: Brian had the 150 mm file open in Studio, which warned "Prime Tower is too close to others" and "Conflicts of gcode paths ... layer 17 (WipeTower <-> NACS wall holder)". In that file's CLI slice the tower's box was 9.4 mm from the plate. `make_coupon_3mf.py` now measures that gap from the G-code (`tower_gap_mm`, skirt left out) and the holder job asserts 15 mm; the 4 in part has 22.5 mm.

## Files (2026-09-17)

- `holder.scad` (+ `nose_outline.scad`): the model; `part="coupon"` gives the fit coupon. `render.sh` renders `images/scad/*.png`; `renders_page.py` builds `plan.html` (published as the "NACS Holster Plan" artifact, https://claude.ai/artifact/D2zPQ4v2W97wuq1hMqpYa6 since 2026-10-08; the earlier artifact was deleted).
- `coupon.stl`, `coupon-print.3mf`, `coupon-slice.json`, `images/scad/coupon-*.png`: the fit coupon, generated from holder.scad (`part="coupon"`, export needs `-D show_wall=false` or the render's wall plane comes along): the v7 nose cavity and the cleat, cut off 1 mm past the nose shoulder (`coupon_cut`), 3 mm walls, 0.9 mm base, print orientation unchanged: 72 x 67 x 57 mm. Real slice: 1 h 36 min, 59 g (55 g PETG including the prime tower, 3.8 g support). The first printed coupon (v4, commit cb42b65) had the small drafted cleat and the step roof. Set `coupon_cut` past the mouth to get the whole opening.
- `rim_round.scad`: GENERATED by `pipeline/rim_round.py` (the mouth rim's roundover stations), included by `holder.scad`; never edit by hand.
- `images/scad/entry.png` and `edges.png` (from `render.sh`) and `entry-before.png` (one-off: the stepped entry of commit 4e9f8d9 on the 4 in body).
- `holder.stl`, `holder-print.3mf`, `holder-slice.json`: the full part, built by `pipeline/make_coupon_3mf.py holder` (the same script builds the coupon with no argument). Retrospective: `knowledge/learnings/nacs-wall-holder.md`.
- `pipeline/insertion.py`: the docking and hold check (WAY IN, HOLD) for the model as built or with `name=value` overrides; `--png` draws the path and the hanging pose (`images/docking/docking-path.png`). Run it after any change to the cavity, the cleat or the wand angles. `render.sh` also renders the docking poses (`dock-1-in`, `dock-2-stop`; ghost pose via `pose_tilt`, `pose_out`).
- Renders use `--render`, not `--preview`: in preview the docked handle's clip plane paints over the holder's whole cut face in section views. `part="clash"` intersects the docked handle with the holder and must come out empty (checked: 0 mm3).
- `pipeline/make_coupon_3mf.py`: X2D 0.6 nozzle, 0.30mm Standard, Bambu PETG Basic on nozzle 1, Bambu Support For PLA/PETG on nozzle 2 as the support interface, tree supports with Bambu's recommended parameters for that pairing. Lessons baked in: the CLI writes one extruder variant per filament, so every per-variant filament key is expanded to filaments x 6 variants like a Studio-saved file; flush matrix = filaments^2 x len(flush_multiplier) with one multiplier per extruder; the CLI's default prime tower position (165, 236) is off the bed.

## Sources

- Face size, reference values only: Amphenol NACS datasheet (amphenol.co.jp/military/catalog/NACS.pdf), AC connector face 41 mm wide x 36 mm nose height, 52 mm at the front with the handle, 194 mm long.
- Full Tesla spec set, retrieved 2026-09-16 into `spec/` (Tesla unlinked it in 2024 when SAE J3400 replaced it):
  - `TS-0023666-NACS-Technical-Specification.pdf` (30 pages; section 7 is connector, inlet and system mechanics)
  - `NACS-AC-Charging-Connector-Datasheet.pdf`: the Tesla North American 48A AC connector, Brian's handle
  - `NACS-DC-Charging-Connector-Datasheet.pdf` and `NACS-AC-DC-Pin-Sharing-Appendix.pdf`
  - Official CAD: `NACS-500V-Connector-and-Inlet.stp`, `NACS-1kV-Connector.stp`, `NACS-1kV-Inlet.stp`
- How it was retrieved: the Wayback search API was blocked by the archive's bot protections (HTTP 429/503). The archived Oct 2023 `tesla.com/support/charging/product-guides` page still loads and gave the real links. The archive's STEP copies are Common Crawl captures truncated at 1 MiB, but `digitalassets.tesla.com/tesla-contents/raw/upload/v1681681730/<file>.stp` still serves the complete files.

## Connector facts from the Tesla spec (TS = TS-0023666 rev 1.1, DS = 48A AC datasheet)

- Brian's handle is 240 VAC / 500 VDC rated, so the 500V drawings apply. The latch geometry is the same for 500V and 1kV (TS p24).
- Handle: 41.5 wide x 35.1 tall at the nose x 194.5 long (DS). Cable Ø14.5 mm; lengths 2.6 / 5.5 / 7.3 m (DS). Polycarbonate, IP67.
- Nose: 32.49 from the front face to datum C (TS p14). Inlet cavity depth 33.25 ±0.2 (TS p21-22). Cross-section only in the 3D model (profile tolerance 0.3, TS p12-13).
- Lock pocket: on the nose UNDERSIDE (the ground/data-socket side, opposite the HV sockets and the button), centered left to right (TS p25; DS).
  - Along the nose: centered 20.24 from the front face; base walls at 17.14 and 23.34 (6.2 ±0.2 long).
  - Size: 9.71 ±0.2 wide, 4 ±0.2 deep, walls drafted up to 3° (mouth about 6.6 x 10.1).
- Vehicle lock pin: rises up into the pocket, perpendicular to insertion. Base 4 in a 4.8 slot, 2.85 flat tip, 20° flank on the opening side (TS p24-25).
- Forces: insertion and withdrawal under 90 N (DS). No passive detent: the car's lock is the only retention (TS p7).
- End caps (TS 9.1) apply only to inlet caps; no rule limits a dock on the connector face.

## Reference socket measurements (organizer STL, measured only)

- Sideways socket, 40 mm deep to a square stop face; shield cross-section, widest just above center.
- Width 43.5 at the mouth, 41.2 at 8 deep, 40.9 at 16 deep, 39.7 at the stop.
- Height (square to the axis) about 38.5 at the mouth, 36.5, then 35.8 at 16 deep.
- About 2.5 mm clearance at the mouth, near line-to-line by 16 mm deep. The stop is narrower than Amphenol's 41 mm Ref width, so the nose likely tapers.
- Retention: a spring tab in the floor, about 12 wide x 2.7 thick x 22 long, with a 2 mm bump (rejected for our design: fixed cleat instead).
- Cable hook: trough 60 wide, lip 15 to 19 above the saddle.

## Shipped (2026-09-19)

Brian: "charger holder is on the wall and working great." The part mounted on the wall,
holding the wand with its cable on the drum, is the final one: 4 in base, round flange,
1/16 in roundovers, `holder.stl` / `holder-print.3mf` as committed in 9585fc0. This closes
out every open question below and in the last handoff:

- The reading of "reduce the size" (drum 80, flange 104, not only a smaller plate) works in
  practice.
- The rounded floor lip's small change to the hang (3.5 degrees tilt, 1.75 mm of the cleat's
  edge engaged, HOLD 20.4 mm) holds the real connector under real use.
- The housing and the grip past the end of Tesla's CAD, never covered by a coupon, fit; no
  report of a bind or a gap there.
- Project is closed. Any further change is a new request, not open work.

## Superseded open items (kept for history)

- Cleat position and size: design it to engage the lock notch on the bottom of the connector nose (the one the car's charge-port lock pin enters), from the Tesla spec once retrieved. The cleat and the extra opening room both depend on that notch's location and depth.
- Cable diameter: Ø14.5 mm per Tesla's 48A datasheet. This replaces the 18 mm forum estimate. The cable is 5.5 m (18 ft). Coiled in loops about 300 mm across (about 0.94 m of cable each), that is about 6 loops, 87 mm side by side at 14.5 mm, so a hook about 100 mm wide. Settle the hook size in the design plan.
- The Gen 3 handle has a button on top that opens the car's charge port; the holster must not press it.
