---
name: speaker-cab-system-design
description: Approved design for the custom guitar speaker cabinet capability (intake, voicing engine, parametric generator, /speaker-cab skill, knowledge base)
type: design-spec
status: approved-pending-user-review
created: 2026-09-08
tags: [project, speaker-cab, maximocabs, design, acoustics, woodworking]
---

# Custom guitar speaker cabinet system: design

**Goal.** Design guitar speaker cabinets custom for each MaximoCabs customer. The customer picks the line (tolex or hardwood), wood or tolex, speaker, grill cloth, and hardware. The cabinet is voiced for the tone they want, taking into account their amps, guitars, pedals, music style, venues, and physical constraints. Each order ends with a builder package (CAD, cut list, voicing sheet) and a customer proposal.

**Approach.** Fork the furniture workflow ([[drawer-bench-design]] is the reference project) into a `/speaker-cab` skill, add a deterministic and unit-tested acoustics script, and add a knowledge base with a machine-readable speaker catalog. Built in three phases: knowledge base and engine, parametric generator, skill.

## Decisions locked in brainstorming (2026-09-08)

- **Range**: 1x12 and 2x12, closed-back ported and open-back. Parametric in driver count and back type. 4x12, 1x10, combos, isolation and bass cabs are out of scope.
- **Deliverables**: builder package (CAD, cut list, voicing sheet) plus a customer proposal. No site configurator.
- **Acoustic depth**: Thiele-Small modeling for closed and ported boxes plus documented tone rules. Open-back uses empirical rules. No diffraction or panel simulation.
- **Validation**: ears only for now. Every predicted number is labeled unverified. Structured listening notes after each build feed the speaker catalog.
- **Architecture**: approach A, fork furniture plus acoustics script plus knowledge base. Prose-only and standalone-app approaches rejected.
- **Intake revision (2026-09-09)**: added speaker impedance preference, primary amp, where the cab lives, jack configuration with stereo 2x12, and placement. Dropped modulation-type pedals, asked amp type, and separate transport and stacking lines. Needed-by date and speaker budget left out.

## Context

- MaximoCabs (`~/ClaudeProjects/MaximoCabs`) is a quote-only Astro marketing site. It fixes the vocabulary: two 1x12 closed-back ported models, default 20 x 18 x 11 in external, floating 3/4 in birch baffle with felt isolation. Tolex line: 13-ply Baltic birch, finger joints, recessed metal jack plate. Hardwood line: resawn walnut, cherry, hard maple, or sapele, book-matched panels, through-tenon corner posts glued and pinned, recessed brass jack plate. Four tolex colors, four grill cloths, seven named speakers plus customer-supplied. Source files: `src/content/cabinets/*.md`, `src/lib/quote-schema.ts`, `src/components/QuoteForm.astro`.
- The site advertises volume, port, and baffle designed around the rig, but neither repo holds any acoustic math, speaker data, bracing rules, or cut lists. Everything acoustic is net new.
- The vault's `/furniture` skill (`skills/furniture/SKILL.md`) supplies the workflow to fork: build123d backend, brief with load-bearing questions only, plan with joinery declared before modeling, one growing parametric file with a `PARTS` registry, per-feature renders, asserts as tests, buildability table, `scripts/cutlist.py` for the cut list, retrospective and memory afterward.
- The furniture skill description currently claims the trigger word "cabinet". Both existing skill descriptions get a one-line carve-out sending guitar speaker cabinets to `/speaker-cab`.

## Architecture

Three units with written interfaces. Each can be built and tested alone.

| Unit | Does | Consumes | Produces |
|---|---|---|---|
| Knowledge base and acoustics engine | Holds construction and voicing rules and the speaker catalog. Computes enclosure alignments. | Speaker note frontmatter, tone target, constraints | `voicing.json`, `voicing.md` |
| Parametric cabinet generator | Builds the cabinet solid and parts from parameters. | `voicing.json`, aesthetics block | `PARTS` registry, `cab.step`, renders, cut list via `scripts/cutlist.py` |
| `/speaker-cab` skill | Runs the order end to end with the operator (Brian). | Quote email or interview | `brief.md`, `voicing.md`, `proposal.md`, retrospective |

Data flows one way: intake to tone target to voicing to geometry to deliverables. Listening notes flow back into speaker notes after the build.

## Unit 1a: Intake

**Source.** Brian is the operator. A design starts from a pasted MaximoCabs quote email or a conversation with the customer. The skill creates `projects/Cab-<Customer>-<NxS>-<line>/` (example `Cab-Smith-1x12-tolex`) and writes `brief.md` from the intake template. It fills what the email gives, asks only load-bearing follow-ups in one batch, and states assumptions for everything else.

**Intake template, Rig block.** Every field is present in the template even when empty, so a missing answer is visible.

- **Order**: customer, contact, line (tolex or hardwood), driver count (1 or 2), back type (closed-ported, open, semi-open, or recommend).
- **Amps**: one entry per amp: model, rated power in W, impedance taps in ohms, head or combo, and which amp is primary. Amp type (tube, solid state, modeling) is derived from the model and asked only when the model is unknown. The voicing serves the primary amp and is checked for compatibility with the others. The skill assigns a voicing family from [[speaker-cab-voicing]] (blackface Fender, tweed Fender, Marshall, Vox, modern high gain, boutique clean, modeling).
- **Guitars**: pickup type and output (single coil, P90, humbucker, active), and low-end shifters (baritone, 7-string, drop tunings, bass VI).
- **Pedals**: dirt (fuzz, overdrive, distortion, and which models), boosts and EQ, and whether the amp is a pedal platform or the drive source. Nothing else is asked.
- **Music and use**: genre, approach (clean, edge of breakup, high gain), typical venue, typical volume, mic'd or filling the room by itself, and placement (on the floor, raised, or tilted back).
- **Tonal goals**: customer's own words, reference records or players, cabs they love or dislike.
- **Physical**: weight limit, size limits (including the vehicle it travels in), dimensions to match (head width and depth for a stack base, existing cabs it stacks with), and where it lives (climate, hardwood line only, feeds the wood-movement check).
- **Connections**: jack configuration: mono, mono with a parallel out, or stereo (2x12 only, one driver per chamber).
- **Aesthetics**: wood species or tolex color, grill cloth, piping, corners, handle type, jack plate, logo.
- **Speaker**: chosen from the catalog with an impedance preference (8 or 16 ohm), customer supplied (datasheet link if available, impedance stated), or recommend.

**Site note.** Guitars, pedals, jack configuration, and placement are not on the site's quote form. The skill's retrospective template has a line to record site-form gaps. Changing the site is out of scope.

## Unit 1b: Voicing engine

### Layer 1: judgment (skill plus knowledge notes)

From the Rig block the skill writes a **tone target** into `brief.md` and into `voicing.json`:

```json
{
  "tone_target": {
    "low_end": "tight | balanced | big",
    "mids": "scooped | neutral | forward",
    "top": "chimey | smooth | dark",
    "breakup": "early | moderate | clean",
    "dispersion": "focused | wide",
    "placement": "floor | raised | tilted",
    "min_power_w": 0,
    "impedance_options_ohm": [4, 8, 16]
  }
}
```

Rules that produce it live in [[speaker-cab-voicing]]: amp family to tendencies, genre and approach to targets, pickups to adjustments, dirt pedals to breakup and low-end adjustments, venue and mic'd-or-not to dispersion, placement to the low end (on the floor shifts `low_end` one step toward tight because floor coupling adds low end, tilted counts as raised). The skill then ranks catalog speakers against the target using each speaker note's descriptors, chooses a back type, and writes one reason line per choice. Brian approves the voicing before any CAD. The approval is recorded in the "Decisions locked" block of `brief.md`.

**Power rule.** `min_power_w` is 1.5 times the highest rated amp power. Hard stop if total speaker handling is below the amp's rated power. Warning if below `min_power_w`. A target of `breakup: early` may accept the warning explicitly, and the acceptance is written into "Decisions locked".

### Layer 2: deterministic math, `scripts/cabvoice.py`

Importable module and CLI. All internal units SI (m, m3, Hz, ohm); reports in mm, liters, cubic feet, inches.

**Inputs**: speaker slug(s) resolved from `knowledge/speakers/`, driver count, enclosure type, tone target, external size limits, panel thickness, displacement of drivers, bracing, and port.

**Functions and formulas** (so the implementation is unambiguous):

- `load_speaker(slug)`: parses the note's YAML frontmatter, validates required fields and units, returns a driver record with `data_status`.
- `closed_box(driver, vb_net)`: alpha = Vas / Vb, Qtc = Qts * sqrt(1 + alpha), Fc = Fs * sqrt(1 + alpha), F3 and a response table from the second-order high-pass with Qtc, 20 Hz to 400 Hz in third-octave steps. `closed_box_for_qtc(driver, qtc)` inverts it.
- `ported_box(driver, vb_net, fb)`: Small's vented-box fourth-order transfer function with box loss QL = 7, reporting F3, peak height, and the same response table.
- `port_dims(vb_net, fb, diameter or slot w x h)`: Helmholtz, L = (c^2 * A) / (4 * pi^2 * Fb^2 * Vb) minus end correction 0.85 times the effective diameter (one flanged end, one free). Slot ports use the effective diameter of their area. Speed of sound c = 343 m/s.
- `port_air_speed(driver, fb, area)`: worst case v = Sd * Xmax * 2 * pi * Fb / A. Limit 17 m/s. Above the limit the script enlarges the port and re-solves the length.
- `open_back(baffle_w, baffle_h, depth, open_fraction, driver_center)`: path = depth plus the distance from the driver center to the nearest open edge of the back. f_cancel = c / (2 * path). Reports f_cancel and a 6 dB per octave roll-off below it relative to the closed response. Open fraction 0.40 of the back area for open-back and 0.25 for semi-open, split as two horizontal panels top and bottom, from [[speaker-cab-construction]].
- `wiring(drivers, taps, jack_config)`: mono gives series and parallel results for two drivers matched against the amp taps; mono with parallel out adds the second jack in parallel; stereo gives one driver per jack at the driver's own impedance. Warnings for unequal impedance or sensitivity greater than 2 dB apart. Also emits the jack plate wiring text.
- `alignment_character(qtc or peak)`: closed: Qtc below 0.6 lean, 0.6 to 0.8 tight, 0.8 to 1.0 balanced, 1.0 to 1.2 big, above 1.2 peaky. Ported: peak height below 1 dB flat, 1 to 3 dB punchy, above 3 dB boomy. These words are the bridge back to the tone target.
- Two drivers share one chamber unless the jack configuration is stereo. Stereo splits the box with a divider into two equal chambers, one driver each, and each chamber is voiced as a 1x12 with its own port when ported. Per-driver Vb is total net volume divided by two in both cases.
- Net volume = gross internal volume minus driver displacement (from the speaker note, default 1.5 L with `estimated` flag), minus brace volume (from CAD), minus port volume.

**Modes.**

- `propose`: tone target plus constraints to a recommended net volume, port, and internal dimensions. Internal dimensions default to the site box proportions (external 20 x 18 x 11 in) scaled to volume, respecting a pinned width when a head must be matched and a minimum width of two cutouts plus margins for a 2x12. Advisory: no two internal dimensions within 5 percent of each other or of an integer ratio.
- `evaluate`: given dimensions and port, the predicted behavior. The site's default box with each catalog speaker is the first evaluation set and is stored in [[speaker-cab-voicing]] as a calibration table.

**Output `voicing.json`** (consumed by the generator) holds: tone target, chosen speakers and wiring, enclosure type, net and gross volume targets, internal dimensions, port geometry and location, predicted F3 or f_cancel, alignment character, power and impedance results, warnings, and `prediction_status: "unverified, ears only"`. `voicing.md` renders the same content as a sheet for Brian with a short plain-language reading of the numbers.

### Speaker catalog, `knowledge/speakers/<slug>.md`

One note per speaker. Frontmatter is the machine-readable record:

```yaml
name: celestion-vintage-30
type: speaker
brand: Celestion
model: Vintage 30
diameter_in: 12
impedance_ohm: [8, 16]
power_w: 60
sensitivity_db: 100
magnet: ceramic
fs_hz: 75
qts: 0.0
qes: 0.0
qms: 0.0
vas_l: 0.0
xmax_mm: 0.0
sd_cm2: 0.0
re_ohm: 0.0
le_mh: 0.0
cutout_mm: 283
bolt_circle_mm: 295
bolt_count: 4
depth_mm: 0
weight_kg: 0.0
displacement_l: 1.5
data_status: datasheet | third-party | analog | estimated | missing
sources: [https://...]
status: unverified-starting-values
```

Body sections: Character (tone descriptors in the tone-target vocabulary), Best with (amp families, genres), Field notes (listening notes appended after builds, dated). Amendment 2026-09-09 (planning research): Celestion publishes no Thiele-Small data beyond Fs and Re, so `third-party` (an independent measurement) and `analog` (scaled from a measured relative, with `analog_of`) were added to the status values; the seed list gained the Heritage G12H(55) as the measured analog source. Zero values above are placeholders only in this spec. In the vault every value comes from a datasheet URL or is marked `estimated` with the reasoning.

**Seed list.** Site speakers: Celestion G12H-30 Anniversary (the site's "G12H Greenback", confirm with Brian), Celestion Vintage 30, Eminence Cannabis Rex, WGS Veteran 30, Celestion Blue, Celestion Gold, Eminence Tonker. Alternatives: Celestion G12M-25 Greenback, G12M-65 Creamback, G12H-75 Creamback, Celestion Cream, Celestion G12-65 Heritage, Jensen P12N, Jensen C12N, Eminence Swamp Thang, Eminence Texas Heat, Eminence Red White and Blues, WGS ET65, WGS Green Beret. Customer-supplied speakers get a new note from their datasheet.

## Unit 2: Parametric cabinet generator

**Shape.** Shared library `scripts/cabmodel.py` (build123d). Each order has a thin `projects/Cab-<...>/cab.py` that sets parameters from `voicing.json` and the aesthetics block, calls the library, fills the `PARTS` registry (`name`, `solid`, `qty`, `material`, `notes`), runs asserts, and calls `scripts/cutlist.py`. Same env gates as furniture: `TMP_STL`, `EXPORT`, `SHOW`.

**Parameters.** External W, H, D; panel thickness; line; driver count, cutout diameter, bolt circle and count (from the speaker note); back type; port (shape round or slot, location rear or front, dimensions); grill frame inset; jack configuration, jack plate cutouts and positions; handle type and position; corner hardware allowance; feet or tilt-back legs; bracing; chamber divider; open-back panel heights.

**Construction defaults** (starting values, held in [[speaker-cab-construction]] with `status: unverified-starting-values`, corrected by Brian):

- **Tolex line**: 18 mm Baltic birch shell (top, bottom, two sides) with finger joints at all four shell corners. Fingers are modeled in CAD so the assembly render and STEP are truthful. Cut list parts stay rectangular blanks with a finger machining note. Default finger width 18 mm.
- **Hardwood line**: four corner posts 38 x 38 mm with the side, top, and bottom panels (19 mm resawn) tenoned through the posts, glued and pinned. Panels declared book-matched with show face and grain direction in the plan phase.
- **Both**: floating 18 mm birch baffle on 18 x 18 mm cleats with felt isolation strips, set back 20 mm from the front edge. Separate grill frame from 18 x 40 mm strips, cloth wrapped, retained with hook and loop to the baffle. Closed back: 12 mm birch back panel screwed to cleats, removable, with the port and jack plate in it when rear-ported. Open back: two horizontal 12 mm panels top and bottom sized from the open fraction, jack plate in the lower panel. Front slot port: the baffle stops short of the bottom panel, leaving a full-width slot whose depth is set by a shelf behind it, so port length equals shelf depth. Rear round port: a flanged tube through the back panel. Recessed jack plate. Center vertical brace 18 x 60 mm between top and bottom on every mono 2x12. Stereo 2x12: a full-height, full-depth 18 mm divider replaces the brace, with one jack plate and, when ported, one port per chamber. Mono with parallel out: one plate carrying two jacks wired in parallel. Tilt-back legs on the tolex line when placement is tilted. Handle: top center strap on the tolex line, recessed side handles on the hardwood line, in both cases positioned over the loaded center of mass.
- **Tolex wrap**: not a part. The cut list gains a tolex yardage line computed from the external surface area plus 15 percent, on the 54 in or 32 in roll width from the site's material list.

**Derived quantities.** Weight from part volumes times material density (birch ply 680 kg/m3, species densities in the construction note) plus speaker weight plus 1 kg hardware. Center of mass from the same masses with the speaker at the baffle. Head match: external width equals the head width plus 0 to 10 mm.

**Renders.** `scripts/render_stl.py` four views plus an exploded view. No photoreal finishes. The proposal uses the swatch images from the MaximoCabs repo (`public/materials/`), copied into the order's `images/`.

**Verification.** The library reproduces the site's default 20 x 18 x 11 in 1x12 closed-back within 1 mm on every external dimension. Asserts per order: net internal volume within 5 percent of the voicing target, no interference between port, magnet, brace, and back, magnet depth to back panel clearance at least 25 mm, cutout diameter equals the speaker note, handle within 15 mm of the center of mass on the width axis, expected part count, every part's bounding box within stock limits, and for stereo the two chamber volumes equal within 1 percent.

## Unit 3: The `/speaker-cab` skill

`skills/speaker-cab/SKILL.md`, symlinked to `~/.claude/skills/speaker-cab`. Description names the triggers (guitar speaker cabinet, guitar cab, 1x12, 2x12, extension cab, voicing a cab, MaximoCabs order) and sends other woodworking to `/furniture`. The furniture and 3d-model descriptions each gain one sentence sending guitar speaker cabinets here. Backend rule unchanged: build123d by default, FreeCAD only for the same escalation cases as furniture.

**Phases.**

1. **Intake**: Unit 1a. Ends with the Rig block filled and assumptions stated.
2. **Voicing**: Unit 1b. Ends with the tone target, ranked speakers with reasons, back type, `voicing.json`, `voicing.md`, and Brian's approval in "Decisions locked". No CAD before this approval.
3. **Plan**: ordered part list, joinery per connection, grain and show faces, hardware positions, port location.
4. **Build loop**: `cab.py`, per-feature render viewed as PNG, asserts, identical to the furniture loop.
5. **Buildability and acoustic check**: the furniture table's seven rows (stock thickness, rectangularity, grain and show face, joinery fit, stock yield with 3 mm kerf, wood movement, transport) plus: net volume within 5 percent, port clearance, magnet to back clearance, handle over center of mass, impedance and power versus amp, weight versus customer limit, head width match, port air speed, internal dimension ratio advisory, and for stereo equal chambers and per-chamber port clearance. Each row gets a verdict line.
6. **Export**: `cutlist.md` and `cutlist.csv` (with the tolex yardage line), `cab.step`, `images/` renders, `voicing.md`, `proposal.md`.
7. **Handoff**: `brief.md` updated with paths and locked decisions, `.claude/context-check/last-handoff.md` written, git commit and push.
8. **After the build**: retrospective in `knowledge/learnings/cab-<customer>-<config>.md` using the listening-notes template. The notes are appended, dated, to the Field notes section of the speaker's note. Any corrected construction default is promoted into [[speaker-cab-construction]]. Memory updated when a rule changes.

**Listening-notes template**: amp and settings, guitar, pedals in use, volume level, room, then low end (tight, balanced, big, boomy), mids, top, breakup onset, dispersion, the customer's words, Brian's words, and whether the prediction held (agree, partly, disagree) with a one-line reason.

**Customer proposal, `proposal.md`**, written in the MaximoCabs voice from the site's homepage copy:

1. Your rig and goals, restated in the customer's words.
2. The recommended cabinet: line, driver count, back type, speaker and why, external dimensions in inches and mm, estimated weight, impedance and wiring.
3. What it is designed to do, in plain language. "Designed for" wording only, never measured claims.
4. Alternatives considered and why not, one line each.
5. Finishes: chosen wood or tolex, grill cloth, hardware, with swatch images.
6. Lead time from the site's range for the line. Price left as a line for Brian to fill. No pricing logic exists.

## Knowledge base

- `knowledge/speaker-cab-construction.md`: materials and thicknesses, species densities, joinery per line, baffle and cleats, bracing, driver cutouts, grill frame, back panels and open fraction, port construction, jack plate, handles, corners, feet, tolex wrap and seam rules, weight and center of mass method.
- `knowledge/speaker-cab-voicing.md`: tone target vocabulary, enclosure type rules (closed, ported, open, semi-open), amp family table, genre and approach table, pickup adjustments, dirt pedal adjustments, venue and mic'd rules, placement rule, jack configuration and stereo rule, power and impedance rules with the safety factor, alignment character thresholds, the calibration table of the site's default box with each seed speaker.
- `knowledge/speakers/<slug>.md`: the catalog above.

All three start with `status: unverified-starting-values`, the same convention as [[woodworking-stock]]. Every number carries a source URL. Datasheets are gathered by web research during implementation. Where a source is missing, the value is marked `estimated` with the reasoning, and the script's output carries the flag forward.

## Testing

- `scripts/tests/test_cabvoice.py`: closed-box Vb for Qtc 0.707 against Vb = Vas / ((Qtc / Qts)^2 - 1); Helmholtz port length against a hand-computed case; ported alignment against Eminence's published cabinet recommendations for two seed speakers where they exist, otherwise against a hand-computed reference case, within 10 percent on volume and tuning; port air speed and enlargement; open-back cancellation frequency; wiring and impedance cases for mono, parallel out, and stereo including mismatches; stereo chamber split; frontmatter schema validation for every note in `knowledge/speakers/`.
- Generator: the asserts above, run via `cab.py`, plus a fixture order that reproduces the site default.
- Skill: dry run on the sample intake from the site's tests (roots and alt-country, low-volume gigs, small clubs, tight low end and rolled highs, Celestion G12H 16 ohm) ending with every deliverable file present and the check table filled.

## Error handling

- Missing T/S fields: the script degrades to the rules-of-thumb volume table in [[speaker-cab-voicing]] and labels every derived number `rule-of-thumb`.
- Customer-supplied speaker with no datasheet: nearest catalog analog by size, magnet, and power, with a warning in the voicing sheet and the proposal.
- Impossible impedance combination, handling below the amp's rated power, or a target volume that cannot fit the size limit: the skill stops and presents the trade-off (smaller box raises Qtc toward big or peaky, different speaker, different wiring) for Brian to decide. The decision is recorded in "Decisions locked".
- Two identical build123d failures escalate to FreeCAD per the furniture rule.

## File layout

```
skills/speaker-cab/SKILL.md
scripts/cabvoice.py
scripts/cabmodel.py
scripts/tests/test_cabvoice.py
knowledge/speaker-cab-construction.md
knowledge/speaker-cab-voicing.md
knowledge/speakers/<slug>.md
projects/Speaker-cab-system/           (this design, the plan, fixtures)
projects/Cab-<Customer>-<NxS>-<line>/  (per order: brief.md, voicing.json, voicing.md, cab.py, cab.step, cutlist.md, cutlist.csv, proposal.md, images/)
knowledge/learnings/cab-<customer>-<config>.md
```

## Build order

1. **Knowledge base and engine**: construction note, voicing note, seed speaker notes with sources, `cabvoice.py` with tests, calibration table.
2. **Generator**: `cabmodel.py`, site-default reproduction, 2x12 and brace, open-back panels, hardwood line, tolex yardage, renders and exploded view.
3. **Skill**: SKILL.md, carve-outs and symlink, intake template, voicing sheet template, proposal template, listening-notes template, dry run, retrospective, memory.

## Assumptions to confirm during implementation

- The site's "G12H Greenback" is the Celestion G12H-30 Anniversary.
- Construction defaults above match Brian's actual practice. They are starting values and the construction note is where corrections land.
- Project directories may carry the customer's surname. Brian can substitute a code.
- Web research for datasheets is allowed during implementation.

## Out of scope

Pricing, site configurator or any change to the MaximoCabs site, photoreal renders, 4x12 and 1x10 cabinets, combos, isolation and bass cabinets, measurement-based validation, port and enclosure optimization beyond the alignments listed.
