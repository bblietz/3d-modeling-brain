---
type: project
project: NACS-wall-holder
date: 2026-09-16
status: v4 2026-09-17 (drum 75, Tesla T recessed in the flange, fit coupon sliced); coupon-print.3mf ready to print, 1 h 32 min; awaiting the fit result
tags: [x2d, nacs, tesla, wall-mount]
---

# NACS wall holder (Tesla Wall Connector Gen 3, 48A)

Our own design for a wall-mounted dock for Brian's Tesla Gen 3 Wall Connector handle, with a cable wrap hook.

## Decisions already locked (2026-09-17, supersedes the nose-down socket of 09-16)

- Handle: Tesla Wall Connector Gen 3 (AC, 48A), 18 ft (5.5 m) cable.
- Form, to mimic Brian's sample (photos in `images/`): a cylinder (drum) perpendicular to the wall on a square backing plate with four screw holes; a teardrop front flange; the cable wraps around the drum.
- The charge wand comes out of the drum's RIGHT side, angled 45 degrees DOWN (front view). It must also lean AWAY from the wall so the grip and cable boot clear the wall (Brian: "the charge wand would hit the wall"); working value 20 degrees out, adjustable.
- The nose cavity is cut to Tesla's connector profile plus 0.5 mm; the sample's opening was "much too large for the adapter".
- Retention: a FIXED cleat in the connector's lock notch, NO spring tab, and the cleat sits on the DOWNWARD (lower) wall of the cavity so gravity seats the nose on it. Not on the back (wall-side) wall. The notch therefore faces down and the button faces up along the wand. The cavity roof is relieved so the nose can be lifted over the cleat on the way in, but stays tight over the last few mm at the tip so the handle's weight cannot lever the tip up and lift the notch off the cleat.
- Tooling: Brian asked for OpenSCAD for this design (2026-09-17), not build123d; render views from the real model, do not hand-draw plans.
- No geometry from the licensed Printables organizer (CC BY-NC-SA, [[NACS-organizer]]); it is a measurement reference only.
- Drum 75 mm long (Brian, 2026-09-17, down from 120); the wand stays at the far end. The cable hangs in loops over the top of the drum as on the sample (39 mm of straight drum between the blends), it is not wound under the wand.
- Tesla T recessed 1 mm into the flange face, 70 mm tall, centred on the drum axis: 57% of the round part, as measured on the sample photos. Official emblem artwork (`reference/tesla-t.svg`, Wikimedia `Tesla_Motors.svg` with the wordmark removed, PD-textlogo), never rebuilt from primitives.

## Files (2026-09-17)

- `holder.scad` (+ `nose_outline.scad`): the model; `part="coupon"` gives the fit coupon. `render.sh` renders `images/scad/*.png`; `renders_page.py` builds `plan.html` (published as the "NACS Holster Plan" artifact).
- `coupon.stl`, `coupon-print.3mf`, `coupon-slice.json`: fit coupon, 54 x 55 x 60 mm, the cavity, cleat and mouth with 3 mm walls on a 0.9 mm slice of the plate, print orientation unchanged. Real slice: 1 h 32 min, 53 g (49 g PETG, 4 g support), 17 g of it prime tower.
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

## Open

- Cleat position and size: design it to engage the lock notch on the bottom of the connector nose (the one the car's charge-port lock pin enters), from the Tesla spec once retrieved. The cleat and the extra opening room both depend on that notch's location and depth.
- Cable diameter: Ø14.5 mm per Tesla's 48A datasheet. This replaces the 18 mm forum estimate. The cable is 5.5 m (18 ft). Coiled in loops about 300 mm across (about 0.94 m of cable each), that is about 6 loops, 87 mm side by side at 14.5 mm, so a hook about 100 mm wide. Settle the hook size in the design plan.
- The Gen 3 handle has a button on top that opens the car's charge port; the holster must not press it.
