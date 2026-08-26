---
tags: [printing, settings, decision, reference]
---

# Smooth surfaces on the X2D

Decision (2026-07-31): smooth top finish is the DEFAULT for all prints,
via ironing plus mild top-surface tuning baked into both slicing routes.
Bottom finish is a plate decision, not a settings decision.

## Where each face's finish comes from

| Face | Shaped by | Smoothness lever |
|---|---|---|
| Walls | Nozzle side | Already excellent on the X2D; nothing to do |
| Tops | Open-air extrusion lines | Slicer settings (ironing + tuning) |
| Bottoms | The build plate (molded cast) | Plate choice only; no slicer fix |

## Default top-surface settings (0.18 mm Balanced base, 0.6 nozzle)

One package, always applied together:

| Setting | Value | Bambu Studio key |
|---|---|---|
| Ironing | Top surfaces only | `ironing_type` = `top` |
| Ironing pattern | zig-zag | `ironing_pattern` |
| Ironing flow | 10% | `ironing_flow` |
| Ironing line spacing | 0.15 mm | `ironing_spacing` |
| Ironing speed | 30 mm/s | `ironing_speed` |
| Top surface line width | 0.55 mm | `top_surface_line_width` |
| Top shell layers | 5 | `top_shell_layers` |
| Top surface speed | 120 mm/s | `top_surface_speed` |
| Monotonic top fill | on (default) | `top_surface_pattern` |

Applied on both routes:

- **GUI route** (single-color parts sliced by hand): one-time user
  process preset in Bambu Studio, named
  `0.18mm Balanced Ironing @BBL X2D 0.6 nozzle`, derived from
  `0.18mm Balanced Quality @BBL X2D 0.6 nozzle` with the table above.
- **CLI route** (project 3MFs from the [[3d-model]] pipeline): the
  preset-flattening step injects the same keys as overrides into the
  flattened process JSON.

Costs and limits: ironing adds roughly 5 to 15 percent print time (more
on plate-like parts) and smooths FLAT tops only.

**PETG exception (2026-08-22, [[sharks-nametag]] coupons, 0.4 nozzle):**
do NOT iron PETG parts with small raised top art. Both the PLA-tuned
package above (10% / 0.15 / 30) and a PETG-tuned one (15% / 0.1 /
20 mm/s) dragged the 0.5 to 1 mm wide raised tops: pits showing the
color underneath, swirl/drag marks, wavy edges. What won the A/B/C
coupon plate was `ironing_type` no ironing + `top_one_wall_type`
"not apply" (two walls on every top surface) + `top_surface_speed` 60:
the second top loop hides the fill-line ends, which is most of what
ironing was buying on small regions. Treat the table above as the PLA
default; for PETG start from the no-ironing + two-top-walls recipe and
coupon-test before ironing anything. Curved or sloped
cosmetic surfaces need the 0.4 mm nozzle (situational escalation; the
0.6 high-flow stays installed) or accept the finish.

## Bottom surfaces (textured PEI policy)

The textured PEI plate molds its random sandblasted texture into every
first layer; no setting changes that. Policy:

- Orient a part's presentation face as an ironed TOP when geometry
  allows, not against the bed.
- A Bambu Smooth PEI plate (about 35 to 45 USD) is the unlock for
  mirror-gloss bottoms; buy when bottom finish starts to matter. Select
  the matching plate type in Bambu Studio when using it.
- No rafts as a texture workaround; they trade one bad face for a worse
  one.

## Rollout status

2026-07-31: all seven project 3MFs (Clawd-mascot x3, Lego rockets x3,
project-box-ironing) patched in place via `scripts/apply_smooth_top.py`
and round-trip verified through Bambu Studio's reader (ironing keys,
diff list, and filament colors preserved).

Gotcha found on the first patch attempt: Bambu Studio's GUI resolves an
opened project as "named system preset + `different_settings_to_system`
diff list". Setting values inside `project_settings.config` is NOT
enough; every changed key must also appear in
`different_settings_to_system[0]`, or the GUI silently shows and slices
the system value ("No ironing"). The CLI reader does not normalize this
way, so a CLI round trip cannot catch the mistake; GUI ground truth
requires opening the file once. `apply_smooth_top.py` handles values
and diff list together.
Geometry-only 3MFs (Kelkom button, project-box.3mf) carry no embedded
settings; they get the defaults from the GUI ironing preset at slice
time.

## Verification plan

Reprint the [[build123d-trial]] lid (and box) with the new preset:

- Flat lid top comes out visibly line-free.
- Time delta acceptable versus the un-ironed print.
- Doubles as the pending 0.2 mm friction-fit validation; record the
  measured fit in the trial retrospective.

Related: [[printer-x2d]]
