"""Pickup height gauge for a Fender Precision Bass.

A four-arm feeler gauge printed flat. Each arm is one of Fender's
pickup-height starting points (bottom of the string to the top of the
pole piece, strings depressed at the last fret), from the Fender support
article "How do I set up my bass guitar properly?" (read 2026-10-13):

    2.0 mm  5/64 in  treble side (G string), Standard "J" or "P"
    2.4 mm  6/64 in  treble side (G string), Vintage style and Noiseless;
                     also the bass side for "American/Mexican Std" on
                     Fender's "What are factory setup specs?" page
    2.8 mm  7/64 in  bass side (E string), Standard "J" or "P"
    3.2 mm  8/64 in  bass side (E string), Vintage style and Noiseless

Opposite arms are a pair: 2.0 and 2.8 (standard), 2.4 and 3.2 (vintage).

Use: slide an arm across under the E string from the bass edge of the
bass-side half (or under the G string from the treble edge of the
treble-side half) so it rests on the two pole pieces that flank the
string; raise the pickup until the string just touches the arm.
P-Bass geometry behind the arm size (StewMac, Nordstrand, Amplified
Parts spec sheets): pole pairs 9.5 mm apart with the string between
them, 4.95 mm poles, 19 mm between string pairs, the outer string about
18 mm from the end of its 55.5 mm half-cover. A 10 mm wide arm covers a
pole; a 28 mm arm reaches 8 mm past the string with the hub still clear
of the cover end.

Run:  .venv/bin/python projects/Pickup-height-gauge/pickup_height_gauge.py
      SHOW=1 (or SHOW=reset) pushes the part to the OCP viewer.
"""
import os
import sys

from build123d import (
    Align, Axis, Box, Compound, Location, Mesher, Mode, Plane, Pos, Rot, Text,
    chamfer, export_stl, extrude, fillet, FontStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "pickup-height-gauge"

# --- dimensions (mm) ------------------------------------------------------
ARM_T = {"E": 2.0, "N": 2.4, "W": 2.8, "S": 3.2}   # arm thickness by direction
ARM_LEN = 28.0          # from the hub edge to the tip
ARM_W = 10.0            # across the arm (along the string when in use)
HUB = 26.0              # hub square side
HUB_T = 5.0             # hub thickness
HUB_R = 6.0             # hub corner radius
TIP_R = 2.5             # arm tip corner radius (plan view)
TIP_CHAMFER = 0.6       # top edge of the arm tip, eases the slide under the string
HUB_CHAMFER = 0.6       # hub top edges, grip comfort
LABEL_H = 5.0           # label cap height
LABEL_DEPTH = 0.6       # debossed into the hub top
LABEL_INSET = 2.5       # label baseline distance from the hub edge
LABEL_FONT = "DejaVu Sans"

DIRS = {"E": 0.0, "N": 90.0, "W": 180.0, "S": 270.0}   # arm direction, degrees from +X


def arm(direction: str) -> "Part":
    t = ARM_T[direction]
    # Arm along +X from the hub center; overlap the hub by 1 mm so the union is clean.
    length = HUB / 2 + ARM_LEN
    a = Box(length + 1.0, ARM_W, t, align=(Align.MIN, Align.CENTER, Align.MIN))
    a = Pos(-1.0, 0, 0) * a
    tip_edges = a.edges().filter_by(Axis.Z).group_by(Axis.X)[-1]
    a = fillet(tip_edges, TIP_R)
    # chamfer the top edge of the tip (the rounded end), not the hub side
    top_tip = [e for e in a.edges().group_by(Axis.Z)[-1] if e.center().X > HUB / 2 + ARM_LEN - TIP_R - 0.01]
    a = chamfer(top_tip, TIP_CHAMFER)
    return Rot(0, 0, DIRS[direction]) * a


def label(direction: str) -> "Part":
    txt = f"{ARM_T[direction]:.1f}"
    t = Text(txt, font_size=LABEL_H, font=LABEL_FONT, font_style=FontStyle.BOLD,
             align=(Align.CENTER, Align.CENTER))
    solid = extrude(t, LABEL_DEPTH + 0.5)
    # place at the arm root, reading toward the arm: baseline parallel to the hub edge
    solid = Pos(HUB / 2 - LABEL_INSET - LABEL_H / 2, 0, HUB_T - LABEL_DEPTH) * Rot(0, 0, -90) * solid
    return Rot(0, 0, DIRS[direction]) * solid


def build() -> "Part":
    hub = Box(HUB, HUB, HUB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hub = fillet(hub.edges().filter_by(Axis.Z), HUB_R)
    part = hub
    for d in DIRS:
        part = part + arm(d)
    part = chamfer(part.edges().group_by(Axis.Z)[-1], HUB_CHAMFER)
    for d in DIRS:
        part = part - label(d)
    return part


def check(part) -> None:
    bb = part.bounding_box()
    span = HUB + 2 * ARM_LEN
    assert len(part.solids()) == 1, "gauge must be one solid"
    assert abs(bb.size.X - span) < 1e-3 and abs(bb.size.Y - span) < 1e-3, bb.size
    assert abs(bb.min.Z) < 1e-6 and abs(bb.max.Z - HUB_T) < 1e-6, bb
    # each arm's top face is at its nominal thickness: probe a 6x6 column at the tip
    for d, ang in DIRS.items():
        probe = Rot(0, 0, ang) * Pos(HUB / 2 + ARM_LEN - 6.0, 0, 0) * Box(6, 6, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
        cut = part & probe
        assert abs(cut.bounding_box().max.Z - ARM_T[d]) < 1e-6, (d, cut.bounding_box().max.Z)
        assert abs(cut.volume - 6 * 6 * ARM_T[d]) < 0.5, (d, cut.volume)


if __name__ == "__main__":
    part = build()
    check(part)
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, NAME + ".stl")
    export_stl(part, out, tolerance=0.01, angular_tolerance=0.1)
    print("volume mm3", round(part.volume, 1), "bbox", part.bounding_box().size, "->", out)
    if os.environ.get("SHOW"):
        from ocp_vscode import show, Camera
        show(part, names=["gauge"],
             reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
