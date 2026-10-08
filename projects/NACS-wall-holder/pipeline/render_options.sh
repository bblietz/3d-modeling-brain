#!/usr/bin/env bash
# Option renders for Brian's 2026-10-08 revision, into images/options-2026-10-08/ (page: pipeline/options_page.py).
# The crest lip (front, iso, with the frame line), the generic emblems, top-screw access (driver holes from the front, keyhole slots
# on the plate without the lip), the deeper drum (right view), and the cavity depth sections (today vs 1/4 in deeper).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=images/options-2026-10-08
mkdir -p "$OUT"
O="$HOME/.local/bin/openscad"
C="--backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --render --viewall"
S="--backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --render -D show_wall=false"

# section camera (same recipe as render.sh), for a given set of -D overrides
cam() {
  $O -o "$OUT/.cam.echo" "$@" holder.scad >/dev/null 2>&1
  python3 - "$OUT/.cam.echo" <<'PY'
import math, re, sys
e = open(sys.argv[1]).read()
vec = lambda k: [float(x) for x in re.search(k + r"=\[([^\]]*)\]", e).group(1).split(",")]
d = vec(" d"); w = vec(" w"); T = vec(" T")
mouth = float(re.search(r"mouth depth=([-0-9.]+)", e).group(1))
c = [T[i] + 0.5 * mouth * d[i] for i in range(3)]
print(f"{c[0]:.0f},{-c[2]:.0f},{c[1]:.0f}", f"{-math.degrees(math.atan2(-w[0], w[2])):.1f}")
PY
  rm -f "$OUT/.cam.echo"
}

FRONT="--projection=o --camera=0,0,0,90,0,0,500"
BACK="--projection=o --camera=0,0,0,90,0,180,500"
ISO="--camera=0,0,0,60,0,30,500"
RIGHT="--projection=o --camera=0,0,0,90,0,90,500"
FACE="--projection=o --camera=0,-105,20,90,0,0,290 -D show_wall=false -D show_nose=false"   # the whole face, flange and lip, square on (display frame: z up, camera at -y)

( $O -o "$OUT/crest-front.png" $FRONT $C -D 'emblem="none"' holder.scad ) &
( $O -o "$OUT/crest-iso.png" $ISO $C -D 'emblem="none"' holder.scad ) &
( $O -o "$OUT/crest-frame-front.png" $FRONT $C -D 'emblem="none"' -D 'tab_trim="frame"' holder.scad ) &
for em in bolt plug nacs ev; do
  ( $O -o "$OUT/emblem-$em.png" $FACE --backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --render -D "emblem=\"$em\"" holder.scad ) &
done
wait
( $O -o "$OUT/access-holes-front.png" $FRONT $C -D 'top_mount="holes"' -D 'emblem="none"' holder.scad ) &
( $O -o "$OUT/access-keyhole-front.png" $FRONT $C -D 'tab_style="none"' -D 'emblem="none"' -D show_wall=false -D show_nose=false holder.scad ) &
( $O -o "$OUT/access-keyhole-corner.png" --camera=-40,-10,45,60,0,-20,120 --backend=Manifold --colorscheme=Tomorrow --imgsize=1100,850 --render -D 'tab_style="none"' -D show_wall=false -D show_nose=false holder.scad ) &
( $O -o "$OUT/drum-right.png" $RIGHT $C holder.scad ) &
( $O -o "$OUT/drum-iso.png" $ISO $C holder.scad ) &
wait
# cavity depth: section along the wand, today's depth and 1/4 in deeper (mouth_z 1 mm lower keeps the mouth top under the flange)
read -r CEN ROTZ <<<"$(cam -D show_nose=false)"
( $O -o "$OUT/depth-now.png" --projection=o --camera=$CEN,90,0,$ROTZ,250 $S -D section=1 holder.scad ) &
MZ=$(python3 -c "import re;print(float(re.search(r'^mouth_z = ([-0-9.]+)', open('holder.scad').read(), re.M).group(1)) - 1)")
read -r CEN2 ROTZ2 <<<"$(cam -D cleat_depth=38.1 -D mouth_z=$MZ -D show_nose=false)"
( $O -o "$OUT/depth-quarter.png" --projection=o --camera=$CEN2,90,0,$ROTZ2,250 $S -D section=1 -D cleat_depth=38.1 -D mouth_z=$MZ holder.scad ) &
wait
rm -f "$OUT"/style-*.png "$OUT"/trim-*.png "$OUT"/access-keyhole-back.png
ls "$OUT"
