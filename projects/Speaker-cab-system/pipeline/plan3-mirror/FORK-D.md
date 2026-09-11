# Fork D report: knowledge-note touches, canonical genre keys, site copy note (Plan 3 Task 3 and the note updates)

Everything below lives in `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/`; nothing landed was touched and nothing was committed. Tests: `test_cabvoice.py` 431 to 432; full mirror `./run_tests.sh` 509 passed in 72 s (432 + 3 cutlist + 50 layout + 24 CAD).

## Files changed or created (mirror only)

- `knowledge/speaker-cab-voicing.md`: ten exact replacements, calibration table block untouched (Fork A's header line still at line 133).
- `knowledge/speaker-cab-construction.md`: five exact replacements.
- `knowledge/speakers/*.md` (20 notes): Best with section rewritten by the script.
- `projects/Speaker-cab-system/pipeline/catalog_genres.py`: new, idempotent, `--apply` writes.
- `projects/Speaker-cab-system/site-copy-notes.md`: new.
- `scripts/test_cabvoice.py`: one existing test modified (see Deviations), one block appended at the end.

## Voicing note, section by section

- Frontmatter: `updated: 2026-09-11` added (the note had no `updated` field; added for parity with the construction note).
- Enclosure type rules: two bullets after the choice rule, "Precedence when the rules disagree" and "Evaluate first", then the bridge table (both quoted below).
- Amp families: "every note's Best with line" is now "every note's Amp families line".
- Genre and approach: a Key column (`roots-country`, `blues`, `classic-rock`, `indie-alternative`, `jazz`, `metal-high-gain`, `worship-pop`, `funk-rnb`, backticked) and, after "Approach overrides genre", the paragraph "The Key column holds the canonical genre keys: every catalog note's Genres line lists them, the skill's ranking matches the intake's genre to them, and a genre outside the table earns no genre point (map it to the nearest row by ear and say so in the brief)."
- Rig adjustments, low-end shifters: "baritone, 7-string, drop tunings, and bass VI set low_end big and take closed-ported at the lowest tuning in range (`--fb 45`, raised in 5 Hz steps only while the sheet reads boomy or the port does not fit; see Enclosure type rules), and a 2x12 over a 1x12 when weight allows."
- Power and impedance, first bullet: `min_power_w` is 1.5 x the highest rated amp among the customer's amps, computed by the skill into `tone.json`; the engine reads the amp's rating back as `min_power_w` / 1.5 (that is what `propose` does at `amp_power = tone["min_power_w"] / POWER_SAFETY_FACTOR`) and stops hard below it; the early-breakup acceptance names `--accept-low-headroom`.
- Box alignment, Port bullet: the stale Plan 1 numbers (75 mm start, 150 mm maximum, 20 mm minimum) replaced by the landed engine (77.3 mm start, 10 percent area growth, snap to `PORT_TUBE_ID_MM` 52.0/77.3/101.5/153.2, 153.2 maximum, 24 mm minimum, the corrected clamp remedy "a larger port, a lower Fb, or a smaller box lengthens it"), plus `--port-tube` (pinned, `port.pinned`) and `--fb` (`port.fb_override_hz`) and the `--port-count` flag.
- Speaker ranking procedure, item 2: genre point on the customer's key appearing on the note's Genres line; precedence sentences (amp-family table over the note's own Amp families line; genre points only on canonical keys). Point values unchanged.
- Model limits: the 16 ohm Eminence caveat was already there; its parenthetical now reads "(deferred past Plan 3, see [[2026-09-11-plan-3-skill-design]] section 13)".

## Construction note, section by section

- Frontmatter `updated: 2026-09-11`; the intro's revision paragraph gains the 2026-09-11 sentence (24 mm minimum, port mouth rule, default front slot, remedy order).
- Backs and ports, rear round port: "length from the voicing sheet measured through the back panel and never under 24 mm (the 12 mm back panel plus the 12 mm flange ring, the engine's `MIN_PORT_LENGTH_MM`)"; the no-fit sentence is now: "When no spot fits, the layout's `port fit` blocker says so (`chamber 0 port 0: no round port of 153.2 mm fits with 25 mm clearance; raise Fb, use a smaller tube or a larger box, or a front slot`) and the skill's port loop re-runs the voicing once with the next tube down the table pinned (`--port-tube`: 153.2, then 101.5, 77.3, 52.0); when that run warns (a clamped length, an air speed over the limit) or blocks again, the remedies go to Brian in this order: the front slot below, accepting the pinned tube's clamped tuning as the sheet reports it, raising Fb with the larger tube, a larger box."
- Backs and ports, front slot, appended (the default slot statement): "Default slot for the port loop (starting values): height 40 mm; width the chamber's full internal width, read from the last sheet's `box.chamber_internal_width_mm`, for a 1x12 and for each stereo chamber (no cheeks), and for a mono 2x12 two slots of (chamber width minus 18) / 2 each, split by the center cheek; so `--port-slot <width> 40`. The engine then adds the slot's 58 mm to the height floor (40 plus the 18 mm shelf) and may rescale the width to hold the volume: a slot wider than the new chamber blocks (`slots ... do not fit the chamber`) and the skill re-runs once with the new width; a narrower slot only gains thin cheeks. A 40 mm slot across a 352 mm chamber is 141 cm2, above the 101.5 mm tube's 81 cm2, so the air speed stays low." Derivation: `cablayout.slot_ports` builds a full-chamber-width slot with cheeks for anything narrower and an 18 mm center cheek between two slots; `cabmodel`'s `2x12-mono-slot` demo uses (w_int minus 18) / 2 at 40 mm and Fork A's Cannabis Rex test uses 352 x 40; `min_internal_height_mm` adds slot height plus 18. The 40 mm height is a note-level starting value: the engine has no slot height default.
- Backs and ports, new "Port mouth" bullet: the one-diameter rule, the check's warn form (`chamber 0 port 0: mouth 84 mm from the speaker 0 magnet (18 percent of the mouth), under one diameter (101.5 mm)`, percentage informational), the three places it warns today (the site box's rear tube; a 1x12 slot in a box wide enough for a bottom stiffener, at 0 mm; a slot in a shallow box, on the back cleat), Brian's per-order acceptance into Decisions locked, the 25 mm standoff kept as the hard rule.

## Evaluate-first paragraph (verbatim, voicing note)

"Evaluate first: a standard-size order (the site's 20 x 18 x 11 in box, one driver, no size limit, no head to match) is evaluated before anything is proposed, with the site port on a ported box: `cabvoice.py evaluate --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40` (the calibration port, the 101.5 mm tube at 40 mm; box and port fix Fb, the speaker sets the character) plus the order's speaker, impedance, enclosure, tone, and line. The site box is accepted when the sheet's character is the bridge word for the target's `low_end` in the table below; otherwise, or when a size limit, a pinned width, or a second driver applies, the skill runs `propose`. Open and semi-open boxes carry no character word (the estimate reports the cancellation frequency, about 370 Hz for any box near the site depth), so an open-back site box is accepted whenever the rules above chose open or semi-open; only a size limit or a second driver makes it propose."

Bridge table (verbatim):

| Predicted character | Enclosure | Serves `low_end` |
|---|---|---|
| lean (Qtc below 0.6) | closed | none: propose a smaller box or a ported one |
| tight (Qtc 0.6 to 0.8) | closed | tight |
| balanced (Qtc 0.8 to 1.0) | closed | balanced |
| big (Qtc 1.0 to 1.2) | closed | big |
| peaky (Qtc above 1.2) | closed | none: open or semi-open, or a lower-Qts driver |
| flat (peak below 1 dB) | closed-ported | tight |
| punchy (peak 1 to 3 dB) | closed-ported | balanced |
| boomy (peak above 3 dB) | closed-ported | big only; for any other target the engine grows the box or lowers Fb |
| open, cancellation frequency reported | open, semi-open | balanced with open panels, big with semi-open panels (the panel choice, not the box, sets the low end) |

## Fb range statement (verbatim, Precedence bullet)

"The override may take any value in the engine's own tuning range, 45 to 90 Hz (`FB_MIN_HZ` to `FB_MAX_HZ`, the range every proposed Fb is clamped to); the engine does not check the flag, so the skill keeps it in that range. The low-end-shifter rule starts at 45 Hz, the bottom of the range, and raises it in 5 Hz steps (the engine's own boomy step) while the sheet reads boomy or the port does not fit. Starting values; listening notes decide." (From `ported_targets`: Fb = clamp(Fs x 0.9 / 0.8 / 0.7, 45, 90) and the boomy loop's 5 Hz step.)

## Genre mapping (old string on the Best with line to key)

| Old string | Key |
|---|---|
| Roots, country, alt-country | roots-country |
| Blues | blues |
| Classic rock | classic-rock |
| Indie and alternative | indie-alternative |
| Jazz | jazz |
| Metal and modern high gain | metal-high-gain |
| Worship and pop | worship-pop |
| Funk and R&B | funk-rnb |

Every string in the twenty notes matched a row exactly, except celestion-blue's "Worship and pop at low volume", which maps to `worship-pop` with the qualifier kept as a sentence. Judgment call: the section is three bullets, not two. The Amp families line is unchanged text; the Genres line holds only keys, no trailing period; a third bullet keeps the notes' qualifier sentences (celestion-blue "worship-pop at low volume.", g12m-25 and green-beret "two per cabinet", swamp-thang "Suits baritone and drop tunings.", the three high-Qts open-back sentences, p12n's open-back history) followed by "Families and genres per [[speaker-cab-voicing]]." so no information and no wikilink was dropped. Example (celestion-blue):

```
- Amp families: Vox, Boutique clean up to 15 W, or two Blues under a 30 W amp (the accepted early-breakup case).
- Genres: indie-alternative, blues, worship-pop
- worship-pop at low volume. Families and genres per [[speaker-cab-voicing]].
```

Script runs (from `.vault`): dry run ends `20 note(s) would change`; `--apply` ends `20 note(s) written`; a second `--apply` prints every note `unchanged` and ends `0 note(s) written`. Per-note tail: `wgs-green-beret: patched, genres classic-rock, blues`, `wgs-veteran-30: patched, genres classic-rock, metal-high-gain, worship-pop`.

## Tests

- Modified `test_catalog_best_with_uses_table_labels` (deviation from "change nothing else": the test encoded the single-line form). Two assertions changed: the genre-label-on-the-Amp-families-line assertion is gone, and the wikilink is asserted in the section instead of on that line. The table-label assertions against the voicing note stay, so the genre table carries both the label and the key.
- Appended under `# ---- Plan 3 Task 3: canonical genre keys ----`: `GENRE_KEYS` (the same tuple as the script; the engine gets no constant) and `test_catalog_genres_lines_use_canonical_keys` (every key appears as a backticked table cell in the voicing note; every note has exactly one Amp families line and one Genres line; every Genres token is a key; no duplicates).
- `test_cabvoice.py` 431 to 432 passed; `-k catalog` 6 passed; `./run_tests.sh` 509 passed (the layout suite reads 50, not the 47 in Fork B's report; Fork B must have added tests after writing it).

## Site copy note

`projects/Speaker-cab-system/site-copy-notes.md` (frontmatter name, description, type note, created, tags) with three sections quoting the site files by path and line as of 2026-09-11: the hardwood joinery row (`hardwood-1x12.md` line 33, against `tolex-1x12.md` line 33 and `index.astro` line 28, suggested row text); the closed-back wording (both pages' line 30 `configuration: "1x12 closed-back, ported"` and the tolex description's "Closed-back for focused low end." at line 39, as a default with a suggested form); the loaded weights (`~32 lb loaded`, `~38 lb loaded (varies by species)` at line 37 of each) against the site-default fixture's 17.0 kg, 37.5 lb (11.3 kg parts, 4.7 kg speaker, 1 kg hardware), listed as a thing to weigh, not a fact.

## Open questions for the plan writer

1. Port loop step 1 does not match the layout: the `port fit` blocker names no tube (Fork A and Fork B agree). The construction note now says the loop pins the next tube down the table; design section 5 step 1 and Fork E's SKILL.md Phase 4 step 1 still say "the tube the blocker names". Reconcile in the plan (recommended: the table step-down, deterministic and needing no layout change), or ask Fork B to extend the blocker.
2. The bridge is strict on ported boxes (punchy serves balanced only). The sample intake's target is tight; the G12H on the site box reads punchy at Fb 67 (the calibration port), so the golden dry run will propose rather than keep the site box. If Brian wants the site box kept for that order, the bridge needs a tolerance he chooses.
3. Both dry-run fixtures will carry a `port mouth` warn (Fork B's deviation 1 and 3); the construction note states where it fires, and the answer sheet should expect it.
4. The old label test keeps the genre table's labels load-bearing next to the keys; if the labels ever change, both the test's `GENRES` tuple and the script's `LABEL_TO_KEY` move.
5. `--fb` is uncapped in the engine; the note binds the skill to 45 to 90 Hz. If the plan wants the cap in code, that is an engine touch Fork A did not make.

## Addendum (coordinator's message, applied)

Construction note updated after Fork B's addendum: the rear round port bullet quotes the `port fit` blocker in its final forms (`the longest table tube that fits at the 24 mm minimum is 101.5 mm`, `no table tube fits; use a front slot or a larger box`, `longest tube that fits at this diameter is 155 mm`) and the loop now pins the named tube, which matches design section 5 step 1 and SKILL.md again (open question 1 above is closed); the front slot bullet quotes the shelf forms (`the deepest shelf that fits is 207 mm`, `no shelf fits`); the port mouth bullet records the three expected warns (site-box rear tube, 1x12 slot with a floor stiffener at 0 mm and about 8 percent coverage, slot in a shallow box on the back cleat) with the per-order remedies (accept or a smaller tube; move the stiffener back; a deeper box) and the coverage figure as information only. No test reads the note; the suites are unchanged at 509.
