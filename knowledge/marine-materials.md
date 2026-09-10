---
title: Marine materials, printed vs sheet
type: knowledge
created: 2026-09-09
tags: [materials, marine, asa, hdpe, starboard]
---

# Marine materials: ASA vs King Starboard (HDPE)

Settled while choosing a material for [[garmin-943-helm-panel]]. Typical
published values, good enough to choose between materials, not for stress work.

| Property | King Starboard (HDPE) | ASA (printed) | Matters because |
|---|---|---|---|
| Water absorption | under 0.01 percent | about 0.3 percent, plus porosity between layers | HDPE is genuinely impervious; a printed part is not |
| Impact | very tough, ductile even cold | brittle-ish, fails along layer lines | a dropped winch handle dents one and cracks the other |
| Chemical resistance | inert to fuel, solvents, cleaners, salt | attacked by acetone, MEK, and SUNSCREEN | sunscreen on hands is guaranteed on a boat and attacks ABS-family plastics |
| UV | stabilised and pigmented through, 10+ years direct sun | UV stable but chalks eventually | Starboard also hides scratches, colour goes all the way through |
| Stiffness | about 900 MPa | about 2000 MPa, near 1400 effective with sparse infill | ASA is stiffer per mm |
| Creep | significant under sustained load, worse when hot | minimal | HDPE keeps sagging for months under a fixed load |
| Max service temp | about 82 C | about 95 C | ASA has more headroom behind glass |
| Thermal expansion | about 0.15 to 0.2 mm/m/C | about 0.08 mm/m/C | over 470 mm and 30 C, HDPE moves about 2 mm; use oversized fastener holes |

## The decision rule

ASA's advantages are stiffness, creep and heat. All three are cured by making
the sheet thicker, and thickness is nearly free in sheet stock. Starboard's
advantages are imperviousness, impact toughness, chemical resistance and being
one piece. None of those can be engineered into a printed panel.

So for a flat exterior marine part, **use Starboard and go one size thicker.**
Stiffness matches at roughly 1/2 in Starboard to 3/8 in printed ASA.

## When printing still wins

- Geometry a router cannot make: recessed pockets, cable channels, integrated
  ribs, moulded-in bosses.
- Anything larger than the bed needs splitting, and every seam is a bonded
  joint that can wick water and work loose. Three seams was the cost on the
  helm panel.
- If you do print an exterior part: ASA, not ABS or PETG. Acetone vapour smooth
  it to seal the surface porosity. ASA-CF is stiffer and warps less, at the
  cost of brittleness, and needs a hardened nozzle.
- PLA and nylon are both disqualified outright, PLA on heat and nylon on water
  absorption.
