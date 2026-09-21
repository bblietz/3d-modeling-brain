---
type: knowledge
topic: TPU on the X2D
date: 2026-09-20
status: SEED, unvalidated. Facts below come from Bambu's presets and one real CLI slice; nothing here has been confirmed by a print yet. Update after the first TPU print ([[iphone-15-pro-max-case]]).
tags: [x2d, tpu, materials]
---

# TPU on the X2D

First TPU work in the vault: `projects/iPhone-15-Pro-Max-case/` (2026-09-20). Printer rules: [[printer-x2d]].

## What Bambu's presets say (Studio 02.08, `~/.config/BambuStudio/system/BBL/filament/`)

| Preset (X2D 0.4 nozzle) | Max volumetric speed | Nozzle | Textured plate |
|---|---|---|---|
| Bambu TPU 95A HF | 12 mm3/s | 230 C | 35 C |
| Bambu TPU 95A | 3.6 mm3/s | | |
| Bambu TPU 90A | 2.8 mm3/s | | |
| Generic TPU | 3.2 mm3/s | | |
| Bambu TPU for AMS | 18 mm3/s | | |

- Retraction 0.8 mm (95A HF). The X2D presets carry six values per key, one per extruder variant, through the include `fdm_filament_template_direct_bowden_e3d`.
- "TPU for AMS" is a separate, stiffer product with its own preset family. Plain TPU 95A and 95A HF are external-spool filaments (inferred from the preset families and Bambu's naming; confirm on the printer).
- The unsuffixed X2D process presets (`0.20mm Standard @BBL X2D`) are the 0.4 nozzle ones; the 0.6 ones carry the nozzle in the name.

## Slicer settings chosen for thin TPU parts, and why

- `wall_generator = arachne`: a 1.5 mm wall prints as solid variable-width lines. With the classic generator a 1.5 mm wall is two loops plus gap fill, and gap fill in TPU means many short retracting moves.
- `wall_loops = 4` and `sparse_infill_density = 100%` (zig-zag): nothing in a thin flexible part should have a sparse core; a 15% core in a 2.5 to 5 mm section is a soft spot. Bambu keeps the "Sparse infill" G-code label at 100%, so verify solidity by weight (sliced grams vs mesh volume x 1.22 g/cm3).
- `reduce_crossing_wall = 1` (avoid crossing walls): travels follow the wall instead of crossing an open cavity, where TPU strings.
- Textured PEI, no supports, no ironing.

## Design rules used (to be confirmed by the print)

- No supports in TPU if the design can avoid them: supports fuse, and the supported face comes out rough. A feature that must stand proud of the bed face (a phone case's camera guard) is better printed as a second flat part and bonded with flexible CA.
- Tall thin TPU prints are out: a 160 mm tall channel of 1.5 mm walls deflects about 15 mm under 0.5 N of nozzle drag (E about 50 MPa).
- Window roofs in a vertical TPU wall: keep the wall lines running along the bridge, flare the outer part of the roof at 45 degrees so only the inner 0.75 mm is a true bridge. Longest tried: 22 mm (result pending).
- Cavity for a gripping fit: phone + 0.10 mm per side (result pending).
