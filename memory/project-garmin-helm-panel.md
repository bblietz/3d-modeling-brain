---
name: project-garmin-helm-panel
description: Garmin GPSMAP 943xsv helm panel for Brian's boat; Starboard panel plus one printed router template, built 2026-09-09, awaiting print and test fit
metadata:
  type: project
---

Brian is replacing the hinged clear cover behind the helm wheel with a fixed black King Starboard panel that flush mounts a Garmin GPSMAP 943xsv. He routs the panel outline from the old cover himself. The only designed part is a printed router template (window exactly 222.4 x 139.0 mm, four 2.8 mm pilot guides on 190.9 x 150.5 mm) in `projects/Garmin-943-helm-panel/`, built 2026-09-09 with build123d, not yet printed as of that date.

**Why:** the compartment opening and perimeter fastening are Brian's to copy from the old cover, so the vault holds only the cutout template and the Garmin mounting data.

Garmin's 9x3 template draws the four screw holes 1.24 mm toward the unit's bottom relative to the cutout (top row 4.5 mm above the cutout, bottom row 7.0 mm below), not centered. The first build assumed centered and had to be fixed; measure hole positions from a template's vector geometry, never derive them from labeled pitches.

**How to apply:** when this comes up again, check `projects/Garmin-943-helm-panel/brief.md` for the Garmin numbers and build results before searching the web again. Verify the window measurement after the print and write the retrospective. Related: [[user-printer-hardware]], [[feedback-minimal-test-coupons]].
