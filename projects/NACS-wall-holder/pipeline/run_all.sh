#!/usr/bin/env bash
# The whole pipeline after a cavity, drum or plate change, in order: cavity budget, mouth rim roundover, docking and hold
# check, body and inlay exports (with the recess check), print 3MF with both solid modifiers (sliced and checked), the
# renders, the modifier figures, the corner figures, and the pages. Logs go to $SCRATCH/run-all/.
set -euo pipefail
cd "$(dirname "$0")/.."
P=/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python
O="$HOME/.local/bin/openscad"
L="${SCRATCH:-/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/612fec58-43f6-4bff-a4e8-46ee5353df03/scratchpad}/run-all"
mkdir -p "$L"
X="--backend=Manifold -D display=false -D show_nose=false -D show_wall=false -D show_inlay=false"
$P pipeline/zbudget.py > "$L/zbudget.log" 2>&1 && tail -n 4 "$L/zbudget.log"
$P pipeline/rim_round.py > "$L/rim_round.log" 2>&1 && tail -n 2 "$L/rim_round.log"
$P pipeline/insertion.py > "$L/insertion.log" 2>&1 && grep -i "way in\|hold\|hanging\|engaged" "$L/insertion.log" | tail -n 6
# shellcheck disable=SC2086
$O $X -o holder.stl holder.scad > "$L/export-body.log" 2>&1
# shellcheck disable=SC2086
$O $X -D 'part="inlay"' -o holder-inlay.stl holder.scad > "$L/export-inlay.log" 2>&1
$P - <<'PY'
import trimesh
b, i = trimesh.load("holder.stl"), trimesh.load("holder-inlay.stl")
pts = trimesh.sample.volume_mesh(i, 300)
inside = int(b.contains(pts).sum())
print(f"body {abs(b.volume) / 1000:.1f} cm3, {len(b.split())} body, watertight {b.is_watertight}, bounds {b.bounds.round(2).tolist()}")
print(f"inlay {abs(i.volume) / 1000:.2f} cm3, {len(i.split())} bodies, {inside} of {len(pts)} volume samples inside the body (must be 0)")
assert len(b.split()) == 1 and b.is_watertight and inside == 0
PY
( ./render.sh > "$L/render.log" 2>&1 ) &
$P pipeline/make_coupon_3mf.py holder > "$L/3mf.log" 2>&1 && grep "solid check\|holder-print" "$L/3mf.log"
wait
$P pipeline/modifier_views.py > "$L/modifier_views.log" 2>&1 && grep "cm3" "$L/modifier_views.log"
git checkout -- images/modifier-ring.png     # the before-and-after ring figure is history: the squared ring on the 4 in plate
$P pipeline/corner_check.py "" -fixed > "$L/corner_check.log" 2>&1 && tail -n 3 "$L/corner_check.log"
$P renders_page.py | tail -n 1
$P pipeline/corner_page.py
$P pipeline/plate_options_page.py
echo "run_all done"
