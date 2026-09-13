---
title: Leader cards
type: project-brief
status: design approved 2026-09-12, hook-bend slot hitch and wavy wrap edges added same day. Next is the slot test coupon
created: 2026-09-12
tags: [fishing, tackle, petg, leader, x2d]
---

# Leader cards

Printed replacement for the cardboard cards Brian wraps long fishing leaders on (salmon, halibut, and rockfish rigs, up to 36 in of leader) so they fit in the tackle box. Cardboard works when new but the slits tear, the hook holes enlarge, and the card goes soft once wet. Reference: `images/cardboard-card.jpg`.

## Locked decisions

- One universal card for every rig. The card holds only the leader line. Hooks, swivels, and lure bodies hang free off the ends and may be longer than the card.
- Line: 25 to 40 lb, about 0.5 to 0.7 mm diameter, mono or fluoro.
- Both ends lock the line in slots. No hook-point holes, no swivel notches.
- Each slot has a hook-bend hitch so a line that goes slack stays caught. Chosen over a bump detent because it needs no flexing of a stiff 3 mm PETG wall, so print tolerance matters little.
- The two short wrap edges carry a smooth wave so a slack wrap stays in its valley instead of sliding along the edge. Fine wave chosen: 3 mm spacing, about 0.6 mm deep, every peak and valley rounded, nothing sharp. Rejected: 5 mm spacing with 1 mm deep valleys.
- Wrapping order: start at the swivel, wrap toward the lure, finish near the lure.
- Storage: rigs go back on the cards wet and stay closed in the box between trips. Material must not absorb water; the card must have no pockets that hold water.
- Material: white PETG. PLA (heat) and nylon (water) are out; ASA is out on sunscreen ([[marine-materials]]).
- Approach: flat card with slots (option 1 of 3). Rejected: railed spool card (thicker, traps water) and TPU slot inserts (two materials, TPU feeds poorly in the AMS; held in reserve if PETG slots fail).
- First batch: 1 card.
- Card size 3 x 2 in (Brian, 2026-09-12), replacing the 70 x 45 mm estimate from the photo.
- Nothing sharp touches the line (Brian, 2026-09-12): the slot walls get the same 0.6 mm top round and 0.6 mm bottom chamfer as the card edge, and the slot's outside corners (hook tongue, funnel, mouth) are rounded to 0.8 mm in plan view.
- Gradual exit (Brian, 2026-09-12): a 15 degree exit ramp on both faces, from the pocket wall toward the wrap edge, so line under wrap tension does not bend 90 degrees over the face edge and take a permanent kink. Chosen over an angled entry from the long edge.
- Visual options are shown on an HTML page, never ASCII art ([[feedback-html-visual-companion]]). Slot variants page: https://claude.ai/code/artifact/18ae8924-111d-4f77-ab7c-6c4948e84995

## Card geometry

- Footprint 3 x 2 in (76.2 x 50.8 mm), set by Brian. Under the 86 x 54 mm credit card ceiling.
- Thickness 3 mm.
- Line wraps end to end around the long axis, bending over the two 50.8 mm short edges. About 152 mm per wrap, about 6 wraps for 36 in.
- Plan-view corners: 2.9 mm radius, chosen so the straight part of each short edge is exactly 45.0 mm, a whole number of wave pitches.
- Short (wrap) edges: the straight 45 mm between the corners is a wave of alternating tangent arcs, 3 mm peak to peak, 0.6 mm deep, arc radius about 1.09 mm, giving 15 valleys per edge.
- Whole perimeter: 0.6 mm round on the top face, 0.6 mm 45 degree chamfer on the bottom face so the edge prints without a feather lip at the bed. Both are capped at 0.6 mm because a larger round or chamfer cannot follow the 1.09 mm wave peaks.
- Both faces plain and flat. No pockets, ribs, or text. The slots are through cuts, so they drain.

## Slots

One slot per end, each cut through the full thickness. The two slots sit on opposite long edges about 8 mm in from their short edges, so the card is the same after a half turn.

Each slot is a hook bend in two parts:

1. **Lead-in:** straight in from the long edge, about 1.2 mm wide with a small funnel at the mouth so the line finds it by feel, about 6 mm deep.
2. **Pocket:** at the bottom of the lead-in the slot turns toward the nearest short edge and angles back toward the mouth side, about 4 to 5 mm long, tapering from about 1.0 mm to closed. Keep at least 2 mm of solid wall between the pocket and the long edge.

Why it holds: the line leaves the slot heading for the nearest short edge, so wrap tension on either slot pulls toward that edge and seats the line in the pocket tip, where heavier line stops shallower and lighter line deeper. If the wraps go slack, the line still sits in the pocket; to escape it must travel backward, away from the short edge, and around the corner into the lead-in.

In use: press the line into the lead-in, slide it around the corner into the pocket, then run it to the nearest short edge. Start slot just past the swivel, wrap toward the lure, laying each wrap in a valley, and finish in the other slot; the lure hangs off that end. To unwind, slide the line back around the corner and out.

Edge treatment, verified in the prototype build (`prototype/leader_card.py`, 2026-09-12):

- **Pocket tip:** ends in a 0.15 mm radius, a 0.3 mm gap, still narrower than 25 lb line. A truly sharp tip makes the rounds on the two pocket walls collide and the top round cannot be built.
- **Slot walls:** 0.6 mm round on top, 0.6 mm chamfer underneath. Outside corners 0.8 mm in plan view.
- **Exit ramp:** on both faces, over the band where the line sits, 0.7 mm deep at the pocket wall, rising at 15 degrees along the card (about 2.6 mm run), with a 0.3 mm round where it meets the wall. The square pinch band left at mid-thickness is about 1.2 mm (1.16 mm on the 50 degree hook, the thinnest); the build fails below 1.0 mm.
- **Printing:** the ramp on the bed side is a shallow groove roof bridged across under 3 mm.

Final lead-in width, pocket angle, and pocket taper come from the test coupon, not from this brief. A fifth option (6 mm long pocket) is on the variants page; Brian decides which variants go on the coupon.

## Test coupon (before any card)

Minimal per [[feedback-minimal-test-coupons]]: a 52 x 11.8 x 3 mm strip carrying four hook-bend slot variants (varying lead-in width, pocket angle, and pocket taper) along one long edge. Its two short ends carry the same wave as the card (2 valleys each), so the wave is tested too. Nothing else. Quote print time from a real slice.

Brian tests each variant with real 25 lb and 40 lb line. Pass criteria:

1. Line goes in and around the corner by hand without a tool.
2. Line holds with the lure's weight hanging on it and does not creep out.
3. With the line slack, shaking the coupon does not free it from the pocket.
4. Line comes out with no visible crimp or nick.
5. About 20 in and out cycles do not wear the slot open.
6. A slack wrap around the coupon's length stays in its end valleys when the coupon is shaken lightly.

The best variant goes on the card. If no variant holds 25 lb line reliably, revisit the TPU slot insert approach. If the wave does not hold slack wraps, revisit the 5 mm wave with 1 mm deep valleys.

## Printing

- Nozzle: 0.4 mm. Before slicing and before printing, confirm the physically installed nozzle and the Bambu Studio machine profile both read 0.4 ([[printer-x2d]]).
- Flat on the bed, chamfered edges down, no supports. Chamber fan on cool (PETG).

## Build sequence

1. Test coupon: CAD, STL and 3MF, print. Stop: Brian tests with real line and picks a variant.
2. One card with the winning slot. Stop: Brian checks tackle box fit and wraps a real 36 in rig.
3. Retrospective in `knowledge/learnings/leader-cards.md`.

## Files

All in `projects/Leader-cards/`: this brief, the CAD source, and STL and 3MF for the coupon and the card. Built with the `/3d-model` skill.
