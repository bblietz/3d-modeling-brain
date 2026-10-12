#!/usr/bin/env bash
# Option renders for the drum's foot and flange running past the 4 in plate (Brian, 2026-10-11: "the center cylinder extends past the
# edge of the base on all 4 sides"), into images/options-2026-10-11/ (page: pipeline/plate_options_page.py). Since the 2026-10-08 drum
# (90 across, 7 mm blend, flange 104) the blend's foot sits 52 from the axis and the plate's edge 50.8. Every option keeps the screw pattern.
#   now   as built
#   a45   plate 4.5 in, the corner radius growing with hole_in so each countersink stays centred in its corner
#   d425  plate 4.25 in, same rule
#   c4    plate 4 in kept; the blends 7 to 4 mm at both ends, so the foot lands at 49 and the flange and lip go to 98 across
# Views: base (print frame, over the plate's corner), foot (close on the plate's left edge where the blend meets it), front (display frame).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=images/options-2026-10-11
mkdir -p "$OUT"
O="$HOME/.local/bin/openscad"
R="--backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --render -D show_wall=false -D show_nose=false -D show_inlay=false"
P="-D display=false --projection=p"
BASE="$P --camera=150,-230,135,-6,6,12"
FOOT="$P --camera=-150,-85,42,-47,0,7"
FRONT="--projection=o --camera=0,0,0,90,0,0,500 --viewall"
declare -A OPT=(
  [now]="-D plate_w=101.6 -D hole_in=10 -D plate_r=10"      # as built until 2026-10-11 (holder.scad has had pick A since)
  [a45]="-D plate_w=114.3 -D hole_in=16.35 -D plate_r=16.35"
  [d425]="-D plate_w=107.95 -D hole_in=13.175 -D plate_r=13.175"
  [c4]="-D fillet_plate=4 -D fillet_flange=4 -D tab_w=98 -D logo_h=56"
)
for k in now a45 d425 c4; do
  # shellcheck disable=SC2086
  ( $O -o "$OUT/$k-base.png" $BASE $R ${OPT[$k]} holder.scad >/dev/null 2>&1 ) &
  # shellcheck disable=SC2086
  ( $O -o "$OUT/$k-foot.png" $FOOT $R ${OPT[$k]} holder.scad >/dev/null 2>&1 ) &
  # shellcheck disable=SC2086
  ( $O -o "$OUT/$k-front.png" $FRONT $R ${OPT[$k]} holder.scad >/dev/null 2>&1 ) &
done
wait
ls "$OUT"/*.png | sed 's#.*/##' | tr '\n' ' '; echo
