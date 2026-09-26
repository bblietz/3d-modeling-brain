---
title: Garmin 943xsv helm panel
type: learning
project: Garmin-943-helm-panel
created: 2026-09-11
tags: [marine, starboard, router-template, garmin, bambu-cli]
---

# Garmin GPSMAP 943xsv helm panel

Flat panel replacing the hinged clear cover behind the wheel, with the 943xsv
flush mounted through it. Status 2026-09-11: **router template printed and fits**
(Brian's words: "fit perfect"). The panel itself is not cut yet.

## What worked

- **Window at exactly the Garmin cutout, no offset.** The bearing rides the
  template edge, so the template window IS the 222.4 x 139.0 mm cutout. No
  bushing offset arithmetic to get wrong.
- **Let the bit set the corner radius.** A 1/4 in bit leaves R3.175, which
  matches Garmin's drawn R3.7 closely enough that the corners need no filing.
  The template's own window corners are modelled sharp.
- **Counterbored drill guides.** 2.8 mm modelled (prints about 2.5) with a
  6 mm counterbore 6 mm deep, so the guide is short enough for a normal jobber
  bit to reach the workpiece while still starting the bit square.
- **TOP debossed on the counterbored face.** Not decoration: the hole pattern is
  asymmetric top to bottom, so the template is only symmetric left to right and
  a flipped template would misplace every pilot.
- **V notches at the four outer edge midpoints** to register against centrelines
  drawn on the workpiece.
- **0.6 mm chamfer on the bed-side window edge** so elephant foot cannot narrow
  the window.
- **Brim OFF.** At 252.4 mm on a 256 mm bed there is only about 1.8 mm per side;
  a brim does not fit. The footprint is large enough not to need one.

Print recipe in the brief: 0.6 nozzle, PLA, textured PEI at 65 C, 0.30 mm
Standard, about 1 h 28 min and 96 g, centred on the plate, counterbored face up.
(Which preset Brian actually ran was not recorded, nor a caliper reading of the
printed window. Expected 222.4 x 139.0 within 0.3 mm.)

## What failed, and the catch that mattered

- **Garmin's screw pattern is NOT centred on the cutout.** It sits 1.24 mm
  toward the unit's bottom: top holes 4.5 mm above the cutout edge, bottom holes
  7.0 mm below. Revision A assumed centred and would have put all four pilots
  1.24 mm high, which exceeds the radial clearance of M3 in Garmin's 3.5 mm
  nut-plate holes. Found only by extracting the vector geometry from Garmin's
  own template PDF (190-02761-05_0D) rather than trusting its printed labels.
  **Rule: measure a template's drawn geometry, never derive positions from
  labelled pitches.** The labels are rounded to 1/16 in (7 1/2 in is 190.5, not
  the true 190.9).
- A Garmin FAQ page lists "190.9 x 150.5 x 139.0 mm" as the cutout. That is the
  hole pitch and cutout height run together, not a cutout. The template governs.
- Counterbore had to drop from 7 mm to 6 mm: the top row of holes sits only
  4.5 mm above the window, and 7 mm left a 1.0 mm wall.
- A volume-reconciliation assert caught the seam chamfer as unaccounted material,
  and a bounding-box clearance assert falsely failed on correct geometry because
  a perpendicular offset shrinks a bowtie's bbox more than its face gap. Probe
  the real interference, not bounding boxes.

## Material decision: 1/2 in King Starboard, routed one piece

Chosen over a printed four-tile ASA panel. The reasoning generalises and is in
[[marine-materials]]: ASA's advantages (stiffness, creep, heat) are all cured by
thicker sheet, which is nearly free, while Starboard's (impervious to water,
tough, immune to sunscreen and solvents, seamless) cannot be engineered into a
printed part. 1/2 in because HDPE is softer than printed ASA and creeps, so it
needs one size up; it lands at 0.23 mm total deflection, matching 3/8 in ASA.

Thickness study, deflection at the Garmin screws under the 1.6 kg unit plus a
firm 30 N screen press:

| | 1/8 in | 1/4 in | 3/8 in | 1/2 in |
|---|---|---|---|---|
| printed ASA | 5.60 mm | 0.70 mm | 0.21 mm | 0.09 mm |
| Starboard, incl. creep | - | 1.84 mm | 0.54 mm | 0.23 mm |

1/8 in was rejected outright: 64x floppier than 1/2 in, cannot hold a 6 mm
bowtie pocket, and leaves the Garmin screws 3.2 mm of engagement. It is fine in
aluminium (0.11 mm), which is probably where the number came from.

HDPE **filament** was considered and rejected: the only seriously engineered PE
filament (Braskem FL300PE) died with Xtellar in 2024/25, printed unfilled
polyolefin is about half the stiffness of HDPE sheet, and polyethylene cannot be
glued, which would leave any tile seam permanently unbonded.

## Reusable slicer findings

All now in [[printer-x2d]]:

- `bambu-studio --export-3mf` exits **243** and writes nothing when given an
  absolute path while `--outputdir` is also set. Pass a bare filename.
- The CLI **cannot slice its own project files** (rc 156): the live X2D extruder
  and variant keys are only written by the GUI. `Sharks-nametag/pipeline/graft_slice.py`
  supplies them to a throwaway copy. Studio resolves them on open, so a shipped
  file needs no graft.
- `curr_bed_type` defaults to **"Cool Plate"**, which for ASA means a 0 C bed.
  Override it and list the override in `different_settings_to_system`.
- **Studio lays multi-plate projects out in a TWO-COLUMN grid running in
  NEGATIVE Y**, not a single row along X. Plate p (0-indexed) sits at
  `((p % 2) * 307.2, -(p // 2) * 307.2)`. The vault had recorded a single row,
  which is indistinguishable for two plates and wrong from the third onward:
  plates 3 and 4 round tripped cleanly and rendered EMPTY in the GUI.
- The CLI does **not keep objects in input order**. Map object ids by the source
  filename in `model_settings.config`, not by document position.
- A CLI round trip does not prove a plate is real. Ask Studio's reader how many
  objects it finds per plate, and open the file in the GUI.

## Decisions locked

- Panel replaces the hinged cover, fixed in place. Hinges come off.
- SUPERSEDED 2026-09-26: the panel is now PRINTED IN ASA as four tiles at 3/8 in.
  The routed 1/2 in black King Starboard one-piece stays as the alternative.
- Garmin flush mount, screws through the bezel into the HDPE. No printed bezel.
- One printed router template; window 222.4 x 139.0, guides on Garmin's offset
  pattern, TOP on the counterbored face.
- Nothing else on the panel. Under a hardtop. Vertical cutout placement decided
  by Brian at layout.

## Still open

- Caliper reading of the printed window, and which preset was actually run.
- Opening measurements and photos; the outline and corner radius come from the
  old cover, so the modelled 18.5 x 11.5 in and R1/2 in are still provisional.
- The rout itself, the test fit of the unit, and the install.
- The ASA print itself: plate 1 corner check, then the other three, then the
  acetone weld and the screw hold in printed ASA.

## Switched to printing in ASA, 2026-09-26

Brian chose to print the panel after all. The four-tile path built on 2026-09-09
became the active build, and rebuilding it surfaced one real trap.

**A thickness constant served two materials.** `PANEL_T` had been changed to
12.7 mm for the Starboard decision, and the ASA tiles were generated from the
same constant. Running `TILES=1` after that change would have produced 12.7 mm
ASA tiles: a third more time and filament than the analysis calls for, and
silently different from the 9.525 mm tiles already sliced and verified. Worse,
the ASA path exported the one-piece panel first, so it would have overwritten
the routed Starboard deliverable with an ASA-thickness copy.

The fix is to derive the material-dependent numbers from the build rather than
let one path inherit the other's value:

```python
ASA = os.environ.get("TILES") == "1"
PANEL_T = (0.375 if ASA else 0.5) * IN
PILOT_DEPTH = 7.0 if ASA else 10.0
```

and to let only the routed build own `helm-panel.stl` and `.step`.

**Lesson: when a decision changes a material, audit every constant that material
justified.** The 1/2 in existed only because HDPE is soft and creeps. It had no
business surviving into a printed part, and nothing in the file said so. A brief
that records WHY a number was chosen is what makes that audit possible; this one
did, which is the only reason the stale value was caught before 8 hours of ASA.

The brief's own tile table had already drifted: it read 12.7 mm thickness beside
a 3.5 mm front skin over a 6 mm pocket, which only reconciles at 9.525 mm. Two
numbers in one table that cannot both be true is a reliable smell.

**Infill changes the stiffness answer, but not the conclusion.** The 0.21 mm
deflection assumed a solid section. At the slicer's 15 percent the panel is two
roughly 1.2 mm solid skins over a sparse core, and the second moment falls to
about 64 percent of solid, so deflection is nearer 0.33 mm. Still imperceptible.
Raising infill barely helps, because bending stiffness lives in the material
furthest from the neutral axis. Print flat structural panels at default infill
and buy stiffness with thickness instead.

**Regression check worth repeating.** After the refactor, the four tiles and the
key regenerated byte for byte identical to the versions Studio had already
accepted. Checksumming print meshes before and after a source change is cheap
and turns "I think it is unchanged" into proof.

### Verified state

Rebuilt on Bambu Studio 02.08.02.61: four plates, every one slices for real,
Studio's reader reports 1, 1, 1 and 11 objects. 7 h 55 min, 376 g.

### Still gating a good print

The panel OUTLINE is still an 18.5 x 11.5 in estimate. The router template was
safe to print against a guess because it only locates the cutout. A printed
panel bakes the guess into 8 hours of ASA, so the opening needs measuring first.
And the files are built for the 0.6 high-flow nozzle while the 0.4 has been in
since 2026-08-06; Studio re-slices to the installed profile without warning.
