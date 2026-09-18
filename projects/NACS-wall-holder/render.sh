#!/usr/bin/env bash
# Render holder.scad views into images/scad/. Extra args are passed to openscad (e.g. -D wand_lean=25).
# Camera is OpenSCAD's gimbal form: centre x,y,z, rot x,y,z, distance; in the display frame +Z is up
# and the wall is the XZ plane, so rot 90,0,0 faces the wall from the front (camera at -Y; rotz 90 puts it at +X, the right side).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p images/scad
O="$HOME/.local/bin/openscad"
C="--backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --render --viewall"
# true renders (--render): in preview the docked handle's clip plane paints over the holder's whole cut face
# section cameras come from the model: centred mid-cavity, square to the cut along the wand, and straight down the wand from the grip end
$O -o images/scad/.cam.echo "$@" holder.scad >/dev/null 2>&1
read -r CEN ROTZ DOWN <<<"$(python3 - <<'PY'
import math, re
e = open("images/scad/.cam.echo").read()
vec = lambda k: [float(x) for x in re.search(k + r"=\[([^\]]*)\]", e).group(1).split(",")]
d, w, T = vec(" d"), vec(" w"), vec(" T")
mouth = float(re.search(r"mouth depth=([-0-9.]+)", e).group(1))
c = [T[i] + 0.5 * mouth * d[i] for i in range(3)]
dd = (d[0], -d[2], d[1])                                   # display frame: (x, -z, y)
rx = math.degrees(math.acos(dd[2])); rz = math.degrees(math.atan2(dd[0], -dd[1]))
print(f"{c[0]:.0f},{-c[2]:.0f},{c[1]:.0f}", f"{-math.degrees(math.atan2(-w[0], w[2])):.1f}", f"{rx:.1f},0,{rz:.1f}")
PY
)"
rm -f images/scad/.cam.echo
S="--backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --render -D show_wall=false"
$O -o images/scad/front.png --projection=o --camera=0,0,0,90,0,0,500 $C "$@" holder.scad
$O -o images/scad/right.png --projection=o --camera=0,0,0,90,0,90,500 $C "$@" holder.scad
$O -o images/scad/iso.png --camera=0,0,0,60,0,30,500 $C "$@" holder.scad
$O -o images/scad/below.png --camera=0,0,0,115,0,30,500 $C "$@" holder.scad
$O -o images/scad/section-cleat.png --projection=o --camera=$CEN,90,0,$ROTZ,250 $S -D section=1 "$@" holder.scad
$O -o images/scad/section-notch.png --projection=o --camera=$CEN,$DOWN,190 $S -D section=2 "$@" holder.scad
# coupon views are in print orientation (display=false: bed = XY, +Z up)
$O -o images/scad/coupon-iso.png --camera=0,0,0,55,0,25,250 --viewall $S -D display=false -D 'part="coupon"' "$@" holder.scad
$O -o images/scad/coupon-mouth.png --camera=0,0,0,65,0,125,250 --viewall $S -D display=false -D 'part="coupon"' -D show_nose=false "$@" holder.scad
$O -o images/scad/coupon-top.png --projection=o --camera=0,0,0,0,0,0,250 --viewall $S -D display=false -D 'part="coupon"' -D show_nose=false "$@" holder.scad
$O -o images/scad/coupon-section.png --projection=o --camera=$CEN,90,0,$ROTZ,260 $S -D 'part="coupon"' -D section=1 "$@" holder.scad
ls images/scad/*.png | sed 's#.*/##' | tr '\n' ' '; echo
