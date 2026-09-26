---
name: project-garmin-helm-panel
description: Garmin GPSMAP 943xsv helm panel for Brian's boat; switched 2026-09-26 to printing four interlocking ASA tiles at 3/8 in; router template already printed and fits
metadata:
  type: project
---

Brian is replacing the hinged clear cover behind the helm wheel with a fixed black panel that
flush mounts a Garmin GPSMAP 943xsv. He copies the panel outline from the old cover himself.

DECIDED 2026-09-26: the panel is PRINTED IN ASA as four interlocking tiles joined by ten loose
bowtie keys, superseding the 2026-09-09 decision to rout it from one piece of 1/2 in King
Starboard. The Starboard path stays in the repo as the alternative. Print file is
`helm-panel-all-plates.3mf`, four plates, 7 h 55 min, 376 g.

The ASA panel is 3/8 in (9.525 mm), NOT the 1/2 in from the Starboard decision. 1/2 in was an
allowance for HDPE being softer and creeping; printed ASA reaches the same deflection at 3/8 in.
`helm-panel.py` now derives thickness from the build (`TILES=1` selects ASA) so neither path can
inherit the other's number.

The router template (window exactly 222.4 x 139.0 mm, four 2.8 mm pilot guides on
190.9 x 150.5 mm) printed and was confirmed fitting by Brian on 2026-09-11.

**Why:** the compartment opening and perimeter fastening are Brian's to copy from the old cover,
so the vault holds only the cutout geometry and the Garmin mounting data.

Garmin's 9x3 template draws the four screw holes 1.24 mm toward the unit's bottom relative to the
cutout (top row 4.5 mm above, bottom row 7.0 mm below), not centered. The first build assumed
centered and had to be fixed; measure hole positions from a template's vector geometry, never
derive them from labeled pitches.

**How to apply:** check `projects/Garmin-943-helm-panel/brief.md` for the Garmin numbers and build
results before searching the web again. Two things still gate a good print: the panel OUTLINE is
still Brian's 18.5 x 11.5 in estimate, and a printed panel bakes that estimate into 8 hours of
ASA; and the files are built for the 0.6 high-flow nozzle while the 0.4 has been installed since
2026-08-06. Related: [[user-printer-hardware]], [[marine-materials]], [[printer-x2d]].
