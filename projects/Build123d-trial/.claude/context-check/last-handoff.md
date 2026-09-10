# Handoff: Build123d-trial, learnings back-applied (2026-09-10)

## State

Six weeks of vault learnings applied to the project files. Nothing about
the geometry changed; everything about the assumptions around it did.

- `project_box.py` re-runs clean. New: a `NOZZLE` constant driving
  `MIN_WALL` off the two-perimeter floor table, calibration provenance on
  the fit constants, a re-measure of the fit on the exported mesh, a parse
  -back check of the exported 3MF, and a layer-grid advisory.
- `pipeline/make_print_3mf.py` + `pipeline/x2d-pla-0.6-settings.json` build
  `project-box-print.3mf` from the STLs. Idempotent, self-verifying.
- `project-box.3mf` regenerated from source (a Studio re-save on 2026-09-10
  had left it with 8 duplicate object entries).
- New turnkey note `knowledge/friction-fits-x2d.md`; retrospective and
  brief brought up to date.

## Decisions already locked

- **Target nozzle is 0.6 high-flow**, set by `NOZZLE` in `project_box.py`.
  The box is a coarse part with 2.4 mm walls and a flat ironed top, and
  the ironing package is a set of 0.6 numbers. The resident nozzle is
  0.2 in both positions since 2026-08-23, so printing needs a swap. This
  is stated in the source, the brief and the pipeline output.
- **`project-box-print.3mf` is the print file.** Every other 3MF in the
  directory is superseded history and must not be printed - the
  `-ironing` ones carry a 55 C textured plate with an empty filament diff
  slot, so the GUI resets the temperature on open.
- **Settings come from a Studio-written template, not the flattener.**
  `scripts/flatten_presets.py` reads the stale 02.07.00.08 bundle and
  never merges the machine preset's `include` gcode. The pipeline patches
  `x2d-pla-0.6-settings.json` (Studio 02.08.02.61's own output) instead.
- **`different_settings_to_system` is positional:** [0] process,
  [1..N] filaments, [N+1] machine. Bed temps are filament-scope. The
  pipeline writes the slots itself; `scripts/apply_smooth_top.py` only
  covers slot 0 and is not called.
- **The fit constants are one calibration**, not portable values: 0.6
  high-flow, classic wall generator, PLA Basic, the 2026-07-31 spool.
  Nozzle, wall generator, filament brand or material changing means a
  coupon first.
- **Brian chose a full reprint file over a corner coupon**, having been
  shown the coupon rule and the tradeoff.

## Next

1. Swap to the 0.6 high-flow nozzle; confirm with `scripts/x2d-status.py`.
2. Select the 0.6 nozzle printer preset in Studio's Prepare tab BEFORE
   opening the project.
3. Open `project-box-print.3mf` and confirm the plate renders both parts.
   This is the mandatory ground truth - a hand-patched 3MF has passed a
   CLI round trip and still rendered empty. CLI slicing cannot substitute:
   it only works on Studio-saved projects.
4. Print. Record the v4 result in `knowledge/learnings/build123d-trial.md`:
   does the fingernail scoop actually open the lid barehanded, and does
   the rib fit still hold after the nozzle swap.

## Blocked, unrelated to this work

`scripts/x2d-status.py` cannot reach the printer:
`~/.config/BambuStudioBeta/BambuStudio.conf` is **0 bytes**, so the LAN
access code is gone. Re-enter it in Studio Beta, or set `X2D_ACCESS_CODE`.
