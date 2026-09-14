---
name: cab-blietz-1x12-hardwood
description: MaximoCabs order brief for Cecilia Blietz, a 1x12 hardwood cabinet in walnut, open back, Eminence Cannabis Rex 8 ohm
type: order
status: built
created: 2026-09-13
customer: Cecilia Blietz
line: hardwood
configuration: 1x12
tags: [order, speaker-cab, maximocabs]
---

# Order: Cecilia Blietz, 1x12 hardwood

Source: pasted quote email dated 2026-09-13, the first quote the live site wizard sent (production went live that day). The email matched the Phase 1 format: the first line carries name, email, and phone, then the ten blocks in the brief's order, one row per field.
Design rules: [[speaker-cab-voicing]], [[speaker-cab-construction]].

## Order

- Customer: Cecilia Blietz
- Contact: andradem74@gmail.com, 415 407 5201
- Line: hardwood
- Driver count: 1
- Back type asked: open (the wizard's "Open-back"; the back-type rule and stop one decide, see Assumptions stated)

## Rig block

Every field stays in this list even when empty; an empty value means the customer was not asked or did not say.

- **Amps** (one line per amp; the primary amp is the one the voicing serves)
  - Dr. Z MAZ 38 (the customer's "Dr Z Max 38 Sr Studio Lead", read as the MAZ 38 Sr. or its forerunner the MAZ 38 Studio Lead): rated 38 W, taps [4, 8, 16] (separate 4, 8, and 16 ohm jacks on the MAZ 38 Sr., one output at a time, no extension jack; the Studio Lead's jacks unverified), head or combo (not stated), primary: yes, type tube (four EL84, cathode biased, GZ34 rectifier; derived from the model), family boutique clean (the amp-family table names Dr Z)
- **Guitars**
  - Pickups and output: humbucker (the customer's "humbuckers")
  - Low-end shifters: none
- **Pedals**
  - Dirt: overdrive, two Tube Screamers (the customer's "tubescreamer (x2)")
  - Boosts and EQ: (not asked)
  - Drive source: pedal platform with a lightly driven amp (the customer's words: "The amp is slight overdrive, but can't be more due to volume. Most comes from the 2 tubescreamers")
- **Music and use**
  - Genre: "rock, funk, country" (canonical keys: classic-rock, funk-rnb, roots-country; "rock" is not a table row and maps to classic-rock, the nearest row, by ear)
  - Approach: edge of breakup
  - Typical venue: practice room
  - Typical volume: practice volume, "About 20% of amp volume"
  - Mic'd or filling the room: room (the customer's "Filling the room")
  - Placement: floor
- **Tonal goals**
  - Customer's words: "Crisp leads with milky high notes and noticable low end"
  - Reference records or players: (not asked)
  - Cabs loved: (not asked) / disliked: (not asked)
- **Physical**
  - Weight limit: (not asked)
  - Size limits: (not asked) (vehicle: not stated)
  - Dimensions to match: (not asked)
  - Where it lives (hardwood line, wood movement): home (climate and heating not stated)
- **Connections**
  - Jack configuration: mono ((not asked), which on a 1x12 means the field does not apply)
- **Aesthetics**
  - Wood species or tolex color: Walnut (the site's domestic black walnut, oil finish)
  - Grill cloth: Salt and Pepper, 32" (a site cloth, swatch on file)
  - Piping: no; corners: none; handle: (not asked); jack plate: (not asked); logo: (not asked)
- **Speaker**
  - recommend (the customer's "Recommend one for me")

## Assumptions stated

- Amp model: "Dr Z Max 38 Sr Studio Lead" is a Dr. Z MAZ 38. Dr. Z never sold a model officially named Studio Lead; owners use the name for the MAZ 38 Sr.'s forerunner, which has a Presence knob where the Sr. has Cut. Either way it is 38 W from four cathode-biased EL84s with a GZ34 rectifier and no negative feedback. The model is known, so no power or tap follow-up was asked. Sources: https://drzamps.com/product/maz38/, the MAZ 18/38 manual http://drzamps.com/wp-content/uploads/2016/12/Maz-18-38-12-1-2016.pdf, https://ztalk.proboards.com/thread/78200/studio-lead.
- Taps and impedance: [4, 8, 16] from the MAZ 38 Sr. manual (separate jacks). The Studio Lead's jacks are unverified, so the order voices the 8 ohm variant of the chosen speaker, which every MAZ 38 version has a tap for; the unverified jacks cannot cause a mismatch.
- Load: the MAZ 38 has no extension jack and Dr. Z says to use one output at a time, so this cabinet is the amp's only load, whether the amp is a head or a combo with its own speaker unplugged. No combined parallel load applies.
- Power: rated 38 W at full power (the Mk.II's 18 W half-power setting is not assumed), so `min_power_w` is 57 W. The practice volume allows early breakup and low-power speakers under the venue rule, but the engine still stops under 38 W of handling and warns under 57 W.
- Amp tone: Dr. Z describes the MAZ 38 as "mid 60s blackface" with "UK flavored chime" and more "low end push" than the MAZ 18; owners call its top trebly; Dr. Z calls it a pedal platform. These feed the tone target's reason lines, not its values; the family row is boutique clean.
- Three genres: the note has no rule for several genres. The intake reads each tone field from the three rows (classic-rock, funk-rnb, roots-country) by the value two of the three share, with the first-listed genre (rock) breaking a three-way split; the ranking's genre point counts once when a note lists any of the three keys. This reading is presented at stop one.
- Tonal words: none of "crisp", "milky", or "noticable" names a vocabulary value, so each only leans and becomes a reason line: "crisp leads" toward an articulate top, "milky high notes" toward smooth, "noticable low end" away from tight.
- Filling the room: an unmic'd practice room the cab fills by itself is read like the venue rule's unmic'd small club, so dispersion reads wide.
- Placement on the floor shifts low_end one step toward tight (boundary gain).
- Back type asked: open-back is recorded as the customer's ask. The note's choice rule sets the back type from the tone target; where the rule and the ask disagree, both go to stop one.
- Boosts and EQ (not asked): none assumed; boosts and EQ do not change the target either way.
- Drive source: most of the drive comes from the two Tube Screamers into an amp just past clean at practice volume, a pedal platform with a lightly driven amp; the edge-of-breakup approach already sets breakup moderate.
- References and cabs loved or disliked (not asked): no ranking adjustment.
- Weight, size, and dimensions to match (not asked): none, so the order is standard size and the site box is evaluated first; no head width is pinned.
- Where it lives: "home", assumed a heated indoor house; the hardwood wood-movement rule applies with the construction note's defaults.
- Jack configuration (not asked): does not apply on a 1x12; mono.
- Aesthetics (not asked): handle a leather strap and jack plate recessed, the hardwood page's defaults; no logo assumed, Brian's call at stop two. Piping no and corners none as asked, which match the page's "typically omitted" for hardwood.
- Customer: Cecilia Blietz shares Brian's surname; treated as a real order, with the surname in the directory name.

## Follow-ups asked

- none (the batch was empty on 2026-09-13: the model is known as a 38 W MAZ 38, an 8 ohm driver matches every version's taps, no limit was named, the jack is mono on a 1x12, and no speaker is supplied). Optional and not blocking, for Brian's next note to the customer: head or combo, and whether the front panel reads Presence or Cut (Studio Lead or Sr.).

## Tone target

| Field | Value | Reason |
|---|---|---|
| low_end | balanced | the rule reading is tight (the funk-rnb and roots-country rows read tight, the classic-rock row balanced, and the floor shifts one step toward tight); her "noticable low end" is read as not tight, a departure from the note's lean rule that Brian approved with the open back at stop one; an open back's low end is set by its panels, and balanced takes open panels |
| mids | scooped | two of the three rows read neutral (funk-rnb, roots-country); humbuckers push one step toward scooped; the two Tube Screamers bring their own mid hump (overdrive is neutral in the note) |
| top | smooth | the classic-rock and roots-country rows read smooth; "milky high notes" leans smooth and "crisp leads" toward an articulate top; the MAZ 38's trebly EL84 chime argues against chimey, which humbuckers allow but do not set |
| breakup | moderate | edge of breakup sets moderate (the approach override); the classic-rock and roots-country rows agree |
| dispersion | wide | "Filling the room" unmic'd in a practice room, read like the venue rule's unmic'd small club; her open-back ask agrees (two of the three genre rows read focused, for stage use) |
| placement | floor | the customer's answer |
| min_power_w | 57 | 1.5 x 38 W, the Dr. Z MAZ 38, the only amp |
| impedance_options_ohm | [4, 8, 16] | the MAZ 38 Sr.'s three output jacks; the Studio Lead's jacks are unverified, and the 8 ohm driver matches every version |

Written to `tone.json` on 2026-09-13. Stop one's other targets ran from scratch tone files outside the order directory: tight (the rule reading, closed-ported) and big (semi-open, the recommendation).

## Speaker ranking

Hard filters: the power rule drops every speaker handling under the amp's 38 W rating (Celestion Blue 15 W, G12H Anniversary 30 W, G12M-25 Greenback 25 W, Heritage G12H(55) 30 W, WGS Green Beret 25 W); every remaining note offers 8 ohm. Scored 2 per matching character word (balanced, scooped, smooth, moderate; no catalog note reads scooped, so no speaker scores on mids), 1 for the boutique clean row of the amp-family table (Celestion Gold, Cream, Cannabis Rex, Vintage 30), 1 when the note's Genres line holds any of classic-rock, funk-rnb, roots-country; no loved or disliked cab.

| Candidate | Points | Matched keys | Data status | Reason |
|---|---|---|---|---|
| eminence-cannabis-rex | 8 | low_end, top, breakup, family, genre | datasheet | the boutique clean row's datasheet speaker: balanced low end, neutral mids under two Tube Screamers, a smooth top for "milky high notes" on a trebly EL84 amp; its note says closed or open back both suit it (Qts 0.64); 50 W, a power warning |
| celestion-g12m-65-creamback | 7 | low_end, top, breakup, genre | missing | the same balanced, smooth, moderate words with forward mids and 65 W headroom, but no family point and no Thiele-Small data |
| celestion-vintage-30 | 6 | low_end, top, family, genre | analog | boutique clean row and 60 W, but clean breakup and forward mids on paper, a harder voice for edge-of-breakup humbucker leads |

Next at 5: celestion-g12-65-heritage (missing), celestion-gold (missing), eminence-texas-heat (datasheet), jensen-c12n (datasheet), jensen-p12n (datasheet), wgs-et65 (estimated), wgs-veteran-30 (estimated). The Cannabis Rex also ranked second under the rule reading's tight target (the G12-65 Heritage, no Thiele-Small data, first at 7) and first under the semi-open big target.

Chosen: eminence-cannabis-rex at 8 ohm. Top of the ranking with the best data; the 8 ohm variant matches a tap on every MAZ 38 version.

## Back type

open: the customer asked for an open back, and with dispersion wide and low_end balanced the choice rule leads to open or semi-open, balanced taking open panels. Precedence: the rule reading's tight low end would beat wide dispersion and take closed-ported; Brian chose the open back as asked at stop one (see Trade-offs presented). The Cannabis Rex's Qts 0.64 sits under the 0.9 threshold, so the driver adds no preference; no low-end shifter.

## Voicing decision

- Mode: evaluate on the site box (an open back is accepted on the site box whenever the rules choose open; no size limit, pinned width, or second driver)
- Engine command (verbatim), exit 0, no blockers:

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py evaluate --speaker eminence-cannabis-rex --impedance 8 \
    --enclosure open --tone projects/Cab-Blietz-1x12-hardwood/tone.json --line hardwood --species walnut \
    --internal 472 421.2 229.4 --name Cab-Blietz-1x12-hardwood --out projects/Cab-Blietz-1x12-hardwood/
  ```

- Reading: the site box, 42.6 L net (45.6 L gross; 42.3 L at approval, before hardwood shells dropped their stiffeners), internal 472 x 421 x 229 mm, external 508 x 457 x 279 mm (20.0 x 18.0 x 11.0 in), walnut walls voiced at 18 mm. The back is open: two panels, top and bottom, each 126 mm tall, leaving about 168 mm open across the middle (40 percent). The engine's estimate puts the front-to-back cancellation at 369 Hz: below it the back wave thins the low end at 6 dB per octave against a closed box, about 3 dB down at 254 Hz, 9 dB at 127 Hz, and 13 dB at 80 Hz. For Cecilia that is an airy, wide sound that fills the practice room at low volume and suits an EL84 amp at edge of breakup; the low end is lighter than any closed box would give, and the floor's boundary gain and a nearby wall give some of it back, so her "noticable low end" rests on the Cannabis Rex's balanced low end, the floor, and the room. The open-back figure is a path-length estimate that ranks options, not a response curve. Wiring: a single 8 ohm driver on the amp's 8 ohm jack, the only output in use (the MAZ 38 takes one output at a time). Power: the Cannabis Rex's 50 W clears the amp's 38 W rating and sits under the 57 W target, a warning, accepted: edge of breakup at about 20 percent volume at home will not push 38 W into this cabinet. Advisory: width to depth 2.06:1, within 5 percent of 2:1 (coincident standing waves), the site box's own advisory. Every number here is unverified, ears only.
- Stop one presented four options (see Trade-offs presented): semi-open (recommended), the open back as asked, closed-ported with the site port, and the strict rule reading.
- Approved by Brian on 2026-09-13: redirected from the recommended semi-open to the open back the customer asked for (balanced target, two 126 mm panels)

## Plan

- Parts in build order: shell (top, bottom, two sides, 19 mm resawn walnut, finger-jointed at the four front-to-back corners, a 1/2 in (12.7 mm) roundover on every outside edge routed after glue-up); baffle (18 mm Baltic birch, floating, front face 20 mm behind the front edge, the Cannabis Rex's 281 mm cutout with 8 bolts on a 294.4 mm circle, T-nuts from the back); baffle cleats (18 x 18 mm birch, felt strip, screws); no brace or divider (1x12, mono); no stiffeners (hardwood shell panels take none, Brian's rule of 2026-09-13; the first export carried two 18 x 40 x 193 mm birch stiffeners under the top and bottom); baffle cleats top and bottom only (18 x 18 mm, the open-back default; no side cleats, since there is no sealed volume to protect on an open back); back cleats (18 x 18 mm) for the two open-back panels; two open-back panels (12 mm birch, 126 mm tall, top and bottom, screwed to the cleats, about 168 mm open between them), the upper one carrying the jack plate (moved from the lower panel 2026-09-14); grill frame (12 x 40 mm birch strips, half-lap corners, Salt and Pepper cloth wrapped and stapled, hook-and-loop to the baffle); hardware (recessed brass jack plate, leather strap handle, four rubber feet). No port. The layout kernel produces the actual list; this is what Brian can object to first.
- Joinery per connection: finger joints at the four shell corners (9.5 mm fingers on 19 mm walnut, an odd count so both ends are full fingers, cut to measured thickness; through dovetails are the hardwood option, not chosen, the customer was not asked); the baffle floating on felt-isolated cleats; the open-back panels screwed to cleats; no divider. Cleats are glued and screwed full length like the tolex line's (Brian relaxed the hardwood glue rule on 2026-09-13: with the grain wrapping, the cleats run with the grain).
- Grain and show faces (hardwood): walnut (domestic black walnut, oil finish), resawn to thickness, show face out, grain wrapping around the box (left to right on the top and bottom, vertical on the sides, never front to back) so the finger corners are cut in end grain and all four panels move together along the depth axis (about 2.9 mm per 4-point moisture swing flatsawn); no book-matching, since book-matching runs along the side grain and these panels join at the corners in end grain (Brian, 2026-09-14); "home" is assumed a heated house.
- Hardware positions: one recessed brass jack plate at the bottom center of the upper open-back panel, 25 mm below the top cleat (moved from the lower panel 2026-09-14); the leather strap handle, arched between two brass end caps, centered on the top panel side to side and front to back (the center of mass stays within 15 mm on the width axis), screw pair 228.6 mm apart, 50 mm inside the edges; no corners; four 40 mm rubber feet inset 32 mm; no piping.
- Port location: none (open back)
- Aesthetics block written into `cab.py` on 2026-09-13: copied from `projects/Speaker-cab-system/fixtures/site-default/cab.py`; changed `corners` to "none", `tolex_color` to "" (the hardwood line takes its finish from the species in voicing.json), and `grill_cloth` to 'Salt and Pepper, 32"'; corner_joint finger, baffle_mount floating, handle strap, piping False, feet rubber, tolex_roll_in 54 (unused on hardwood), head_width_mm None already matched the intake; the module docstring reduced to one line naming the order, nothing below it changed. The handle's leather qualifier and the jack plate's recessed default (the form left both unasked) live in this brief only

## Trade-offs presented

- 2026-09-13: stop one, the rule reading (a tight low end beats wide dispersion, so closed-ported) against the customer's open-back ask and "noticable low end", presented with four options, each the Cannabis Rex 8 ohm in the site box unless noted, every run exit 0 with no blockers: semi-open, the recommendation (low_end big, two 158 mm panels, the same 369 Hz estimate as open, so its extra low end is builder lore); the open back as asked (low_end balanced, two 126 mm panels); closed-ported with the site port (punchy, Fb 67.8 Hz, F3 98.8 Hz, 1.9 dB peak, focused); and the strict rule reading (low_end tight, closed-ported: the site box's punchy misses tight's bridge word flat, so propose a smaller ported box; the top-ranked G12-65 Heritage has no Thiele-Small data, Fb 67.4 Hz, character unpredicted). Brian chose the open back as asked; command re-run: the evaluate command under Voicing decision.
- 2026-09-13: the first export's `spans` warn (top and bottom panel spans 470 mm over 450, a glued-flat 18 x 40 mm birch stiffener added under each) and the note's grain wording, which read both front to back and wrapping around the box, presented with: mount the stiffeners like cleats, leave them out, or keep grain front to back as generated. Brian ruled that hardwood grain never runs front to back (it wraps around the box) and that hardwood shell panels get no stiffeners on any order; the generator, check table, construction note, and skill were changed to match, and the evaluate and `cab.py` runs are repeated on the changed tools.
- 2026-09-13, at stop two: the hardwood cleat rule (screwed through slotted holes, glued at the center 100 mm only) and the fixed-baffle rule (glued in the front 100 mm of its dado only), both from the old front-to-back grain wording, presented as open now that the cleats and dados run with the wrapped grain; Brian chose to relax both. The tools, construction note, and skill were changed to match, and the export, check table, and verify re-run on the changed tools.
- 2026-09-13: `cabreport.py`'s swatch table was older than the site's Mojotone photos (7 of 14 entries pointed at missing files, and Salt and Pepper did not resolve), presented with fix now or skip for this order; Brian chose fix now.

## Decisions locked

- 2026-09-13: voicing approved (eminence-cannabis-rex at 8 ohm, open back, evaluate on the site box: 42.6 L net after the stiffener change (42.3 L at approval), 508 x 457 x 279 mm external, two 126 mm back panels, cancellation 369 Hz predicted); redirected at stop one from the recommended semi-open to the open back the customer asked for
- 2026-09-13: tone target low_end balanced instead of the rule reading's tight: her "noticable low end" read past the note's lean rule, approved with the open back
- 2026-09-13: the 8 ohm variant, so every MAZ 38 version's taps match (the Studio Lead's jacks are unverified)
- 2026-09-13: power warning accepted: handling 50 W under the 57 W target and above the amp's 38 W rating; no `--accept-low-headroom` (the flag is for an early-breakup target; this one is moderate)
- 2026-09-13: engine advisory accepted: width to depth 2.06:1, within 5 percent of 2:1, the site box's own advisory
- 2026-09-13: hardwood grain wraps around the box on all four shell panels, never front to back (Brian's rule, recorded in [[speaker-cab-construction]] and memory)
- 2026-09-13: no stiffeners on hardwood shell panels, on this and every hardwood order (Brian); the tools were changed rather than the shop omitting parts the CAD shows
- 2026-09-13: swatch table fixed in `cabreport.py` so the proposal shows the walnut and Salt and Pepper swatches (Brian)
- 2026-09-13: client share page (Brian: the matplotlib PNG renders are not fit to share): an interactive three.js model built from the order's own CAD parts in the MaximoCabs brand (bone, ink, oak, rust; Cormorant Garamond and Inter), with the walnut and Salt and Pepper photos as textures, the grain wrapping around the box, a Front, Three-quarter, and Open back viewpoint set, and a grill-off toggle; no price and no contact details on the page
- 2026-09-13: a 1/2 in (12.7 mm) roundover on every outside edge of the walnut shell (Brian, asked from the share page): set as `roundover_mm=12.7` in `cab.py`, a new generator aesthetics option that is off by default; the internal volume and voicing are unchanged
- 2026-09-13: the floating baffle's cleat edges become a modeled option (Brian: pick what sounds and builds best, not just the mechanical default). Open and semi-open cabs float on top and bottom cleats only (no sealed volume to protect, fewer parts, a freer-sitting baffle); closed and closed-ported cabs keep all four cleats, because the perimeter seal is what the Thiele-Small volume model assumes. Her cab is open-back, so it now resolves to top-and-bottom cleats by default and drops the two side cleats; a re-export follows.
- 2026-09-13: the strap handle is centered on the top panel side to side and front to back, on every strap-handle cab (Brian: it sat about 35 mm forward on the loaded center of mass); the cab hangs slightly nose-down when carried, and the width-axis handle check is unchanged
- 2026-09-13: the 1/2 in roundover becomes the default on every hardwood cab (Brian, after seeing it on this order); tolex keeps none, and `roundover_mm=0` gives sharp edges. This order's explicit 12.7 equals the default, so nothing here changes.
- 2026-09-13: the strap handle is drawn as a real leather strap arching between two end caps on the 228.6 mm screw spacing instead of a solid block (Brian: the block read as a stray strip of wood on the share page); the caps take the line's hardware finish, brass on hardwood
- 2026-09-13: hardwood glue rules relaxed (Brian): cleats glued and screwed full length like the tolex line's, and a fixed baffle glued along its full dado, since both run with the wrapped grain; on every hardwood order
- 2026-09-13: operator rows judged in `checks.md` from the brief: no weight or size limit, no head to match, no vehicle stated (a one-hand carry at 31.5 lb), walnut in a home assumed heated with the grain wrapping around the box, finger joints and stock thickness on the construction note's defaults, stock yield well under one walnut glue-up and one birch sheet of each thickness; the two warn rows kept (power with its engine warning, and the 2:1 advisory) are covered by the acceptances above; the proposal's four slots filled and `cabreport.py --verify` exit 0

## Artifacts

- `projects/Cab-Blietz-1x12-hardwood/tone.json`, `voicing.json`, `voicing.md`
- `projects/Cab-Blietz-1x12-hardwood/cab.py`, `cab.json`, `cab.step` and `cab.stl` (regenerated, ignored by the vault, not committed)
- `projects/Cab-Blietz-1x12-hardwood/checks.md`, `cutlist.md`, `cutlist.csv`
- `projects/Cab-Blietz-1x12-hardwood/proposal.md`, `images/` (`cab-iso.png`, `cab-front.png`, `cab-top.png`, `cab-right.png`, `cab-exploded.png`, the rear view `cab-rear.png` rendered from the export's STL at `0,90` because the five renders do not show the open back, and the `walnut.jpg` and `salt-and-pepper.jpg` swatches)
- `projects/Cab-Blietz-1x12-hardwood/share/index.html`: the client share page, an interactive 3D model built from `cab.step` by `projects/Speaker-cab-system/pipeline/share-viewer/build_share.py` and published as a private Artifact at https://claude.ai/code/artifact/b3bd15d9-6352-44da-a776-91057f659b8e (Brian shares the link)
- `projects/Cab-Blietz-1x12-hardwood/share/cutlist.html`: a shop traveler page (cut list grouped by material with to-scale part diagrams, plus the assembly build sequence and the exploded/rear/top/side renders), written directly from `cutlist.md`, `cutlist.csv`, and the brief's Plan; published as a private Artifact at https://claude.ai/code/artifact/7e3eb053-1e56-4e85-8749-408b53445b66
- `projects/Cab-Blietz-1x12-hardwood/.claude/context-check/last-handoff.md`
- Retrospective: `knowledge/learnings/cab-blietz-1x12.md` (after the build)

## Site-form gaps

- None that bound this order. Two soft gaps: the Amps question takes a model name only, so head or combo and whether a combo's own speaker stays connected are not asked (moot here: the MAZ 38 has no extension jack); and "Where it lives" takes a place, not the climate or heating the wood-movement rule reads.

## Outcome

- 2026-09-13: package built on the changed tools. The evaluate command re-ran with exit 0 (net 42.6 L, inside parts 1.00 L matching the layout); plain `cab.py` exit 0 with every layout check passing (21 parts, spans pass); `TMP_STL=... EXPORT=1 cab.py` exit 0 (28 solids, no pair overlapping, air volume 42.20 L measured against 42.20 L, 21 solids for 21 blanks); rear render from the STL at `0,90`; mass 14.5 kg. The first export (23 parts, 41.9 L, spans warn) was superseded. `checks.md` judged (33 rows, none left `operator`), `proposal.md` slots filled and verified (exit 0), swatches copied. Stop two pending: Brian reviews `checks.md`, the renders, and `proposal.md`, fills `Price:`, and sends.
- 2026-09-13: re-run with the 1/2 in roundover and the real strap handle. `cab.py` exited 0, and the export exited 0 (30 solids, no interference, air volume 42.20 L). The shell cut-list notes carry the roundover. `checks.md` was re-judged (33 rows, none left `operator`) and `proposal.md` verified. The share page was rebuilt and republished to the same link.
- 2026-09-14: Brian asked for a visual HTML cut list, then for it to also show assembly ("the html file should also show assembly"). Built as a one-off shop traveler for this order (not a generic tool): the three cut-list groups by material, each with to-scale part-size swatches (size only, not mounting orientation) and a data table; the exploded render as the assembly diagram; a seven-step build sequence sourced from the brief's Plan (shell glue-up, roundover, baffle, baffle cleats, back cleats and panels, grill frame, hardware); rear, top, and side renders as assembly reference. Caught and fixed two stale Plan lines that still said the jack plate was on the lower panel (left over from the 2026-09-14 move) before building the page from them. Published as a private Artifact.
- 2026-09-14: the shop renders looked rough (visible triangulation hatching on flat panels). Fixed in scripts/render_stl.py, a shared tool used by every order: flatten shading within each coplanar facet group to its mean value (matplotlib's Poly3DCollection has no true z-buffer, and per-triangle floating-point normal variance across a nominally flat surface showed as hatching), plus antialiased=False. The dense crosshatch on flat panels is gone; a faint residual hairline or two remains on views with several overlapping parts (an inherent limit of matplotlib's painter's algorithm across a multi-part compound, not something this fix reaches). Re-exported and re-rendered; the cutlist traveler was republished with the corrected images.
- 2026-09-14: the jack plate moved from the lower to the upper open-back panel, 25 mm below the top cleat (mirrored from the old 25 mm above the bottom cleat), and its share-page texture replaced with a recessed dish, a jack socket, and four corner screws instead of a flat colored block (Brian, looking at the share page: "the jackplate should go in the top section of the back, not the bottom" and "the jackplate looks horrible"). Both changes are now defaults: the jack plate position for every open and semi-open cab (closed and closed-ported are unchanged), and the plate texture for every cab, in `projects/Speaker-cab-system/pipeline/share-viewer/viewer.html`. Re-run: `cab.py` exit 0 with the check now reading "plates fit below the cleat"; export exit 0 (28 solids, no interference, air volume 42.45 L, mass unchanged at 14.285 kg); `checks.md` re-judged (33 rows, none operator); `proposal.md` verified with no stale facts. The share page was rebuilt and republished (version 4).
- 2026-09-13: re-run again once the roundover became the hardwood default, the strap handle was centered on the top panel, the floating baffle dropped its side cleats on this open-back order, and the engine's volume allowance was corrected to match. Voicing re-evaluated: net 42.9 L (up from 42.6 L, two fewer cleats free more air), inside parts 0.75 L against the layout's measured 0.7488 L. `cab.py` exited 0 with 19 parts (`cleat_baffle_left`/`right` gone). Export exited 0: 28 solids, no interference, air volume 42.45 L both ways, mass 14.285 kg (31.5 lb). `checks.md` re-judged (33 rows, none `operator`). The proposal's weight line was still 31.9 lb (14.5 kg) from the earlier mass; `--verify` caught it (`missing fact mass_kg`, `missing fact mass_lb`), fixed to 31.5 lb (14.3 kg), then verified clean. The share page was rebuilt and republished to the same link (version 3).
- 2026-09-14: the 09-14 hatching fix above was incomplete: Brian, looking at the traveler again, "images have not changed. They still look horrible." The dense marks were real geometry, not a shading bug: the 1/2 in roundover fillet exports as a band of many thin, near- but not exactly coplanar triangles, and matplotlib flat-shades each one from its own face normal, so the fillet's fast-sweeping curvature banded into stripes wherever a panel sat near edge-on (any of them, depending on view angle; confirmed by testing zsort strategies and a 9x finer STL retessellation, neither of which moved it). Two changes to `scripts/render_stl.py`: `vertex_shade()` shades each triangle from the mean of its own three vertex normals (already the area-weighted blend of every face touching that vertex) instead of its single face normal, approximating smooth per-vertex shading without true Gouraud support; and the Poly3DCollection now strokes each triangle's edge in its own fill color at 3 px instead of `edgecolor="none"`, which caulks the residual painter's-algorithm flicker between near-tied triangles that the color fix alone left in place (confirmed by testing linewidths from 0.3 to 5 px; the artifact does not fade gradually, it stays until the stroke is wide enough to bridge the flicker, then is gone). All five renders regenerated and dropped into `images/`, `share/cutlist.html` re-embedded with them, and the published Artifact's `images/*.png` files republished to match. This is a shared render tool; every future order's shop traveler benefits.
- 2026-09-14: Brian, from experience: the floating baffle's 1 mm side clearance leaves no room for the grill cloth to wrap around the frame's edge. Traced to the wrong part at first (the bare-wood baffle has no cloth on it at all; it is the separate grill frame, on `GRILL_CLEARANCE_MM`, that carries the cloth) and confirmed with him before changing anything. Widened `GRILL_CLEARANCE_MM` from 2 to 4 mm in `scripts/cablayout.py` (a shared constant, every order's grill frame). `SHELL_MARGIN_MM` (cutout to shell wall) turned out to already equal `grill strip + 2 x GRILL_CLEARANCE_MM`, not `+ grill strip + clearance + 2` as its comment read (the two numbers happened to coincide at the old 2 mm clearance); caught by the Plan 3 mirror's exhaustive 1200-case matrix test blocking on `grill opening` at the corrected margin, so it went to 48 mm (was 44), synced in `cabvoice.py` too (`assert`-checked equal to `cablayout.py`'s copy at import). Landed mirror-first: `scripts/cablayout.py`, `scripts/cabvoice.py`, and their tests in `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/`, verified there (557 tests), then the identical diff to the real `scripts/`, verified again (563 tests) plus the mirror re-verified after syncing back (557). Two of the plan's fixture orders (`sample-roots-1x12`, `rex-roots-1x12`) had voicing pinned tall enough for the old floor but not the new one; re-ran `cabvoice.py propose` with their original arguments (reconstructed from each fixture's own `tone.json` and `voicing.json`) so the engine resolved a taller box against the corrected floor, in both the mirror's fixture copies and the real ones. `knowledge/speaker-cab-construction.md` updated (margins, the grill frame's clearance, two illustrative examples) to match.
  This order re-run clean: `cab.py` exit 0, `grill opening` now "clear every cutout by 4 mm" (was 2), `cutout` at 48 mm shell margins (was 44); part count, volumes, and mass unchanged (only the grill frame's own size shrank, 462 x 411.2 mm was 466 x 415.2). `checks.md` re-judged (33 rows, none `operator`); `proposal.md` verified clean. Both Artifacts republished with the fresh renders and cut list: the shop traveler and the interactive 3D model.
  Noticed in passing, not fixed here since it is a separate call: this order's cut list still says "book-matched, show face out" for the shell panels, the same claim Brian had me drop from the MaximoCabs site's hardwood spec sheet this session as not how the shop actually builds it. The generator's grain-and-show-face note (`checks.md`, `cutlist.md`) was not touched; flagging for Brian to decide whether the generator's own book-matching language should go too.
- 2026-09-14: Brian: "you can't book match wood if you are joining it on the endgrain. Book match is along side grain," then "there won't be any book matching." Confirms the flag above: book-matching was never buildable on this design (the finger-jointed corners are end grain; a book-match seam needs a side-grain, long-grain glue line), not just a business-practice choice. Dropped `book-matched` everywhere it described the generator's own output, a shared fix for every hardwood order: `HARDWOOD_GRAIN_NOTE` in `scripts/cablayout.py`, the `grain and show face` row text in `scripts/cabreport.py`, `knowledge/speaker-cab-construction.md`'s Hardwood line note, and `skills/speaker-cab/SKILL.md`'s Phase 3 build-plan line (which had said "book-matched panels" and "grain wrapping around the box" in the same breath, self-contradictory once you know book-matching needs a long-grain seam). Landed mirror-first (mirror's `cablayout.py`, `cabreport.py`, `SKILL.md`, and the knowledge doc, which turned out already behind the mirror on unrelated earlier text from this session; brought fully current, not just this fix), then `embed_plan_code.py --plan plan-3-skill.md --mirror plan3-mirror` to resync the plan document, `--check` confirms in sync. This order's own Plan text (`book-matched panels glued up from resawn boards`) and `checks.md`'s judged "grain and show face" and "stock yield" rows carried the same claim; fixed in the brief and re-judged. Re-ran `cab.py` (all checks pass, geometry unchanged, text only) and `cabreport.py` (`checks.md` re-judged 33 rows none `operator`, `proposal.md --verify` clean, no book-matching mention there to begin with). The shop traveler's cut list note updated the same way and republished; the interactive 3D model had no such text.
