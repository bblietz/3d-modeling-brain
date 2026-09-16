---
name: cab-elshaieb-1x12-hardwood
description: MaximoCabs order brief for Shahir ElShaieb, a 1x12 hardwood cabinet, open, Weber Silver Bell (Alnico, hemp cone)
type: order
status: proposed
created: 2026-09-15
customer: Shahir ElShaieb
line: hardwood
configuration: 1x12
tags: [order, speaker-cab, maximocabs]
---

# Order: Shahir ElShaieb, 1x12 hardwood

Source: pasted MaximoCabs quote-wizard email dated 2026-09-15.
Design rules: [[speaker-cab-voicing]], [[speaker-cab-construction]].

## Order

- Customer: Shahir ElShaieb
- Contact: adelta@gmail.com, 408-431-0926
- Line: hardwood
- Driver count: 1
- Back type asked: recommend (resolved to open, see Back type below)

## Rig block

Every field stays in this list even when empty; an empty value means the customer was not asked or did not say.

- **Amps** (one line per amp; the primary amp is the one the voicing serves)
  - Ceriatone Overtone Special 50 (OTS-50): rated 50 W, taps [4, 8, 16] ohm, head, primary: yes, type tube (confirmed from the manual: 3x 12AX7 preamp, 2x 6L6GC power, solid-state rectifier), family boutique clean (a Dumble Overdrive Special clone; not literally named in [[speaker-cab-voicing]]'s Amp families table, classified by the table's own "full range, dynamic" description and its Dr Z/Two-Rock/Carr examples)
  - Amp 2 line in the quote was a spec link for the same OTS-50, not a second physical amp
- **Guitars**
  - Pickups and output: humbucker (medium output, Les Paul) and single coil (standard Strat) - a mixed rig; pulls roughly cancel toward neutral mids rather than pushing to scooped or smooth
  - Low-end shifters: none
- **Pedals**
  - Dirt: TS808 (overdrive), Klon (overdrive/boost), germanium Fuzz Face (fuzz)
  - Boosts and EQ: none
  - Drive source: pedals
- **Music and use**
  - Genre: "always slightly overdriven cleans, pushed drive, and some really heavy thick saturation stuff" (canonical key: indie-alternative). This describes a gain range, not a named genre; matched by ear from the reference players below (Hendrix leans classic-rock; The Edge/U2, Trans Am, and Sigur Ros lean indie-alternative). indie-alternative was chosen because its neutral-mids/wide-dispersion/moderate-breakup profile fits the customer's own "not too strident" ask better than classic-rock's forward mids; flagged as a judgment call, not a clean match.
  - Approach: edge of breakup (overrides genre's breakup value directly: breakup = moderate)
  - Typical venue: studio, outdoor
  - Typical volume: low to medium low
  - Mic'd or filling the room: mic'd
  - Placement: floor
- **Tonal goals**
  - Customer's words: "I just want a pretty cab made out of real wood that has some girth and some warmth. not too strident"
  - Reference records or players: Hendrix, The Edge (U2), Trans Am, Sigur Ros
  - Cabs loved: Mesa Boogie widebody 1x12, most Marshall 4x12 / disliked: not many (no named speaker penalty applied)
- **Physical**
  - Weight limit: (not asked); no binding limit stated
  - Size limits: customer said "normal" (no special limit), but Brian overrode with an exact target: external width 22.75 in (577.85 mm) and height 16.5 in (419.1 mm), pinned exactly to mimic the real Mesa Boogie 1x12 WideBody cabinet's own external dimensions (confirmed via the product's spec sheet); depth was explicitly left to be solved for the correct net volume rather than copied from the reference (vehicle: not stated)
  - Dimensions to match: the Mesa Boogie 1x12 WideBody cabinet (https://www.gibson.com/products/mesa-boogie-1x12-widebody-cabinet), "the customer wants to mimic this cab, but in hardwood" (Brian, 2026-09-15) - width and height matched exactly, depth independently solved, construction executed in the hardwood line (not the reference's Baltic Birch plywood)
  - Where it lives (hardwood line, wood movement): studio, home
- **Connections**
  - Jack configuration: (not asked) - does not apply on a 1x12
- **Aesthetics**
  - Wood species or tolex color: walnut (confirmed by Brian, 2026-09-15; the customer's own form answer was "(not asked)", inferred from their grill-cloth pairing comment and now confirmed directly)
  - Grill cloth: Fender Style Oxblood, 36" (Mojotone) - customer said "probably oxblood?", Brian confirmed the exact product 2026-09-15; matches the site's own catalog entry (hardwood-1x12.md and tolex-1x12.md) exactly
  - Piping: yes; corners: none; logo: none; notes: "handle would be nice, alternate woods for striping e.g. purpleheart or maple" (an accent-stripe hardware detail for Phase 3, not the primary species; resolved 2026-09-15, see Plan)
- **Speaker**
  - Weber Silver Bell, Alnico, hemp cone, 16 ohm, 75 W (customer named two options without picking one - see Speaker ranking below; catalog note knowledge/speakers/weber-silver-bell-alnico-hemp.md, `data_status: missing`)

## Assumptions stated

- No binding weight or vehicle limit: customer said "normal" and did not answer weight; only the width/height pin (from Brian, matching the reference cab) actually binds this order's box.
- Site-form gaps: none - the current quote wizard asked every Rig block group; the amp's exact wattage/taps and the reference-cab dimensions were researched, not gaps in the form itself.
- Weber Silver Bell wattage (75 W) and magnet (Alnico) were not specified by the customer (Weber sells this cone as a build-to-order choice of 15/30/50/75/100 W and ceramic/alnico); Brian chose 75 W and Alnico at intake, 2026-09-15.
- Bolt circle (297 mm, 4 bolts) for the Weber note is an assumed common 12 inch pattern, not a Weber-published number - verify against the physical speaker before drilling the baffle.

## Follow-ups asked

- 2026-09-15, Brian (not the customer): exact width/height to pin (22.75 x 16.5 in, from the Mesa Boogie WideBody) and confirmation to mimic that reference cab in hardwood. Answered directly by Brian.
- 2026-09-15, batched via AskUserQuestion: speaker choice (Weber Silver Bell, Recommended, chosen), Weber wattage (75 W, Recommended, chosen), Weber magnet (Alnico, Recommended, chosen), low_end override (big, Recommended, chosen). All four resolved to the recommended option.

## Tone target

| Field | Value | Reason |
|---|---|---|
| low_end | big | Genre baseline (balanced) shifted one step toward tight by floor placement would mechanically give "tight" - overridden to big per Brian's explicit choice: the customer's own "some girth" ask and the WideBody format's whole design purpose (rear-mounting and widening the box specifically for more open-back low end) both argue against a mechanically-tight result. Uses the 56 L open-back rule-of-thumb volume. |
| mids | neutral | indie-alternative genre baseline; mixed pickups (humbucker pushes scooped, single coil pushes neutral) roughly cancel, no further shift. |
| top | smooth | Fuzz pedal rule ("fuzz sets top dark or smooth") plus the Weber hemp cone's own marketed character ("darker, warmer... mellower top"); matches the customer's explicit "not too strident." |
| breakup | moderate | Approach "edge of breakup" overrides genre directly. |
| dispersion | wide | Open-back construction (see Back type); the generic "mic'd sets focused" rig rule was overridden by Brian's explicit direction to mimic an open-back reference cab. |
| placement | floor | As stated. |
| min_power_w | 75 | 1.5 x the Ceriatone OTS-50's rated 50 W. |
| impedance_options_ohm | [4, 8, 16] | Ceriatone OTS-50's rear-panel rotary impedance selector taps (confirmed from the amp's own manual). |

Written to `tone.json` on 2026-09-15.

## Speaker ranking

The customer named two specific, non-catalog speakers rather than asking for a recommendation (Weber Silver Bell hemp cone, 16 ohm; EVM12L, 16 ohm) - not a full catalog ranking, a two-way judgment call:

| Candidate | Points | Matched keys | Data status | Reason |
|---|---|---|---|---|
| Weber Silver Bell, Alnico, hemp cone | n/a (customer-named, not catalog-scored) | warm/dark top, "not too strident" | missing (Weber publishes no T/S data for any Silver Bell) | Weber's own copy describes the hemp cone as darker, warmer, with a mellower top and less immediate attack than paper - closely matches the customer's explicit ask. For an open-back build the engine uses rule-of-thumb volume regardless of T/S data, so the missing data has no real modeling cost here. |
| EVM12L | n/a (customer-named, not catalog-scored) | high headroom, boutique-clean pairing reputation | datasheet (Fs 55 Hz, Qts 0.232, Vas 82.9 L, Xmax 3.3 mm, 100 dB, 200-300 W) | Real data and a strong community reputation as the Dumble-amp speaker of choice, but its own reputation notes describe it as "a tad harsh" and best at high volume - working against the customer's low-to-medium-low volume and warmth/not-strident ask. Its very low Qts (0.232, far below anything else in this catalog) is moot for an open-back build anyway, since the model doesn't use Qts/Vas for the open-back estimate. |

Chosen: weber-silver-bell-alnico-hemp at 16 ohm, 75 W. Customer named both options; Brian chose the Weber for its closer tonal fit to "not too strident"/warmth, confirmed 2026-09-15 (AskUserQuestion, recommended option).

## Back type

open: matches the customer-loved reference cabinet (Mesa Boogie 1x12 WideBody) exactly, per Brian's explicit direction to mimic it - confirmed open-back with high confidence from Gibson's product copy and Mesa's own spec sheet ("Open Back (WideBody)"). This overrides the generic rig-rule read, which would have leaned closed-ported from "mic'd" and "tight low end beats wide dispersion" alone; the override is well-supported since Mesa's own marketing pitches this exact format for "clean, low and medium-gain styles... added bass response and overall fullness... not high-gain," matching the customer's stated goals (warmth, girth, not strident, low-to-medium-low volume, studio use) closely. Built genuinely "open" (0.40 open fraction), not "semi-open," to match the reference cabinet's literal open-back construction - the model's own bridge table would pair "semi-open" with a "big" low_end target, but that panel-fraction heuristic is called "builder lore, unverified" in [[speaker-cab-voicing]], and the real physical mechanism behind the WideBody's extra low end is a bigger box, not a smaller back opening, which our simplified model has no way to represent directly.

## Voicing decision

- Mode: propose (a size limit applies - the pinned width and height - so the site box is not evaluated first)
- Engine command (verbatim):

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  .venv/bin/python scripts/cabvoice.py propose --speaker weber-silver-bell-alnico-hemp --impedance 16 \
    --enclosure open --tone projects/Cab-ElShaieb-1x12-hardwood/tone.json \
    --jack mono --line hardwood --species walnut \
    --pinned-width 577.85 --pinned-height 419.1 \
    --name Cab-ElShaieb-1x12-hardwood --out projects/Cab-ElShaieb-1x12-hardwood/
  ```

  `--pinned-height` did not exist before this order; added to `scripts/cabvoice.py` (mirroring the existing `--pinned-width`), with tests, the plan3-mirror copy, and `plan-3-skill.md`'s embedded code kept in sync (commit 7033c61). Pinning both width and height leaves depth as the sole free axis, solved for the target net volume.

- Reading: The box came out at 578 x 419 x 331 mm external (22.75 x 16.5 x 13.03 in) - the pinned width and height land exactly on the WideBody's own size; depth solved to 331 mm (about 45 mm deeper than the real WideBody's 11.25 in) to hit the 56 L "big" rule-of-thumb net volume, since this driver and target aren't the same as Mesa's own Celestion C90 build. The open-back estimate gives no closed/ported-style character word, only a cancellation frequency: about 311 Hz, rolling off 6 dB per octave below that relative to an equivalent closed box (for example -15.8 dB by 50 Hz). That roll-off shape is the same for every open-back box in this model regardless of size - the model can't rank a "big" open box above a "balanced" one on low end, so the real bass weight this cab delivers rides on the actual driver's own character, which is exactly why the hemp cone (warmer, less bright, per Weber's own description) was the deciding factor rather than a modeled number. No Thiele-Small data exists for this speaker at all, so there's no closed-box Qtc/F3 or ported Fb to report - every acoustic curve is skipped outright, not approximated. Wiring: the single 16 ohm driver lands directly on one of the amp's 4/8/16 ohm taps, no mismatch. Power: the chosen 75 W handling clears both the amp's 50 W rating and the 75 W (1.5x) safety target with real margin. Two warnings, both benign: the schema's generic 1.5 L driver-displacement placeholder (used for every speaker without a stated displacement, not specific to this one), and a width:depth ratio landing within 5 percent of 2:1 (1.93) - a coincident-standing-wave advisory the note itself says the site's own default box also trips and is "noted, not changed" as standard practice. Every number here is unverified, ears only.
- Approved by Brian on 2026-09-15: yes. The speaker, wattage, magnet, and low_end target were confirmed via the batched AskUserQuestion before this engine run; the resulting box, back type, and reading were presented in full afterward, and Brian's only redirect was confirming the species assumption (walnut) - no other part of the package was changed.

## Plan

- Parts in build order: shell (top, bottom, two sides), baffle, cleats (baffle and back), single lower back panel, grill frame (four strips), hardware (handle, feet, jack plate). 15 parts total, per the cut list.
- Joinery per connection: finger joints (35 fingers of 9.5 mm; Brian confirmed over the through-dovetail option, 2026-09-15); baffle floating on top-and-bottom cleats only (the open-back default, unaffected by the back panel's own style)
- Grain and show faces (hardwood): walnut, wrapping around the box per [[feedback-hardwood-grain-wraps]] (never front to back), no book-matching (end-grain corners). Accent striping (Brian, 2026-09-15): a 1 in (25.4 mm) maple stripe centered on the shell's depth, plus a 0.25 in (6.35 mm) maple stripe on each side, 0.75 in (19.05 mm) from the center stripe's own edge, walnut elsewhere, wrapping all the way around on all four shell panels. Required a new `cablayout.py` capability, `Aesthetics.accent_stripes` (hardwood only, validated species and non-overlap), and `cabmodel.py` cutting each stripe as its own solid off the finished, joint-cut panel (a striped shell panel now emits one solid per stripe segment - 7 per panel on this order - instead of one for the whole panel); a stripe crossing a finger straddles both species in that finger, expected from cutting the joint into the lamination after glue-up, not a defect. Mass rose from 15.1 to 15.2 kg (maple is denser than walnut). Documented in [[speaker-cab-construction]]
- Back panel: **single-lower**, not the generator's previous "split" (two symmetric panels) default - one 12 mm panel over the bottom half (191 mm of 383 mm internal height), the rest of the back fully open above it. This matches the real Mesa Boogie 1x12 WideBody's own construction, confirmed from Gibson's and Mesa's own back-view product photos (cross-checked against two independent retail units) after Brian redirected away from the generator's symmetric two-panel default (2026-09-15). Required a new `cablayout.py` capability, `Aesthetics.open_back_style` (commit bd46228): the existing "split" style is unchanged and remains the default for every other order.
- Hardware positions: one jack plate, on the single back panel (the only place it can go - "top" is now a rejected input combination, since there is no upper panel); top-center strap handle, confirmed (2026-09-15); no metal corners (hardwood default, matches the customer's own "Corners: none"); piping yes (customer asked for it); rubber feet (standard, no tilt-back - placement is floor, not tilted)
- Back cleats: bottom, left, and right only (matching the single panel's own edges), not the generator's original top-and-upper-side set left behind from the "split" style - Brian caught this 2026-09-15 ("remove the cleats from the top half of the back. There isn't anything to put on them"), a real gap in the single-lower fix: `cleat_blanks()` in `cablayout.py` had never been updated for the new style at all, so it kept building all six of the old "split" style's cleats regardless. Fixed with its own test; part count dropped from 18 to 15
- Port location: none (open back)
- Aesthetics block written into `cab.py` on 2026-09-15
- Second accent-stripe option (Brian, 2026-09-16, "add another striping option"): 0.75 in (19.05 mm) cherry stripe centered, flanked with no gap by a 1.5 in (38.1 mm) maple stripe on each side (touching the cherry's own edge), walnut elsewhere, same wrap-around treatment. Built as its own comparison order, `cherry-maple-stripe/` (own `cab.py`, checks pass, 31 solids for 15 blanks - 5 segments per shell panel instead of the maple design's 7), not a change to the canonical order. Exposed and fixed a float-precision bug in `cablayout.py`'s stripe-overlap and gap-fill checks (touching stripes with inexact offsets could misread as overlapping or grow a sliver of base material; commit 7eb5a0d, two regression tests added)

## Trade-offs presented

- 2026-09-15: speaker choice (Weber Silver Bell vs EVM12L, ask the customer), Weber wattage (15/30/50/75/100 W), Weber magnet (ceramic/Alnico), and low_end target (big/balanced/keep tight) presented together via AskUserQuestion; Brian chose the recommended option on all four (Weber Silver Bell, 75 W, Alnico, big). No engine re-run needed - these fed the first and only engine run.
- 2026-09-15: handle style (top-center strap vs recessed side) and corner joint (finger vs through-dovetail) presented via AskUserQuestion; Brian chose the recommended option on both (strap, finger). Jack plate position question was presented as top vs bottom, but Brian redirected past both options to a construction change instead (see below).
- 2026-09-15: Brian redirected the open-back construction itself ("back should be open but only 1 piece... bottom half... see the mesa cab product images"), rejecting the generator's existing symmetric two-panel default. Verified against real product photos (five independent sources, four in agreement: one solid panel in the bottom ~half, fully open above); built as a new `open_back_style="single-lower"` capability rather than a one-off workaround, with tests, mirrored to plan3-mirror and plan-3-skill.md (commit bd46228).

## Decisions locked

- 2026-09-15: voicing approved as presented at stop one (Weber Silver Bell, Alnico, hemp cone, 16 ohm, 75 W; open back; propose mode, pinned width and height; species walnut confirmed)
- 2026-09-15: mimic the Mesa Boogie 1x12 WideBody's width and height exactly, hardwood construction, depth solved for volume rather than copied (Brian)
- 2026-09-15: back type open, not semi-open, despite the model's own bridge table nominally pairing "big" with semi-open - the reference cabinet's literal open-back construction wins over the model's unverified panel-fraction heuristic (judgment call, flagged above under Back type)
- 2026-09-15: back cleats limited to the single panel's own edges (bottom, left, right), not the full "split"-style set; the generator now handles this correctly for every future single-lower order too (`cleat_blanks()` fix, part of commit alongside the redirect)
- 2026-09-15: genre canonical key indie-alternative, a judgment call given mixed reference-player signals (see Rig block, Genre)
- 2026-09-15: Weber Silver Bell wattage 75 W and magnet Alnico, chosen by Brian (not specified by the customer)
- 2026-09-15: both dimension-ratio-advisory and driver-displacement warnings accepted as benign/expected, no re-run needed
- 2026-09-15: handle strap, corner joint finger, back panel single-lower (all confirmed by Brian; see Trade-offs presented)
- 2026-09-15: grill cloth confirmed as Fender Style Oxblood, 36" (Mojotone), matching the site's own catalog name exactly; swatch copied in and the proposal verified with it
- 2026-09-15: price line set to "TBD - at cost" (Brian); proposal verified with it, brief status set to `proposed`
- 2026-09-15: client-shareable 3D model page hosted on the live MaximoCabs site (maximocabs.pages.dev/share/cab-elshaieb-1x12-hardwood/), unlisted, direct-link only - Brian's new standing policy for every order sent to a customer, replacing the first order's claude.ai Artifact approach. Required two fixes to the shared share-viewer template (a CSP-safe JSON data island instead of an executing per-order script, and a hemp-cone detection bug that would have shown this exact speaker with the wrong cone texture) and a CSP/header change on the live site (vault commit c636599; MaximoCabs commits f5fd893, 5a891a6)
- 2026-09-15: CAD package built clean (exit 0, no blockers); checks.md's 8 operator rows judged, all pass (grill cloth swatch match remains open, noted in their rows/Site-form gaps)
- 2026-09-15: accent striping added per Brian's exact spec (1 in maple center stripe, two 0.25 in maple stripes each 0.75 in from the center stripe's edge, wrapping all the way around); the pre-stripe build is preserved at `projects/Cab-ElShaieb-1x12-hardwood/original/` (cab.json, cab.step, cutlist, renders - Brian, 2026-09-15, "make sure to save the original version too") and the client 3D preview carries a with/without-stripe selector so the customer can view the cabinet either way (Brian, 2026-09-15, "update the webpage to let the customer choose which to view"; changed from an initial single toggle button to a selector button pair per Brian's follow-up, "instead of a toggle, make it a selection")
- 2026-09-16: a second accent-stripe option added to compare against the maple one (Brian: "add another striping option"; exact spec above under Plan), built as its own comparison order at `projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe/` - the canonical order (top-level directory, still driving the proposal's weight and spec text) remains the maple stripe until Brian picks one. The client 3D preview's selector became three options - "No stripe", "Maple stripe", "Cherry and maple stripe" - defaulting to the maple stripe as before, per Brian: "make sure to keep all versions available in the website."
- 2026-09-16: the "take off the grill" toggle removed from the client 3D preview entirely (Brian: "remove the option to take off the grill in the website ui"); the grill (frame and cloth) is now always shown, its previous default state. Since `viewer.html` is the shared share-viewer template, this also applies to any future order's preview; Shahir's is the only one currently live on the site.
- 2026-09-16: fixed the preview looking tiny on a phone (Brian: "update the cabinet webpage to be responsive. It looks tiny on my phone") - the page had no `<!DOCTYPE html>` and no viewport meta tag, so phones rendered it at a desktop-width virtual viewport and shrank the whole page to fit; the existing `@media (max-width: 900px)` rules never had a chance to fire. Added the doctype and a standard viewport meta tag; verified no horizontal scroll at 390 and 360 px emulated widths. Cecilia Blietz's separate claude.ai Artifact preview almost certainly has the same bug (built from an older copy of this same template) - flagged in Decisions/Open items, not touched.

## Artifacts

- `projects/Cab-ElShaieb-1x12-hardwood/tone.json`, `voicing.json`, `voicing.md`
- `knowledge/speakers/weber-silver-bell-alnico-hemp.md` (new catalog note, commit 3710c73)
- `projects/Cab-ElShaieb-1x12-hardwood/cab.py`, `cab.json`, `cab.step` (regenerated, not committed), `cab.stl` (regenerated, not committed)
- `projects/Cab-ElShaieb-1x12-hardwood/checks.md`, `cutlist.md`, `cutlist.csv` - final, 0 operator rows remaining
- `projects/Cab-ElShaieb-1x12-hardwood/proposal.md` (verified), `images/` (six renders including a rear view showing the single back panel and jack plate, plus the walnut and Fender Style Oxblood swatches)
- Retrospective: `knowledge/learnings/cab-elshaieb-1x12.md` (after the build)
- Engine changes: `scripts/cabvoice.py` `--pinned-height` (commit 7033c61), `scripts/cablayout.py` `open_back_style="single-lower"` (commit bd46228), `scripts/cablayout.py`/`scripts/cabmodel.py` `Aesthetics.accent_stripes` (2026-09-15), and `scripts/cablayout.py`'s stripe-overlap/gap-fill float-precision fix (2026-09-16, commit 7eb5a0d), all mirrored to `projects/Speaker-cab-system/pipeline/plan3-mirror/` and `projects/Speaker-cab-system/plan-3-skill.md`
- `projects/Cab-ElShaieb-1x12-hardwood/original/` - the pre-stripe build preserved in full (cab.json, cab.step, cutlist, six renders), at Brian's request, 2026-09-15
- `projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe/` - the cherry-and-maple comparison build preserved in full (own cab.py, cab.json, cab.step, cutlist, six renders), 2026-09-16
- `projects/Speaker-cab-system/pipeline/share-viewer/build_share.py`'s `--stripe-option` flag (2026-09-16): generalizes the selector from a fixed on/off pair to an ordered N-option list, each `none`/`primary` (recolor the primary mesh) or another order's directory (tessellates that order's own shell parts as a second geometry set)
- Client 3D model preview: https://maximocabs.pages.dev/share/cab-elshaieb-1x12-hardwood/ (unlisted; Brian shares the link) - now carries a three-way "No stripe / Maple stripe / Cherry and maple stripe" selector

## Site-form gaps

- none - the current quote wizard asked every Rig block group; everything else needed (amp spec verification, reference-cab dimensions, Weber configuration) was operator research and judgment, not a form gap.

## Outcome

- 2026-09-15: proposal.md complete (price "TBD - at cost") and verified; ready for Brian to send to the customer. Delivery outcome pending.
