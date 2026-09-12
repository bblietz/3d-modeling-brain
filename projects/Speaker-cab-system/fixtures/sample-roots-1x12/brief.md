---
name: sample-roots-1x12
description: MaximoCabs order brief for Pat Player, a 1x12 tolex cabinet, closed-ported, Celestion G12H Anniversary 16 ohm
type: order
status: proposed
created: 2026-09-11
customer: Pat Player
line: tolex
configuration: 1x12
tags: [order, speaker-cab, maximocabs]
---

# Order: Pat Player, 1x12 tolex

Source: pasted quote email dated 2026-09-11 (the site's quote template filled from its test fixture; the Plan 3 Task 7 dry run of the `/speaker-cab` skill, the customer is the site's test persona, the order directory is the fixture path `projects/Speaker-cab-system/fixtures/sample-roots-1x12/`).
Design rules: [[speaker-cab-voicing]], [[speaker-cab-construction]].

## Order

- Customer: Pat Player
- Contact: pat@example.com
- Line: tolex
- Driver count: 1
- Back type asked: recommend (the quote form has no back-type field; tolex-1x12 is the site's closed-ported product)

## Rig block

Every field stays in this list even when empty; an empty value means the customer was not asked or did not say.

- **Amps** (one line per amp; the primary amp is the one the voicing serves)
  - 1965 Fender Deluxe Reverb reissue: rated 22 W, taps [8] (one 8 ohm output winding; the extension jack is in parallel with the combo's own 8 ohm speaker, so the amp sees 8 ohm in parallel with this cabinet), combo, primary: yes, type tube (derived from the model), family blackface Fender
- **Guitars**
  - Pickups and output: (not asked by the form; no pickup adjustment applied)
  - Low-end shifters: none (assumed; nothing in the style or notes points to baritone, 7-string, drop tunings, or bass VI)
- **Pedals**
  - Dirt: (not asked by the form; no dirt-pedal adjustment applied)
  - Boosts and EQ: (not asked)
  - Drive source: (not asked)
- **Music and use**
  - Genre: "Roots, alt-country, low-volume gigs" (canonical key: roots-country)
  - Approach: (not stated; no approach override, the roots-country row's moderate breakup stands)
  - Typical venue: Small clubs, 150 cap max
  - Typical volume: low-volume gigs
  - Mic'd or filling the room: (not asked; assumed mic'd, see Assumptions stated)
  - Placement: floor (assumed; the form does not ask)
- **Tonal goals**
  - Customer's words: "Want a tight low end and rolled highs."
  - Reference records or players: (none given)
  - Cabs loved: (none given) / disliked: (none given)
- **Physical**
  - Weight limit: none (assumed; the form does not ask and the customer named none)
  - Size limits: none (vehicle: not stated)
  - Dimensions to match: none (the amp is a combo; no head to match)
  - Where it lives (hardwood line, wood movement): a house (assumed; the tolex line carries no wood-movement rule)
- **Connections**
  - Jack configuration: mono (one amp, one cabinet on the combo's extension jack)
- **Aesthetics**
  - Wood species or tolex color: Fender Style Black (the form's "Black tolex"), 54 in roll
  - Grill cloth: Salt-and-pepper (the customer's words; not a site cloth, no swatch on file)
  - Piping: no; corners: black; handle: strap (leather); jack plate: recessed; logo: (not stated)
- **Speaker**
  - celestion-g12h-30-anniversary at 16 ohm (the form's "Celestion G12H Greenback (16 ohm)", the site's "G12H Greenback, 30 W"; customer-chosen, fixed)

## Assumptions stated

- The 1965 Fender Deluxe Reverb reissue is a 22 W tube combo with one 8 ohm output winding; its extension jack is in parallel with the internal 8 ohm speaker, so with this 16 ohm cabinet the amp sees 8 || 16 = 5.3 ohm (the note's combo rule). The model is known, so no power or tap follow-up was asked.
- No weight limit, no size limit, no head to match: the quote form does not ask and the customer named none, so the order is standard size and the site box is evaluated first.
- Jack configuration mono: one amp, one cabinet.
- Placement on the floor: the form does not ask; an extension cabinet at a small club sits on the floor beside the combo. The floor shifts low_end one step toward tight; the target is already tight.
- Where it lives: a house; the tolex line has no wood-movement rule, so the answer does not bind.
- "Black tolex" is the site's Fender Style Black on the 54 in roll.
- "Salt-and-pepper" is not a site grill cloth: no swatch on file, and the proposal says so.
- "Celestion G12H Greenback (16 ohm)" is the catalog note celestion-g12h-30-anniversary at 16 ohm; the speaker is fixed by the customer, so the ranking is shown for the alternatives only.
- Mic'd or filling the room was not asked: assumed mic'd (a 150-cap club normally puts a 22 W combo through the PA), so dispersion reads focused. Unmic'd would read wide on the roots-country row, and a tight low end beats wide dispersion in the note's precedence rule, so the back type does not move either way.
- Approach not stated: no override applied; the roots-country row's moderate breakup stands (an edge-of-breakup reading would give the same word).
- Pickups, pedals, and drive source were not asked: no rig adjustment applied.
- Low-end shifters none: nothing in the style or the notes points to one.

## Follow-ups asked

- none (the batch was empty on 2026-09-11: the amp model is known, no limit binds, the jack is mono on a 1x12, and the speaker is a catalog note)

## Tone target

| Field | Value | Reason |
|---|---|---|
| low_end | tight | the roots-country row reads tight and the customer wrote "tight low end"; on the floor shifts one step toward tight, and the target is already there |
| mids | neutral | the roots-country row reads neutral; pickups not asked, no adjustment; a blackface amp is scooped on its own |
| top | smooth | the roots-country row reads smooth; the customer's "rolled highs" points away from chimey on a bright blackface amp and is read as smooth (rounded), not dark (the fuzz-taming word; no fuzz in the rig) |
| breakup | moderate | the roots-country row reads moderate; no approach stated, so no override |
| dispersion | focused | the roots-country row reads focused when mic'd; assumed mic'd (Assumptions stated); a tight low end beats wide either way |
| placement | floor | assumed floor; the form does not ask |
| min_power_w | 33 | 1.5 x 22 W, the Deluxe Reverb reissue, the only amp |
| impedance_options_ohm | [8] | the Deluxe Reverb's one 8 ohm output winding: the taps are the winding and are never edited to pass a sheet; the 16 ohm driver's 2:1 mismatch is accepted on the engine command (see Trade-offs presented), and the extension jack puts the cabinet in parallel with the combo's own 8 ohm speaker, a combined 5.3 ohm load (Rig block) |

Written to `tone.json` on 2026-09-11 with taps [8]. The taps stay the winding; the impedance mismatch is accepted on the engine command with `--accept-impedance-mismatch`, never by editing the taps (see Trade-offs presented).

## Speaker ranking

Hard filters: Celestion Blue (15 W) drops on the power rule (under the amp's 22 W rating); every other note offers 8 ohm, and all but the Red White and Blues offer 16 ohm. Scored 2 per matching character word (tight, neutral, smooth, moderate), 1 for the blackface Fender row of the amp-family table (Cannabis Rex, Jensen C12N, Celestion Gold, G12H-75 Creamback), 1 for `roots-country` on the note's Genres line; no loved or disliked cab. Ties at 6 broken on data status.

| Candidate | Points | Matched keys | Data status | Reason |
|---|---|---|---|---|
| eminence-cannabis-rex | 8 | mids, top, breakup, family, genre | datasheet | the blackface row's roots speaker: neutral mids, smooth top, moderate breakup, 50 W; balanced low end on paper, and a tight box does the tightening |
| jensen-c12n | 6 | mids, breakup, family, genre | datasheet | the classic blackface driver, but Qts 1.02 wants an open back; closed-ported reads boomy in the calibration table, so it would take the open-back rule |
| celestion-g12-65-heritage | 6 | low_end, top, breakup | missing | tight, smooth, moderate on paper, no family or genre point (a Marshall voice); no Thiele-Small data, rule-of-thumb volume only |
| celestion-g12h-30-anniversary (chosen) | 2 | breakup | analog | fixed by the customer; big low end, forward mids, chimey top on paper against a tight, neutral, smooth target; the small box and the combo's own speaker carry the tightening |

Next: celestion-g12h-75-creamback 5 (missing), eminence-red-white-and-blues 5 (datasheet, 8 ohm only).

Chosen: celestion-g12h-30-anniversary at 16 ohm. Fixed by the customer (the form's "Celestion G12H Greenback (16 ohm)"); the ranking above feeds the proposal's alternatives only.

## Back type

closed-ported: the target's low_end is tight and its dispersion focused, and both take closed-ported by the choice rule; the customer chose the tolex-1x12, the site's closed-ported product; the G12H Anniversary's Qts 0.58 sits under the 0.9 open-back threshold; no low-end shifter. Precedence: had dispersion read wide (unmic'd), a tight low end beats wide dispersion, so closed-ported either way. The port tuning (76.5 Hz predicted) sits under the speaker's 85 Hz Fs, adding weight rather than boom.

## Voicing decision

- Mode: propose (the site box was evaluated first and read punchy; the bridge word for a tight target on a ported box is flat, so the skill proposed a tone-driven box)
- Engine command (verbatim):

  Evaluate first, the site box with the site port, one run with `--accept-impedance-mismatch` (the 16 ohm driver against the amp's single 8 ohm tap is otherwise the impedance blocker, see Trade-offs presented): exit 0, character punchy, Fb 67.4 Hz, F3 69.2 Hz, peak 1.3 dB, no blockers, `wiring.mismatch_accepted` true with the two wiring warnings (`no wiring option matches amp taps [8]`, `impedance mismatch accepted: 16 ohm cabinet on amp taps [8]`):

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py evaluate --speaker celestion-g12h-30-anniversary --impedance 16 \
    --enclosure closed-ported --tone projects/Speaker-cab-system/fixtures/sample-roots-1x12/tone.json --line tolex \
    --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40 \
    --name sample-roots-1x12 --out projects/Speaker-cab-system/fixtures/sample-roots-1x12/ --accept-impedance-mismatch
  ```

  The command that produced `voicing.json` (exit 0, no blockers, the same flag):

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py propose --speaker celestion-g12h-30-anniversary --impedance 16 \
    --enclosure closed-ported --tone projects/Speaker-cab-system/fixtures/sample-roots-1x12/tone.json \
    --jack mono --line tolex --name sample-roots-1x12 --out projects/Speaker-cab-system/fixtures/sample-roots-1x12/ --accept-impedance-mismatch
  ```

- Reading: the engine's tone-driven box is the smallest practical one for this driver. The Thiele-Small volume for a tight target (19.7 L) sits under the engine's 30 L floor, so the box starts at the clamped 30.0 L net (33.1 L gross): internal 424 x 378 x 206 mm, external 460 x 414 x 256 mm (18.1 x 16.3 x 10.1 in), about 2 in narrower, 1.7 in shorter, and 0.9 in shallower than the site box. Tuned at Fb 76.5 Hz (0.9 x the speaker's 85 Hz Fs, the tight rule) through one rear 101.5 mm tube 51 mm long (snapped up from 85 mm), worst-case air speed 2.3 m/s against the 17 m/s limit. Predicted character punchy: a 2.1 dB low-mid lift around 130 to 200 Hz with F3 at 79 Hz, so the bottom rolls off faster and earlier than the site box's (F3 69 Hz, 1.3 dB peak). For this player that is a drier, faster low end under the Deluxe Reverb's own 8 ohm speaker, with the port adding low-mid weight rather than boom, which is what "tight low end" asks for; the bridge word for tight is flat, and punchy is the closest this driver reaches inside the 30 L floor (the site box reads punchy with more bottom, so the smaller box serves tight better of the two). Wiring: single driver, 16 ohm, and no tap matches: the sheet warns twice (`no wiring option matches amp taps [8]`, `impedance mismatch accepted: 16 ohm cabinet on amp taps [8]`) and records `wiring.mismatch_accepted` true; the amp's extension jack puts the cabinet in parallel with the combo's 8 ohm speaker, 8 || 16 = 5.3 ohm on the 8 ohm winding, accepted as a 2:1 mismatch within a tube amp's tolerance. Power: the G12H Anniversary's 30 W clears the amp's 22 W rating and sits under the 33 W (1.5 x) target, a warning, accepted: a 22 W blackface combo at low-volume gigs, sharing its output with its own speaker, will not push 30 W into this cabinet. Remaining warnings: the clamped volume (above); driver displacement assumed 1.5 L (the note has no figure); width to depth 2.06:1, within 5 percent of 2:1, coincident standing waves, the same advisory the site box trips; the port diameter snapped to the 101.5 mm tube. Every number here is a prediction from Thiele-Small values scaled from the Heritage G12H(55) (data status analog): unverified, ears only.
- Stop one, presented past the bridge word: the proposal's character (punchy) misses the bridge word for tight (flat), and the sheet's clamped-volume warning says why (the Thiele-Small volume for tight is 19.7 L, under the engine's 30 L floor, so the box starts from the clamped 30.0 L). Presented as the closest this driver reaches inside the floor, with the reading above, beside the alternatives: the closed box (no port; a smaller, drier bottom than the ported 30 L box can give, at the cost of the port's low-mid weight; not run, named as the alternative), and the next-ranked speaker (the Eminence Cannabis Rex, the blackface row's roots speaker, whose datasheet volume for tight would sit inside the floor; the customer chose the G12H Anniversary, so this is the alternative the proposal's section 4 carries).
- Approved by Brian on 2026-09-11: yes (the dry run's answer sheet: approve as presented; the proposal chosen over the closed box and the next-ranked speaker)

## Plan

- Parts in build order: shell (top, bottom, two sides, 18 mm Baltic birch, finger-jointed at the four front-to-back corners); baffle (18 mm birch, floating, front face 20 mm behind the front edge, 283 mm cutout on a 297 mm bolt circle, 4 bolts on T-nuts); baffle cleats (18 x 18 mm, felt strip, screws); no brace or divider (1x12, mono); back cleats (18 x 18 mm); back panel (12 mm birch, removable, screwed to the cleats) carrying the 101.5 mm rear port tube with its 12 mm flange ring and the recessed jack plate; grill frame (12 x 40 mm birch strips, half-lap corners, cloth wrapped and stapled, hook-and-loop to the baffle); hardware (jack plate, strap handle, four black corners, four rubber feet). The layout kernel produces the actual list; this is what Brian can object to first.
- Joinery per connection: finger joints at the four shell corners (9 mm fingers on 18 mm birch, cut to measured thickness); the baffle floating on felt-isolated cleats; the back panel screwed to cleats; no divider.
- Grain and show faces (hardwood): n/a, tolex line.
- Hardware positions: one recessed jack plate at the bottom center of the back panel, 25 mm above the cleat; the leather strap handle top center over the loaded center of mass (within 15 mm on the width axis), 50 mm inside the edges; four black metal corners (cutouts 50 mm from the external corners); four 40 mm rubber feet inset 32 mm; no piping.
- Port location: rear round (the sheet's 101.5 mm tube, 51 mm through the back panel, one per chamber; the layout places it at the first spot in the construction note's order with 25 mm clearance)
- Aesthetics block written into `cab.py` on 2026-09-11: copied from `projects/Speaker-cab-system/fixtures/site-default/cab.py`; only `grill_cloth` changed ("Salt-and-pepper"); corner_joint finger, baffle_mount floating, handle strap, corners black, piping False, feet rubber, tolex_roll_in 54, tolex_color Fender Style Black, head_width_mm None already matched the intake; the module docstring reduced to one line naming the order, nothing below the docstring changed. The form's "Leather strap handle" is `handle="strap"`; the leather qualifier lives in this brief only

## Trade-offs presented

- 2026-09-11: the impedance blocker (`no wiring option matches the amp's impedance taps`, exit 2 without the flag: the 16 ohm speaker against the Deluxe Reverb's single 8 ohm winding, taps [8]) presented with the skill's three options: accept the mismatch with `--accept-impedance-mismatch` (a 2:1 mismatch on a tube amp, within tolerance; the extension jack puts this cabinet in parallel with the combo's 8 ohm speaker, 8 || 16 = 5.3 ohm on the 8 ohm winding), the matching-impedance variant of the same speaker (the 8 ohm G12H Anniversary, 4 ohm combined), or a different speaker; Brian chose the flag (the dry run's answer sheet); the taps in `tone.json` stay [8]; the evaluate and propose commands above ran with the flag (exit 0 each), the sheet warns twice and records `wiring.mismatch_accepted` true

## Decisions locked

- 2026-09-11: voicing approved (celestion-g12h-30-anniversary at 16 ohm, closed-ported, propose: 30.0 L net box 460 x 414 x 256 mm external, one rear 101.5 mm tube 51 mm long, Fb 76.5 Hz predicted, character punchy)
- 2026-09-11: impedance mismatch accepted with `--accept-impedance-mismatch` on the evaluate and propose commands: a 16 ohm cabinet on the Deluxe Reverb's 8 ohm extension jack (8 || 16 = 5.3 ohm, a 2:1 mismatch on a tube amp, within tolerance); the sheet records `wiring.mismatch_accepted` true and its two wiring warnings are accepted with it; the taps in `tone.json` stay [8]
- 2026-09-11: power warning accepted: the G12H Anniversary's 30 W handling is under the 33 W target (1.5 x 22 W) and above the amp's 22 W rating; no `--accept-low-headroom` (the flag applies to an early-breakup target only, this one is moderate)
- 2026-09-11: engine advisories accepted: the clamped volume (19.7 L for tight, started from the 30 L floor), driver displacement assumed 1.5 L, width to depth 2.06:1 within 5 percent of 2:1, port diameter snapped to the 101.5 mm tube from 85 mm
- 2026-09-11: `port mouth` warn accepted: the rear 101.5 mm tube's inner mouth sits 50 mm behind the magnet with 23 percent of the mouth facing it, under one diameter; the 25 mm standoff holds (magnet to back 89.1 mm), the same class of warn as the site box's rear tube
- 2026-09-11: operator rows judged in `checks.md` from the brief: no weight or size limit stated, no vehicle stated (a one-hand carry), wood movement n/a on the tolex line, joinery fit and stock thickness on the construction note's defaults, stock yield one sheet of each thickness
- 2026-09-11: stop two: the package (`checks.md`, the renders, `proposal.md`) approved as presented, no edits; `Price:` line left empty

## Artifacts

- `projects/Speaker-cab-system/fixtures/sample-roots-1x12/tone.json`, `voicing.json`, `voicing.md`
- `projects/Speaker-cab-system/fixtures/sample-roots-1x12/cab.py`, `cab.json`, `cab.step` (regenerated by `cab.py`, not committed; ignored by the vault's `projects/Speaker-cab-system/fixtures/**/*.step` rule)
- `projects/Speaker-cab-system/fixtures/sample-roots-1x12/checks.md`, `cutlist.md`, `cutlist.csv`
- `projects/Speaker-cab-system/fixtures/sample-roots-1x12/proposal.md`, `images/` (`cab-iso.png`, `cab-front.png`, `cab-top.png`, `cab-right.png`, `cab-exploded.png`, the rear view `cab-rear.png` rendered from the export run's STL at `0,90` because the port is rear-mounted, and the `fender-black.jpg` finish swatch; no swatch on file for the Salt-and-pepper cloth)
- `projects/Speaker-cab-system/fixtures/sample-roots-1x12/.claude/context-check/last-handoff.md`
- Retrospective: none (dry-run fixture, no cabinet built, Phase 8 skipped)

## Site-form gaps

- Guitars and pickups, pedals and the drive source, jack configuration, placement (floor, raised, tilted), mic'd or filling the room, weight and size limits and the vehicle, a head to match, where the cabinet lives, and whether the cabinet hangs on a combo's extension jack (the combined impedance the amp sees) are all needed by the intake and not asked by the quote form. The form also lets a grill cloth outside the site list through ("Salt-and-pepper" arrived with no swatch on file).

## Outcome

- 2026-09-11: package approved at stop two as presented (the dry run's answer sheet); `Price:` line left empty for Brian; no proposal sent (Pat Player is the site's test persona); Phase 8 skipped, no cabinet built; nothing committed by this session, the controller commits the fixture.
- 2026-09-11: fixture regenerated the same day from the amended skill (the `--accept-impedance-mismatch` fix wave): taps back to [8], the flag on both engine commands, the same box (30.0 L net, 460 x 414 x 256 mm external, rear 101.5 mm tube 51 mm, Fb 76.5 Hz, punchy), `checks.md` now 38 rows with the wiring row a warn, the rear render added, the operator rows judged again; still nothing committed by this session.
