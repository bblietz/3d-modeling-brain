---
name: rex-roots-1x12-handoff
type: handoff
project: rex-roots-1x12
created: 2026-09-11
tags: [handoff, speaker-cab, maximocabs]
---

# Handoff: rex-roots-1x12 (Speaker Cab Plan 3, Task 8 dry run, the port-loop order)

## State

- Order: Pat Player (the site's test persona), 1x12 tolex, closed-ported with a front slot, Eminence Cannabis Rex at 8 ohm, on the '65 Deluxe Reverb reissue's extension jack.
- Brief `status: proposed`. Stop one (voicing), the port-loop trade-off stop, and stop two (package review) were answered from the task's answer sheet, not by Brian.
- Package on disk in `projects/Speaker-cab-system/fixtures/rex-roots-1x12/`: `brief.md`, `tone.json`, `voicing.json`, `voicing.md`, `cab.py` (one-line docstring naming the order; `grill_cloth` the one AESTHETICS edit), `cab.json`, `cab.step`, `cutlist.md`, `cutlist.csv`, `checks.md` (32 rows, 0 read `operator`), `proposal.md` (verified, `Price:` empty), `images/` (five renders and the `tolex-fender-black.jpg` swatch; no rear view, the port is a front slot; no swatch on file for the Salt-and-pepper cloth).
- Not committed: this session ran no `git add`, `git commit`, or `git push`; the controller commits the fixture. Phase 8 skipped (no cabinet built).
- Dry-run findings on the skill text: `.superpowers/sdd/task-8-report.md`.

## Commands run (from the vault root, in order; `<order>` is `projects/Speaker-cab-system/fixtures/rex-roots-1x12`)

1. `scripts/cabvoice.py evaluate --speaker eminence-cannabis-rex --impedance 8 --enclosure closed-ported --tone <order>/tone.json --line tolex --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40 --name rex-roots-1x12 --out <order>/`: exit 0; punchy, Fb 67.8 Hz, F3 98.8 Hz, peak 1.9 dB; wiring matches the tap; no blockers; the bridge word for tight is flat, so propose.
2. `scripts/cabvoice.py propose --speaker eminence-cannabis-rex --impedance 8 --enclosure closed-ported --tone <order>/tone.json --jack mono --line tolex --name rex-roots-1x12 --out <order>/`: exit 0; 33.4 L net, external 482 x 434 x 267 mm, rear round 153.2 x 90 mm (snapped from 113.2), Fb 86.4 Hz, F3 102.5 Hz, peak 2.97 dB, punchy, no blockers. Stop one approved on this sheet.
3. `<order>/cab.py`: exit 2; `port fit` blocker form 1 (no 153.2 mm port fits; the longest tube at the 24 mm minimum is 101.5 mm) plus the consequential `net volume` blocker.
4. Command 2 with `--port-tube 101.5`: exit 0; external 475 x 428 x 263 mm, rear 101.5 x 24 mm, Fb 81.0 Hz against the 86.4 Hz target, punchy; warnings `port too short (10.6 mm) ... clamped to 24 mm` and `port clamped at the 24 mm minimum with the pinned 101.5 mm tube`.
5. `<order>/cab.py`: exit 0; `port fit` pass, `port mouth` warn (90 mm from the magnet). The sheet's port warning makes this the trade-off stop; the sheet chose the front slot.
6. Command 2 with `--port-slot 438.9 40 --pinned-width 474.9` (the widths from the pinned sheet's `box.chamber_internal_width_mm` and `box.external_mm[0]`): exit 0; slot 439 x 40 x 83 mm, Fb 86.4 Hz, external 475 x 463 x 252 mm, punchy, one advisory (width to height 1.03:1).
7. `<order>/cab.py`: exit 0; 15 checks, `port fit` pass (slot built), one `port mouth` warn (the floor-level back cleat, 119 mm, 46 percent).
8. `EXPORT=1 <order>/cab.py`: exit 0; 19 checks, the same warn; `cab.step`, five renders, `cutlist.md`, `cutlist.csv`, `cab.json` written.
9. `scripts/cabreport.py <order>/ --customer "Pat Player"`: exit 0; `checks.md` 32 rows, 7 `operator` (then judged from the brief), `proposal.md` written with empty slots, warning `no swatch on file for the grill cloth`. The swatch `fender-black.jpg` copied into `images/`.
10. `scripts/cabreport.py <order>/ --customer "Pat Player" --verify`: exit 0, verified.

## Decisions already locked

- 2026-09-11: voicing approved (eminence-cannabis-rex at 8 ohm, closed-ported, propose: 33.4 L net; the stop-one sheet carried a rear 153.2 mm tube in a 482 x 434 x 267 mm box, Fb 86.4 Hz, punchy; the port loop moved the port to a front slot in a 475 x 463 x 252 mm box at the same volume and tuning)
- 2026-09-11: port loop, form 1 automatic re-run with `--port-tube 101.5`, no stop
- 2026-09-11: port loop trade-off: the front slot chosen (`--port-slot 438.9 40 --pinned-width 474.9`) over the clamped tuning, a raised Fb with the larger tube, and a larger box; the final sheet's `port.shape` is `slot`
- 2026-09-11: no engine impedance mismatch (8 ohm on taps [8]); the combined 4 ohm load on the extension jack (8 || 8) recorded in the Rig block and the proposal
- 2026-09-11: no power warning; no `--accept-low-headroom`
- 2026-09-11: engine advisory accepted: width to height 1.03:1
- 2026-09-11: `port mouth` warn accepted: the floor-level back cleat 119 mm behind the slot mouth, 46 percent, under the 149.5 mm effective diameter; the 25 mm standoff holds
- 2026-09-11: operator rows judged from the brief: no weight or size limit, no vehicle (a one-hand carry), wood movement n/a on tolex, joinery fit and stock thickness on the construction note's defaults, stock yield one sheet of each thickness
- 2026-09-11: stop two: package approved as presented, no edits; `Price:` line left empty

## Next

- Nothing for the order itself. If the fixture is regenerated, every `cabreport.py` run without `--verify` rewrites `checks.md`, so the seven operator rows must be judged again, and `proposal.md` must be deleted first to be rewritten.
