---
name: sample-roots-1x12-handoff
type: handoff
project: sample-roots-1x12
created: 2026-09-11
tags: [handoff, speaker-cab, maximocabs]
---

# Handoff: sample-roots-1x12 (Speaker Cab Plan 3, Task 7 dry run)

## State

- Order: Pat Player (the site's test persona), 1x12 tolex, closed-ported, Celestion G12H Anniversary at 16 ohm, on the '65 Deluxe Reverb reissue's extension jack.
- Brief `status: proposed`. Stop one (voicing) and stop two (package review) were answered from the dry run's answer sheet, not by Brian.
- Regenerated on 2026-09-11 from the amended skill after the `--accept-impedance-mismatch` fix wave: `tone.json` taps `[8]` (the winding, never edited), the flag on the evaluate and propose commands, the same box as the first run.
- Package on disk in `projects/Speaker-cab-system/fixtures/sample-roots-1x12/`: `brief.md`, `tone.json`, `voicing.json`, `voicing.md`, `cab.py` (one-line docstring naming the order; `grill_cloth` the one AESTHETICS edit), `cab.json`, `cab.step`, `cutlist.md`, `cutlist.csv`, `checks.md` (38 rows, 0 read `operator`, the `wiring` row a warn), `proposal.md` (verified, `Price:` empty), `images/` (five renders, the rear view `cab-rear.png`, and the `fender-black.jpg` swatch; no swatch on file for the Salt-and-pepper cloth).
- Not committed: this session ran no `git add`, `git commit`, or `git push`; the controller commits the fixture. Phase 8 skipped (no cabinet built).
- Dry-run findings on the skill text: `.superpowers/sdd/task-7-report.md` (first run) and `.superpowers/sdd/task-7-rerun-report.md` (this regeneration).

## Commands run (from the vault root, in order)

1. `scripts/cabvoice.py evaluate --speaker celestion-g12h-30-anniversary --impedance 16 --enclosure closed-ported --tone <order>/tone.json --line tolex --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40 --name sample-roots-1x12 --out <order>/ --accept-impedance-mismatch` with `tone.json` taps `[8]`: exit 0; punchy, Fb 67.4 Hz, F3 69.2 Hz, peak 1.3 dB; `wiring.mismatch_accepted` true, warnings `no wiring option matches amp taps [8]` and `impedance mismatch accepted: 16 ohm cabinet on amp taps [8]`, no blockers; the bridge word for tight is flat, so propose.
2. `scripts/cabvoice.py propose --speaker celestion-g12h-30-anniversary --impedance 16 --enclosure closed-ported --tone <order>/tone.json --jack mono --line tolex --name sample-roots-1x12 --out <order>/ --accept-impedance-mismatch`: exit 0; 30.0 L net, internal 424 x 378 x 206 mm, external 460 x 414 x 256 mm, rear round 101.5 x 51 mm, Fb 76.5 Hz, F3 79.1 Hz, peak 2.1 dB, punchy, no blockers, seven warnings (the five of the first run plus the two wiring warnings).
3. `<order>/cab.py`: exit 0, 15 checks, one warn (`port mouth`: 50 mm from the magnet, 23 percent of the mouth).
4. `TMP_STL=/tmp/cab.stl EXPORT=1 <order>/cab.py`: exit 0, 19 checks, the same warn; `cab.step`, five renders, `cutlist.md`, `cutlist.csv`, `cab.json` written, plus the STL.
5. `scripts/render_stl.py /tmp/cab.stl <order>/images/cab-rear.png 0,90`: exit 0, the rear view (back panel, port hole, jack plate).
6. `rm <order>/proposal.md`, then `scripts/cabreport.py <order>/ --customer "Pat Player"`: exit 0; `checks.md` 38 rows, 7 `operator` (then judged from the brief), `proposal.md` written with empty slots, warning `no swatch on file for the grill cloth`.
7. `scripts/cabreport.py <order>/ --customer "Pat Player" --verify`: exit 0, verified.

## Decisions already locked

- 2026-09-11: voicing approved (celestion-g12h-30-anniversary at 16 ohm, closed-ported, propose: 30.0 L net box 460 x 414 x 256 mm external, one rear 101.5 mm tube 51 mm long, Fb 76.5 Hz predicted, character punchy; presented past the bridge word as the closest this driver reaches inside the 30 L floor, beside the closed box and the next-ranked speaker)
- 2026-09-11: impedance mismatch accepted with `--accept-impedance-mismatch` on the evaluate and propose commands: a 16 ohm cabinet on the Deluxe Reverb's 8 ohm extension jack (8 || 16 = 5.3 ohm, a 2:1 mismatch on a tube amp, within tolerance); the sheet records `wiring.mismatch_accepted` true; the taps in `tone.json` stay [8]
- 2026-09-11: power warning accepted: 30 W handling under the 33 W target (1.5 x 22 W), above the amp's 22 W rating; no `--accept-low-headroom` (moderate breakup)
- 2026-09-11: engine advisories accepted: clamped volume (19.7 L for tight, started from the 30 L floor), displacement assumed 1.5 L, width to depth 2.06:1, port snapped to the 101.5 mm tube
- 2026-09-11: `port mouth` warn accepted: mouth 50 mm behind the magnet, 23 percent of the mouth, under one diameter; the 25 mm standoff holds
- 2026-09-11: operator rows judged from the brief: no weight or size limit, no vehicle (a one-hand carry), wood movement n/a on tolex, joinery fit and stock thickness on the construction note's defaults, stock yield one sheet of each thickness
- 2026-09-11: stop two: package approved as presented, no edits; `Price:` line left empty

## Next

- Nothing for the order itself. If the fixture is regenerated, every `cabreport.py` run without `--verify` rewrites `checks.md`, so the seven operator rows must be judged again, and `proposal.md` must be deleted first to be rewritten.
