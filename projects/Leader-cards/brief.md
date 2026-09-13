---
title: Leader cards
type: project-brief
status: design approved 2026-09-12. Next is the slot test coupon
created: 2026-09-12
tags: [fishing, tackle, petg, leader, x2d]
---

# Leader cards

Printed replacement for the cardboard cards Brian wraps long fishing leaders on (salmon, halibut, and rockfish rigs, up to 36 in of leader) so they fit in the tackle box. Cardboard works when new but the slits tear, the hook holes enlarge, and the card goes soft once wet. Reference: `images/cardboard-card.jpg`.

## Locked decisions

- One universal card for every rig. The card holds only the leader line. Hooks, swivels, and lure bodies hang free off the ends and may be longer than the card.
- Line: 25 to 40 lb, about 0.5 to 0.7 mm diameter, mono or fluoro.
- Both ends lock by pinching the line in tapered slots. No hook-point holes, no swivel notches.
- Wrapping order: start at the swivel, wrap toward the lure, finish near the lure.
- Storage: rigs go back on the cards wet and stay closed in the box between trips. Material must not absorb water; the card must have no pockets that hold water.
- Material: white PETG. PLA (heat) and nylon (water) are out; ASA is out on sunscreen ([[marine-materials]]).
- Approach: flat card with tapered slots (option 1 of 3). Rejected: railed spool card (thicker, traps water) and TPU slot inserts (two materials, TPU feeds poorly in the AMS; held in reserve if PETG slots fail).
- First batch: 1 card.

## Card geometry

- Footprint 70 x 45 mm, matching the cardboard card (smaller than a credit card). If Brian measures the cardboard card before CAD, his measurement replaces 70 x 45. Hard ceiling: 86 x 54 mm (credit card).
- Thickness 3 mm.
- Line wraps end to end around the long axis, bending over the two 45 mm short edges. About 140 mm per wrap, about 6.5 wraps for 36 in.
- Short (wrap) edges: rounded on the top face, 45 degree chamfer on the bottom face so the edge prints without a feather lip at the bed.
- Corners and long edges lightly rounded.
- Both faces plain and flat. No pockets, ribs, or text.

## Slots

- One slot per end, entering from a long edge about 8 mm in from the short edge. The two slots sit on opposite long edges, so the card is the same after a half turn.
- Each slot slants about 45 degrees toward its nearest short edge, so wrap tension pulls the line deeper rather than out.
- Through the full thickness. Mouth about 1.2 mm with a small lead-in funnel, tapering to closed over about 8 to 10 mm. Heavier line stops shallower, lighter line deeper; print tolerance only moves the stop point.
- Final taper numbers come from the test coupon, not from this brief.

## Test coupon (before any card)

Minimal per [[feedback-minimal-test-coupons]]: a 3 mm thick strip carrying four slot variants (varying taper length and mouth width) and one wrap edge profile. Nothing else. Quote print time from a real slice.

Brian tests each variant with real 25 lb and 40 lb line. Pass criteria:

1. Line presses in by hand without a tool.
2. Line holds with the lure's weight hanging on it and does not creep out.
3. Line pulls out with no visible crimp or nick.
4. About 20 in and out cycles do not wear the slot open.

The best variant goes on the card. If no variant holds 25 lb line reliably, revisit the TPU slot insert approach.

## Printing

- Nozzle: 0.4 mm. Before slicing and before printing, confirm the physically installed nozzle and the Bambu Studio machine profile both read 0.4 ([[printer-x2d]]).
- Flat on the bed, chamfered edges down, no supports. Chamber fan on cool (PETG).

## Build sequence

1. Test coupon: CAD, STL and 3MF, print. Stop: Brian tests with real line and picks a variant.
2. One card with the winning slot. Stop: Brian checks tackle box fit and wraps a real 36 in rig.
3. Retrospective in `knowledge/learnings/leader-cards.md`.

## Files

All in `projects/Leader-cards/`: this brief, the CAD source, and STL and 3MF for the coupon and the card. Built with the `/3d-model` skill.
