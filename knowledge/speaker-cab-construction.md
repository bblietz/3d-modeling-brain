---
name: speaker-cab-construction
description: Construction rules and starting values for MaximoCabs guitar speaker cabinets (tolex and hardwood lines, 1x12 and 2x12, closed-ported and open-back)
type: reference
status: unverified-starting-values
created: 2026-09-09
tags: [knowledge, speaker-cab, woodworking, reference]
---

# Speaker cabinet construction

Starting values for the `/speaker-cab` skill and the cabinet generator, in
the same locked-constants spirit as [[woodworking-stock]]: change only with
evidence from a build, then record the change in the retrospective. Nothing
here has been verified against Brian's shop practice yet. Product facts come
from the MaximoCabs site content (`~/ClaudeProjects/MaximoCabs/src/content/cabinets/`);
everything else is general builder practice unless a source is given.

## Materials

| Material | Use | Thickness | Density | Source |
|---|---|---|---|---|
| Baltic birch plywood, 13-ply | Tolex line shell, baffle, cleats | 18 mm (3/4 in nominal) | 680 kg/m3 | site content; density is the common trade figure, unverified |
| Baltic birch plywood | Back panels, open-back panels | 12 mm (1/2 in nominal) | 680 kg/m3 | starting value |
| Black walnut, resawn | Hardwood line panels | 19 mm | 610 kg/m3 | https://www.wood-database.com/black-walnut/ |
| Black cherry, resawn | Hardwood line panels | 19 mm | 560 kg/m3 | https://www.wood-database.com/black-cherry/ |
| Hard maple, resawn | Hardwood line panels | 19 mm | 705 kg/m3 | https://www.wood-database.com/hard-maple/ |
| Sapele, resawn | Hardwood line panels | 19 mm | 670 kg/m3 | https://www.wood-database.com/sapele/ |
| Hardwood, same species | Corner posts, hardwood line | 38 x 38 mm | as species | starting value |

Sheet stock is 2440 x 1220 mm with a 3 mm kerf for yield, as in [[woodworking-stock]].

## Shell per line

- **Tolex line**: 18 mm birch top, bottom, and two sides joined with finger joints at all four corners, finger width 18 mm, glued. The generator models the fingers so renders and STEP are truthful; the cut list keeps each panel as a rectangular blank with a "finger joint, 18 mm fingers" note. Recessed metal jack plate. Metal corners, black or chrome. Site: "13-ply void-free Baltic birch, hand-cut finger joints".
- **Hardwood line**: four 38 x 38 mm corner posts. Side, top, and bottom panels are 19 mm resawn, book-matched, and tenoned through the posts, glued and pinned. Show face and grain direction are declared per panel in the plan phase. Recessed brass jack plate. No metal corners. Oil finish. Site: "resawn solid hardwood, book-matched panels, through-tenon corner posts glued + pinned".
- **Wood movement (hardwood line)**: a solid panel moves across its grain. Run each panel's grain along its long axis so the cross-grain width is the shorter dimension, and treat any cross-grain width over 150 mm with the movement rule in [[woodworking-stock]]. The intake's "where it lives" answer sets the expected humidity swing.

## Baffle

- 18 mm birch, floating: sits on 18 x 18 mm cleats glued to the shell, with a felt strip between cleat and baffle, held with screws through the cleats. Site: "floating 3/4 in birch with felt isolation".
- Front face of the baffle sits 20 mm behind the front edge of the shell (the recess that holds the grill frame).
- Driver cutout, bolt circle, and bolt count come from the speaker note (`cutout_mm`, `bolt_circle_mm`, `bolt_count`). Typical: Celestion 283 mm cutout on a 297 mm circle, Eminence 281 mm on 294 mm, Jensen 277 mm on 293.5 mm. Driver mounts from the front of the baffle onto T-nuts fitted from the back. Bolts M6 or 1/4-20.
- Cutout margin: at least 25 mm from a cutout edge to any shell panel, brace, or the other cutout. Minimum internal width for two drivers = 2 x cutout + 3 x 25 mm.
- Magnet clearance: at least 25 mm from the back of the magnet to the inside of the back panel, and 25 mm from any port tube or brace.

## Bracing and dividers

- Mono 2x12: one vertical 18 x 60 mm birch brace between top and bottom at the center of the baffle span, glued, notched around the baffle cleats.
- Stereo 2x12: a full-height, full-depth 18 mm birch divider replaces the brace and splits the box into two equal chambers, sealed with glue on all four edges. Each chamber gets its own jack plate and, when ported, its own port.
- Any unbraced panel span over 450 mm gets one 18 x 40 mm stiffener across its middle, glued flat to the panel.

## Backs and ports

- **Closed**: 12 mm birch back panel screwed to 18 x 18 mm cleats every 150 mm, removable. The jack plate sits in the back panel.
- **Closed-ported, rear round port**: a flanged tube through the back panel (ABS or PVC pipe with a plywood flange ring, or a purchased flared port), diameter and length from the voicing sheet, one per driver in the chamber (a mono 2x12 gets two identical ports, each sized as a 1x12 port in half the chamber; the sheet's `port.count` and `construction.port_count` say how many). Keep the tube 25 mm clear of the magnet.
- **Closed-ported, front slot port**: the baffle stops short of the bottom panel, leaving a full-chamber-width slot; a shelf behind the slot sets the port length, so port length equals shelf depth. Used when the customer wants no visible rear port or the rear port would be too long for the depth.
- **Open-back**: two horizontal 12 mm panels, top and bottom, each (1 - open fraction) x internal height / 2 tall, screwed to cleats. Open fraction 0.40 for open, 0.25 for semi-open (from [[speaker-cab-voicing]]). The jack plate sits in the lower panel.

## Grill

- Frame from 18 x 40 mm birch strips with half-lap corners, sized to the recess with 2 mm clearance per side, cloth wrapped around the frame and stapled at the back.
- Retained with hook-and-loop strips to the baffle. Sits in the 20 mm front recess.
- Piping (optional) is glued into the corner between grill frame and shell.

## Hardware

- **Jack plate**: recessed dish plate, metal on the tolex line, brass on the hardwood line. Cutout is measured from the plate purchased; starting value 110 x 70 mm for a standard recessed dish. Mono: one 1/4 in jack. Mono with parallel out: two jacks on one plate wired in parallel. Stereo: one plate per chamber.
- **Handle**: top-center strap handle on the tolex line; recessed side handles on the hardwood line. Both positioned within 15 mm of the loaded center of mass on the width axis.
- **Feet**: four rubber feet. Tilt-back legs on the tolex line when the intake says placement is tilted.
- **Corners**: metal corners on the tolex line only.

## Tolex

- Roll widths from the site's material list: 54 in (1372 mm) for the British and Fender black styles, 32 in (813 mm) for tweed.
- Yardage = external surface area (all six faces) x 1.15 for wrap and waste. The cut list carries this as a line item, not a part.
- Seams run along the bottom panel. Contact cement.

## Weight and center of mass

- Cabinet mass = sum over parts of volume x density (table above) + speaker mass from the note + 1 kg hardware allowance.
- Center of mass = mass-weighted mean of part centroids, with the speaker mass placed at the baffle at the cutout center. The handle check compares its center to this point on the width axis (15 mm tolerance).
- Site reference: tolex 1x12 about 32 lb (14.5 kg) loaded, hardwood 1x12 about 38 lb (17.2 kg).

## Site defaults (calibration)

- External 20 x 18 x 11 in (508 x 457.2 x 279.4 mm), 1x12 closed-back ported.
- Internal with the rules above: 472 x 421.2 x 229.4 mm, gross 45.6 L, net about 44 L after one driver.
