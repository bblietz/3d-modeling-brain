Continuing the MaximoCabs order Cab-ElShaieb-1x12-hardwood (vault ~/ClaudeProjects/3d-modeling-brain, /speaker-cab skill). Quote received 2026-09-15 from the site wizard.

Order: Shahir ElShaieb, Hardwood 1x12.
- Cabinet: walnut, with two accent-stripe designs now on the table for Brian/the customer to compare (canonical build is still the maple one; neither is dropped) - (1) a maple stripe (1 in center stripe, two 0.25 in stripes each 0.75 in from the center stripe's own edge, wrapping all the way around) and (2) a cherry-and-maple stripe (0.75 in cherry centered, flanked with no gap by a 1.5 in maple stripe on each side) - plus the plain no-stripe look; Fender Style Oxblood 36" grill cloth (Mojotone, confirmed by Brian and matched to the site's own catalog entry), open back (single-lower style), Weber Silver Bell Alnico hemp cone 16 ohm 75 W (new catalog note).
- Size: pinned to the Mesa Boogie 1x12 WideBody's own width and height (22.75 x 16.5 in / 577.85 x 419.1 mm external), depth solved for the target net volume - 331 mm (13.03 in), 15.2 kg (33.5 lb, up 0.1 kg from the pre-stripe 15.1 kg since maple is denser than walnut).
- His rig: a Ceriatone Overtone Special 50 (tube, 50 W, 4/8/16 ohm taps, a Dumble Overdrive Special clone) with humbuckers and single coils into a TS808, a Klon, and a germanium fuzz, edge of breakup up to heavy saturation, studio/outdoor at low-to-medium-low volume, mic'd, on the floor.

Current state: brief status `proposed`, past stop two; the accent-stripe feature was added and built after that stop under Brian's direct, explicit spec (not a fresh stop-two gate, the same as the earlier cleat-fix bug report).
- `checks.md`: 33 rows, all judged, none left `operator`; solid count 39 solids for 15 blanks (accent stripes split the 4 shell panels into 7 solids each); interference, air volume, rectangularity all pass.
- `proposal.md`: verified clean (`cabreport.py --verify` exit 0); weight and "Finish" lines updated for the stripe.
- Renders: six (including a rear view from the export's STL); these builder-facing renders are uniform blue-gray shaded and do not show the stripe's color (render_stl.py has never been species-aware, for any material) - the real visual is the client 3D preview's texture-mapped viewer, see below.
- `projects/Cab-ElShaieb-1x12-hardwood/original/`: the complete pre-stripe build (cab.json, cab.step, cutlist, six renders including rear) preserved untouched, at Brian's request ("make sure to save the original version too").
- `projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe/`: a second complete comparison build (own cab.py, cab.json/step/stl, cutlist, six renders, sharing the order's voicing.json), added 2026-09-16 for the cherry-and-maple stripe option (Brian: "add another striping option"). Not the canonical order - that stays the top-level directory, still the maple stripe.

Commands that produced the current package (from the vault root):

```bash
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py propose --speaker weber-silver-bell-alnico-hemp --impedance 16 \
  --enclosure open --tone projects/Cab-ElShaieb-1x12-hardwood/tone.json \
  --jack mono --line hardwood --species walnut \
  --pinned-width 577.85 --pinned-height 419.1 \
  --name Cab-ElShaieb-1x12-hardwood --out projects/Cab-ElShaieb-1x12-hardwood/
# accent_stripes added to cab.py's AESTHETICS block, then:
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-ElShaieb-1x12-hardwood/cab.py
EXPORT=1 /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-ElShaieb-1x12-hardwood/cab.py
TMP_STL=projects/Cab-ElShaieb-1x12-hardwood/cab.stl EXPORT=1 /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-ElShaieb-1x12-hardwood/cab.py
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/render_stl.py projects/Cab-ElShaieb-1x12-hardwood/cab.stl projects/Cab-ElShaieb-1x12-hardwood/images/cab-rear.png 0,90
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabreport.py projects/Cab-ElShaieb-1x12-hardwood/ --customer "Shahir ElShaieb"
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabreport.py projects/Cab-ElShaieb-1x12-hardwood/ --customer "Shahir ElShaieb" --verify
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Speaker-cab-system/pipeline/share-viewer/build_share.py projects/Cab-ElShaieb-1x12-hardwood --customer "Shahir ElShaieb" \
  --stripe-option "No stripe=none" --stripe-option "Maple stripe=primary" \
  --stripe-option "Cherry and maple stripe=projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe"
```

The pre-stripe snapshot in `original/` was produced by the same `cab.py`, before the AESTHETICS edit, redirected with `CAB_OUT`:
```bash
EXPORT=1 CAB_OUT=projects/Cab-ElShaieb-1x12-hardwood/original /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-ElShaieb-1x12-hardwood/cab.py
TMP_STL=projects/Cab-ElShaieb-1x12-hardwood/original/cab.stl EXPORT=1 CAB_OUT=projects/Cab-ElShaieb-1x12-hardwood/original /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-ElShaieb-1x12-hardwood/cab.py
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/render_stl.py projects/Cab-ElShaieb-1x12-hardwood/original/cab.stl projects/Cab-ElShaieb-1x12-hardwood/original/images/cab-rear.png 0,90
```

The cherry-and-maple comparison in `cherry-maple-stripe/` is its own `cab.py` (AESTHETICS.accent_stripes swapped, everything else identical), sharing the order's `voicing.json`:
```bash
EXPORT=1 /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe/cab.py
TMP_STL=projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe/cab.stl EXPORT=1 /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe/cab.py
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/render_stl.py projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe/cab.stl projects/Cab-ElShaieb-1x12-hardwood/cherry-maple-stripe/images/cab-rear.png 0,90
```

Final results (striped, current): propose exit 0, no blockers, net 56.0 L (55.7 L achieved); layout exit 0, 15 parts; export exit 0, 39 solids for 15 blanks (accent stripes split some shell panels), interference 48 solids none over 1 mm3, air volume +0.00 percent, mass 15.2 kg.

Tool changes made during this order, each mirror first, then landed, then `plan-3-skill.md` re-embedded; embed `--check` in sync throughout; landed and mirror suites both green:
- `cabvoice.py`: `--pinned-height` alongside the existing `--pinned-width` (commit 7033c61).
- `cablayout.py`: `Aesthetics.open_back_style` = `"split"` (unchanged default) or `"single-lower"` (commit bd46228), plus its cleat-generation fix (commit b24e5ad, from Brian's bug report "remove the cleats from the top half of the back").
- `cablayout.py` / `cabmodel.py`: `Aesthetics.accent_stripes` (2026-09-15, not yet committed as of this handoff) - `((offset_mm, width_mm, species), ...)` measured across the panel's depth from its center, hardwood only, validated species and non-overlap. `cablayout.stripe_layout()` computes the (y0, y1, material, density) segments shared by all four shell panels; `cablayout.blank_mass_kg()` splits a striped panel's mass by each segment's share of the depth (an approximation, documented in its own docstring). `cabmodel.strip_part_entries()` cuts each segment as its own solid (a boolean intersection of the finished, joint-cut, roundover-clipped shell solid with the segment's Y-axis slab) so the STEP export, renders, and cut list all carry the real per-species geometry; `cabmodel.build()`'s air-subtraction loop was changed from a positional `zip(parts, layout.parts)` to explicit (blank, solid) pairs, since a striped blank now emits more solids than blanks; `check_build()`'s "solid count" check now compares against the expected per-blank strip count instead of assuming 1:1. New knowledge note section in [[speaker-cab-construction]] ("Accent stripes").
- New catalog note `knowledge/speakers/weber-silver-bell-alnico-hemp.md` (commit 3710c73), plus a same-day fix to 4 latent catalog-content test failures the note's first version had never been tested against (commit 8c99f3d).
- `projects/Speaker-cab-system/pipeline/share-viewer/build_share.py` / `viewer.html`: a "With accent stripe" / "Without stripe" selector, styled like the existing Viewpoint button group (2026-09-15, Brian: "update the webpage to let the customer choose which to view", then "instead of a toggle, make it a selection" - the first pass was a single toggle button, replaced with this button pair). No second mesh payload - the striped geometry alone represents both looks, since the selector just swaps each accent-strip mesh's material between its own species and the shell's base material (which butts against it with a continuous, seamless UV-mapped grain, since both share the same parent-panel seed). `build_share.py` computes `accent_strip_species()` from `cab.json`'s `aesthetics.accent_stripes` field to know which of the CAD-emitted `<panel>_stripN` solids are which species.
- `cablayout.py` (2026-09-16, commit 7eb5a0d): fixed a float-precision bug the cherry-and-maple option exposed - `Aesthetics.validate()`'s overlap check and `stripe_layout()`'s gap-fill check both compared stripe edges with a bare `>` instead of the file's usual `1e-6` mm epsilon, so two stripes meant to share an exact edge (no gap, unlike the maple design's real 0.75 in gaps) could read as a false overlap or grow a femtometre-wide sliver of base material from binary floating point noise in `offset - width / 2` arithmetic. Two regression tests added with the real inexact offsets (19.05, 28.575, 38.1 mm) that triggered it.
- `projects/Speaker-cab-system/pipeline/share-viewer/build_share.py` / `viewer.html` (2026-09-16, Brian: "add another striping option. make sure to keep all versions available in the website."): generalized the on/off selector into an N-option one via `--stripe-option LABEL=<none|primary|PATH>` (repeatable, order preserved); `none`/`primary` still just recolor the primary mesh's own accent parts as before, and a PATH tessellates that other order's own shell parts only (`is_shell_part()` filter on `mesh_payload()`) as a second geometry set, since a genuinely different stripe pattern has different cut lines, not just a different color on the same one - one mesh can't represent two different real boundary positions. `CAB.stripeOptions` carries the list; `viewer.html` builds the selector's buttons from it and toggles the primary shell group's visibility against each "alt" option's own lazily-built THREE.Group. An order with no `--stripe-option` keeps the exact previous on/off pair (or no selector) unchanged.

Decisions already locked (accent-stripe and earlier):
- 2026-09-15: accent striping - 1 in maple center stripe, two 0.25 in maple stripes each 0.75 in from the center stripe's own edge, walnut elsewhere, all the way around all four shell panels (Brian's exact spec). A stripe crossing a finger or dovetail joint shows both species in that finger - inherent to cutting the joint into the lamination after glue-up, stated as an assumption, not asked about further.
- 2026-09-15: the pre-stripe build preserved at `projects/Cab-ElShaieb-1x12-hardwood/original/` (Brian: "make sure to save the original version too").
- 2026-09-15: the client 3D preview gets a with/without-stripe selector (Brian: "update the webpage to let the customer choose which to view"; "instead of a toggle, make it a selection").
- 2026-09-16: a second accent-stripe design added to compare against the maple one (Brian's exact spec): 0.75 in cherry centered, flanked with no gap by a 1.5 in maple stripe on each side. Built as its own comparison order, `cherry-maple-stripe/`, same treatment as `original/`. The canonical order (top-level directory, still driving the proposal's weight and spec text) stays the maple stripe until Brian says otherwise.
- 2026-09-16: the client 3D preview's selector became three options - "No stripe", "Maple stripe", "Cherry and maple stripe" - defaulting to the maple stripe (unchanged default), per Brian: "make sure to keep all versions available in the website."
- 2026-09-15 voicing: Weber Silver Bell (Alnico, hemp cone, 75 W, 16 ohm) over the customer's other named option, EVM12L - chosen for tonal fit, confirmed via AskUserQuestion. low_end overridden to `big` against the mechanical rule result (`tight`).
- Back type open, matching the customer-loved reference cab exactly; built genuinely "open" (0.40 fraction) rather than the model's own "big"/"semi-open" bridge-table pairing.
- Species walnut, confirmed directly by Brian.
- Handle top-center strap, corner joint finger (both via AskUserQuestion, recommended each time).
- Back panel single-lower, redirected by Brian past the original jack-plate-position question entirely; back cleats limited to the single panel's own edges after Brian's bug report.
- Two engine warnings accepted as benign (driver-displacement placeholder; 2:1 width:depth advisory).

Stop two complete (before the accent-stripe addition): Brian reviewed `checks.md`, the renders, and `proposal.md`; confirmed the grill cloth and price ("TBD - at cost"). The accent-stripe package built after that is presented here for Brian's look before the proposal actually goes out, since it changes what the customer sees, but per his own direction it did not need a second formal stop-two gate.

Open items for Brian (not blocking):
- Which stripe design (or neither) actually ships is still open - the proposal's weight, cutlist, and checks.md all describe the maple stripe only; the cherry-and-maple option exists as a full comparison build (its own checks pass, 31 solids for 15 blanks) but has no proposal-facing paperwork of its own yet, same as `original/` never got any. Say the word once one is chosen and its own proposal/checks can be written if wanted.
- Bolt circle (297 mm, 4 bolts) on the Weber note is an assumed common 12 inch pattern, not Weber-published - verify against the physical speaker before drilling the baffle.
- Grill cloth "oxblood" is the customer's own guess, not a matched swatch name off the site's list originally - now matched to Mojotone's exact product, but no swatch photo of the physical roll in hand.
- Weber Silver Bell wattage (75 W) and magnet (Alnico) were Brian's picks, not the customer's stated answer - worth a line in the sent proposal or a quick confirmation email if that matters to the customer.
- Wood movement: the maple accent stripes move at a higher per-inch rate than walnut (3.7 vs 2.9 mm per 4-point swing over a full panel depth), but scaled to each stripe's own narrow width the mismatch across a glue line is a few hundredths of a millimeter - flagged in checks.md's "wood movement" row as low-risk, not re-verified against a real glue-up.

Resolved since the last handoff: back cleats limited to the single panel's own edges (Brian's bug report, commit b24e5ad); accent striping designed, built, and verified (this pass); the pre-stripe build preserved; the client 3D preview gained a with/without-stripe selector; a second accent-stripe design (cherry and maple) added and built as its own comparison order; the selector generalized to three options; a latent float-precision bug in `cablayout.py`'s stripe-overlap and gap-fill checks fixed.

Client 3D model preview live: https://maximocabs.pages.dev/share/cab-elshaieb-1x12-hardwood/ (unlisted - no nav/sitemap link, robots.txt disallows /share/, X-Robots-Tag noindex; Brian shares the direct link). Rebuilt three times now for the accent-stripe work: the maple stripe itself, the toggle-to-selection change, and now the second (cherry-and-maple) option; the site's inline-script CSP hash for viewer.html's module script changed each time (`public/_headers` and `src/lib/security-headers.ts`, both updated together and re-verified with `npm test`/`npm run check` every time), read from a real CSP-violation console message via `npx wrangler pages dev dist` locally, not hand-computed. Verified end to end (local wrangler, then the live URL, both via chrome-devtools MCP): zero CSP violations; the live page's own embedded `CAB.stripeOptions` was read back and confirmed (`No stripe`/`primary`/`Maple stripe`/`primary`/`Cherry and maple stripe`/`alt` with 20 mesh parts). The 3D view itself could not be visually confirmed in this sandbox (no GPU/WebGL support here, a standing, already-known limitation, not a regression) - a real browser will render it; Brian should give it a look on his own machine before sending.
