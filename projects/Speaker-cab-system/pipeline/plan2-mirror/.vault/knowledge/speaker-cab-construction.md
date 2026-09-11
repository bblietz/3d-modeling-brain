---
name: speaker-cab-construction
description: Construction rules and starting values for MaximoCabs guitar speaker cabinets (tolex and hardwood lines, 1x12 and 2x12, closed, closed-ported and open-back)
type: reference
status: unverified-starting-values
created: 2026-09-09
updated: 2026-09-10
tags: [knowledge, speaker-cab, woodworking, reference]
---

# Speaker cabinet construction

Starting values for the `/speaker-cab` skill and the cabinet generator, in
the same locked-constants spirit as [[woodworking-stock]]: change only with
evidence from a build, then record the change in the retrospective. Nothing
here has been verified against Brian's shop practice yet. Product facts come
from the MaximoCabs site content (`~/ClaudeProjects/MaximoCabs/src/content/cabinets/`);
everything else is general builder practice unless a source is given. The
2026-09-10 revision follows [[2026-09-10-plan-2-generator-design]]: finger
joints on both lines, a dovetail option on hardwood, no corner posts, the
grill frame on the speaker flanges, and margins the generator can assert.

## Materials

| Material | Use | Thickness | Density | Source |
|---|---|---|---|---|
| Baltic birch plywood, 13-ply | Tolex line shell, baffle, cleats, brace, divider, shelf | 18 mm (3/4 in nominal) | 680 kg/m3 | site content; density is the common trade figure, unverified |
| Baltic birch plywood | Back panels, open-back panels, grill frame strips, port flange rings | 12 mm (1/2 in nominal) | 680 kg/m3 | starting value |
| Black walnut, resawn | Hardwood line shell | 19 mm | 610 kg/m3 | https://www.wood-database.com/black-walnut/ |
| Black cherry, resawn | Hardwood line shell | 19 mm | 560 kg/m3 | https://www.wood-database.com/black-cherry/ |
| Hard maple, resawn | Hardwood line shell | 19 mm | 705 kg/m3 | https://www.wood-database.com/hard-maple/ |
| Sapele, resawn | Hardwood line shell | 19 mm | 670 kg/m3 | https://www.wood-database.com/sapele/ |
| PVC or ABS pipe, Schedule 40 | Rear round port tubes | inside 52.0, 77.3, 101.5, 153.2 mm (outside 60.3, 88.9, 114.3, 168.3) | ignored in mass | [[speaker-envelopes-and-port-stock]]; which size Brian buys is not settled |

Sheet stock is 2440 x 1220 mm with a 3 mm kerf for yield, as in [[woodworking-stock]]. Hardwood shell panels are glued up from resawn boards; the generator's stock check uses 3050 x 600 mm per panel as a starting limit.

## Shell per line

- **Both lines**: top, bottom, and two sides joined at the four front-to-back corner edges. The tolex line gets finger joints; the hardwood line gets finger joints by default or through dovetails as the option. The generator models the joint so renders and STEP are truthful; the cut list keeps each panel as a rectangular blank with the joint schedule in the note.
- **Tolex line**: 18 mm birch. Recessed metal jack plate. Metal corners, black or chrome, or none. Site: "13-ply void-free Baltic birch, hand-cut finger joints".
- **Hardwood line**: 19 mm resawn, book-matched panels, show face out. Recessed brass jack plate. No metal corners by default. Oil finish. The site copy still says "through-tenon corner posts glued + pinned" while the site's own renders show finger joints; the copy is wrong and is a site fix outside this vault.
- **Joinery survey**: finger joints are the plurality at the top of the market and the vintage-correct choice; the through dovetail is the only structural peer for solid wood; miters and rabbets are styling or budget choices. Details and sources in [[guitar-cab-joinery-survey]].

## Joinery conventions

- **Fingers**: width half the panel thickness (9 mm on 18 mm birch, 9.5 mm on 19 mm hardwood), count the nearest odd integer to depth / width so both ends are full fingers, width recomputed as depth / count. The top and bottom panels carry a full finger at the front edge; the sides start with a gap. Trade practice runs 1/4 in fingers; the width is a parameter.
- **Dovetails** (hardwood only): tails on the side panels so a lift by the top handle loads the joint in its locked direction, pins on top and bottom, half-pins at both ends, slope 1:8, pin width half the panel thickness at the outer face, tails about 30 mm.
- **Wood movement (hardwood line)**: grain runs front to back on all four shell panels so every panel moves along the depth axis together; expect roughly 2.6 mm (cherry), 2.8 (sapele), 2.9 (walnut), 3.7 mm (hard maple) of depth change per 4-point moisture swing flatsawn, about half quartersawn. Every cleat on the hardwood line runs across the grain, so cleats are screwed through slotted holes and glued only at their center 100 mm, and a fixed baffle is glued in the front 100 mm of its dado only. The intake's "where it lives" answer sets the expected humidity swing.

## Baffle

- 18 mm birch on both lines. Front face 20 mm behind the front edge of the shell (the recess that holds the grill frame). Driver mounts from the front of the baffle onto T-nuts fitted from the back. Bolts M6 or 1/4-20, 6.5 mm holes on the note's bolt circle, first hole at twelve o'clock.
- **Floating (default)**: 1 mm clearance to each side, on 18 x 18 mm cleats glued to the shell, felt strip between cleat and baffle, held with screws through the cleats, removable. Site: "floating 3/4 in birch with felt isolation".
- **Fixed (option)**: glued into a 6 mm deep dado in all four shell panels, blank 12 mm larger in width and height, no baffle cleats. On hardwood see the cross-grain rule above.
- Driver cutout, bolt circle, bolt count, frame diameter, and magnet diameter come from the speaker note. Typical: Celestion 283 mm cutout on a 297 mm circle, Eminence 281 mm on 294 mm, Jensen 277 mm on 293.5 mm; frames 306 to 310 mm, so the flange overhangs the cutout by 11 to 15 mm; flange thickness 5 mm starting value.
- **Margins**: at least 44 mm from a cutout edge to any shell panel (grill strip 40 plus 2 mm clearance plus 2), 25 mm from a cutout edge to the brace or divider, so the two cutouts of a 2x12 sit 68 mm apart (18 plus 2 x 25). Minimum internal width = n x cutout + (n - 1) x 68 + 2 x 44, the same for mono and stereo since the divider replaces the brace (2x12 with 283 mm cutouts: 722 mm internal, 758 mm external, 29.8 in). Minimum internal height = cutout + 88, plus slot height + 18 with a front slot port.
- **Speaker envelope** (for clearance checks): behind the baffle a basket cylinder at the cutout diameter for the first 100 mm from the baffle front face, then the magnet cylinder at the note's magnet diameter plus 12 mm cover allowance (185 mm when the note has none), total length the note's depth. At least 25 mm from any envelope part to the back panel, a port tube, a cleat, a shelf, a stiffener, the brace, or the divider.

## Bracing and dividers

- Mono 2x12: one vertical 18 x 60 mm birch brace between top and bottom at the center of the baffle span, its front face 2 mm behind the baffle back, glued to top and bottom, notched around the baffle cleats (no notch with a fixed baffle).
- Stereo 2x12: a full-height 18 mm birch divider from the baffle back face to the back panel inner face replaces the brace and splits the box into two equal chambers, sealed with glue on top and bottom. The divider carries no cleats: the baffle and the back screw into its front and rear edges (cleats on its faces would crowd the 25 mm cutout margin). Each chamber's cutout sits 44 mm from the shell and 25 mm from the divider at the minimum width, any surplus split evenly. Each chamber gets its own jack plate and, when ported, its own port.
- Any shell or back panel span over 450 mm between glued members gets one 18 x 40 mm stiffener across its middle, glued flat to the panel (on a mono 2x12 that is the back panel).

## Backs and ports

- **Closed**: 12 mm birch back panel, flush with the rear edge, screwed to 18 x 18 mm cleats every 150 mm, removable. The jack plate sits in the back panel.
- **Closed-ported, rear round port**: a Schedule 40 PVC or ABS tube through the back panel with a 12 mm plywood flange ring (outside diameter tube plus 60 mm) glued to the inside face; inside diameter snapped by the voicing engine to the tube table above, length from the voicing sheet measured through the back panel, one per driver in the chamber (a mono 2x12 gets two identical ports, each sized as a 1x12 port in half the chamber; the sheet's `port.count` and `construction.port_count` say how many). Placement order: outboard of the driver at driver height, below the driver, lower outboard corner, above the driver; the first spot with 25 mm clearance to the speaker envelope, walls, cleats, brace, divider, and jack plate wins. When no spot fits, the generator names the longest tube that does; the voicing is then re-run with a larger diameter or a slot.
- **Closed-ported, front slot port**: the baffle stops short of the bottom panel by the slot height plus an 18 mm shelf; the shelf's front edge is flush with the baffle face, its depth equals the port length, and it doubles as the bottom baffle cleat. A slot narrower than the chamber gets two cheeks; a mono 2x12 gets two slots split by an 18 mm center cheek in line with the brace. The shelf must leave at least max(25 mm, slot height) of free depth behind it. Round rear tubes are a bass-cab convention; the published vented guitar cabs (EV TL806, Mesa Thiele) use the front slot.
- **Open-back**: two horizontal 12 mm panels, top and bottom, each (1 - open fraction) x internal height / 2 tall, screwed to cleats. Open fraction 0.40 for open, 0.25 for semi-open (from [[speaker-cab-voicing]]). The jack plate sits in the lower panel. Stereo keeps the divider and one plate per chamber.

## Grill

- Frame from 12 x 40 mm birch strips with half-lap corners, outer size the recess opening minus 2 mm per side, cloth wrapped around the frame and stapled at the back. The frame rests on the speaker flanges and on 5 mm felt spacers at its corners, so its face sits 3 mm behind the front edge; a strip may cover a flange but must clear every cutout by 2 mm. With a front slot port the frame covers only the baffle above the shelf.
- Retained with hook-and-loop strips to the baffle. Piping (optional) is glued into the corner between grill frame and shell.

## Hardware

- **Jack plate**: recessed dish plate, metal on the tolex line, brass on the hardwood line. Cutout is measured from the plate purchased; starting value 110 x 70 mm (the Marshall-style CJP-1 dish cuts 76.2 x 87.3 mm, so reconcile against the part bought). Placed at the bottom center of the back panel or lower open-back panel, 25 mm above the cleat, one per chamber. Mono: one 1/4 in jack. Mono with parallel out: two jacks on one plate wired in parallel. Stereo: one plate per chamber.
- **Handle**: top-center strap handle by default on both lines (the site shows a strap on the hardwood cab too), screw pair 228.6 mm apart (Marshall style; Fender style 203.2 mm), centered on the loaded center of mass in width and depth, kept 50 mm inside the edges. Recessed side handles as the option, one per side at the depth center of mass in the upper third, cutout 140 x 90 mm starting value (Penn Elcom H7154Z flange 161 x 107 mm, dish 8.5 mm). The handle check: within 15 mm of the loaded center of mass on the width axis.
- **Feet**: four rubber feet, 40 mm, inset 32 mm from the bottom corners. Tilt-back legs on the tolex line when the intake says placement is tilted: pivot screws 100 mm from the front and bottom edges, a hardware line only.
- **Corners**: metal corners on the tolex line by default (black or chrome), none on hardwood. Leg length is unpublished by every supplier, so every cutout keeps 50 mm from the external corners.
- Hardware dimensions and sources: [[speaker-envelopes-and-port-stock]].

## Tolex

- Roll widths from the site's material list: 54 in (1371.6 mm) for the British and Fender black styles, 32 in (812.8 mm) for tweed.
- Yardage = external surface area (all six faces) x 1.15 for wrap and waste, divided by the roll width, reported in metres and yards. The cut list carries this as a line item under "Materials not cut", not a part.
- Seams run along the bottom panel. Contact cement.

## Weight and center of mass

- Cabinet mass = sum over parts of volume x density (table above; the four shared corner blocks counted once) + speaker mass from the note + 1 kg hardware allowance.
- Center of mass = mass-weighted mean of part centroids, with the speaker mass placed at the baffle at the cutout center. The handle check compares its center to this point on the width axis (15 mm tolerance).
- Site reference: tolex 1x12 about 32 lb (14.5 kg) loaded, hardwood 1x12 about 38 lb (17.2 kg).

## Site defaults (calibration)

- External 20 x 18 x 11 in (508 x 457.2 x 279.4 mm), 1x12 closed-ported.
- Internal with the rules above: 472 x 421.2 x 229.4 mm, gross 45.6 L, net about 44 L after one driver.
- The engine voices both lines with the tolex line's 18 mm walls; the hardwood line's 19 mm panels take about 1 percent more of the same external size, inside the model's error, so no separate voicing. The line and species travel in voicing.json's construction block so the generator picks the density and joinery.
- A slot-ported 1x12 on the site box grows from 18.0 to 18.3 in tall through the engine's height floor; a 2x12 starts at 29.8 in wide.
