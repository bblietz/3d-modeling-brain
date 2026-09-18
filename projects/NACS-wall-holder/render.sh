#!/usr/bin/env bash
# Render holder.scad views into images/scad/. Extra args are passed to openscad (e.g. -D wand_lean=25).
# Camera is OpenSCAD's gimbal form: centre x,y,z, rot x,y,z, distance; in the display frame +Z is up
# and the wall is the XZ plane, so rot 90,0,0 faces the wall from the front (camera at -Y; rotz 90 puts it at +X, the right side).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p images/scad
O="$HOME/.local/bin/openscad"
C="--backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --preview --viewall"
$O -o images/scad/front.png --projection=o --camera=0,0,0,90,0,0,500 $C "$@" holder.scad
$O -o images/scad/right.png --projection=o --camera=0,0,0,90,0,90,500 $C "$@" holder.scad
$O -o images/scad/iso.png --camera=0,0,0,60,0,30,500 $C "$@" holder.scad
$O -o images/scad/below.png --camera=0,0,0,115,0,30,500 $C "$@" holder.scad
$O -o images/scad/section-cleat.png --projection=o --camera=24,-35,-24,90,0,-27,260 --backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --preview -D section=1 -D show_wall=false "$@" holder.scad
$O -o images/scad/section-notch.png --projection=o --camera=24,-35,-24,131,0,63,170 --backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --preview -D section=2 -D show_wall=false "$@" holder.scad
ls images/scad/*.png | sed 's#.*/##' | tr '\n' ' '; echo
