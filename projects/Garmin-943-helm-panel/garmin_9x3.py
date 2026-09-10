"""Garmin GPSMAP 9x3 flush mount numbers. Single source for this project.

Every value is measured from Garmin's own template PDF 190-02761-05_0D
(July 2022) or its install manual. See brief.md for sources, and for the
2026-09-09 note explaining why the hole pattern is NOT centered on the cutout.

Imported by both router-template.py and helm-panel.py so the jig and the
panel can never disagree about a dimension.
"""

CUTOUT_W = 222.4
CUTOUT_H = 139.0
HOLE_PITCH_X = 190.9
HOLE_PITCH_Y = 150.5
# The drawn hole pattern sits 1.24 mm toward the unit's bottom relative to the
# cutout: top holes 4.5 mm above the cutout, bottom holes 7.0 mm below.
HOLE_SHIFT = 1.24
PILOT_DRILL = 2.3  # Garmin pilot for wood or plastic screws

UNIT_W = 233.0
UNIT_H = 162.3
UNIT_D = 75.8
REAR_CLEARANCE = 33.2  # cables behind the housing

# bezel overlap past the cutout, as drawn with the trim caps on
BEZEL_OVER_SIDE = 5.6
BEZEL_OVER_TOP = 12.4
BEZEL_OVER_BOTTOM = 14.9

CUTOUT_CORNER_R_DRAWN = 3.7  # Garmin draws R3.7; a 1/4 in bit leaves 3.175

# +1 is the unit's top, -1 its bottom, measured from the cutout center
HOLE_Y = {1: HOLE_PITCH_Y / 2 - HOLE_SHIFT, -1: -HOLE_PITCH_Y / 2 - HOLE_SHIFT}
