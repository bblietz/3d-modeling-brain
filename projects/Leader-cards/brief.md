---
title: Leader cards
type: project-brief
status: LC2 built and sliced 2026-09-12 (3 x 1.5 in, comb wrap edges, 3 side slots, 15 min, 6.9 g). Waiting on Brian to print, check tackle box fit, and wrap a real rig
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
- Slot pick (Brian, 2026-09-12): variant 5 reversed. A 6 mm pocket (1.0 mm wide, 30 degree hook, 1.2 mm lead-in) mirrored so the lead-in sits on the wrap-edge side and the pocket and exit ramp point toward the card centre; wrap tension runs toward the far wrap edge.
- Slot 3x longer (Brian, 2026-09-12): variant 5's lead-in and pocket are both 18 mm (were 6 mm); widths stay 1.2 mm lead-in and 1.0 mm pocket start. 25 lb line stops about 9 mm and 40 lb about 5.4 mm into the pocket; 9 mm of wall under the pocket. Lead-in depth is now a per-variant value (`lead_d`), so coupon variants 1 to 4 keep 6 mm.
- Version label (Brian, 2026-09-12): every printed version carries a label, same material, recessed into the face (not raised, so it cannot catch line). Text is `VERSION` in `leader_card.py`, DejaVu Sans Bold about 3.6 mm tall, 0.6 mm deep, in the top-face strip along the -Y long edge that the wraps never cover. Bump `VERSION` on every design change and add a row to the version log.
- Corner lugs (Brian, 2026-09-12): the four corners stand 1.5 mm proud of the wavy wrap edge so slack wraps cannot slide off its ends. Overall size stays 3 x 2 in.
- Visual options are shown on an HTML page, never ASCII art ([[feedback-html-visual-companion]]). Slot variants page: https://claude.ai/code/artifact/18ae8924-111d-4f77-ab7c-6c4948e84995

## LC2 decisions (Brian, 2026-09-12)

These supersede the hook slot, entry channel, funnel, exit ramp, wave, corner lug, 3 x 2 in size and label strip items above; everything else still holds. Page: https://claude.ai/code/artifact/8d43738c-84e6-45d4-b31c-25e05321d7f0

- Card 3 x 1.5 in (76.2 x 38.1 mm), 3 mm thick, white PETG.
- One slot shape everywhere: straight taper 3/8 in (9.5 mm) deep, 1.2 mm mouth closing to a 0.2 mm end (7.2 degree taper), gradual enough that 10 lb line wedges. Typical stops: 10 lb (0.28 mm) 7.3 mm deep, 25 lb 5.6 mm, 40 lb 4.0 mm.
- Side slots (Brian, third pass the same day): the two corner long-edge slots were dropped, then three of the same tapered slots were added on the +Y long edge, opposite the label, at 25, 50 and 75 percent of the length (x = -19.05, 0, +19.05 mm), for starting and finishing the leader.
- Wrap edges: a comb of the same slots, 9 per edge, 3 mm apart; teeth 1.8 mm at the tip, 3 mm at the root. Each wrap sits in its own comb slot.
- Removed: corner long-edge slots, hook, 18 mm entry channel, funnel, exit ramps ("lead-in", not helping), wave, raised corners (the comb stops the line sliding off).
- Kept: 0.6 mm top round and bottom chamfer on every edge including slot walls; slot mouths and tooth tips rounded 0.8 mm in plan; recessed version label (LC2) centred in the -Y long-edge strip outside the comb span.
- Files are versioned: `leader-card-LC2.*`; LC1 files renamed `leader-card-LC1.*`.

## Card geometry

- Footprint 3 x 2 in (76.2 x 50.8 mm), set by Brian. Under the 86 x 54 mm credit card ceiling.
- Thickness 3 mm.
- Line wraps end to end around the long axis, bending over the two 50.8 mm short edges. About 152 mm per wrap, about 6 wraps for 36 in.
- Plan-view corners: 2.9 mm radius, chosen so the straight part of each short edge is exactly 45.0 mm, a whole number of wave pitches.
- Short (wrap) edges: the straight 45 mm between the corners is a wave of alternating tangent arcs, 3 mm peak to peak, 0.6 mm deep, arc radius about 1.09 mm, giving 15 valleys per edge.
- Corner lugs: the wave is set back 1.5 mm from the card ends. Each corner is a 5.9 mm wide lug out to the full 3 in length, its flank landing on a wave peak, rounded 0.8 mm into the wave and at its tip. 13 valleys stay exposed per wrap edge. Verified in `prototype/leader_card.py` (LC1 card: 16 min, 8.7 g real slice).
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

Minimal per [[feedback-minimal-test-coupons]]: a 52 x 17.8 x 3 mm strip (widened so two wave valleys stay exposed between its corner lugs) carrying four hook-bend slot variants (varying lead-in width, pocket angle, and pocket taper) along one long edge. Its two short ends carry the same wave as the card (2 valleys each), so the wave is tested too. Nothing else. Quote print time from a real slice.

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

1. Test coupon: skipped. Brian picked variant 5 reversed from the variants page and chose to print the card directly (2026-09-12).
2. One card with the winning slot. Stop: Brian checks tackle box fit and wraps a real 36 in rig.
3. Retrospective in `knowledge/learnings/leader-cards.md`.

## Files

All in `projects/Leader-cards/`: this brief, the CAD source, and STL and 3MF for the coupon and the card. Built with the `/3d-model` skill.

## Version log

| Label | Date | Design |
|---|---|---|
| LC1 | 2026-09-12 | 3 x 2 in PETG; variant 5 reversed with the slot 3x longer (18 mm lead-in, 18 mm pocket, 30 degree hook); 15 degree exit ramps both faces; 1.5 mm corner lugs; 3 mm wave, 13 exposed valleys. Not printed; files `leader-card-LC1.*` |
| LC2 | 2026-09-12 | 3 x 1.5 in PETG; comb of 9 straight tapered 3/8 in slots (1.2 mm to closed) per wrap edge at 3 mm; 3 same slots on the +Y long edge at 25/50/75 percent; no hook, ramps, wave or corner lugs; files `leader-card-LC2.*` |

## Outcomes

### Card (2026-09-12)

- Source: `leader_card.py` (`WINNER = 5`), run `PART=card .venv/bin/python projects/Leader-cards/leader_card.py`. All checks pass: 76.2 x 50.8 x 3 mm, one solid, 13 exposed valleys per wrap edge, four corner lugs, both slots open with rounded face edges, exit ramps on both faces, pinch band 1.23 mm. Slot 3x longer (18 mm lead-in, 18 mm pocket) since the first build. Recessed label `LC1` (9.2 x 3.6 mm, 0.6 mm deep) checked: letters empty, floor intact, clear of the slot mouth. Legibility of recessed text this small is untested on the X2D ([[lettering-x2d]] covers raised text only); judge it on this print.
- Files: `leader-card.stl`, `leader-card.3mf`, `leader-card-print.3mf` (open this one in Bambu Studio). Renders `images/final-card.png`, `images/final-card-corner.png`.
- Real slice: 16 min, 8.7 g. Bambu Lab X2D 0.4 nozzle, 0.20mm Standard, Bambu PETG Basic, Textured PEI Plate. Print flat as loaded, chamfered edge on the bed, no supports.
- Printability: thinnest wall 9.0 mm under the pocket; lugs 5.9 mm wide; bed-side ramps are shallow bridges under 3 mm; only sloped underside is the 45 degree chamfer. The pocket's last 0.3 mm of taper is under one 0.4 mm line width and may print closed, which is fine because both lines stop where the gap is 0.5 mm or wider.
- Printer at build time (`scripts/x2d-status.py`): white PETG Basic in AMS slot 3 at 68 percent. The first read that day reported the main nozzle as 0.4 mm HH01 (high flow); a later read reported 0.4 mm HS01 (standard flow) in both positions, and Brian confirmed he has no high-flow 0.4. The standard 0.4 profile the file was sliced with is correct ([[x2d-printer-control]]).
- Variants page: https://claude.ai/code/artifact/18ae8924-111d-4f77-ab7c-6c4948e84995. The coupon files were not exported to the project; `COUPON_SLOTS` still lists variants 1 to 4 if a coupon is ever wanted.

### LC2 card (2026-09-12)

- Source: `leader_card.py` (`VERSION = "LC2"`), run `.venv/bin/python projects/Leader-cards/leader_card.py`. All checks pass: 76.2 x 38.1 x 3 mm, one solid, 21 slots (9 comb per wrap edge, 3 side slots), every slot open at the mouth and at the 10 lb stop, solid past 3/8 in, face edges rounded; every comb tooth present; label LC2 recessed, floor intact, clear of the combs.
- Files: `leader-card-LC2.stl`, `leader-card-LC2.3mf`, `leader-card-LC2-print.3mf` (open this one). Renders `images/final-card-LC2.png`. Page: https://claude.ai/code/artifact/8d43738c-84e6-45d4-b31c-25e05321d7f0
- Real slice: 15 min, 6.9 g. Same settings as LC1 (0.4 standard-flow nozzle, 0.20mm Standard, PETG Basic, Textured PEI).
- Printability: comb teeth 1.8 mm at the tip, 3 mm at the root, 9.5 mm long; the last 0.2 to 0.4 mm of each taper is under one line width and may print closed, which is below where 10 lb line stops.

