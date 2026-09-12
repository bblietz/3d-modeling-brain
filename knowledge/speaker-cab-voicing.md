---
name: speaker-cab-voicing
description: How a customer's rig and tonal goals become a tone target, a speaker choice, an enclosure type, and a box alignment; rules, thresholds, and model limits for the cabvoice engine
type: reference
status: unverified-starting-values
created: 2026-09-09
updated: 2026-09-11
tags: [knowledge, speaker-cab, acoustics, reference]
---

# Speaker cabinet voicing

Rules for phase 2 of the `/speaker-cab` skill. Layer 1 (this note plus
judgment) turns the intake into a tone target and a ranked speaker list.
Layer 2 (`scripts/cabvoice.py`) turns the tone target into volumes, port,
wiring, and predictions. Every value is a starting value: unverified until
listening notes from real builds say otherwise. Construction rules live in
[[speaker-cab-construction]]; per-speaker data in `knowledge/speakers/`.

## Tone target vocabulary

| Field | Values | Meaning |
|---|---|---|
| low_end | tight, balanced, big | tight = smaller box, faster and drier low mids; big = larger box, more weight and bloom under 150 Hz |
| mids | scooped, neutral, forward | how much 400 Hz to 1.5 kHz presence the speaker should add |
| top | chimey, smooth, dark | 2 kHz to 5 kHz character: bell-like and bright, rounded, or rolled off |
| breakup | early, moderate, clean | whether the speaker itself should compress and distort at gig volume |
| dispersion | focused, wide | closed back beams and projects; open back spreads and fills |
| placement | floor, raised, tilted | where the cab sits; the floor adds low end by boundary gain |

Plus `min_power_w` (1.5 x the highest rated amp power in the rig) and `impedance_options_ohm` (the amp's taps).

The customer's own tonal words (the email's `Notes:`) are read before the genre row. A word that names a vocabulary value (tight, big, dark, chimey, scooped, forward, early, clean, focused, wide) sets that field outright; a word that only leans (for example "rolled highs" against `top`) keeps the genre row's value and is recorded as the reason in the brief's tone-target table.

## Enclosure type rules

- **closed-ported** (the product default): focused dispersion, tight to balanced low end with a low-mid lift from the port, best for mic'd stages and high gain. The port tuning sits below the speaker's Fs so it adds weight rather than a boom.
- **closed**: like closed-ported with less low-mid lift; use when the customer wants the driest, punchiest response or when the port would need to be too large.
- **open**: wide dispersion, airy top, less low end (the back wave cancels the front wave below the cancellation frequency, about 370 Hz for the site's box, 6 dB per octave). Best for clean and edge-of-breakup players in rooms the cab must fill by itself.
- **semi-open**: between the two: more low end than open, still wide. Open fraction 0.25 versus 0.40.
- Choice rule: dispersion wide plus low_end not tight leads to open or semi-open; dispersion focused or low_end tight or approach high gain leads to closed-ported. Mic'd cabs prefer closed-ported. Drivers with Qts above 0.9 (the Jensen C12N at 1.02, the WGS ET65 at 0.91, and the WGS Green Beret at 1.18, as printed; the Jensen P12N sits at 0.77) prefer open or semi-open because any practical closed box makes them peaky.
- Precedence when the rules disagree: a tight low end beats wide dispersion (closed or closed-ported over open-back); a low-end shifter (baritone, 7-string, drop tunings, bass VI) beats wide and takes closed-ported at the lowest tuning in range, applied with the engine's `--fb` flag. The override may take any value in the engine's own tuning range, 45 to 90 Hz (`FB_MIN_HZ` to `FB_MAX_HZ`, the range every proposed Fb is clamped to); the engine does not check the flag, so the skill keeps it in that range. The low-end-shifter rule starts at 45 Hz, the bottom of the range, and raises it in 5 Hz steps while the port does not fit the box (a higher tuning needs a shorter port). Raising Fb does not cure a boomy sheet, and a low-end-shifter sheet needs no cure: the shifter sets `low_end` big, and boomy serves a big target whether the customer asked for big or a shifter set it (the bridge table below), so judge that sheet by its character word, which should read boomy or punchy, not by a warning. For any other target the engine's own remedy grows the box in 10 percent steps to 68 L, then lowers Fb in 5 Hz steps to 45 Hz, and the sheet warns when it still reads boomy; that warning is what step 4 of the ranking reacts to. Starting values; listening notes decide.
- Evaluate first: a standard-size order (the site's 20 x 18 x 11 in box, one driver, no size limit, no head to match) is evaluated before anything is proposed, with the site port on a ported box: `cabvoice.py evaluate --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40` (the site port, the 101.5 mm tube at 40 mm the engine's evaluate fixture uses; box and port fix Fb, the speaker sets the character) plus the order's speaker, impedance, enclosure, tone, and line. The site box is accepted when the sheet's character is the bridge word for the target's `low_end` in the table below; otherwise, or when a size limit, a pinned width, or a second driver applies, the skill runs `propose`. Open and semi-open boxes carry no character word (the estimate reports the cancellation frequency, about 370 Hz for any box near the site depth), so an open-back site box is accepted whenever the rules above chose open or semi-open; only a size limit, a pinned width, or a second driver makes it propose.

| Predicted character | Enclosure | Serves `low_end` |
|---|---|---|
| lean (Qtc below 0.6) | closed | none: propose a smaller box or a ported one |
| tight (Qtc 0.6 to 0.8) | closed | tight |
| balanced (Qtc 0.8 to 1.0) | closed | balanced |
| big (Qtc 1.0 to 1.2) | closed | big |
| peaky (Qtc above 1.2) | closed | none: open or semi-open, or a lower-Qts driver |
| flat (peak below 1 dB) | closed-ported | tight |
| punchy (peak 1 to 3 dB) | closed-ported | balanced |
| boomy (peak above 3 dB) | closed-ported | big only; for any other target the engine grows the box, then lowers Fb, and warns when it still reads boomy |
| open, cancellation frequency reported | open, semi-open | balanced with open panels, big with semi-open panels (the panel choice, not the box, sets the low end) |

## Amp families

| Family | Examples | Tendency | Speakers that suit |
|---|---|---|---|
| Blackface Fender | Deluxe Reverb, Twin, Princeton | scooped mids, bright, clean headroom | Cannabis Rex, Jensen C12N, Celestion Gold, G12H-75 Creamback |
| Tweed Fender | Deluxe 5E3, Bassman | forward mids, early amp breakup | Jensen P12N, G12H Anniversary, G12M-25 Greenback |
| Marshall | Plexi, JCM800, JTM45 | forward mids, EL34 grind | G12M-25 Greenback, G12M-65 Creamback, G12H Anniversary, Vintage 30 |
| Vox | AC15, AC30 | chime, EL84 compression | Celestion Blue, Gold, Cream, G12M-25 Greenback |
| Modern high gain | Mesa Rectifier, 5150, Friedman | tight low end, saturated | Vintage 30, G12H-75 Creamback, Swamp Thang, Veteran 30 |
| Boutique clean | Dr Z, Two-Rock, Carr | full range, dynamic | Celestion Gold, Cream, Cannabis Rex, Vintage 30 |
| Modeling and solid state | Kemper, Helix, Quilter, Tone Master | flat power section, high headroom | Tonker, Swamp Thang, Red White and Blues, G12H-75 Creamback |

Speaker names in the table are the canonical short forms used by the ranking and by every note's Amp families line; each maps to one catalog note by slug (Celestion Blue, Gold, and Cream are celestion-blue, celestion-gold, celestion-cream; G12M-25 Greenback is celestion-g12m-25-greenback; G12H Anniversary is celestion-g12h-30-anniversary; the rest match their note's `model` field). Amp type (tube, solid state, modeling) is derived from the model; ask only when the model is unknown. A combo used with an extension cab has its own speaker in parallel with the cabinet, so the combined impedance is what the amp sees; the Impedance bullet under Power and impedance carries the load rule and the taps.

## Genre and approach

| Genre or approach | Key | low_end | mids | top | breakup | dispersion |
|---|---|---|---|---|---|---|
| Roots, country, alt-country | `roots-country` | tight | neutral | smooth | moderate | focused (mic'd) or wide (unmic'd) |
| Blues | `blues` | balanced | forward | smooth | early | wide |
| Classic rock | `classic-rock` | balanced | forward | smooth | moderate | focused |
| Indie and alternative | `indie-alternative` | balanced | neutral | chimey | moderate | wide |
| Jazz | `jazz` | balanced | neutral | dark | clean | wide |
| Metal and modern high gain | `metal-high-gain` | tight | scooped | smooth | clean | focused |
| Worship and pop | `worship-pop` | balanced | neutral | chimey | clean | focused |
| Funk and R&B | `funk-rnb` | tight | neutral | chimey | clean | focused |

Approach overrides genre: clean sets breakup clean; edge of breakup sets moderate; high gain sets tight and focused.

The Key column holds the canonical genre keys: every catalog note's Genres line lists them, the skill's ranking matches the intake's genre to them, and a genre outside the table earns no genre point (map it to the nearest row by ear and say so in the brief).

## Rig adjustments

- **Pickups**: single coils push top toward smooth and mids toward neutral (they are bright already). Humbuckers push mids toward scooped and allow chimey. P90s sit between. Active pickups set breakup clean and, in the ranking, prefer speakers whose handling is at least 25 percent above `min_power_w` (a starting value; they hit the amp harder). `min_power_w` itself stays 1.5 x the rated power, so the engine's hard stop does not move.
- **Low-end shifters**: baritone, 7-string, drop tunings, and bass VI set low_end big and take closed-ported at the lowest tuning in range (`--fb 45`, raised in 5 Hz steps only while the port does not fit; see Enclosure type rules), and a 2x12 over a 1x12 when weight allows.
- **Dirt pedals**: fuzz sets top dark or smooth (fuzz fizz needs a rolled top). Overdrive is neutral. Distortion and high-gain pedals set low_end tight and dispersion focused. Boosts and EQ pedals do not change the target. A pedal-platform amp favors clean headroom and higher power handling; an amp used as the drive source favors early or moderate breakup.
- **Venue and volume**: bedroom and studio allow early breakup and low-power speakers; small club unmic'd sets dispersion wide or a 2x12; mic'd stage sets focused; large stage sets closed-ported and clean.
- **Placement**: on the floor shifts low_end one step toward tight (boundary gain adds low end). Tilted counts as raised. Raised keeps the target.
- **Jack configuration**: mono for one amp; mono with parallel out when the customer daisy-chains a second cab; stereo on a 2x12 for stereo rigs and wet-dry, which divides the box into two chambers each voiced as a 1x12.
- **Cabs loved or disliked**: a named cab tells you a speaker and an enclosure. Start the ranking from the loved cab's speaker (plus 2 in the score); the disliked cab's speaker takes minus 2 and stays in the list.

## Power and impedance

- `min_power_w` = 1.5 x the highest rated amp power among the customer's amps (`POWER_SAFETY_FACTOR`), computed by the skill and written into `tone.json`; the voicing serves the primary amp, the power rule guards against the strongest amp. The engine reads that amp's rating back as `min_power_w` / 1.5 and stops hard when total handling is below it. Warning below the target; an early-breakup target may accept it explicitly (`--accept-low-headroom`) and the acceptance goes into "Decisions locked".
- Stereo: check each side against the amp's per-channel power. For a stereo amp the intake records the per-channel rating as its rated power, so `min_power_w` / 1.5 is already the per-channel figure the engine checks each side against.
- Two drivers: parallel first, then series, whichever matches a tap. Unequal impedances get a warning (the spec's rule; the engine still lists any option that matches a tap). Sensitivity more than 2 dB apart gets a warning.
- Impedance: `impedance_options_ohm` is the amp's taps (the winding). A single driver whose impedance matches no tap is a sheet blocker; a 2:1 mismatch on a tube amp is within tolerance and is accepted with `--accept-impedance-mismatch`, recorded on the sheet as `wiring.mismatch_accepted` and in "Decisions locked"; the taps in `tone.json` are never edited to make a sheet pass. A combo used with an extension cab has its own speaker in parallel with the cabinet, so the combined parallel load (8 || 16 = 5.3 ohm) is what the amp sees; the brief's Rig block and the proposal's rig and goals state that load.
- Vintage-style 15 W to 30 W speakers are for amps up to 20 W or for two-speaker cabs; the classic AC30 into two Blues is exactly the accepted early-breakup case.

## Box alignment (Layer 2 values)

- Per-driver net volume from Thiele-Small data: Vb = Vas / alpha with alpha 1.5 (tight), 1.0 (balanced), 0.65 (big), clamped to 30 to 68 L per 12 inch driver. The clamp exists because hi-fi Qtc targets give absurd sizes for guitar drivers, which Celestion also warns about (https://celestion.com/blog/thinking-of-using-thiele-small-parameters-to-design-a-guitar-speaker-cab-think/).
- Rule-of-thumb per-driver net volume when there is no T/S data, and for every open back: 34 L (tight), 44 L (balanced), 56 L (big). The site's default box is 44 L net, so it is "balanced".
- When a speaker note lacks Qts, Vas, or Fs (only allowed with `data_status: missing`), the engine uses the rule-of-thumb volume, predicts no response, and prints the character as "unpredicted (no Thiele-Small data)" with a warning; sizes the port for air speed with an assumed Sd of 530 cm2 and Xmax of 0.8 mm (`FALLBACK_SD_CM2`, `FALLBACK_XMAX_MM`, starting values for a 12 inch guitar driver), and assumes 1.5 L of driver displacement flagged `estimated` when the note gives none (that default applies to any note without a displacement). The ranking step that reacts to a boomy warning cannot fire for these speakers; judge them by their note's Character section and the rule-of-thumb volume alone.
- Ported tuning: Fb = Fs x 0.9 (tight), 0.8 (balanced), 0.7 (big), clamped to 45 to 90 Hz. If the predicted alignment is boomy and "big" was not asked, the box grows in 10 percent steps to 68 L, then Fb drops in 5 Hz steps to 45 Hz.
- Port: one round rear port per driver in the chamber (a mono 2x12 gets two identical ports, each sized as a 1x12 port in half the chamber; `Constraints.port_count` and the `--port-count` flag, 1 or 2, override), 77.3 mm starting diameter (the 3 inch tube), one flanged end, end correction 0.85 x diameter, grown in 10 percent area steps until the worst-case air speed (full Xmax at Fb) is under 17 m/s, then snapped up to the next purchasable tube inside diameter (52.0, 77.3, 101.5, 153.2 mm, `PORT_TUBE_ID_MM`) and re-solved; the physical length is at least 24 mm (`MIN_PORT_LENGTH_MM`, the 12 mm back panel plus the 12 mm flange ring). Maximum 153.2 mm diameter (the largest tube), and a slot is capped at the same area; a port that still needs less than 24 mm at that size is clamped to 24 mm, the prediction then follows the tuning the clamped port actually gives, and the sheet warns; a larger port, a lower Fb, or a smaller box lengthens it. `--port-tube` pins one tube instead (no growth, no snap; a clamped length or an air speed over the limit becomes a warning, and the sheet records `port.pinned`); on `evaluate` the same flag is a validated `--port-diameter` (the engine treats it as the port's tube inside diameter from the table; give one or the other, not both). `--fb` exists on `propose` only; it overrides the tuning target and the sheet records `port.fb_override_hz`.
- Closed-box character by Qtc: below 0.6 lean, 0.6 to 0.8 tight, 0.8 to 1.0 balanced, 1.0 to 1.2 big, above 1.2 peaky. Ported character by peak height: below 1 dB flat, 1 to 3 dB punchy, above 3 dB boomy. Both scales are half-open intervals: a value on a boundary takes the upper word (Qtc 0.8 is balanced, 1.2 is peaky, a 3.0 dB peak is boomy).
- Open fraction of the back area: 0.40 open, 0.25 semi-open, as two horizontal panels top and bottom.
- Internal dimension advisory: no two internal dimensions within 5 percent of 1:1, 2:1, or 3:1. The site's default box trips the 2:1 width-to-depth advisory; noted, not changed.

## Speaker ranking procedure

1. Hard filters: impedance available for a matching wiring option; power rule not a hard stop; customer-supplied or chosen speaker fixed if given.
2. Score each remaining catalog speaker against the tone target using the Character and Best with sections of its note: 2 points per matching low_end, mids, top, breakup word, 1 point if the speaker is named in the rig's amp-family row above, and 1 point if the customer's genre key (the Key column of the genre table) appears on the note's Genres line (starting values), minus 2 for a disliked-cab speaker, plus 2 for a loved-cab speaker. Precedence: the amp-family table wins over a note's own Amp families line when they disagree (the line earns nothing on its own); genre points count only on canonical keys matched between the intake's genre and the note's Genres line, so a genre outside the table earns nothing.
3. Present the top three with one reason line each and the data status of each (datasheet, third-party, analog, estimated, missing). At equal score prefer, first, with active pickups, the speaker whose handling is at least 25 percent above `min_power_w`; then the one with better data.
4. Run the engine for the top choice (`evaluate` on the site box first for a standard-size order, else `propose`; see Enclosure type rules); if the sheet has blockers, or carries the engine's boomy warning (`propose` says the alignment stays boomy at the practical limits after its remedy has grown the box to 68 L and lowered Fb to 45 Hz; a big target never carries it, because boomy serves big), show the trade-off and try the next.

## Model limits

- Celestion publishes only Fs and Re for its guitar speakers. The only measured Celestion data is Voice Coil magazine's test of the Heritage G12H(55), 16 ohm (https://celestion.com/wp-content/uploads/2019/10/141.pdf): Qts 0.37 to 0.46, Vas 53 to 71 L, Xmax 0.7 mm across two samples. The Heritage G12H(55) note carries that measurement as `data_status: third-party`; the G12H Anniversary and Vintage 30 notes carry values scaled from it (`analog`); the other seven Celestion notes are `missing` and use the rule-of-thumb volumes.
- WGS publishes T/S values with inconsistent units (Vas labeled in cubic feet at values that can only be liters, Sd of 366 with no unit). Those notes are `estimated` and say what was assumed.
- The vented model (Small 1973, QL = 7) reproduces Eminence Designer's F3 within about 2 percent for three of five published designs (Beta-12A-2 at 1.75 and 1.25 cu ft, Delta-12A at 0.75 cu ft) and is 6 to 10 percent low for the two larger Delta-12A designs (2.75 cu ft at Fb 55 Hz: 56 Hz against Eminence's 61.9; 1.35 cu ft at Fb 70 Hz: 74 Hz against 78.9). Cause not identified on 2026-09-09. The closed-box check against Eminence's sealed Beta-12A-2 design (0.904 cu ft, Qtc 1.10) reads 6.6 percent low (86 Hz against 92.1). Ported peak height is read off the third-octave grid, so a design within a few tenths of a dB of a threshold can flip words (the Beta-12A-2 1.25 cu ft, 60 Hz design lands at 3.10 dB, boomy by 0.1 dB).
- The open-back estimate is a path-length cancellation frequency with a 6 dB per octave roll-off, not a dipole model. It ranks options; it does not predict a curve. Under this formula open and semi-open share the same cancellation frequency and roll-off and differ only in panel height, so the estimate cannot rank one above the other on low end; the enclosure rule above is builder lore, unverified.
- The schema holds one Thiele-Small set per note, the 8 ohm one. Eminence's 16 ohm variants differ: Texas Heat 16 ohm Fs 91 Hz, Qts 0.81, Vas 44.5 L against the note's 8 ohm 79 Hz, 0.65, 50.9 L (https://eminence.com/products/texas_heat_16) and Swamp Thang 16 ohm Fs 113 Hz, Qts 0.62, Vas 26.4 L against 97 Hz, 0.53, 41.3 L (https://eminence.com/products/swamp_thang_16), so a 16 ohm choice of either is voiced with the 8 ohm data until a per-impedance schema lands (deferred past Plan 3, see [[2026-09-11-plan-3-skill-design]] section 13). The calibration table below voices those rows the same way.
- Wall material and stiffness are not in the model. The Thiele-Small math treats the panels as rigid, so a hardwood cab and a tolex cab with the same internal volume predict identically; the engine carries the line and species in voicing.json's construction block for the generator and the sheet but uses them in no calculation. Species changes weight (densities in [[speaker-cab-construction]]), wood movement (the hardwood-line grain rule), and panel resonance, which only ears can judge; bracing is the lever, not species.
- Nothing here has been checked with a microphone. Listening notes go into the speaker notes' Field notes sections after each build.

## Calibration table

Calibration table, every number prediction_status "unverified, ears only". Generated 2026-09-11 with `evaluate` (closed, site box 472 x 421.2 x 229.4 mm internal) and `propose` (closed-ported, low_end balanced), 16 ohm where the note lists it (voiced with the note's 8 ohm T/S set, see Model limits), amp 40 W.

| Speaker | Data | Net L in site box | Closed Qtc | Closed character | Closed F3 Hz | Proposed ported net L | Fb Hz | Ported character | Notes |
|---|---|---|---|---|---|---|---|---|---|
| [[celestion-blue]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) | speaker handling 15 W is below the amp's 40 W |
| [[celestion-cream]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12-65-heritage]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 68 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12h-30-anniversary]] | analog | 42.5 | 0.755 | tight | 105 | 30.0 | 68 | punchy | speaker handling 30 W is below the amp's 40 W; celestion-g12h-30-anniversary: Thiele-Small volume 29.5 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L |
| [[celestion-g12h-75-creamback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12m-25-greenback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) | speaker handling 25 W is below the amp's 40 W |
| [[celestion-g12m-65-creamback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-gold]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-heritage-g12h55]] | third-party | 42.5 | 0.605 | tight | 109 | 68.0 | 45 | flat | speaker handling 30 W is below the amp's 40 W; celestion-heritage-g12h55: Thiele-Small volume 71.3 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 68.0 L |
| [[celestion-vintage-30]] | analog | 42.5 | 0.701 | tight | 105 | 37.9 | 60 | flat |  |
| [[eminence-cannabis-rex]] | datasheet | 42.0 | 0.924 | balanced | 115 | 45.5 | 77 | punchy |  |
| [[eminence-red-white-and-blues]] | datasheet | 42.0 | 1.040 | big | 114 | 66.0 | 73 | punchy | port too short (6.5 mm) for Fb 78 Hz in 66.0 L; clamped to 24 mm; a larger port, a lower Fb, or a smaller box lengthens it; port clamped at the size cap: tuned 73.5 Hz, target 78.0 Hz; lower Fb or use a smaller box |
| [[eminence-swamp-thang]] | datasheet | 41.8 | 0.747 | tight | 131 | 41.3 | 78 | flat |  |
| [[eminence-texas-heat]] | datasheet | 42.0 | 0.967 | balanced | 95 | 50.9 | 63 | punchy |  |
| [[eminence-tonker]] | datasheet | 41.8 | 0.633 | tight | 138 | 34.1 | 71 | flat |  |
| [[jensen-c12n]] | datasheet | 42.5 | 1.262 | peaky | 102 | 64.3 | 45 | boomy | jensen-c12n: Thiele-Small volume 22.6 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L; ported alignment stays boomy at the practical limits; consider a closed back or a lower-Qts driver |
| [[jensen-p12n]] | datasheet | 42.5 | 1.037 | big | 95 | 67.4 | 62 | punchy |  |
| [[wgs-et65]] | estimated | 42.5 | 1.235 | peaky | 98 | 63.4 | 49 | punchy |  |
| [[wgs-green-beret]] | estimated | 42.5 | 1.454 | peaky | 109 | 64.3 | 45 | boomy | speaker handling 25 W is below the amp's 40 W; wgs-green-beret: Thiele-Small volume 22.0 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L; ported alignment stays boomy at the practical limits; consider a closed back or a lower-Qts driver |
| [[wgs-veteran-30]] | estimated | 42.5 | 1.023 | big | 103 | 62.5 | 71 | punchy |  |

## Sources

- MaximoCabs site content: `~/ClaudeProjects/MaximoCabs/src/content/cabinets/tolex-1x12.md` and `hardwood-1x12.md`, `src/lib/quote-schema.ts`.
- Small, R. H., "Vented-Box Loudspeaker Systems", JAES 1973 (the fourth-order response and its coefficients).
- Eminence cabinet designs: https://cdn.shopify.com/s/files/1/0270/8665/1462/files/Beta_12A-2_cab.pdf and https://cdn.shopify.com/s/files/1/0270/8665/1462/files/Delta_12A_cab.pdf.
- Celestion on T/S for guitar cabs: https://celestion.com/blog/thinking-of-using-thiele-small-parameters-to-design-a-guitar-speaker-cab-think/.
- Amp family, genre, and rig tables: builder lore, unverified.
