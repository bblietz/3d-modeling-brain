---
title: Leader cards
type: project-brief
status: LC3 printed 2026-09-13, fits the tackle box. Brian field-testing (real rig, real line); retrospective pending his report
created: 2026-09-12
tags: [fishing, tackle, petg, leader, x2d]
---

# Leader cards

Printed replacement for the cardboard cards Brian wraps long fishing leaders on (salmon, halibut, and rockfish rigs, up to 36 in of leader) so they fit in the tackle box. Cardboard works when new but the slits tear, the hook holes enlarge, and the card goes soft once wet. Reference: `images/cardboard-card.jpg`.

## What LC3 is (current, as printed)

- **Card:** 3 x 1.5 in (76.2 x 38.1 mm), 3 mm thick, white PETG, 2.9 mm corner radius. Holds only the leader line; hooks, swivels, and lure bodies hang free off the ends and may be longer than the card.
- **Line range:** 10 to 40 lb mono or fluoro (about 0.28 to 0.70 mm).
- **One slot shape, used everywhere (21 slots total):** a straight taper cut in from an edge, 3/8 in (9.5 mm) deep, from a 1.2 mm mouth narrowing to a 0.2 mm gap at the tip (7.2 degree included angle). Each line size wedges at its own depth: 10 lb about 7.3 mm in, 25 lb 5.6 mm, 40 lb 4.0 mm. No hook, no entry funnel, no exit ramp -- those were all tried and dropped (see Decision history).
- **Comb, both wrap edges (the two ends, x = &plusmn;38.1 mm):** 9 of the taper slots per edge, 3 mm apart (y = -12 to +12 mm), one wrap of leader per slot.
- **Side slots, one long edge (y = +19.05 mm):** 3 more of the same taper, at 25/50/75 percent of the length (x = -19.05, 0, +19.05 mm), opposite the label. The leader starts in one and finishes in another.
- **Edges:** every slot's face edges get the same 0.6 mm top round and 0.6 mm bottom chamfer as the card's outer edge; slot mouths and comb-tooth tips are rounded 0.8 mm in plan. Nothing sharp touches the line.
- **Version label:** recessed 0.6 mm, DejaVu Sans Bold, centred on the -Y long edge (opposite the side slots), currently reads **"LC3"** -- it tracks `VERSION` in `leader_card.py`, so it always names the design it's printed on.
- **Wordmark:** "leader" over "board", lower case, same font, tight leading, recessed 0.6 mm, centred between the version label and the side-slot band. Sized to 45.7 mm wide (80 percent of the full 2.25 in gap between the two combs), ending up about 21 mm tall for both lines.
- **Material reasoning:** white PETG. PLA is out (softens hot in a car/boat); nylon is out (absorbs water); ASA is out (attacked by sunscreen) -- see [[marine-materials]]. Rigs go back on the cards wet and stay closed in the tackle box between trips, so nothing may absorb water or trap it; every slot is a through-cut, so it drains.
- **Printing:** 0.4 mm standard-flow nozzle, 0.20mm Standard, Bambu PETG Basic, Textured PEI plate, flat on the bed, chamfered edge down, no supports ([[printer-x2d]], [[x2d-printer-control]]).

Source: `projects/Leader-cards/leader_card.py`, run with `.venv/bin/python projects/Leader-cards/leader_card.py`. Print file: `leader-card-LC3-print.3mf`, real slice 18 min, 7.3 g.

## Decision history

Design went through three named revisions the same week, each printed except LC1. Full detail on what each replaced is in the Version log and Outcomes below; the highlights:

- **LC1** (not printed): a hook-bend slot with a long entry channel, funnel, and 15 degree exit ramps on both faces, plus a wavy wrap edge and raised corner lugs to keep slack wraps from sliding off. Built and checked, but replaced before printing.
- **LC2**: dropped the whole LC1 approach for one plain straight-taper slot shape, repeated as a comb on both wrap edges plus 3 side slots on one long edge. Simpler, and the taper alone (no hook) turned out to hold line fine down to 10 lb. Card also shrank from 3 x 2 in to 3 x 1.5 in.
- **LC3**: added the "leader" / "board" wordmark. Picked from four to-scale options checked against the real slot geometry (page: https://claude.ai/code/artifact/79b741a8-77dd-4a83-bb4c-5eadf0df6dee), then resized down 20 percent and the text changed twice (Leader Card -> Leader Board -> lower case). The small version label briefly had its text frozen at "LC2" for field-test continuity, then Brian asked it to track the real version again -- it now always matches `VERSION`.

Standing project rules, not tied to one version:
- One universal card for every rig; approach is a flat slotted card (rejected: a railed spool card, thicker and traps water; TPU slot inserts, two materials and TPU feeds poorly in the AMS -- held in reserve only if a PETG slot ever fails to hold line).
- Visual design questions get an HTML page built from the real CAD geometry, never ASCII art ([[feedback-html-visual-companion]]).
- Before printing, confirm the physically installed nozzle and Bambu Studio's machine profile both read 0.4 mm, and which flow type is actually set on the printer, not assumed ([[x2d-printer-control]]).

## Version log

| Label | Date | Design |
|---|---|---|
| LC1 | 2026-09-12 | 3 x 2 in PETG; variant 5 reversed with the slot 3x longer (18 mm lead-in, 18 mm pocket, 30 degree hook); 15 degree exit ramps both faces; 1.5 mm corner lugs; 3 mm wave, 13 exposed valleys. Not printed; files `leader-card-LC1.*` |
| LC2 | 2026-09-12 | 3 x 1.5 in PETG; comb of 9 straight tapered 3/8 in slots (1.2 mm to closed) per wrap edge at 3 mm; 3 same slots on the +Y long edge at 25/50/75 percent; no hook, ramps, wave or corner lugs; files `leader-card-LC2.*` |
| LC3 | 2026-09-12 | LC2 geometry unchanged, plus a recessed "leader" / "board" wordmark (DejaVu Sans Bold, tight leading, lower case, 80% of the full 2.25 in interior); files `leader-card-LC3.*` |

## Outcomes

### LC1 (2026-09-12, not printed)

- Source: `leader_card.py` (`WINNER = 5`) at the time. All checks passed: 76.2 x 50.8 x 3 mm, one solid, 13 exposed valleys per wrap edge, four corner lugs, both slots open with rounded face edges, exit ramps on both faces, pinch band 1.23 mm.
- Real slice: 16 min, 8.7 g. Superseded by LC2 before printing; kept in `prototype/leader_card.py` and git history.
- Variants page: https://claude.ai/code/artifact/18ae8924-111d-4f77-ab7c-6c4948e84995

### LC2 (2026-09-12, printed)

- Source: `leader_card.py` (`VERSION = "LC2"`). All checks passed: 76.2 x 38.1 x 3 mm, one solid, 21 slots (9 comb per wrap edge, 3 side slots), every slot open at the mouth and at the 10 lb stop, solid past 3/8 in, face edges rounded; every comb tooth present; label recessed, floor intact, clear of the combs.
- Files: `leader-card-LC2.stl`, `leader-card-LC2.3mf`, `leader-card-LC2-print.3mf`. Renders `images/final-card-LC2.png`. Page: https://claude.ai/code/artifact/8d43738c-84e6-45d4-b31c-25e05321d7f0
- Real slice: 15 min, 6.9 g, 0.4 standard-flow nozzle, 0.20mm Standard, PETG Basic, Textured PEI.
- Printer at build time (`scripts/x2d-status.py`): white PETG Basic in AMS slot 3 at 68 percent. The nozzle briefly read high-flow before Brian corrected the printer's own nozzle-type setting to match his actual hardware (no high-flow 0.4 owned); both readings were accurate for their moment, not a sensor fault ([[x2d-printer-control]]).

### LC3 (2026-09-13, printed)

- Source: `leader_card.py` (`VERSION = "LC3"`, also the on-card label text). All checks passed, including the LC2 checks plus: wordmark text non-empty, fully recessed, floor intact beneath it, and zero real overlap with any slot cut (checked with an actual 2D boolean against the slot geometry, not a bounding-box guess).
- Files: `leader-card-LC3.stl`, `leader-card-LC3.3mf`, `leader-card-LC3-print.3mf`. Renders `images/final-card-LC3.png` (four views) and `images/final-card-LC3-wordmark.png` (raking-light close-up -- the default top-down render flattens 0.6 mm recessed text almost to invisibility).
- Real slice: 18 min, 7.3 g. Same settings as LC2.
- **Printed and fits the tackle box (Brian, 2026-09-13).** Field test in progress: real rig, real line, wrap and unwrap by feel, wordmark and label legibility. Retrospective in `knowledge/learnings/leader-cards.md` follows his report.

## Open

- Field-test report from Brian: line grip at 10/25/40 lb, wrap and unwrap by feel, wordmark and label legibility at 0.6 mm deep.
- Retrospective (`knowledge/learnings/leader-cards.md`) once the field test is in.
- Batch size beyond the first LC3 card, once the design is confirmed.
