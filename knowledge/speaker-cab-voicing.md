---
name: speaker-cab-voicing
description: How a customer's rig and tonal goals become a tone target, a speaker choice, an enclosure type, and a box alignment; rules, thresholds, and model limits for the cabvoice engine
type: reference
status: unverified-starting-values
created: 2026-09-09
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

## Enclosure type rules

- **closed-ported** (the product default): focused dispersion, tight to balanced low end with a low-mid lift from the port, best for mic'd stages and high gain. The port tuning sits below the speaker's Fs so it adds weight rather than a boom.
- **closed**: like closed-ported with less low-mid lift; use when the customer wants the driest, punchiest response or when the port would need to be too large.
- **open**: wide dispersion, airy top, less low end (the back wave cancels the front wave below the cancellation frequency, about 370 Hz for the site's box, 6 dB per octave). Best for clean and edge-of-breakup players in rooms the cab must fill by itself.
- **semi-open**: between the two: more low end than open, still wide. Open fraction 0.25 versus 0.40.
- Choice rule: dispersion wide plus low_end not tight leads to open or semi-open; dispersion focused or low_end tight or approach high gain leads to closed-ported. Mic'd cabs prefer closed-ported. Drivers with Qts above 0.9 (most Jensens, the WGS Green Beret as printed) prefer open or semi-open because any practical closed box makes them peaky.

## Amp families

| Family | Examples | Tendency | Speakers that suit |
|---|---|---|---|
| Blackface Fender | Deluxe Reverb, Twin, Princeton | scooped mids, bright, clean headroom | Cannabis Rex, Jensen C12N, Celestion Gold, G12H-75 Creamback |
| Tweed Fender | Deluxe 5E3, Bassman | forward mids, early amp breakup | Jensen P12N, G12H-30 Anniversary, G12M-25 Greenback |
| Marshall | Plexi, JCM800, JTM45 | forward mids, EL34 grind | G12M-25 Greenback, G12M-65 Creamback, G12H-30 Anniversary, Vintage 30 |
| Vox | AC15, AC30 | chime, EL84 compression | Celestion Blue, Gold, Cream, G12M-25 Greenback |
| Modern high gain | Mesa Rectifier, 5150, Friedman | tight low end, saturated | Vintage 30, G12H-75 Creamback, Swamp Thang, Veteran 30 |
| Boutique clean | Dr Z, Two-Rock, Carr | full range, dynamic | Celestion Gold, Cream, Cannabis Rex, Vintage 30 |
| Modeling and solid state | Kemper, Helix, Quilter, Tone Master | flat power section, high headroom | Tonker, Swamp Thang, Red White and Blues, G12H-75 Creamback |

Amp type (tube, solid state, modeling) is derived from the model; ask only when the model is unknown. A combo used with an extension cab has its own speaker in parallel with the cabinet, so the combined impedance is what the amp sees.

## Genre and approach

| Genre or approach | low_end | mids | top | breakup | dispersion |
|---|---|---|---|---|---|
| Roots, country, alt-country | tight | neutral | smooth | moderate | focused (mic'd) or wide (unmic'd) |
| Blues | balanced | forward | smooth | early | wide |
| Classic rock | balanced | forward | smooth | moderate | focused |
| Indie and alternative | balanced | neutral | chimey | moderate | wide |
| Jazz | balanced | neutral | dark | clean | wide |
| Metal and modern high gain | tight | scooped | smooth | clean | focused |
| Worship and pop | balanced | neutral | chimey | clean | focused |
| Funk and R&B | tight | neutral | chimey | clean | focused |

Approach overrides genre: clean sets breakup clean; edge of breakup sets moderate; high gain sets tight and focused.

## Rig adjustments

- **Pickups**: single coils push top toward smooth and mids toward neutral (they are bright already). Humbuckers push mids toward scooped and allow chimey. P90s sit between. Active pickups set breakup clean and raise the power target by 25 percent (`min_power_w` x 1.25, a starting value; they hit the amp harder).
- **Low-end shifters**: baritone, 7-string, and drop tunings set low_end big and prefer closed-ported with the lowest tuning in range, and a 2x12 over a 1x12 when weight allows.
- **Dirt pedals**: fuzz sets top dark or smooth (fuzz fizz needs a rolled top). Overdrive is neutral. Distortion and high-gain pedals set low_end tight and dispersion focused. Boosts and EQ pedals do not change the target. A pedal-platform amp favors clean headroom and higher power handling; an amp used as the drive source favors early or moderate breakup.
- **Venue and volume**: bedroom and studio allow early breakup and low-power speakers; small club unmic'd sets dispersion wide or a 2x12; mic'd stage sets focused; large stage sets closed-ported and clean.
- **Placement**: on the floor shifts low_end one step toward tight (boundary gain adds low end). Tilted counts as raised. Raised keeps the target.
- **Jack configuration**: mono for one amp; mono with parallel out when the customer daisy-chains a second cab; stereo on a 2x12 for stereo rigs and wet-dry, which divides the box into two chambers each voiced as a 1x12.
- **Cabs loved or disliked**: a named cab tells you a speaker and an enclosure. Start the ranking from the loved cab's speaker; exclude the disliked one's.

## Power and impedance

- `min_power_w` = 1.5 x the highest rated amp power in the rig (`POWER_SAFETY_FACTOR`); the voicing serves the primary amp, the power rule guards against the strongest amp. Hard stop when total handling is below the amp's rated power. Warning below the target; an early-breakup target may accept it explicitly and the acceptance goes into "Decisions locked".
- Stereo: check each side against the amp's per-channel power. For a stereo amp the intake records the per-channel rating as its rated power, so `min_power_w` / 1.5 is already the per-channel figure the engine checks each side against.
- Two drivers: parallel first, then series, whichever matches a tap. Unequal impedances get a warning (the spec's rule; the engine still lists any option that matches a tap). Sensitivity more than 2 dB apart gets a warning.
- Vintage-style 15 W to 30 W speakers are for amps up to 20 W or for two-speaker cabs; the classic AC30 into two Blues is exactly the accepted early-breakup case.

## Box alignment (Layer 2 values)

- Per-driver net volume from Thiele-Small data: Vb = Vas / alpha with alpha 1.5 (tight), 1.0 (balanced), 0.65 (big), clamped to 30 to 68 L per 12 inch driver. The clamp exists because hi-fi Qtc targets give absurd sizes for guitar drivers, which Celestion also warns about (https://celestion.com/blog/thinking-of-using-thiele-small-parameters-to-design-a-guitar-speaker-cab-think/).
- Rule-of-thumb per-driver net volume when there is no T/S data, and for every open back: 34 L (tight), 44 L (balanced), 56 L (big). The site's default box is 44 L net, so it is "balanced".
- When a speaker note has no Thiele-Small data (`data_status: missing`), the engine uses the rule-of-thumb volume, predicts no response and assigns no character word (the sheet carries a warning saying so), sizes the port for air speed with an assumed Sd of 530 cm2 and Xmax of 0.8 mm (`FALLBACK_SD_CM2`, `FALLBACK_XMAX_MM`, starting values for a 12 inch guitar driver), and assumes 1.5 L of driver displacement flagged `estimated` when the note gives none. The ranking step that reacts to a boomy warning cannot fire for these speakers; judge them by their note's Character section and the rule-of-thumb volume alone.
- Ported tuning: Fb = Fs x 0.9 (tight), 0.8 (balanced), 0.7 (big), clamped to 45 to 90 Hz. If the predicted alignment is boomy and "big" was not asked, the box grows in 10 percent steps to 68 L, then Fb drops in 5 Hz steps to 45 Hz.
- Port: round rear port, 75 mm starting diameter, one flanged end, end correction 0.85 x diameter, grown until the worst-case air speed (full Xmax at Fb) is under 17 m/s and the physical length is at least 20 mm. Maximum 150 mm diameter; beyond that the sheet keeps the warning and the fix is a lower Fb, a smaller box, or a front slot.
- Closed-box character by Qtc: below 0.6 lean, 0.6 to 0.8 tight, 0.8 to 1.0 balanced, 1.0 to 1.2 big, above 1.2 peaky. Ported character by peak height: below 1 dB flat, 1 to 3 dB punchy, above 3 dB boomy. Both scales are half-open intervals: a value on a boundary takes the upper word (Qtc 0.8 is balanced, 1.2 is peaky, a 3.0 dB peak is boomy).
- Open fraction of the back area: 0.40 open, 0.25 semi-open, as two horizontal panels top and bottom.
- Internal dimension advisory: no two internal dimensions within 5 percent of 1:1, 2:1, or 3:1. The site's default box trips the 2:1 width-to-depth advisory; noted, not changed.

## Speaker ranking procedure

1. Hard filters: impedance available for a matching wiring option; power rule not a hard stop; customer-supplied or chosen speaker fixed if given.
2. Score each remaining catalog speaker against the tone target using the Character and Best with sections of its note: 2 points per matching low_end, mids, top, breakup word, 1 point if the speaker is named in the rig's amp-family row and 1 point if it is named in the genre row (starting values), minus 2 for a disliked-cab speaker, plus 2 for a loved-cab speaker.
3. Present the top three with one reason line each and the data status of each (datasheet, third-party, analog, estimated, missing). Prefer, at equal score, the one with better data.
4. Run `cabvoice.py propose` for the top choice; if the sheet has blockers or a boomy warning, show the trade-off and try the next.

## Model limits

- Celestion publishes only Fs and Re for its guitar speakers. The only measured Celestion data is Voice Coil magazine's test of the Heritage G12H(55), 16 ohm (https://celestion.com/wp-content/uploads/2019/10/141.pdf): Qts 0.37 to 0.46, Vas 53 to 71 L, Xmax 0.7 mm across two samples. The G12H-30 Anniversary and Vintage 30 notes carry values scaled from that measurement (`data_status: analog`); the other Celestion notes are `missing` and use the rule-of-thumb volumes.
- WGS publishes T/S values with inconsistent units (Vas labeled in cubic feet at values that can only be liters, Sd of 366 with no unit). Those notes are `estimated` and say what was assumed.
- The vented model (Small 1973, QL = 7) reproduces Eminence Designer's F3 within about 2 percent for three of five published designs (Beta-12A-2 at 1.75 and 1.25 cu ft, Delta-12A at 0.75 cu ft) and is 6 to 10 percent low for the two larger Delta-12A designs (2.75 cu ft at Fb 55 Hz: 56 Hz against Eminence's 61.9; 1.35 cu ft at Fb 70 Hz: 74 Hz against 78.9). Cause not identified on 2026-09-09. The closed-box check against Eminence's sealed Beta-12A-2 design (0.904 cu ft, Qtc 1.10) reads 6.6 percent low (86 Hz against 92.1). Ported peak height is read off the third-octave grid, so a design within a few tenths of a dB of a threshold can flip words (the Beta-12A-2 1.25 cu ft, 60 Hz design lands at 3.10 dB, boomy by 0.1 dB).
- The open-back estimate is a path-length cancellation frequency with a 6 dB per octave roll-off, not a dipole model. It ranks options; it does not predict a curve. Under this formula open and semi-open share the same cancellation frequency and roll-off and differ only in panel height, so the estimate cannot rank one above the other on low end; the enclosure rule above is builder lore, unverified.
- Nothing here has been checked with a microphone. Listening notes go into the speaker notes' Field notes sections after each build.

## Calibration table

Generated by `evaluate` on the site's default box (472 x 421.2 x 229.4 mm internal, closed, one driver, 16 ohm, tone target `projects/Speaker-cab-system/fixtures/tone-roots.json`). Filled in by Task 15 of plan 1.

## Sources

- MaximoCabs site content: `~/ClaudeProjects/MaximoCabs/src/content/cabinets/tolex-1x12.md` and `hardwood-1x12.md`, `src/lib/quote-schema.ts`.
- Small, R. H., "Vented-Box Loudspeaker Systems", JAES 1973 (the fourth-order response and its coefficients).
- Eminence cabinet designs: https://cdn.shopify.com/s/files/1/0270/8665/1462/files/Beta_12A-2_cab.pdf and https://cdn.shopify.com/s/files/1/0270/8665/1462/files/Delta_12A_cab.pdf.
- Celestion on T/S for guitar cabs: https://celestion.com/blog/thinking-of-using-thiele-small-parameters-to-design-a-guitar-speaker-cab-think/.
- Amp family, genre, and rig tables: builder lore, unverified.
