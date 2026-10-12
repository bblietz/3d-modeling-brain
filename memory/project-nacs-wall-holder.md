---
name: project-nacs-wall-holder
description: Tesla Wall Connector wall holder - 2026-09-19 print broke in a drop; 2026-10-08 revision (deeper, crest lip, wordmark, two-colour face) with a solid 1/4 in plate, now 4-1/2 in square, and a solid face, sliced 10 h 19 min / 580 g on 2026-10-11, not printed
metadata:
  type: project
---

Wall-mounted dock for Brian's Tesla Gen 3 Wall Connector charge handle: drum on a 4 in square
plate, flange with the Tesla T, wand out the drum's side hanging on a fixed cleat in the
connector's own lock pocket. **The 2026-09-19 print is mounted and working** ("charger holder is on
the wall and working great").

**Revision 2026-10-08, built and sliced, NOT printed:** drum 1 in deeper (100 mm) and 90 across,
cavity 1/2 in deeper (cleat 1.75 in from the opening), full-width "crest" lip 1.5 in above the
flange (shield sides, arched top), the T, the TESLA wordmark bent along the arc and a frame line
inlaid flush in a second filament colour (AMS filament 3), plain screw holes (top two behind the
lip, driver at a 6 degree tilt), cleat catch window doubled (`tip_gap` 5, hook overhang 20) because
the wand "has a tendency to fall off if not seated perfectly" (the cleat itself fills the pocket and
cannot grow). 8 h 47 min, 442 g. Open: the grip's first 1/2 in now sits inside the opening with no
Tesla CAD behind it; ask Brian to measure the handle 1/2 in and 1 in behind the glossy housing
before printing. **2026-10-10: Brian dropped the mounted holder and a plate corner broke off
"along the contour of the main cylinder".** Cause from the sliced G-code (evidence page
https://claude.ai/artifact/QCeo4UdoVNbcSQv3je5xm4, `pipeline/corner_check.py`): the 5 mm plate was
two 0.9 mm skins over 20% gyroid, solid only in the 12.5 mm screw pads. **Fix built the same day, Brian's
pick of both options:** `plate_t` 6.35 (1/4 in) and a solid-base modifier in the 3MF (whole plate plus
the drum blend ring, 100% monotonic, measured 94 to 100% plastic). Slice now 9 h 22 min, 498 g. The
wand's place is unchanged (mouth_z, cut_top kept); the flange and lip moved out 1.35 mm. Body export
needs `-D show_inlay=false`. 2026-10-11: Brian saw the modifier's squared-off ring in Studio ("it should
round into the wall plate"); the modifier now follows the blend from 0.6 mm inside the body, a layer under
the plate's top and clear of the holes, none of it outside (`pipeline/modifier_views.py` proves it and
draws before and after); see [[feedback-modifiers-inside-the-body]]. Same day Brian asked for
the face solid too ("it will also break if dropped"): `holder.scad` part "facemod" builds it (flange,
lip, blend behind the flange, 0.6 inside every surface), injected as a second modifier; slice 10 h 11 min,
575 g. **OPEN 2026-10-11: "the center cylinder extends past the edge of the base on all 4 sides"**: the
90 drum's blend foot (52) and the 104 flange run past the 4 in plate (edge 50.8) since 2026-10-08. Options
page https://claude.ai/artifact/5YuDCMozLvJvJUdhwWxwJk (A plate 4.5 in recommended, B 4.25 in, C 4 in with
4 mm blends and a 98 face; all keep the screw pattern). **Brian picked A the same evening:** plate 114.3, hole_in and plate_r 16.35, holes still 81.6 apart; holder.scad asserts the foot on the flat top; `pipeline/run_all.sh` ran everything; 10 h 19 min, 580 g. Every pick was made from rendered options on
https://claude.ai/artifact/5u3wgRBUTWngnCdjFuPzKB; plan page https://claude.ai/artifact/D2zPQ4v2W97wuq1hMqpYa6.

Project files and tools: `projects/NACS-wall-holder/` (brief.md "Revision of 2026-10-08",
`holder.scad` with `tab_style` / `emblem` / `top_mount` / `lip_text` options and `part = "inlay"`,
`pipeline/insertion.py` docking and hold check, `pipeline/depth_limit.py` cavity depth vs drum wall,
`pipeline/rim_round.py`, `pipeline/make_coupon_3mf.py holder` which assembles body + inlay on two
filaments). Pipeline order after any cavity or drum change: zbudget.py, rim_round.py, insertion.py,
both exports, make_coupon_3mf.py. See [[feedback-check-docking-and-hold-kinematics]] and
[[feedback-html-visual-companion]].
