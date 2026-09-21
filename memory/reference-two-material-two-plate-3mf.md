---
name: reference-two-material-two-plate-3mf
description: Recipe for one Bambu project 3MF with one plate per material (different filament per plate) from the CLI; working script in the iPhone case pipeline; the fixes the CLI output needs before it will slice
metadata:
  type: reference
---

Working example: `projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py` (plate 1 TPU 95A HF case, plate 2 PETG Basic guard ring, 2026-09-20). Route: the CLI's own multi-plate assembler, `--load-assemble-list spec.json` (first used in `projects/Sharks-nametag/pipeline/plates.py`), NOT hand-written plate blocks: one `plates[]` entry per material, its object with `"filaments": [n]`, `need_arrange: false`; no input files and no `--load-filament-ids` alongside; `--load-filaments "f1.json;f2.json"`. The `/3d-model` skill's "Multi-plate kits" section still says the CLI cannot assign plates; this route is the better one.

What the raw export needs before it slices or reads right:
- `pos_x/pos_y` place the STL's own ORIGIN, plate-relative: subtract the part's bbox centre to centre it.
- Every object is named `assemble_1`: rename object and part by the part's `source_file`; add the object-level `extruder` to match the part's.
- `filament_colour`, `filament_map`, `filament_nozzle_map` come out with ONE entry: set one per filament.
- `flush_multiplier` one per extruder and `flush_volumes_matrix` = extruders x filaments^2 entries (`flush_volumes_vector` extruders x filaments), or the slice fails with "Flush volumes matrix do not match to the correct size!".
- `filament_map_mode` "Manual" in project_settings AND in each plate block (plus `filament_maps`), map `["1", "1"]` to keep both materials on extruder 1 (direct drive; extruder 2 is the low-accuracy Bowden one).
- With the include-merging `flatten()` ([[reference-x2d-preset-includes]]) the per-variant filament keys come out complete (filaments x 6); the NACS script's `expand_variants()` is only needed with the old flattener.

Checks that worked: plates and membership before and after a CLI round trip; `graft_slice(plate=n)` per plate; `slice_info` lists only that plate's filament, `group_id="0"` = extruder 1 (a `T1` in Bambu G-code selects filament 2, not extruder 2); nozzle and bed temperature lines are INDENTED in the X2D start G-code (`^\s*M1[49]0 S70`). The GUI opening the file is still the ground truth. Related: [[project-iphone-case]], [[feedback-stl-to-bambu-3mf]].
