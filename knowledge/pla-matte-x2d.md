---
tags: [materials, pla, bambu, x2d]
source: preset diff Bambu PLA Basic vs Matte @BBL X2D (02.08.01.55), 2026-08-01
---

# PLA Matte on the X2D

Flattened-preset diff of `Bambu PLA Basic @BBL X2D` vs `Bambu PLA Matte
@BBL X2D` (inherits chains resolved). Takeaways:

- **Temps, flow ratio, pressure advance, and max volumetric speed are
  identical** (Matte even allows 22 vs 21 mm3/s standard, 40 high-flow).
  Printing Matte on the Basic profile is NOT a temperature or flow
  mismatch on this printer.
- Real differences: purge volume (`filament_prime_volume` 45 vs 30,
  `filament_change_length` 10 vs 5 - Matte needs more flush, expect
  faint color carryover on changes if using the Basic profile), and
  slightly different shrinkage-compensation polynomials for holes and
  contours (a few um to ~0.01 mm on small bores - relevant to
  press-fit calibration like [[clawd-mascot]] eyes).
- **Matte is brittle: `impact_strength_z` 6.6 vs 13.8 kJ/m2** - about
  half of Basic. Give matte parts real infill and avoid thin
  cantilevers; see [[printer-x2d]] wall rules.
- Ironing: no filament-scoped ironing keys differ; the smooth-top
  process package applies unchanged. The ironed top comes out slightly
  glossier than matte side walls.
- Fit calibrations do not transfer blindly across filament lines: the
  compensation coefficients belong to the filament preset, so re-check
  snug fits (~0.02 mm scale) when switching e.g. Basic to Matte.

## Related

- [[printer-x2d]], [[clawd-mascot]]
