Continuing the MaximoCabs order Cab-Blietz-1x12-hardwood (vault ~/ClaudeProjects/3d-modeling-brain, /speaker-cab skill). This is the first real quote from the live site wizard, received 2026-09-13.

Order: Cecilia Blietz. Hardwood 1x12 in walnut with Salt and Pepper 32" grill cloth, open back, Eminence Cannabis Rex 8 ohm. The site box is 508 x 457 x 279 mm (20 x 18 x 11 in) external and weighs 14.5 kg (31.9 lb). Her amp is a Dr. Z MAZ 38 (38 W, EL84, 4/8/16 ohm jacks), played with humbuckers into two Tube Screamers at edge of breakup, about 20 percent volume, in a practice room with the cab on the floor.

Current state: brief status `built`, at stop two.
- `checks.md`: 33 rows, all judged, none left `operator`.
- `proposal.md`: slots filled, `cabreport.py --verify` exit 0, Price blank for Brian.
- Renders: six renders, including a rear view from the export's STL.
- Swatches: walnut.jpg and salt-and-pepper.jpg copied into images/.

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
```

Results:
- Evaluate exit 0: net 42.6 L, inside parts 1.00 L.
- Layout exit 0: every check passes, 21 parts.
- Export exit 0: 28 solids, no interference, air volume 42.20 L both ways, 21 solids for 21 blanks.

Tool changes made during this order (mirror first, then landed, then `plan-3-skill.md` re-embedded; embed `--check` in sync; landed suites 536 passed):
- `cabreport.py` `SWATCHES`: now matches the site's current option names and photos.
- Grain wording: the cut list, check table, construction note, and skill all say hardwood grain wraps around the box, never front to back.
- Stiffeners: `cablayout.stiffener_blanks` and `cabvoice.inside_parts_l` add no stiffeners to hardwood shell panels (`NO_SHELL_STIFFENER_LINES`).

Decisions already locked:
- 2026-09-13 voicing: Brian approved the Cannabis Rex 8 ohm, open back, evaluated on the site box. He redirected from the recommended semi-open to the open back the customer asked for. Tone target: low_end balanced (not the rule reading's tight), mids scooped, top smooth, breakup moderate, dispersion wide, floor, min_power_w 57, taps [4, 8, 16].
- Accepted warnings: power (50 W handling under the 57 W target, above the amp's 38 W) and the 2:1 width-to-depth advisory.
- Hardwood grain never runs front to back; it wraps around the box. This is Brian's rule, and it is in memory (feedback-hardwood-grain-wraps) and the construction note.
- No glued stiffeners on hardwood shell panels, on every hardwood order (Brian).
- Swatch table fixed now (Brian).
- Aesthetics: corners none, piping no, handle a leather strap and jack plate recessed brass (the page defaults, not asked), finger joints, floating baffle, rubber feet, no logo.

Next action: stop two.
1. Brian reviews `checks.md`, the renders, and `proposal.md`.
2. He fills `Price:` and sends the proposal.
3. Record his edits in Decisions locked, set the brief's status to `proposed`, then commit and push.

Open items for Brian (not blocking):
- The hardwood cleat rule (slotted holes, glued at the center 100 mm) and the fixed-baffle "front 100 mm of its dado" rule came from the old front-to-back wording. With the grain wrapping, cleats and dados run with the grain; whether to relax these is open. The construction note's fixed-baffle bullet still says "see the cross-grain rule above".
- The jack plate: the 110 x 70 mm starting cutout leaves 13 mm above it on the 126 mm lower open-back panel. Reconcile against the plate he buys (a CJP-1 dish at 87.3 mm tall would not fit).
- Customer follow-ups: head or combo, and Presence or Cut on the panel (Studio Lead or Sr.).
- Tool follow-ups:
  - The spans message reads "no panel span over 450 mm" on a hardwood box whose top spans 470 mm.
  - `swatch()` maps tolex and grill `fender-black.jpg` to one image basename.
  - The plan3 mirror lacks the sample-roots and rex-roots fixtures (6 mirror tests fail, the same before and after).
