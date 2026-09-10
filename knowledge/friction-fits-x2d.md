---
title: Friction-fit lids on the X2D, turnkey recipe
type: technique
date: 2026-09-10
status: validated (v3 fit); opening feature modelled but unprinted
tags: [x2d, fits, clearance, crush-ribs, pla, recipe]
---

# Friction-fit lids on the X2D, turnkey recipe

Validated on the Build123d-trial project box: an 80 x 50 x 30 mm PLA box
with a full-perimeter plug lid, four print iterations, 0.6 high-flow
nozzle. Full history in [[build123d-trial]] (learnings) and the project
[[brief]]. Start here; do not rediscover it.

## When this applies

Any lid, cap or cover that grips by friction on a full-perimeter vertical
plug, where the engagement is short (a few millimetres of straight wall).
Symptom without the recipe: the lid seats but rattles, and tightening the
clearance to fix it goes from loose to un-assemblable with almost nothing
in between.

## Why plain clearance does not work

The [[printer-x2d]] "0.2 mm snug / 0.3 mm free" rule is for a local
feature - a pin in a hole, a tab in a slot. It does **not** hold for a
full-perimeter vertical plug fit, for two reasons:

- **No compliance.** A closed rectangular plug inside a closed rectangular
  cavity is stiff in every direction. There is nothing to deflect, so the
  fit is either clear (rattles) or interfering (will not go in). On the
  trial box the plug engaged only 1.2 mm of straight wall once the lead-in
  chamfer was subtracted - nowhere near enough to grab.
- **Process offset runs the wrong way.** Calipers on the trial box: the
  cavity printed 0.22 mm under design and the plug 0.33 mm under, so the
  as-printed gap came out about **0.055 mm per side looser than designed**.
  A plain-clearance friction fit therefore needs designed interference,
  which for a rigid full-perimeter fit is jam territory.

Measured, not guessed: 0.2 mm per side rattled, 0.1 mm per side still had
play. Do not spend prints walking the clearance down.

## The recipe: crush ribs

Relax the plug body to a **free** clearance and let small local ribs own
the fit. The ribs are thin enough to deform; the plug is not.

| Parameter | Value | Why |
|---|---|---|
| Plug body clearance | **0.15 mm per side** | free fit, the body must not touch |
| Ribs | **2 per side, 8 total** | one per side lets the lid cock; two constrain it |
| Rib form | **half-embedded cylinder, R1** | a lens crest, not an edge; deforms predictably |
| Rib proud of plug face | **0.35 mm** | gives 0.20 mm interference over the 0.15 mm clearance |
| Rib top lead-in | **0.5 mm chamfer** | the rib engages only after the plug has aligned |
| Plug lead-in | **0.8 mm, 45 degrees** | aligns the lid before any rib touches |

Designed interference 0.20 mm per side, predicted actual crush about
**0.145 mm** after process offsets. On the X2D in PLA this grips firmly
with no movement.

## Design for removal, from the start

A snug lid that is flush with the box and has a flat top **cannot be
opened barehanded.** This was discovered the hard way and needed an
improvised handle. Every friction-fit lid needs an opening feature
designed in from the beginning: a fingernail scoop, a lip, a notch or a
handle.

What worked on the trial box: a 45-degree cove at each short end, 25 mm
wide, opening to a 1.5 mm nail gap at the edge and tapering to zero while
still over the box rim. A nail slips in and peels one end up, which beats
the ribs' static friction far more easily than a straight pull. Prints
without support.

**Map removal features into the in-use orientation, not the print
orientation.** A plug lid flips to install, so its bed face during printing
is its top face in use. The first attempt cut the coves into the print-bed
face, which after the flip put cosmetic dips on the lid's top and left no
nail gap at all. Build an assembled "lid installed on box" object in the
viewer and look at it - orientation mistakes are obvious there and
invisible in a parts-laid-flat view.

## These numbers are one calibration

`0.15 mm clearance` and `0.35 mm proud` are the result of one calibration,
on:

- nozzle **0.6 high-flow**
- wall generator **classic** (the X2D stock quality preset)
- **PLA Basic**, the spool loaded 2026-07-31
- 0.18 mm layers

Re-run a coupon before trusting them if any of those change:

- **Filament brand or line.** Fit calibration is brand-specific: a
  coupon-validated +0.02 mm interference printed smash-tight after a
  manufacturer change ([[clawd-mascot]]). Shrinkage-compensation
  polynomials live in the filament preset and differ between PLA Basic and
  PLA Matte.
- **Nozzle.** The crest is built out of extrusion widths; changing the
  nozzle changes how a 0.35 mm proud lens is actually laid down.
- **Wall generator.** Classic can absorb a sub-line-width crest into the
  perimeter; arachne gives it its own variable-width bead. Different rib.
- **Material.** PLA Matte has about half the Z impact strength of Basic
  (6.6 vs 13.8 kJ/m^2), and crush ribs are repeatedly-stressed thin
  features. Prefer Basic for the ribbed part. A PETG respin invalidates
  these numbers outright.

The coupon is a corner section only: one cavity corner plus the matching
plug corner carrying one rib, on a thin substrate, nothing else on the
plate. Quote its print time from a real slice before printing it.

## Verify in the model, not just by eye

- Measure the fit from **geometry cross sections**, not from the
  constants. A probe slab through the assembled part gives the cavity, the
  plug body and the rib envelope independently, so an arithmetic error in
  a derived dimension cannot pass.
- Re-measure on the **exported mesh**, which is what the slicer sees.
  Tessellating the corner fillets cuts inside the true surface. On the
  trial box the cost was 0.001 mm of rib envelope, small enough to ignore -
  but that is a measured result, not an assumption, and a coarser
  tessellation or a smaller corner radius will not be as kind.
- When measuring a cavity with a probe slab, take the **largest resulting
  solid**. A square probe pokes past rounded outer corners and leaves
  slivers that inflate the measured bounding box.

Related: [[printer-x2d]], [[build123d-trial]], [[smooth-surfaces-x2d]]
