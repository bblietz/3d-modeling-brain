"""Order rex-roots-1x12: Pat Player's 1x12 closed-ported tolex cab, Eminence Cannabis Rex 8 ohm."""
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
    corner_joint="finger",          # "dovetail" on the hardwood line only
    baffle_mount="floating",        # or "fixed" (glued into 6 mm dados)
    handle="strap",                 # or "recessed-side"
    corners="black",                # "black", "chrome", or "none"
    piping=False,
    feet="rubber",                  # or "tilt-back"
    tolex_roll_in=54,               # 54 for British and Fender black, 32 for tweed
    tolex_color="Fender Style Black",
    grill_cloth="Salt-and-pepper",
    head_width_mm=None,             # set to match a head: external width = head + 0 to 10 mm
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
