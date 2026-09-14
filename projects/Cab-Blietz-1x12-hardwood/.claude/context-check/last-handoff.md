Continuing the MaximoCabs order Cab-Blietz-1x12-hardwood (vault ~/ClaudeProjects/3d-modeling-brain, /speaker-cab skill). This is the first real quote from the live site wizard, received 2026-09-13.

Order: Cecilia Blietz, Hardwood 1x12.
- Cabinet: walnut with Salt and Pepper 32" grill cloth, open back, Eminence Cannabis Rex 8 ohm.
- Size: the site box, 508 x 457 x 279 mm (20 x 18 x 11 in) external, 14.5 kg (31.9 lb).
- Her rig: a Dr. Z MAZ 38 (38 W, EL84, 4/8/16 ohm jacks) with humbuckers into two Tube Screamers, at edge of breakup, about 20 percent volume, in a practice room with the cab on the floor.

Current state: brief status `built`, at stop two.
- `checks.md`: 33 rows, all judged, none left `operator`, re-judged after the last tool changes.
- `proposal.md`: slots filled, `cabreport.py --verify` exit 0, Price blank for Brian.
- Renders and swatches: six builder renders, including a rear view from the export's STL, plus walnut.jpg and salt-and-pepper.jpg.
- Client share page `share/index.html`: an interactive 3D model built from `cab.step` by `projects/Speaker-cab-system/pipeline/share-viewer/build_share.py`, published as a private Artifact at https://claude.ai/code/artifact/b3bd15d9-6352-44da-a776-91057f659b8e. Brian shares the link with Cecilia. It was republished after the roundover and strap handle changes. After a CAD change, run the builder again and republish the same file path from a session that can reach this artifact; from any other conversation, pass that URL.

Commands that produced the package (from the vault root):

```bash
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py evaluate --speaker eminence-cannabis-rex --impedance 8 \
  --enclosure open --tone projects/Cab-Blietz-1x12-hardwood/tone.json --line hardwood --species walnut \
  --internal 472 421.2 229.4 --name Cab-Blietz-1x12-hardwood --out projects/Cab-Blietz-1x12-hardwood/
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-Blietz-1x12-hardwood/cab.py
TMP_STL=projects/Cab-Blietz-1x12-hardwood/cab.stl EXPORT=1 /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-Blietz-1x12-hardwood/cab.py
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/render_stl.py projects/Cab-Blietz-1x12-hardwood/cab.stl projects/Cab-Blietz-1x12-hardwood/images/cab-rear.png 0,90
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabreport.py projects/Cab-Blietz-1x12-hardwood/ --customer "Cecilia Blietz"
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabreport.py projects/Cab-Blietz-1x12-hardwood/ --customer "Cecilia Blietz" --verify
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Speaker-cab-system/pipeline/share-viewer/build_share.py projects/Cab-Blietz-1x12-hardwood
```

Results:
- evaluate: exit 0, net 42.6 L, inside parts 1.00 L.
- layout: exit 0, every check passes with 21 parts; spans reads "hardwood shell panels take no stiffener: top and bottom span 470 mm".
- export: exit 0, 30 solids (the strap handle is now a leather strap and two end caps), no interference, air volume 42.20 L both ways; the shell has a 1/2 in (12.7 mm) roundover on every outside edge.

Tool changes made during this order. Each went mirror first, then landed, then `plan-3-skill.md` re-embedded; embed `--check` is in sync, and landed and mirror suites are both 547 passed.
- The swatch table matches the site's photos. A shared image basename gets its folder prefix (tolex-fender-black.jpg); the two roots fixtures were renamed to match.
- Hardwood grain wraps around the box, never front to back, in the cut list, check table, construction note, and skill.
- No stiffeners on hardwood shell panels, in both the layout and the engine allowance.
- Hardwood cleats and a fixed baffle are glued full length like tolex; the slotted-cleat and front-100-mm rules are gone.
- The spans message now names the unstiffened hardwood shell spans.
- The plan3 mirror now carries the sample-roots and rex-roots fixtures.
- New `Aesthetics.roundover_mm` option, off by default: `cabmodel` intersects each shell panel with the rounded external box, and the cut list notes the roundover. This order sets 12.7.
- The strap handle is drawn as a 5 mm leather strap arching between two end caps (`strap_handle_cap_0` and `strap_handle_cap_1`) on the 228.6 mm screw spacing.

Decisions already locked:
- 2026-09-13 voicing: Brian approved the Cannabis Rex 8 ohm, open back, evaluated on the site box, redirecting from the recommended semi-open to the open back the customer asked for. Tone target: low_end balanced (not the rule reading's tight), mids scooped, top smooth, breakup moderate, dispersion wide, floor, min_power_w 57, taps [4, 8, 16].
- Accepted warnings: power (50 W handling under the 57 W target, above the amp's 38 W) and the 2:1 width-to-depth advisory.
- Brian's rules, on every hardwood order:
  - Grain never runs front to back; it wraps around the box (memory feedback-hardwood-grain-wraps).
  - No glued stiffeners on the shell.
  - Cleats and a fixed baffle are glued full length with the grain.
- Swatch table fixed, and the three tool follow-ups fixed (Brian).
- Client share page instead of the builder PNGs (Brian); no price and no contact details on it.
- A 1/2 in (12.7 mm) roundover on every outside edge of the shell, and the strap handle drawn as a real leather strap on two brass end caps (Brian).
- Aesthetics: corners none, piping no, handle leather strap, jack plate recessed brass (the page defaults, not asked), finger joints, floating baffle, rubber feet, no logo.

Next action: stop two.
1. Brian reviews `checks.md`, the renders, `proposal.md`, and the share page.
2. He fills `Price:`, then sends the proposal and the share link.
3. Record his edits in Decisions locked, set the brief's status to `proposed`, then commit and push.

Open items for Brian (not blocking):
- Jack plate: the 110 x 70 mm starting cutout leaves 13 mm above it on the 126 mm lower open-back panel. Check it against the plate he buys; a CJP-1 dish at 87.3 mm tall would not fit.
- Customer follow-ups: head or combo, and Presence or Cut on the panel (Studio Lead or Sr.).
- Minor leftovers from the swatch rename:
  - The fixture proposals' copies of the template comment keep the old wording.
  - rex-roots' handoff line 29 logs an earlier run naming fender-black.jpg.
  - plan-3-skill.md prose lines 4231 and 4324 say fender-black.jpg outside the embedded code.
