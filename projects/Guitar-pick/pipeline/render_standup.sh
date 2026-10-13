#!/bin/bash
# OpenSCAD renders of the standing print (guitar-pick.stl from standup.py) for the sign-off page:
# images/standup-iso.png (the whole print), standup-neck.png (the left shoulder on its neck and block),
# standup-tip.png (the tip). Cameras are the ones used for the 2026-10-12 page.
#   projects/Guitar-pick/pipeline/render_standup.sh
set -e
cd "$(dirname "$0")/.."
proj=$(pwd)
tmp=$(mktemp -d)
cp guitar-pick.stl "$tmp/standup.stl"
echo 'color("#5b7fb5") import("standup.stl");' > "$tmp/standup.scad"
cd "$tmp"
O=~/.local/bin/openscad
common="--backend=Manifold --preview --colorscheme=Tomorrow"
timeout 300 $O $common --viewall --autocenter --projection=p --imgsize=1400,1000 --camera=60,-70,40,8,0,16 -o standup-iso.png standup.scad >/dev/null 2>&1
timeout 300 $O $common --projection=p --imgsize=1400,900 --camera=-22,-30,14,-7,0,6 -o standup-neck.png standup.scad >/dev/null 2>&1
timeout 300 $O $common --projection=p --imgsize=1400,900 --camera=6,-26,46,0,0,30 -o standup-tip.png standup.scad >/dev/null 2>&1
cp standup-iso.png standup-neck.png standup-tip.png "$proj/images/"
ls -la "$proj"/images/standup-*.png
rm -rf "$tmp"
