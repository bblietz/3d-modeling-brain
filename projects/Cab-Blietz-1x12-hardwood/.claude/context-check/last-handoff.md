Continuing the MaximoCabs order Cab-Blietz-1x12-hardwood (vault ~/ClaudeProjects/3d-modeling-brain, /speaker-cab skill). This is the first real quote from the live site wizard, received 2026-09-13.

Order: Cecilia Blietz, Hardwood 1x12.
- Cabinet: walnut with Salt and Pepper 32" grill cloth, open back, Eminence Cannabis Rex 8 ohm.
- Size: the site box, 508 x 457 x 279 mm (20 x 18 x 11 in) external, 14.285 kg (31.5 lb).
- Her rig: a Dr. Z MAZ 38 (38 W, EL84, 4/8/16 ohm jacks) with humbuckers into two Tube Screamers, at edge of breakup, about 20 percent volume, in a practice room with the cab on the floor.

Current state: brief status `built`, at stop two, package re-run four times today as Brian iterated on the share page (roundover, glue rules, centered handle, floating baffle, corrected engine volume).
- `checks.md`: 33 rows, all judged, none left `operator`.
- `proposal.md`: slots filled, `cabreport.py --verify` exit 0 (its weight line was caught stale once by `--verify` and fixed).
- Renders and swatches: six builder renders, including a rear view from the export's STL, plus walnut.jpg and salt-and-pepper.jpg.
- Client share page `share/index.html`: an interactive 3D model built from `cab.step` by `projects/Speaker-cab-system/pipeline/share-viewer/build_share.py`, published as a private Artifact at https://claude.ai/code/artifact/b3bd15d9-6352-44da-a776-91057f659b8e (currently version 3). Brian shares the link with Cecilia. After any CAD change, run the builder again and republish the same file path from a session that can reach this artifact; from any other conversation, pass that URL.

Commands that produced the current package (from the vault root):

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

Final results:
- evaluate: exit 0, net 42.9 L, inside parts 0.75 L (matching the layout's measured 0.7488 L, since the engine now knows an open-back baffle drops its side cleats).
- layout: exit 0, 19 parts (`cleat_baffle_left`/`right` gone); spans reads "hardwood shell panels take no stiffener: top and bottom span 470 mm"; handle reads "strap handle 0.0 mm from the center of mass on the width axis" (it is now centered front to back too, which this check does not measure).
- export: exit 0, 28 solids, no interference, air volume 42.45 L both ways, mass 14.285 kg.

Tool changes made during this order, each mirror first, then landed, then `plan-3-skill.md` re-embedded; embed `--check` in sync throughout; landed and mirror suites both finished at 553 passed:
- Swatch table matches the site's photos; a shared image basename gets its folder prefix.
- Hardwood grain wraps around the box, never front to back.
- No stiffeners on hardwood shell panels (layout and engine allowance both).
- Hardwood cleats and a fixed baffle glued full length like tolex.
- Spans message names the unstiffened hardwood shell spans.
- The plan3 mirror carries the sample-roots and rex-roots fixtures.
- New `Aesthetics.roundover_mm`, defaulting to 12.7 mm (1/2 in) on hardwood and none on tolex; `cabmodel` rounds all 12 outside shell edges.
- The strap handle is a real leather strap on two end caps, centered on the top panel (not the loaded center of mass).
- New `Aesthetics.baffle_cleat_edges`: `"top-bottom"` by default on open and semi-open (no sealed volume to protect), `"all"` on closed and closed-ported (protects the Thiele-Small seal assumption); `cabvoice.inside_parts_l` resolves the same default so the voicing sheet's allowance matches what `cablayout` builds.

Decisions already locked:
- 2026-09-13 voicing: Brian approved the Cannabis Rex 8 ohm, open back, evaluated on the site box, redirecting from the recommended semi-open to the open back the customer asked for. Tone target: low_end balanced, mids scooped, top smooth, breakup moderate, dispersion wide, floor, min_power_w 57, taps [4, 8, 16].
- Accepted warnings: power (50 W handling under the 57 W target) and the 2:1 width-to-depth advisory.
- Brian's rules, on every hardwood order: grain never front to back; no glued shell stiffeners; cleats and a fixed baffle glued full length.
- Swatch table and three tool follow-ups fixed.
- Client share page instead of the builder PNGs; no price and no contact details on it.
- 1/2 in roundover is the hardwood default (0 for sharp edges, another value overrides).
- Strap handle centered on the top panel, on every strap-handle cab.
- Floating baffle cleat edges are a modeled option; open and semi-open default to top-and-bottom only, closed and closed-ported keep all four, for the sealing reason above.
- Aesthetics: corners none, piping no, handle leather strap, jack plate recessed brass (page defaults, not asked), finger joints, no logo.

Next action: stop two.
1. Brian reviews `checks.md`, the renders, `proposal.md`, and the share page.
2. He fills `Price:`, then sends the proposal and the share link.
3. Record his edits in Decisions locked, set the brief's status to `proposed`, then commit and push.

Open items for Brian (not blocking):
- Jack plate: the 110 x 70 mm starting cutout leaves 13 mm above it on the 126 mm lower open-back panel. Check it against the plate he buys.
- Customer follow-ups: head or combo, and Presence or Cut on the panel (Studio Lead or Sr.).
- Minor leftovers from the swatch rename (fixture proposal template comments, one stale handoff line, two plan prose lines) noted in earlier retrospective text, not touched.
