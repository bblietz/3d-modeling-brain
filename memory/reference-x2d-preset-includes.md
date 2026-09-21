---
name: reference-x2d-preset-includes
description: X2D machine presets keep all G-code in `include` template files; any preset flattener for the Bambu CLI must merge includes as well as inherits, or the verification slice uses a generic start G-code and under-reports time
metadata:
  type: reference
---

Bambu Studio 02.08 X2D machine presets (`~/.config/BambuStudio/system/BBL/machine/Bambu Lab X2D 0.4 nozzle.json`, same for 0.6) define NO G-code themselves: start, end, layer-change, time-lapse and filament-change G-code live in five `... template <name>.json` files listed under the preset's `include` key. X2D filament presets likewise `include` `fdm_filament_template_direct_bowden_e3d` (the six-values-per-key extruder-variant layout).

The vault's older `flatten()` helpers (Garmin-943-helm-panel, NACS-organizer, Leader-cards `make_plate.py`, NACS-wall-holder `pipeline/make_coupon_3mf.py`) follow only `inherits`. Their shipped 3MFs were fine (Studio's GUI re-resolves system presets on open), but their CLI verification slices ran with a generic fallback start G-code (prime lines, `M109 S205`) and under-report print time (7 min 39 s vs 12 min on a small probe). The fixed flattener is in `projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py`: for each preset in the chain, base first, merge its includes, then its own keys; assert `"X2D start gcode" in gcode`. Copy that one for new projects. Also there: plate centring by transform + STL bounds (the CLI does not re-centre meshes on export) and a solidity check by weight (Bambu keeps the "Sparse infill" label at 100%). Related: [[feedback-stl-to-bambu-3mf]], [[project-iphone-case]].
