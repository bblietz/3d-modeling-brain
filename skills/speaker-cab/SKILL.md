---
name: speaker-cab
description: Use when the user asks to design, voice, quote, or build a guitar speaker cabinet (guitar cab, 1x12, 2x12, extension cab, voicing a cab, a MaximoCabs order). For other furniture or woodworking use the furniture skill; for 3D-printable parts use the 3d-model skill.
---

# Design a Guitar Speaker Cabinet (MaximoCabs order workflow)

Run one MaximoCabs order end to end with Brian as the operator: intake
from a quote email or an interview, a voiced enclosure Brian approves,
the CAD package from the generator, a check table, a customer proposal,
and after the build the listening-notes retrospective. Forked from the
furniture skill (same brief, plan, build, check, export discipline)
with a voicing phase in front. Judgment (intake, tone target, ranking,
trade-offs, proposal wording) is prose here and in
[[speaker-cab-voicing]] and [[speaker-cab-construction]]; every number
in a deliverable is written by `scripts/cabvoice.py`, the order's
`cab.py`, or `scripts/cabreport.py`. All modeling in mm; the customer
sees inches beside mm.

## Backend choice

build123d through `scripts/cabmodel.py`, always, driven by the order's
`cab.py`. There is no FreeCAD path for a cabinet: a CAD-layer failure
that repeats identically is a defect in `scripts/cabmodel.py` or
`scripts/cablayout.py`, fixed in the landed file and its mirror under
`projects/Speaker-cab-system/pipeline/` with a test, never worked
around inside an order.

## Prerequisites (check before an order)

- Interpreter: `/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python`
  (the vault venv). Every command below runs from the vault root
  `/home/brian/ClaudeProjects/3d-modeling-brain`. No GUI, no MCP tools.
- Tools in `scripts/`: `cabvoice.py` (`propose`, `evaluate`, `list`),
  `cablayout.py` and `cabmodel.py` (driven by the order's `cab.py`),
  `cabreport.py` (check table and proposal facts), `render_stl.py`.
- Knowledge: [[speaker-cab-voicing]] (tone vocabulary, enclosure
  rules, amp families, genre table with its canonical keys, ranking
  procedure, calibration table), [[speaker-cab-construction]]
  (materials, joinery, margins, ports, the default front slot, the port
  remedy order, hardware), `knowledge/speakers/<slug>.md` (the catalog;
  `/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py list`
  prints the slugs).
- Templates: `skills/speaker-cab/templates/brief.md`, `proposal.md`,
  `listening-notes.md`; the per-order `cab.py` template is
  `projects/Speaker-cab-system/fixtures/site-default/cab.py`.
- Swatches (optional): `~/ClaudeProjects/MaximoCabs/public/materials/`
  (`tolex`, `grill-cloth`, `wood`). Without the repo the proposal
  carries "no swatch on file" lines and still verifies.

Exit codes, shared by `cabvoice.py`, `cab.py`, and `cabreport.py`:

| Exit | Meaning |
|---|---|
| 0 | written, or every check passes or warns |
| 1 | input error, nothing written: fix the input (a tone value, a slug, a tube size, a missing file or flag) |
| 2 | blockers, files still written (`cabvoice.py`, `cab.py`); the proposal failed `--verify` (`cabreport.py`); argparse usage errors also exit 2 |

## Phase 1 - Intake

Source: a pasted MaximoCabs quote email or a conversation. The email is
plain text with fixed labels in this order: `Cabinet:` (tolex-1x12 or
hardwood-1x12), `Finish:`, `Grill:`, `Speaker:`, `Hardware:` (corners,
handle, jack plate, piping), then `--- Use case ---` with `Amps:`,
`Style:`, `Venue:`, `Notes:`; the first line carries the customer's
name and email. `Notes:` usually holds the tonal goals.

1. Create `projects/Cab-<Customer>-<NxS>-<line>/` (example
   `Cab-Smith-1x12-tolex`; Brian may substitute a code for the surname)
   and copy `skills/speaker-cab/templates/brief.md` there as `brief.md`,
   its frontmatter `status` set to `intake`.
2. Fill the Rig block. Every field stays present even when empty, so a
   missing answer is visible. Amp type (tube, solid state, modeling) is
   derived from the model; ask only when the model is unknown. The
   primary amp is the one the voicing serves; the others are checked
   for compatibility.
3. State every assumption instead of asking about it. Ask ONLY
   load-bearing follow-ups, in one batch: the primary amp's rated power
   and taps when the model is unknown, a size or weight limit that
   would bind, the jack configuration on a 2x12, a customer-supplied
   speaker's impedance. Stop for the batch only when it is not empty.
4. Fill the Site-form gaps line: what this intake needed that the quote
   form does not ask (guitars, pedals, jack configuration, placement).
   Changing the site is out of scope.

Under the vault's agent policy a subagent may read the catalog for the
Phase 2 ranking and return the scored table; only conclusions enter the
brief.

## Phase 2 - Voicing

No CAD before Brian approves this phase.

1. **Tone target.** Derive the eight fields from the Rig block with the
   rules in [[speaker-cab-voicing]] (amp family, genre and approach,
   pickups, dirt pedals, venue and mic'd or not, placement: on the floor
   shifts `low_end` one step toward tight, tilted counts as raised).
   Write the table in the brief with one reason line per field, then
   `tone.json` in the order directory:

   ```json
   {"low_end": "tight", "mids": "neutral", "top": "smooth",
    "breakup": "moderate", "dispersion": "focused", "placement": "floor",
    "min_power_w": 33, "impedance_options_ohm": [8]}
   ```

   `min_power_w` is 1.5 x the highest rated amp in the rig, computed
   here; the engine stops hard when speaker handling is under that
   amp's rated power and warns under `min_power_w`. A `breakup: early`
   target may accept the warning with `--accept-low-headroom`; write
   the acceptance into Decisions locked.
2. **Ranking.** Score the catalog by the note's Speaker ranking
   procedure: Character words against the target, the amp-family row
   (the table wins over a note's own Amp families line), the genre key
   on the note's Genres line. Keys are exactly `roots-country`, `blues`,
   `classic-rock`, `indie-alternative`, `jazz`, `metal-high-gain`,
   `worship-pop`, `funk-rnb`; a genre outside the table earns nothing.
   Present the top three with points, matched keys, one reason line,
   and each note's data status. A customer-chosen or supplied speaker
   is fixed; a supplied speaker without a datasheet gets the nearest
   catalog analog and a warning that reaches the sheet and the proposal.
3. **Back type.** From the note's choice rule: a tight low end beats
   wide dispersion (closed or ported over open-back); a low-end shifter
   (baritone, 7-string, drop tunings, bass VI) beats wide and takes the
   lowest tuning in range through `--fb` (45 Hz, raised in 5 Hz steps
   only while the port does not fit; the engine's range is 45 to 90 Hz).
   Write the choice and reason.
4. **Engine run.** A standard-size order (the site's 20 x 18 x 11 in box
   and no size limit) is evaluated first; on a ported box the site port
   (the 101.5 mm tube at 40 mm, the calibration port) goes with it:

   ```bash
   cd /home/brian/ClaudeProjects/3d-modeling-brain
   /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py evaluate --speaker <slug> --impedance <ohm> \
     --enclosure closed-ported --tone projects/Cab-<...>/tone.json --line <line> [--species <species>] \
     --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40 \
     --name Cab-<...> --out projects/Cab-<...>/
   ```

   Accept the site box when the sheet's character is the bridge word
   for the target's `low_end` in the note's Enclosure type rules.
   Otherwise, or when a size limit, a head to match, or a 2x12 applies,
   propose:

   ```bash
   cd /home/brian/ClaudeProjects/3d-modeling-brain
   /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py propose --speaker <slug> --impedance <ohm> \
     --enclosure closed-ported --tone projects/Cab-<...>/tone.json \
     --jack mono --line <line> --name Cab-<...> --out projects/Cab-<...>/ \
     [--species <species>] [--pinned-width <mm>] [--max-external W H D] \
     [--port-diameter <mm>] [--port-slot W H] [--port-tube <mm>] [--fb <hz>] \
     [--port-count <n>] [--accept-low-headroom]
   ```

   `--speaker` repeats for two drivers; `--jack stereo` splits the box
   into two chambers; `--pinned-width` matches a head (external width =
   head width + 0 to 10 mm); `--max-external` is the customer's limit;
   `--port-tube` pins one of the 52.0, 77.3, 101.5, 153.2 mm tubes;
   `--fb` overrides the tuning; `--port-count` sets ports per chamber.
   Exit 2 means blockers: present the trade-off the sheet names (a
   smaller box raises Qtc toward big or peaky, a different speaker,
   different wiring, a relaxed limit) and record Brian's choice before
   re-running. Record the final command verbatim in the brief.
5. **Reading.** Write the plain-language reading of `voicing.md` into
   the brief: what the alignment character, F3 or cancellation
   frequency, wiring, power result, and each warning mean for this
   player. Never write into `voicing.md`; every engine run regenerates
   it. Every predicted number is unverified, ears only; say so.
6. **Stop one.** Present the tone target, the ranking, the back type,
   and the reading. Brian approves or redirects; write the approval as
   a dated line in Decisions locked and set the brief's `status` to
   `voicing-approved`.

## Phase 3 - Plan

- Parts in build order: shell (top, bottom, two sides), baffle, cleats,
  brace or divider, back panel or open-back panels, port tube and
  flange ring or slot shelf and cheeks, grill frame, hardware. The
  layout kernel produces them; list them so Brian can object first.
- Joinery per connection from [[speaker-cab-construction]]: finger
  joints on both lines, through dovetails as the hardwood option; the
  baffle floating on cleats (default) or fixed in a 6 mm dado; the
  divider without cleats.
- Grain and show faces on the hardwood line: book-matched panels, grain
  front to back on all four shell panels, the species.
- Hardware positions: one jack plate per chamber, the strap handle over
  the center of mass (or recessed side handles), corners, feet or
  tilt-back legs, piping. Port location from the sheet.
- Aesthetics block: copy
  `projects/Speaker-cab-system/fixtures/site-default/cab.py` into the
  order directory as `cab.py` and edit its `AESTHETICS` constants
  (`corner_joint`, `baffle_mount`, `handle`, `corners`, `piping`,
  `feet`, `tolex_roll_in`, `tolex_color`, `grill_cloth`,
  `head_width_mm`). Nothing else in `cab.py` changes.

Write the plan into the brief and present it briefly; no stop.

## Phase 4 - Build loop

Run the layout first, then the CAD; read every verdict line.

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-<...>/cab.py            # layout verdicts only, nothing written
EXPORT=1 /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-<...>/cab.py   # CAD verdicts, cab.step, images/, cutlist, cab.json
```

`EXPORT=1` writes `cab.json`, `cab.step`, `cutlist.md`, `cutlist.csv`,
and `images/cab-iso.png`, `cab-front.png`, `cab-top.png`,
`cab-right.png`, `cab-exploded.png` next to `cab.py` (`CAB_OUT=<dir>`
redirects); when it exits 0 with that package on disk, set the brief's
`status` to `built`. View each render with the Read tool before
continuing; a subagent may inspect them and report. `TMP_STL=<path>`
writes an STL for `scripts/render_stl.py <stl> <png> [elev,azim ...]`
when another angle is needed.

The port loop, on a `port fit` blocker from the plain `cab.py` run. The
blocker's message takes one of five forms, and each names the next step:

1. `port fit: chamber 0 port 0: no round port of 153.2 mm fits with 25 mm
   clearance; the longest table tube that fits at the 24 mm minimum is
   101.5 mm; raise Fb, use a smaller tube or a larger box, or a front
   slot`: re-run the same engine command with `--port-tube 101.5` (the
   named tube) added, then `cab.py` again.
2. `port fit: chamber 0 port 0: tube 101.5 x 250 mm reaches the baffle;
   longest tube that fits at this diameter is 155 mm; ...` (or `finds no
   spot with 25 mm clearance`): the tube seats but its port is too long
   for the box; re-run with the next tube down the table pinned
   (`--port-tube`; a smaller area needs a shorter port at the same
   tuning), then `cab.py` again.
3. `port fit: chamber 0 port 0: no round port of 101.5 mm fits with 25 mm
   clearance; no table tube fits; use a front slot or a larger box`: no
   automatic re-run; go to the stop below with the front slot and a
   larger box.
4. `port fit: slot shelf 220 mm deep leaves 27 mm behind it, under the
   40 mm the slot needs to breathe; the deepest shelf that fits is 207 mm;
   lower the slot height or use a round port` (or `no shelf fits`): no
   automatic re-run; the stop offers a lower slot height (`--port-slot W
   <h>`), a round port, or a deeper box.
5. `port fit: chamber 0: 1 slot of 472 mm do not fit the 352 mm chamber;
   narrow the slot or widen the box` (a mono 2x12 reads `2 slots of ...
   with the 18 mm center cheek`): the chamber moved by more than the 1 mm
   the layout trims (a floor lifted it; the slot run's `--pinned-width`
   holds the width itself); re-run once with `--pinned-width` kept and
   the slot width recomputed from the new sheet's
   `box.chamber_internal_width_mm` (the full width for one slot, (width
   minus 18) / 2 each for two), then `cab.py` again.

After an automatic re-run (forms 1, 2, and 5): when the new plain `cab.py`
run has no blocker and the sheet carries no port warning (a clamped
length, an air speed over the limit), continue to the CAD run. Otherwise
stop and present these remedies, in this order:

1. The front slot, `--port-slot <width> 40 --pinned-width <external width>`:
   the width the sheet's `box.chamber_internal_width_mm`, or two slots
   of (width minus 18) / 2 on a mono 2x12, and the external width the
   sheet's `box.external_mm[0]`, the construction note's default. The
   pin holds the chamber so the slot fits it exactly, since a free width
   re-proportions under the slot's shelf and never settles; a slot up to
   1 mm over the chamber is trimmed to the full width by the layout.
2. The pinned tube's clamped tuning, accepted as the sheet reports it.
3. Fb raised with the larger tube (`--port-tube` and `--fb`, within the
   engine's 45 to 90 Hz).
4. A larger box (relax `--max-external` or the pinned width).

Brian picks; run that command, record the trade-off and the choice in
the brief, and continue. Each form gets one automatic re-run per order;
a blocker after it is a stop.

Any other blocker (net volume off the sheet, an impossible box, a power
stop, a width floor over a limit, magnet to back, interference) stops
with the trade-off its message names; Brian's choice goes into
Trade-offs presented and Decisions locked, then the engine and `cab.py`
run again. Exit 1 is an input error: fix the input, never the tool. A
build123d exception that repeats identically is a library defect (see
Backend choice), not something to route around.

## Phase 5 - Check table

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabreport.py projects/Cab-<...>/ --customer "<Customer>"
```

writes `checks.md` on every run from `voicing.json` and `cab.json`: the
layout and CAD verdicts verbatim, the engine rows (power, wiring, port
air speed, alignment, each warning), then the operator rows with their
measured values and the verdict `operator`. Replace every `operator`
with a verdict line judged against the brief:

| Row | Judge against |
|---|---|
| stock thickness | [[speaker-cab-construction]]; nominal is not actual, Brian measures the stock before cutting joinery sized to it |
| grain and show face | the Phase 3 plan (hardwood line only) |
| joinery fit | fingers and dovetails cut to measured thickness, test cut first |
| stock yield | the blank count and area against the sheets Brian has, 3 mm kerf, no nesting assumed |
| wood movement | hardwood plus the brief's "where it lives" answer: cleats slotted, a fixed baffle glued at the front only |
| transport | the brief's vehicle and doorway against the external size and the mass in lb |
| weight vs limit | the brief's weight limit against the mass in kg and lb |
| size vs limit | the brief's size limits and the head to match against the external size |

The file is final when no `operator` remains. Report anything unfixable
without changing the customer's requirements; never silently alter a
limit or a dimension Brian or the customer set.

Every `cabreport.py` run without `--verify` rewrites `checks.md` from the
two JSON files (a `--verify` run writes nothing), so judge the operator
rows only after the last engine and `cab.py` run, and judge them again
after any regeneration. Warn rows are not operator rows: each warn the
order keeps (a `port mouth` warn is expected on the site box's rear tube,
on a 1x12 front slot, and on the floor-level back cleat behind a slot
shelf, which fires on most 2x12 slot boxes at their default depth and on
shallow 1x12 ones, see [[speaker-cab-construction]]; `spans`, `power`,
and engine warnings likewise) gets a dated acceptance line in Decisions
locked, or a re-run that removes it.

## Phase 6 - Export and proposal

The package is on disk from Phase 4. The Phase 5 `cabreport.py` run also
writes `proposal.md` from `skills/speaker-cab/templates/proposal.md` when
the file is absent and never overwrites one. To regenerate it after a
re-run, delete `proposal.md` and run `cabreport.py` again; that run
rewrites `checks.md` too, so the operator rows are judged again. The
module fills the facts (customer, line, configuration, back type,
speaker, wiring, external size in inches and mm, mass in kg and lb,
finish, grill cloth, hardware, swatches, lead time, status line);
predicted frequencies never enter the proposal.

1. Fill the four prose slots between their `<!-- slot: name -->` and
   `<!-- /slot -->` markers, nothing outside them: `rig_and_goals` (the
   rig and goals in the customer's words), `why_this_cabinet` (speaker
   and back type, one reason each), `designed_to_do` (plain language,
   "designed for" wording only, never a measured claim), `alternatives`
   (one line each, from the ranking). Use the site's voice; the
   template's header comment carries the samples. Leave the `Price:`
   line for Brian.
2. Copy the swatches the proposal names from
   `~/ClaudeProjects/MaximoCabs/public/materials/` into
   `projects/Cab-<...>/images/`.
3. Verify; exit 2 lists every missing fact string and every empty slot,
   fixed inside the slots, never in the facts:

   ```bash
   cd /home/brian/ClaudeProjects/3d-modeling-brain
   /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabreport.py projects/Cab-<...>/ --customer "<Customer>" --verify
   ```

## Phase 7 - Handoff

- Update the brief: Artifacts (every path), Decisions locked (dated
  lines for the voicing approval and each trade-off), Outcome.
- Write `projects/Cab-<...>/.claude/context-check/last-handoff.md` with
  the order's state, the exact commands run, and a "Decisions already
  locked" block.
- Commit with explicit paths (never `git add -A`; another session may
  share the tree) and push. `cab.step` is regenerated by `cab.py` and
  stays out of git (the vault ignores `projects/Cab-*/*.step`).

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  git add projects/Cab-<...>/brief.md projects/Cab-<...>/tone.json projects/Cab-<...>/voicing.json projects/Cab-<...>/voicing.md projects/Cab-<...>/cab.py projects/Cab-<...>/cab.json projects/Cab-<...>/checks.md projects/Cab-<...>/cutlist.md projects/Cab-<...>/cutlist.csv projects/Cab-<...>/proposal.md projects/Cab-<...>/images projects/Cab-<...>/.claude/context-check/last-handoff.md
  git commit -m "Cab <Customer> <NxS> <line>: order package"
  git push origin main
  ```

- **Stop two.** Brian reviews `checks.md`, the renders, and
  `proposal.md`, fills the `Price:` line, and sends the proposal.
  Record his edits in Decisions locked, set the brief's `status` to
  `proposed`, and commit again.

## Phase 8 - After the build

- Copy `skills/speaker-cab/templates/listening-notes.md` to
  `knowledge/learnings/cab-<customer>-<config>.md` and fill it with
  Brian: amp and settings, guitar, pedals in use, volume level, room;
  low end, mids, top, breakup onset, dispersion; the customer's words;
  Brian's words; whether the prediction held (agree, partly, disagree)
  with one reason.
- Append the same notes, dated, to the Field notes section of the
  speaker's note in `knowledge/speakers/`.
- Promote any corrected construction default into
  [[speaker-cab-construction]] and any voicing rule that moved into
  [[speaker-cab-voicing]]; update memory when a rule changes.
- Fill the brief's Outcome and the retrospective's site-form gaps; once
  the cabinet has shipped and the listening notes are written, set the
  brief's `status` to `delivered`.
- Commit the retrospective, the speaker note, any promoted rule, the
  memory file, and the brief with explicit paths, the message ending
  with the session's attribution trailers, and push:

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  git add knowledge/learnings/cab-<customer>-<config>.md knowledge/speakers/<slug>.md knowledge/speaker-cab-construction.md knowledge/speaker-cab-voicing.md memory/project-speaker-cab-system.md projects/Cab-<...>/brief.md
  git commit -m "Cab <Customer> <NxS> <line>: listening notes and retrospective" -m "<the session's attribution trailers>"
  git push origin main
  ```

## Error handling

- Exit 1 from any tool is an input error (a tone value outside the
  vocabulary, an unknown slug, a tube outside the table, a missing
  file, a missing `--customer`): fix the input; never patch a tool for
  an order.
- Exit 2 from `cabvoice.py` or `cab.py` is a blocker whose message
  names the trade-off: present it, record the choice, re-run. Never
  retry the identical failing command blindly.
- Exit 2 from `cabreport.py --verify`: edit the proposal inside its
  slots until the listed facts are back and no slot is empty.
- A `cabreport.py` run without `--verify` overwrites a judged
  `checks.md`; judge the operator rows again from the brief rather than
  restoring the old file, since the values may have moved.
- A build123d exception from `cab.py`: reproduce it with the order's
  `voicing.json`, fix `scripts/cabmodel.py` or `scripts/cablayout.py`
  with a test through the mirror discipline, re-run. No FreeCAD.
- Missing Thiele-Small data (`data_status: missing`): the engine
  degrades to rule-of-thumb volumes and labels every number; say so in
  the reading and in the proposal's alternatives.
