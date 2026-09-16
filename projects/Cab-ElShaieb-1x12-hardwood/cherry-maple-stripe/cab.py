"""Cab-ElShaieb-1x12-hardwood, cherry-and-maple stripe option: a comparison build for the
share-viewer's stripe selector, not itself the order (that stays projects/Cab-ElShaieb-1x12-hardwood)."""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def vault_root(start: Path) -> Path:
    """The first directory at or above start holding scripts/cablayout.py."""
    for p in (start, *start.parents):
        if (p / "scripts" / "cablayout.py").exists():
            return p
    raise SystemExit(f"cab.py: no vault above {start} (no directory holding scripts/cablayout.py)")


sys.path.insert(0, str(vault_root(HERE) / "scripts"))
import cablayout as L  # noqa: E402

# --- aesthetics block (from the intake) --------------------------------------
AESTHETICS = L.Aesthetics(
    corner_joint="finger",           # customer asked for "a pretty cab"; dovetail offered, finger chosen (Brian, 2026-09-15)
    baffle_mount="floating",         # default
    baffle_cleat_edges=None,         # None = enclosure default (top-bottom, open back)
    jack_plate_position=None,        # None = single-lower default (bottom, the only panel)
    open_back_style="single-lower",  # one panel over the bottom half, matching the real Mesa WideBody (Brian, 2026-09-15)
    handle="strap",                  # top-center, confirmed (Brian, 2026-09-15)
    corners="none",                  # hardwood default; customer said "Corners: none"
    piping=True,                     # customer asked for piping
    feet="rubber",
    tolex_roll_in=54,                # unused on the hardwood line
    tolex_color="",                  # unused on the hardwood line
    grill_cloth="Fender Style Oxblood, 36\"",  # confirmed by Brian, 2026-09-15: Mojotone, matches the site's own catalog name
    head_width_mm=None,              # not matching a head
    roundover_mm=12.7,               # 1/2 in roundover, hardwood default
    # Accent striping, second option (Brian, 2026-09-16): a 0.75 in cherry stripe centered
    # on the shell's depth, flanked immediately (no gap) by a 1.5 in maple stripe on each
    # side, walnut everywhere else; wraps all the way around on all four shell panels (same
    # pattern since they share one depth). offset is measured from the panel's depth center:
    # cherry at 0; each maple stripe touches the cherry's own edge, so its offset is half the
    # cherry's width plus half its own width = +/-(9.525 + 19.05).
    accent_stripes=((0.0, 19.05, "cherry"), (28.575, 38.1, "maple"), (-28.575, 38.1, "maple")),
)

try:
    spec = L.order_from(L.load_voicing(HERE / "voicing.json"), AESTHETICS)
except ValueError as e:
    print(f"input error: {e}")
    sys.exit(1)
lay = L.layout(spec)
checks = L.check_layout(lay, spec)

if os.environ.get("TMP_STL") or os.environ.get("EXPORT") or os.environ.get("SHOW"):
    import cabmodel as M
    cab = M.build(lay)
    checks += M.check_build(cab, lay)
    if os.environ.get("TMP_STL"):
        from build123d import export_stl
        export_stl(M.compound_of(cab.solids() + list(cab.components.values())), os.environ["TMP_STL"])
    if os.environ.get("EXPORT"):
        out = Path(os.environ.get("CAB_OUT") or HERE)
        files = M.export(cab, lay, checks, out)
        print(f"exported {files['step']} and {len(files['images'])} renders to {out}")
    if os.environ.get("SHOW"):
        from ocp_vscode import show
        show(*cab.solids(), names=[e["name"] for e in cab.parts])

for c in checks:
    print(f"{c.name:16s} {c.level:8s} {c.message}")
sys.exit(2 if any(c.level == "blocker" for c in checks) else 0)
