---
title: Sharks nametag final print files
type: readme
project: Sharks-nametag
date: 2026-08-26
status: final
tags: [sharks-nametag, 3d-print, bambu-x2d, petg, multicolor, final]
---

# Sharks nametag final print files

Production Bambu Studio project files for the 14 Santa Cruz Sharks backpack tags (3 inch, 3 colors, PETG, X2D 0.4 nozzle), built 2026-08-26 from the locked v3.27 design with the recipe that passed the MAX 18 gate print on 2026-08-25. Design history and decisions: [[brief]]. Retrospective and print lessons: [[sharks-nametag]].

`final/` is the production area. `exports/` (recreated on demand by the coupon builders) holds only experiments.

## What is here and which to print

- `sharks-nametag-<name>-<number>.3mf` (14 files): one tag per file, single object named `NAME NUM` at plate center (128, 128), wipe tower beside it at (30, 106.5). Print these when you want one kid at a time or a re-print of a single tag. About 1h36m and 21 g each.
- `sharks-nametag-roster-plates.3mf`: the whole roster in one project on two plates. Plate A = Sami 5, Joe 8, Nathaniel 9, Zachary 10, Jack 12, Kai 14 (6 tags, about 7h05m, 101 g). Plate B = David 15, Callan 17, Max 18, Benji 19, Julian 20, Leonidas 25, Luke 30, Krystof 33 (8 tags, about 9h20m, 132 g). Print this for the batch; each tag is its own object, so a failed tag can be skipped from the printer screen.

Both routes carry identical per-tag geometry and settings; the plates only add the 3 x 3 grid (centers 46 / 128 / 210 mm) and per-plate wipe towers at (106, 183.5) on plate A and (30, 183.5) on plate B.

## Locked recipe (2026-08-25, gate print passed)

- Nozzle: 0.4 mm hardened steel. Presets flattened from Studio 2.08: printer `Bambu Lab X2D 0.4 nozzle`, process `0.12mm High Quality @BBL X2D`, filament `Bambu PETG Basic @BBL X2D 0.4 nozzle` x3. Colors filament 1 white `#FFFFFF`, 2 navy `#00395E`, 3 cyan `#31BAD6`. Textured PEI Plate, 70 C. 37 layers (0.2 first, 0.12 after), tag 4.56 mm tall.
- Process overrides (the coupon C top recipe plus first-layer and tower fixes, all pinned in `different_settings_to_system` so Studio keeps them): no ironing, `top_one_wall_type` not apply (2 top walls), top surface 60 mm/s, wall generator arachne, 2-loop skirt, first layer 30 mm/s, prime tower brim 5 mm with rib wall and fillet wall.
- Letter-tier modifier (C7): a modifier part per tag over the nine raised SANTA CRUZ letters (outlines + 0.3 mm, z 3.92 to 4.64, the five letter-only layers) with `wall_loops` 1, `top_one_wall_type` all top, `top_surface_line_width` 0.3, `internal_solid_infill_line_width` 0.3, `infill_direction` 90.
- Object key per tag: `detect_narrow_internal_solid_infill` 0.
- Back-text modifier: a second modifier part per tag over the back inlay text (this kid's navy outlines + 0.5 mm, z 0.16 to 0.56, layers 2 to 4) with `internal_solid_infill_pattern` concentric, which gives the name and number strokes back the concentric fill the object key takes away.
- Wipe tower rule: tags keep their slots; the tower sits at the free spot closest to the bed center with its brim at least 12 mm from every disc and 15 mm from the bed edges (singles (30, 106.5); plates (106, 183.5) and (30, 183.5)).
- Flush placeholder: the files carry an 18-entry `flush_volumes_matrix` (two 3 x 3 blocks, 280 mm3 between colors, flush vector 140) so Studio 2.08 loads them without the 4-filament NaN bug. It is a placeholder, not a calibrated value: re-calculate Flushing Volumes in Studio before slicing.

## Print checklist (Bambu Studio)

1. Select the printer preset `Bambu Lab X2D 0.4 nozzle` BEFORE opening the file (Studio otherwise re-maps the project to the active nozzle).
2. Open the 3MF as a project (keep the project's presets when asked).
3. AMS mapping as loaded 2026-08-24: filament 1 white -> AMS slot 4, filament 2 navy -> AMS slot 3, filament 3 cyan -> AMS slot 2. Check the colors in the filament list match.
4. Flushing Volumes: click Re-calculate (the file carries a placeholder block).
5. Plate: Textured PEI, bed 70 C (already set). Top vent open, chamber fan on cool for PETG.
6. Slice and compare the estimate: single about 1h36m, plate A about 7h05m, plate B about 9h20m. A wildly different time means the wrong preset or nozzle was applied.
7. Confirm the wipe tower sits where the file puts it (singles: left of the tag on its row; plate A: behind the middle disc; plate B: back-left cell pushed inward), then print.

## Gate print reference

MAX 18, printed 2026-08-25 from the same build (letters modifier + object key + back-text modifier, tower (30, 106.5)); Brian's verdict: "the final print looks great, let's use these settings". `final/sharks-nametag-max-18.3mf` is that build: its 3MF content is identical to the gate file except for three CLI-generated part UUIDs, and its offline slice carries the identical set of extrusion segments on all 37 layers (per-layer segment compare and per-feature totals, 2026-08-26). The only differences between the two slices are travel moves to the wipe tower and the order of some paths on the color-change layers, and the slicer produces the same amount of variation when it slices the gate file twice.

## Files

| file | kid | number | size (bytes) | sha256 |
|---|---|---|---|---|
| `sharks-nametag-sami-5.3mf` | Sami | 5 | 976,474 | `bf5ddbab6d65d1a46b5ea5e57e0af62b9c6d058bb59fe9817b41f8c5b90accd7` |
| `sharks-nametag-joe-8.3mf` | Joe | 8 | 1,055,468 | `965e38f3161e10cfbbe7b2245c28e6426759e83f66bf65f9669763175f8b421c` |
| `sharks-nametag-nathaniel-9.3mf` | Nathaniel | 9 | 981,940 | `c7584fa142c247c62d515ebb00362a058ca1c0babcecac0fa38ef789e3739b36` |
| `sharks-nametag-zachary-10.3mf` | Zachary | 10 | 1,037,994 | `d9b695024d9c8f0838f190ebbd3ce05c2d98e221173240b94445cb7699762502` |
| `sharks-nametag-jack-12.3mf` | Jack | 12 | 954,599 | `efb447e75f4b619151da96bd7e0a7b7f622b7cdf1a07497a15f88f0577419bae` |
| `sharks-nametag-kai-14.3mf` | Kai | 14 | 867,608 | `c7c3d75abbdce9d94383599aeb0fca5d77be44f601f72b59944d88b90fcaaf52` |
| `sharks-nametag-david-15.3mf` | David | 15 | 969,660 | `c108ba36aa50ab49ca5a33263c97f03d5d7b7b404c95c61ef84f93c819794598` |
| `sharks-nametag-callan-17.3mf` | Callan | 17 | 917,922 | `e4346ad88b5fc7d60fe491108deff083efd1068aac03f0f0f6ac5f614ed24c30` |
| `sharks-nametag-max-18.3mf` | Max | 18 | 997,109 | `e9ad9115c3bd316e1fce796d68223802690172c0b7f7b60790efd05a3123d05c` |
| `sharks-nametag-benji-19.3mf` | Benji | 19 | 1,021,088 | `c0f66630eddcee8856d0e82d6b80449494a62b37fe975b0e8b9dfca5a01c4624` |
| `sharks-nametag-julian-20.3mf` | Julian | 20 | 1,014,454 | `29e143360f7380a7daf5b0505517237436dad16c9d841b04759b759005fb6e3c` |
| `sharks-nametag-leonidas-25.3mf` | Leonidas | 25 | 1,102,230 | `f9eff82b4791fc58deed7f41a9852545a9a8951b64f1d1f68e31d5dc9352a1ba` |
| `sharks-nametag-luke-30.3mf` | Luke | 30 | 1,038,528 | `fdeb36741e4bad506e4350260f724b2c0e5cbe776ba400ddcf6ca3c12a82ad6a` |
| `sharks-nametag-krystof-33.3mf` | Krystof | 33 | 1,175,475 | `9222f9e3326ca12fd9533cf06d0a24f69b33b28d7b069d1526981448e9b03f65` |
| `sharks-nametag-roster-plates.3mf` | all 14 (plate A: Sami, Joe, Nathaniel, Zachary, Jack, Kai; plate B: David, Callan, Max, Benji, Julian, Leonidas, Luke, Krystof) | 5 to 33 | 13,957,878 | `9c4b7856a04ad019577611cd90198f3ecf368469d10bf4cd7220f228782e134b` |

Verification 2026-08-26 (offline CLI graft slices, `pipeline/graft_slice.py`): MAX 18 rc 0, 37 layers, 1h35m42s, 17.1 / 2.5 / 1.6 g; Sami 5 rc 0, 37 layers, 1h34m23s, 17.2 / 2.4 / 1.6 g; plate A rc 0, 37 layers, 7h05m20s, 86.7 / 13.2 / 1.4 g; plate B rc 0, 37 layers, 9h19m00s, 113.3 / 16.8 / 1.8 g (white / navy / cyan). Letter tops on both sliced singles: stacked voids 0.00 mm2, 164 starts, top fill 90 deg (along the stems), the judged C7 result.

## How to rebuild

From the vault root (`~/ClaudeProjects/3d-modeling-brain`), with the flattened presets `pipeline/flat-machine.json`, `flat-process.json`, `flat-filament.json` in place (regenerate with `pipeline/flatten_04.py` only if the Studio presets change):

```bash
# all 14 singles -> final/sharks-nametag-<name>-<number>.3mf (about 6 min)
.venv/bin/python projects/Sharks-nametag/pipeline/batch_roster.py
# one kid only
ONLY=max-18 .venv/bin/python projects/Sharks-nametag/pipeline/batch_roster.py
# the two-plate project -> final/sharks-nametag-roster-plates.3mf
# (REUSE_STL=1 reuses pipeline/plates-stl/*.stl; drop it to rebuild the 14 models, about 6 min)
REUSE_STL=1 .venv/bin/python projects/Sharks-nametag/pipeline/plates.py
# dry run somewhere else
OUT=/tmp/dry-run.3mf REUSE_STL=1 .venv/bin/python projects/Sharks-nametag/pipeline/plates.py
# offline slice check (rc, layers, time); --plate 2 for plate B
.venv/bin/python projects/Sharks-nametag/pipeline/graft_slice.py projects/Sharks-nametag/final/sharks-nametag-max-18.3mf /tmp/max-18-sliced.3mf
```

Every builder asserts the recipe on the written file and on a CLI round trip (presets, colors, bed, flush block, tower rule, modifier keys, object key, object names, positions); a red assert means the file must not be printed.
