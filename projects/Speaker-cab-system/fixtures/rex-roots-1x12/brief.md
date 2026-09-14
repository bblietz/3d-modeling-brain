---
name: rex-roots-1x12
description: MaximoCabs order brief for Pat Player, a 1x12 tolex cabinet, closed-ported (front slot), Eminence Cannabis Rex 8 ohm
type: order
status: proposed
created: 2026-09-11
customer: Pat Player
line: tolex
configuration: 1x12
tags: [order, speaker-cab, maximocabs]
---

# Order: Pat Player, 1x12 tolex

Source: pasted quote email dated 2026-09-11 (the site's quote template filled from its test fixture; the Plan 3 Task 8 dry run of the `/speaker-cab` skill, the port-loop order; the customer is the site's test persona, the order directory is the fixture path `projects/Speaker-cab-system/fixtures/rex-roots-1x12/`; every stop answered from the task's answer sheet, not by Brian).
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
  - 1965 Fender Deluxe Reverb reissue: rated 22 W, taps [8] (one 8 ohm output winding; the extension jack is in parallel with the combo's own 8 ohm speaker, so with this 8 ohm cabinet the amp sees 8 || 8 = 4 ohm on the 8 ohm winding), combo, primary: yes, type tube (derived from the model), family blackface Fender
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
  - eminence-cannabis-rex at 8 ohm (the form's "Eminence Cannabis Rex (8 ohm)"; customer-chosen, fixed)

## Assumptions stated

- The 1965 Fender Deluxe Reverb reissue is a 22 W tube combo with one 8 ohm output winding; its extension jack is in parallel with the internal 8 ohm speaker, so with this 8 ohm cabinet the amp sees 8 || 8 = 4 ohm (the note's combo rule): a 2:1 load on the winding, within a tube amp's tolerance and the load any 8 ohm extension cabinet puts on that jack. The engine's impedance check reads the cabinet alone (8 ohm against taps [8], a match), so no `--accept-impedance-mismatch` applies; the combined load is stated here and in the proposal. The model is known, so no power or tap follow-up was asked.
- No weight limit, no size limit, no head to match: the quote form does not ask and the customer named none, so the order is standard size and the site box is evaluated first.
- Jack configuration mono: one amp, one cabinet.
- Placement on the floor: the form does not ask; an extension cabinet at a small club sits on the floor beside the combo. The floor shifts low_end one step toward tight; the target is already tight.
- Where it lives: a house; the tolex line has no wood-movement rule, so the answer does not bind.
- "Black tolex" is the site's Fender Style Black on the 54 in roll.
- "Salt-and-pepper" is not a site grill cloth: no swatch on file, and the proposal says so.
- "Eminence Cannabis Rex (8 ohm)" is the catalog note eminence-cannabis-rex at 8 ohm; the speaker is fixed by the customer, so the ranking is shown for the alternatives only (it also tops the ranking).
- Mic'd or filling the room was not asked: assumed mic'd (a 150-cap club normally puts a 22 W combo through the PA), so dispersion reads focused. Unmic'd would read wide on the roots-country row, and a tight low end beats wide dispersion in the note's precedence rule, so the back type does not move either way.
- Approach not stated: no override applied; the roots-country row's moderate breakup stands.
- Pickups, pedals, and drive source were not asked: no rig adjustment applied.
- Low-end shifters none: nothing in the style or the notes points to one.

## Follow-ups asked

- none (the batch was empty on 2026-09-11: the amp model is known, no limit binds, the jack is mono on a 1x12, and the speaker is a catalog note; the answer sheet confirms every assumption stands)

## Tone target

| Field | Value | Reason |
|---|---|---|
| low_end | tight | the roots-country row reads tight and the customer wrote "tight low end"; on the floor shifts one step toward tight, and the target is already there |
| mids | neutral | the roots-country row reads neutral; pickups not asked, no adjustment; a blackface amp is scooped on its own |
| top | smooth | the roots-country row reads smooth; the customer's "rolled highs" only leans (it names no vocabulary value), so the row's value stands and the words are the reason: rounded, not dark (the fuzz-taming word; no fuzz in the rig) |
| breakup | moderate | the roots-country row reads moderate; no approach stated, so no override |
| dispersion | focused | the roots-country row reads focused when mic'd; assumed mic'd (Assumptions stated); a tight low end beats wide either way |
| placement | floor | assumed floor; the form does not ask |
| min_power_w | 33 | 1.5 x 22 W, the Deluxe Reverb reissue, the only amp |
| impedance_options_ohm | [8] | the Deluxe Reverb's one 8 ohm output winding; the 8 ohm driver matches it, and the extension jack puts the cabinet in parallel with the combo's own 8 ohm speaker, a combined 4 ohm load (Rig block) |

Written to `tone.json` on 2026-09-11.

## Speaker ranking

Hard filters: Celestion Blue (15 W) drops on the power rule (under the amp's 22 W rating); every other note offers 8 ohm, matching the single tap. Scored 2 per matching character word (tight, neutral, smooth, moderate), 1 for the blackface Fender row of the amp-family table (Cannabis Rex, Jensen C12N, Celestion Gold, G12H-75 Creamback), 1 for `roots-country` on the note's Genres line; no loved or disliked cab. Ties at 6 broken on data status.

| Candidate | Points | Matched keys | Data status | Reason |
|---|---|---|---|---|
| eminence-cannabis-rex (chosen) | 8 | mids, top, breakup, family, genre | datasheet | the blackface row's roots speaker: neutral mids, smooth top, moderate breakup, 50 W; balanced low end on paper, and a tight box does the tightening; fixed by the customer and the top score |
| jensen-c12n | 6 | mids, breakup, family, genre | datasheet | the classic blackface driver, but Qts 1.02 wants an open back; closed-ported reads boomy in the calibration table, so it would take the open-back rule |
| celestion-g12-65-heritage | 6 | low_end, top, breakup | missing | tight, smooth, moderate on paper, no family or genre point (a Marshall voice); no Thiele-Small data, rule-of-thumb volume only |
| eminence-red-white-and-blues | 5 | low_end, mids, genre | datasheet | tight and neutral with 120 W of headroom, 8 ohm only; no family point (not in the blackface row); chimey top and clean breakup miss "rolled highs" on a bright amp |

Next: celestion-g12h-75-creamback 5 (missing), eminence-texas-heat 4 (datasheet), jensen-p12n 4 (datasheet).

Chosen: eminence-cannabis-rex at 8 ohm. Fixed by the customer (the form's "Eminence Cannabis Rex (8 ohm)") and the top of the ranking; the rest of the ranking feeds the proposal's alternatives.

## Back type

closed-ported: the target's low_end is tight and its dispersion focused, and both take closed-ported by the choice rule; the customer chose the tolex-1x12, the site's closed-ported product; the Cannabis Rex's Qts 0.64 sits under the 0.9 open-back threshold; no low-end shifter. Precedence: had dispersion read wide (unmic'd), a tight low end beats wide dispersion, so closed-ported either way. The port ended up a front slot through the Phase 4 port loop (see Trade-offs presented); the tuning (86.4 Hz predicted, 0.9 x the speaker's 96 Hz Fs) sits under Fs, adding weight rather than boom.

## Voicing decision

- Mode: propose (the site box was evaluated first and read punchy; the bridge word for a tight target on a ported box is flat, so the skill proposed a tone-driven box)
- Engine command (verbatim):

  Evaluate first, the site box with the site port: exit 0, character punchy, Fb 67.8 Hz, F3 98.8 Hz, peak 1.9 dB, net 41.6 L, one warning (width to depth 2.06:1), no blockers, wiring `single: 8 ohm, matches tap`, power ok (50 W clears 33 W):

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py evaluate --speaker eminence-cannabis-rex --impedance 8 \
    --enclosure closed-ported --tone projects/Speaker-cab-system/fixtures/rex-roots-1x12/tone.json --line tolex \
    --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40 \
    --name rex-roots-1x12 --out projects/Speaker-cab-system/fixtures/rex-roots-1x12/
  ```

  The first propose, presented at stop one (exit 0, no blockers): 33.4 L net, internal 446 x 398 x 217 mm, external 482 x 434 x 267 mm, one rear 153.2 mm tube 90 mm long (snapped up from 113.2 mm), Fb 86.4 Hz, F3 102.5 Hz, peak 2.97 dB, punchy, two warnings (width to depth 2.06:1; port snapped to the 153.2 mm tube):

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py propose --speaker eminence-cannabis-rex --impedance 8 \
    --enclosure closed-ported --tone projects/Speaker-cab-system/fixtures/rex-roots-1x12/tone.json \
    --jack mono --line tolex --name rex-roots-1x12 --out projects/Speaker-cab-system/fixtures/rex-roots-1x12/
  ```

  The command that produced the final `voicing.json` (the Phase 4 port loop's front-slot run, exit 0, no blockers; the chamber width 438.9 mm and the external width 474.9 mm read from the pinned-tube sheet's `box.chamber_internal_width_mm` and `box.external_mm[0]`, see Trade-offs presented):

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py propose --speaker eminence-cannabis-rex --impedance 8 \
    --enclosure closed-ported --tone projects/Speaker-cab-system/fixtures/rex-roots-1x12/tone.json \
    --jack mono --line tolex --name rex-roots-1x12 --out projects/Speaker-cab-system/fixtures/rex-roots-1x12/ \
    --port-slot 438.9 40 --pinned-width 474.9
  ```

- Reading (of the final sheet; the stop-one sheet differed only in the port, the tuning and the box are the same volume): the engine's tone-driven box is the Thiele-Small volume for a tight target, Vas 45.5 L / 1.5 = 33.4 L net (37.9 L gross with the slot), inside the 30 to 68 L practical range, so nothing is clamped: internal 439 x 427 x 202 mm, external 475 x 463 x 252 mm (18.7 x 18.2 x 9.9 in), about 1.3 in narrower, 0.2 in taller (the slot's 58 mm height floor), and 1.1 in shallower than the site box. Tuned at Fb 86.4 Hz (0.9 x the Cannabis Rex's 96 Hz Fs, the tight rule) through one front slot 439 x 40 mm across the full chamber width, 83 mm deep (the shelf depth), worst-case air speed 1.3 m/s against the 17 m/s limit. Predicted character punchy: a 3.0 dB lift (2.97 dB, a hair under the boomy boundary) around 160 to 250 Hz with F3 at 103 Hz, so the bottom rolls off sooner than the site box's (F3 99 Hz, 1.9 dB peak) with a little more low-mid weight from the slot. For this player that is a drier, faster low end under the Deluxe Reverb's own 8 ohm speaker, which is what "tight low end" asks for; the bridge word for tight is flat, and punchy is what the tight-rule volume and tuning give this driver (the tuning sits 0.9 x Fs by the rule; the slot follows it exactly, where the pinned rear tube could not). Wiring: single driver, 8 ohm, matches the amp's one 8 ohm tap; the amp's extension jack puts the cabinet in parallel with the combo's 8 ohm speaker, 8 || 8 = 4 ohm on the 8 ohm winding, the same load any 8 ohm extension cabinet puts there (Rig block). Power: 50 W clears the amp's 22 W rating and the 33 W (1.5 x) target, no warning. Remaining warning: width to height 1.03:1, within 5 percent of 1:1, coincident standing waves (an advisory; the slot's height floor lifted the height to within a hair of the width; the site box trips the same class of advisory at 2:1). Every number here is a prediction from Eminence's published Thiele-Small values (data status datasheet): unverified, ears only.
- Stop one, presented past the bridge word: the proposal's character (punchy) misses the bridge word for tight (flat) with no clamped-volume warning to blame (the 33.4 L box is the unclamped tight-rule volume for this driver; Qts 0.64 and the 0.9 x Fs tuning give the lift). Presented as the closest this driver reaches under the tight rule, with the reading, beside the alternatives: the closed box (run as the same propose command with `--enclosure closed` into a scratch directory outside the order, exit 0: 30.3 L net at the 30 L floor, external 461 x 415 x 257 mm, Qtc 1.01, character big, F3 120 Hz; a step further from tight than the ported box, since this driver's Qts 0.64 lands the closed box in the big band at any practical volume, and it gives up the port's low-mid weight), and no next-ranked speaker (the customer fixed the Cannabis Rex, which also tops the ranking). The site box itself (punchy, 1.9 dB peak, F3 99 Hz) reads punchy too and is not the bridge word either.
- Approved by Brian on 2026-09-11: yes (the dry run's answer sheet: approve as presented; the tone-driven box chosen over the site box and the closed box)

## Plan

- Parts in build order: shell (top, bottom, two sides, 18 mm Baltic birch, finger-jointed at the four front-to-back corners); slot shelf (18 mm birch, 83 mm deep, front edge flush with the baffle face, glued to the sides, doubling as the bottom baffle cleat); baffle (18 mm birch, floating, front face 20 mm behind the front edge, 281 mm cutout on a 294.4 mm bolt circle, 8 bolts on T-nuts, its bottom edge resting on the shelf); baffle cleats (top and two sides, 18 x 18 mm, felt strip, screws); no brace or divider (1x12, mono); back cleats (four, 18 x 18 mm); back panel (12 mm birch, removable, screwed to the cleats) carrying the recessed jack plate; grill frame (12 x 40 mm birch strips, half-lap corners, cloth wrapped and stapled, hook-and-loop to the baffle, covering only the baffle above the shelf); hardware (jack plate, strap handle, four black corners, four rubber feet). The layout kernel produces the actual list; this is what Brian can object to first.
- Joinery per connection: finger joints at the four shell corners (8.7 mm fingers, 29 per corner, on 18 mm birch, cut to measured thickness); the baffle floating on felt-isolated cleats with the shelf as its bottom rest; the shelf glued to the sides; the back panel screwed to cleats; no divider.
- Grain and show faces (hardwood): n/a, tolex line.
- Hardware positions: one recessed jack plate at the bottom center of the back panel, 25 mm above the cleat; the leather strap handle top center over the loaded center of mass (within 15 mm on the width axis), 50 mm inside the edges; four black metal corners (cutouts 50 mm from the external corners); four 40 mm rubber feet inset 32 mm; no piping.
- Port location: front slot (439 x 40 mm across the full chamber width under the baffle, 83 mm shelf, one per chamber; from the port loop's front-slot run, see Trade-offs presented; the plan was first written for the rear round port the stop-one sheet carried and moved to the slot when the loop chose it)
- Aesthetics block written into `cab.py` on 2026-09-11: copied from `projects/Speaker-cab-system/fixtures/site-default/cab.py`; only `grill_cloth` changed ("Salt-and-pepper"); corner_joint finger, baffle_mount floating, handle strap, corners black, piping False, feet rubber, tolex_roll_in 54, tolex_color Fender Style Black, head_width_mm None already matched the intake; the module docstring reduced to one line naming the order, nothing below the docstring changed. The form's "Leather strap handle" is `handle="strap"`; the leather qualifier lives in this brief only

## Trade-offs presented

- 2026-09-11: the layout's `port fit` blocker, form 1, on the plain `cab.py` run against the stop-one sheet (exit 2: `port fit: chamber 0 port 0: no round port of 153.2 mm fits with 25 mm clearance; the longest table tube that fits at the 24 mm minimum is 101.5 mm; raise Fb, use a smaller tube or a larger box, or a front slot`, with a consequential `net volume` blocker, `port not built, so its tube and ring are missing from the inside parts`); the skill's automatic re-run, no stop: the same propose command with `--port-tube 101.5` added (exit 0; 33.4 L net, external 475 x 428 x 263 mm, rear 101.5 mm tube 24 mm long, Fb 81.0 Hz against the 86.4 Hz target, F3 103.6 Hz, peak 2.7 dB, punchy; warnings `port too short (10.6 mm) for Fb 86 Hz in 33.4 L; clamped to 24 mm` and `port clamped at the 24 mm minimum with the pinned 101.5 mm tube: tuned 81.0 Hz, target 86.4 Hz; a larger tube, a lower Fb, or a smaller box lengthens it`, plus the 2:1 advisory), then `cab.py` again (exit 0, `port fit` pass at x 82 z 214, `port mouth` warn 90 mm from the magnet, 42 percent)
- 2026-09-11: the port-loop trade-off stop, because the pinned re-run's sheet carries a port warning (the clamped length), presented with the skill's four remedies in order: (1) the front slot, `--port-slot 438.9 40 --pinned-width 474.9` (the width the sheet's `box.chamber_internal_width_mm` 438.9 mm, the external width its `box.external_mm[0]` 474.9 mm, the construction note's default); (2) the pinned 101.5 mm tube's clamped tuning accepted as the sheet reports it (81.0 Hz against 86.4 Hz); (3) Fb raised with the larger 153.2 mm tube (`--port-tube 153.2 --fb <hz>`, within 45 to 90 Hz); (4) a larger box (the free width relaxed). Brian chose the front slot (the dry run's answer sheet: the first remedy listed); command re-run:

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py propose --speaker eminence-cannabis-rex --impedance 8 \
    --enclosure closed-ported --tone projects/Speaker-cab-system/fixtures/rex-roots-1x12/tone.json \
    --jack mono --line tolex --name rex-roots-1x12 --out projects/Speaker-cab-system/fixtures/rex-roots-1x12/ \
    --port-slot 438.9 40 --pinned-width 474.9
  ```

  exit 0, no blockers, no port warning: slot 439 x 40 mm, 83 mm long, Fb 86.4 Hz on target, external 475 x 463 x 252 mm (the slot's 58 mm height floor lifted the height from 428 to 463 mm; the width held at the pin); one advisory (width to height 1.03:1, within 5 percent of 1:1). `cab.py` again: exit 0, `port fit` pass (`slot port(s) built: chamber 0 slot 439 x 40 mm, shelf 83 mm`), one `port mouth` warn (the floor-level back cleat, 119 mm from the mouth, 46 percent, under the slot's 149.5 mm effective diameter). The loop closed on the second engine re-run; no form fired twice.

## Decisions locked

- 2026-09-11: voicing approved (eminence-cannabis-rex at 8 ohm, closed-ported, propose: 33.4 L net box; at stop one the sheet carried a rear 153.2 mm tube 90 mm long in a 482 x 434 x 267 mm box, Fb 86.4 Hz predicted, character punchy; the port loop then moved the port to a front slot in a 475 x 463 x 252 mm box at the same volume and tuning)
- 2026-09-11: port loop, form 1 automatic re-run: `--port-tube 101.5` pinned on the named tube, no stop
- 2026-09-11: port loop trade-off: the front slot chosen over the clamped tuning, a raised Fb with the larger tube, and a larger box; `--port-slot 438.9 40 --pinned-width 474.9`; the final sheet's `port.shape` is `slot`
- 2026-09-11: no impedance mismatch on the engine (8 ohm driver, taps [8], `single: 8 ohm, matches tap`); the combined 4 ohm load on the Deluxe Reverb's extension jack (8 || 8) recorded in the Rig block and the proposal as a 2:1 load on the winding, within a tube amp's tolerance, not an engine event
- 2026-09-11: no power warning (50 W handling clears the 33 W target); no `--accept-low-headroom`
- 2026-09-11: engine advisory accepted: width to height 1.03:1, within 5 percent of 1:1, coincident standing waves (the slot's height floor lifted the height to 427 mm against the 439 mm width)
- 2026-09-11: `port mouth` warn accepted: the slot's inner mouth faces the floor-level back cleat 119 mm away with 46 percent of the mouth facing it, under the slot's 149.5 mm effective diameter; the construction note names this warn on shallow 1x12 slot boxes (a deeper box, or accept); the 25 mm standoff holds (magnet to back 90.7 mm)
- 2026-09-11: operator rows judged in `checks.md` from the brief: no weight or size limit stated, no vehicle stated (a one-hand carry), wood movement n/a on the tolex line, joinery fit and stock thickness on the construction note's defaults, stock yield one sheet of each thickness
- 2026-09-11: stop two: the package (`checks.md`, the renders, `proposal.md`) approved as presented, no edits; `Price:` line left empty

## Artifacts

- `projects/Speaker-cab-system/fixtures/rex-roots-1x12/tone.json`, `voicing.json`, `voicing.md`
- `projects/Speaker-cab-system/fixtures/rex-roots-1x12/cab.py`, `cab.json`, `cab.step` (regenerated by `cab.py`, not committed; ignored by the vault's `projects/Speaker-cab-system/fixtures/**/*.step` rule)
- `projects/Speaker-cab-system/fixtures/rex-roots-1x12/checks.md`, `cutlist.md`, `cutlist.csv`
- `projects/Speaker-cab-system/fixtures/rex-roots-1x12/proposal.md`, `images/` (`cab-iso.png`, `cab-front.png`, `cab-top.png`, `cab-right.png`, `cab-exploded.png`, and the `tolex-fender-black.jpg` finish swatch; no rear view, the port is a front slot; no swatch on file for the Salt-and-pepper cloth)
- `projects/Speaker-cab-system/fixtures/rex-roots-1x12/.claude/context-check/last-handoff.md`
- Retrospective: none (dry-run fixture, no cabinet built, Phase 8 skipped)

## Site-form gaps

- Guitars and pickups, pedals and the drive source, jack configuration, placement (floor, raised, tilted), mic'd or filling the room, weight and size limits and the vehicle, a head to match, where the cabinet lives, and whether the cabinet hangs on a combo's extension jack (the combined impedance the amp sees) are all needed by the intake and not asked by the quote form. The form also lets a grill cloth outside the site list through ("Salt-and-pepper" arrived with no swatch on file).

## Outcome

- 2026-09-11: package approved at stop two as presented (the dry run's answer sheet); `Price:` line left empty for Brian; no proposal sent (Pat Player is the site's test persona); Phase 8 skipped, no cabinet built; nothing committed by this session, the controller commits the fixture.
