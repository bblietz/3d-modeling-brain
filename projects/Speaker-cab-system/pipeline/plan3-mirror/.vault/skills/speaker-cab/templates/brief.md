---
name: <cab-customer-nxs-line>
description: MaximoCabs order brief for <Customer>, a <NxS> <line> cabinet, <back type>, <speaker>
type: order
status: intake | voicing-approved | built | proposed | delivered
created: <YYYY-MM-DD>
customer: <Customer>
line: tolex | hardwood
configuration: 1x12 | 2x12-mono | 2x12-parallel-out | 2x12-stereo
tags: [order, speaker-cab, maximocabs]
---

# Order: <Customer>, <NxS> <line>

Source: <pasted quote email dated YYYY-MM-DD | interview on YYYY-MM-DD>.
Design rules: [[speaker-cab-voicing]], [[speaker-cab-construction]].

## Order

- Customer: <name>
- Contact: <email, phone>
- Line: <tolex | hardwood>
- Driver count: <1 | 2>
- Back type asked: <closed-ported | open | semi-open | recommend>

## Rig block

Every field stays in this list even when empty; an empty value means the customer was not asked or did not say.

- **Amps** (one line per amp; the primary amp is the one the voicing serves)
  - <model>: rated <W> W, taps <ohm list>, <head | combo>, primary: <yes | no>, type <tube | solid state | modeling> (derived from the model), family <blackface Fender | tweed Fender | Marshall | Vox | modern high gain | boutique clean | modeling>
- **Guitars**
  - Pickups and output: <single coil | P90 | humbucker | active>
  - Low-end shifters: <none | baritone | 7-string | drop tunings | bass VI>
- **Pedals**
  - Dirt: <fuzz | overdrive | distortion, models>
  - Boosts and EQ: <>
  - Drive source: <pedal platform | amp drive>
- **Music and use**
  - Genre: <customer's words> (canonical key: <roots-country | blues | classic-rock | indie-alternative | jazz | metal-high-gain | worship-pop | funk-rnb | none>)
  - Approach: <clean | edge of breakup | high gain>
  - Typical venue: <>
  - Typical volume: <>
  - Mic'd or filling the room: <mic'd | room>
  - Placement: <floor | raised | tilted>
- **Tonal goals**
  - Customer's words: <verbatim>
  - Reference records or players: <>
  - Cabs loved: <> / disliked: <>
- **Physical**
  - Weight limit: <kg / lb | none>
  - Size limits: <W x H x D | none> (vehicle: <>)
  - Dimensions to match: <head width and depth | existing cabs | none>
  - Where it lives (hardwood line, wood movement): <climate, heated or not>
- **Connections**
  - Jack configuration: <mono | mono with parallel out | stereo (2x12 only)>
- **Aesthetics**
  - Wood species or tolex color: <>
  - Grill cloth: <>
  - Piping: <yes | no>; corners: <black | chrome | none>; handle: <strap | recessed side>; jack plate: <recessed | flush>; logo: <>
- **Speaker**
  - <catalog slug at <8 | 16> ohm | customer supplied: <model, impedance, datasheet link> | recommend>

## Assumptions stated

- <one line per assumption, with the reason>

## Follow-ups asked

- <one line per load-bearing question, with the answer and date; "none" when the batch was empty>

## Tone target

| Field | Value | Reason |
|---|---|---|
| low_end | <tight / balanced / big> | <> |
| mids | <scooped / neutral / forward> | <> |
| top | <chimey / smooth / dark> | <> |
| breakup | <early / moderate / clean> | <> |
| dispersion | <focused / wide> | <> |
| placement | <floor / raised / tilted> | <> |
| min_power_w | <1.5 x the highest rated amp> | <amp, rated W> |
| impedance_options_ohm | <taps> | <primary amp's taps> |

Written to `tone.json` on <date>.

## Speaker ranking

| Candidate | Points | Matched keys | Data status | Reason |
|---|---|---|---|---|
| <slug> | <n> | <low_end, mids, family, genre ...> | <datasheet / third-party / analog / estimated / missing> | <one line> |
| <slug> | <n> | <> | <> | <> |
| <slug> | <n> | <> | <> | <> |

Chosen: <slug> at <ohm> ohm. <one line why; "fixed by the customer" when chosen or supplied>

## Back type

<closed-ported | closed | open | semi-open>: <reason from the choice rule; note the precedence used when rules conflicted>

## Voicing decision

- Mode: <evaluate on the site box | propose>
- Engine command (verbatim):

  ```bash
  <the exact cabvoice.py command that produced voicing.json>
  ```

- Reading: <plain-language reading of voicing.md for this player: alignment character, F3 or cancellation frequency, wiring, power result, each warning; every number unverified, ears only>
- Approved by Brian on <date>: <yes | redirected: what changed>

## Plan

- Parts in build order: <>
- Joinery per connection: <finger | dovetail; baffle floating | fixed; divider>
- Grain and show faces (hardwood): <>
- Hardware positions: <jack plate(s), handle, corners, feet or tilt-back legs, piping>
- Port location: <rear round | front slot>
- Aesthetics block written into `cab.py` on <date>

## Trade-offs presented

- <date>: <blocker or warning> presented with <options shown>; Brian chose <choice>; command re-run: <verbatim>

## Decisions locked

- <date>: voicing approved (<speaker>, <back type>, <mode>)
- <date>: <each trade-off choice, each accepted warning>

## Artifacts

- `projects/<Cab-...>/tone.json`, `voicing.json`, `voicing.md`
- `projects/<Cab-...>/cab.py`, `cab.json`, `cab.step` (regenerated, not committed)
- `projects/<Cab-...>/checks.md`, `cutlist.md`, `cutlist.csv`
- `projects/<Cab-...>/proposal.md`, `images/`
- Retrospective: `knowledge/learnings/cab-<customer>-<config>.md` (after the build)

## Site-form gaps

- <what this intake needed that the quote form does not ask; "none" if nothing>

## Outcome

- <date>: <proposal sent | built | delivered; price line filled by Brian; what changed after stop two>
