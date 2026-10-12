"""Trace the Dunlop Tortex 1.0 mm pick outline from Brian's two caliper photos.

    .venv/bin/python projects/Guitar-pick/pipeline/trace_photo.py

Each photo shows the pick clamped in digital calipers, so the pick's extent
along the jaw axis (vertical in both photos) IS the caliper reading. That
gives the mm/px scale per photo without a ruler, and the other axis of each
photo cross-checks the other photo's reading.

Outputs
- images/trace-overlay.png: each photo with its contour, plus the two traces,
  their symmetrized average, and the generic 351 outline in one mm frame.
- outline-dunlop.csv: the measured outline, tip toward -Y, top edge at y=0,
  scaled so width and length equal the caliper readings exactly.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import rgb_to_hsv
from PIL import Image
from scipy import ndimage
from scipy.signal import savgol_filter
from shapely.geometry import MultiPoint, Polygon

PROJECT = Path(__file__).resolve().parent.parent
IMG = PROJECT / "images"

WIDTH, LENGTH = 26.19, 30.38                 # caliper readings, mm
PHOTOS = {"IMG_1656.jpg": WIDTH, "IMG_1657.jpg": LENGTH}   # reading taken along image Y
PRIMARY = "IMG_1657.jpg"
N_ANG = 720


def pick_field(im):
    """1 inside the pick, 0 outside, continuous across the edge pixels.

    The Tortex blue is saturated (s >= 0.6); the caliper steel reflects a dull
    blue at s <= 0.4, so saturation is the separator, ramped 0.35..0.65 so the
    edge keeps subpixel information for the contour.
    """
    hsv = rgb_to_hsv(np.asarray(im.convert("RGB")).astype(float) / 255)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    f = np.where((h > 0.52) & (h < 0.72) & (v > 0.20), np.clip((s - 0.35) / 0.30, 0, 1), 0.0)
    m = f > 0.5
    lab, n = ndimage.label(m)
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    m = ndimage.binary_fill_holes(lab == (np.argmax(sizes) + 1))   # the printed logo is a hole
    f = f * ndimage.binary_dilation(m, iterations=2)                # drop everything else
    f[ndimage.binary_erosion(m, iterations=2)] = 1.0                # interior (logo included) solid
    return f


def contour_px(field):
    """Subpixel outer contour (x, y) in pixels, image y down."""
    f = ndimage.gaussian_filter(field, 0.5)
    cs = plt.contour(f, levels=[0.5])
    plt.close()
    best = None
    for p in cs.get_paths():
        for poly in p.to_polygons():
            if best is None or len(poly) > len(best):
                best = poly
    return np.asarray(best)


def align_mm(pts_px, scale):
    """Scale to mm, rotate the long axis to Y with the tip at -Y, centre X, top at y=0."""
    pts = pts_px * scale
    pts[:, 1] *= -1                            # image y down -> mm y up
    poly = Polygon(pts)
    c = np.array(poly.centroid.coords[0])
    q = pts - c
    w, v = np.linalg.eigh(np.cov(q.T))
    ax = v[:, np.argmax(w)]
    th = np.pi / 2 - np.arctan2(ax[1], ax[0])  # rotate the long axis onto +Y
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    q = q @ R.T
    # the tip is the end farther from the centroid (the 351 is top-heavy)
    if q[:, 1].max() > -q[:, 1].min():
        q[:, 1] *= -1
    q[:, 0] -= (q[:, 0].max() + q[:, 0].min()) / 2
    q[:, 1] -= q[:, 1].max()
    return q


def polar(pts, cy):
    """r(phi) about (0, cy), phi measured from +Y toward +X, resampled on a uniform grid."""
    d = pts - np.array([0.0, cy])
    phi = np.arctan2(d[:, 0], d[:, 1])
    r = np.hypot(d[:, 0], d[:, 1])
    order = np.argsort(phi)
    phi, r = phi[order], r[order]
    grid = np.linspace(-np.pi, np.pi, N_ANG, endpoint=False)
    return grid, np.interp(grid, np.concatenate([phi - 2 * np.pi, phi, phi + 2 * np.pi]),
                           np.concatenate([r, r, r]))


def from_polar(grid, r, cy):
    return np.column_stack([r * np.sin(grid), cy + r * np.cos(grid)])


def size(pts):
    return pts[:, 0].max() - pts[:, 0].min(), pts[:, 1].max() - pts[:, 1].min()


def tip_radius(pts, band=2.5):
    """Least-squares circle through the outline points within `band` mm of the tip."""
    p = pts[pts[:, 1] < pts[:, 1].min() + band]
    A = np.column_stack([2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))])
    b = (p ** 2).sum(axis=1)
    (cx, cy, c), *_ = np.linalg.lstsq(A, b, rcond=None)
    return np.sqrt(c + cx ** 2 + cy ** 2)


def widest_y(pts):
    """How far below the top edge the outline is widest."""
    _, r = polar(pts, 0.0)                       # unused grid; just reuse the resampler
    return pts[:, 1].max() - pts[np.argmax(pts[:, 0]), 1]


def main():
    traces, crops = {}, {}
    for name, reading in PHOTOS.items():
        im = Image.open(IMG / name)
        cpx = contour_px(pick_field(im))
        extent_px = cpx[:, 1].max() - cpx[:, 1].min()     # along the jaw axis
        scale = reading / extent_px
        pts = align_mm(cpx, scale)
        w, l = size(pts)
        print(f"{name}: {extent_px:.1f} px across the jaws -> {scale:.4f} mm/px; "
              f"traced width {w:.2f} mm, length {l:.2f} mm")
        traces[name] = pts
        crops[name] = (im, cpx)

    # IMG_1656 is clipped: the pick's top sits under the caliper beam, so only
    # IMG_1657 (whole outline visible) is used for the shape. 1656 is kept as a
    # cross-check on the tip, which it does show.
    cy = -LENGTH / 2
    grid, r = polar(traces[PRIMARY], cy)
    r = (r + r[::-1]) / 2                        # phi -> -phi mirror (grid is symmetric about 0)
    r = savgol_filter(r, 11, 3, mode="wrap")     # 11 samples = 5.5 deg, about 1.4 mm of arc at the tip

    pts = from_polar(grid, r, cy)
    hull = Polygon(np.asarray(MultiPoint(pts).convex_hull.exterior.coords)[:-1]).simplify(0.02)
    out = np.asarray(hull.exterior.coords)[:-1]
    w, l = size(out)
    out[:, 0] *= WIDTH / w                      # calipers beat the trace on absolute size
    out[:, 1] *= LENGTH / l
    out[:, 1] -= out[:, 1].max()
    out[:, 0] -= (out[:, 0].max() + out[:, 0].min()) / 2
    final = Polygon(out)
    print(f"final outline: {len(out)} points, width {size(out)[0]:.2f}, length {size(out)[1]:.2f}, "
          f"area {final.area:.1f} mm2, convex {final.equals(final.convex_hull)}")
    np.savetxt(PROJECT / "outline-dunlop.csv", out, fmt="%.4f", delimiter=",",
               header="x_mm,y_mm  Dunlop Tortex Standard 1.0 outline traced from caliper photos IMG_1656/1657 (tip toward -Y, top edge at y=0)")

    # compare with the generic 351 outline scaled to the same width and length
    gen = np.loadtxt(PROJECT / "outline-351.csv", delimiter=",")
    gw, gl = size(gen)
    gen[:, 0] *= WIDTH / gw
    gen[:, 1] *= LENGTH / gl
    _, r_gen = polar(gen, cy)
    _, r_fin = polar(out, cy)
    d = r_fin - r_gen
    print(f"measured vs generic 351 (same width/length): max |dr| {np.abs(d).max():.2f} mm, "
          f"rms {np.sqrt((d**2).mean()):.2f} mm")
    # where does it differ most: report by angle from the top (0 = top centre, 180 = tip)
    i = np.argmax(np.abs(d))
    print(f"largest difference at {np.degrees(grid[i]):.0f} deg from the top centre "
          f"(measured r {r_fin[i]:.2f} vs generic {r_gen[i]:.2f})")
    for label, o in (("measured", out), ("generic 351", gen), ("trace 1656 (tip only)", traces["IMG_1656.jpg"])):
        print(f"{label}: tip radius {tip_radius(o):.2f} mm, widest point {widest_y(o):.1f} mm below the top")

    fig, axs = plt.subplots(1, 3, figsize=(16, 7))
    for ax, (name, (im, cpx)) in zip(axs[:2], crops.items()):
        x0, x1 = cpx[:, 0].min() - 15, cpx[:, 0].max() + 15
        y0, y1 = cpx[:, 1].min() - 15, cpx[:, 1].max() + 15
        ax.imshow(im)
        ax.plot(cpx[:, 0], cpx[:, 1], "r-", lw=1)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y1, y0)
        ax.set_title(f"{name}: traced contour")
        ax.axis("off")
        # standalone crop for the comparison page
        f2, a2 = plt.subplots(figsize=(4, 4 * (y1 - y0) / (x1 - x0)))
        a2.imshow(im)
        a2.plot(np.append(cpx[:, 0], cpx[0, 0]), np.append(cpx[:, 1], cpx[0, 1]), "-", color="#ff2d2d", lw=1.2)
        a2.set_xlim(x0, x1)
        a2.set_ylim(y1, y0)
        a2.axis("off")
        f2.subplots_adjust(0, 0, 1, 1)
        f2.savefig(IMG / f"trace-{name[4:8]}.png", dpi=150)
        plt.close(f2)
    ax = axs[2]
    for (name, t), col, note in zip(traces.items(), ("tab:orange", "tab:green"),
                                    (" (top clipped by the beam, tip cross-check only)", " raw")):
        ax.plot(*np.vstack([t, t[:1]]).T, color=col, lw=0.8, label=f"trace {name[4:8]}{note}")
    ax.plot(*np.vstack([out, out[:1]]).T, "k-", lw=2, label="measured: 1657 symmetrized + smoothed")
    ax.plot(*np.vstack([gen, gen[:1]]).T, "b--", lw=1.2, label="generic 351 scaled to size")
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3)
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title(f"mm frame: {WIDTH} x {LENGTH}")
    fig.tight_layout()
    fig.savefig(IMG / "trace-overlay.png", dpi=110)
    print("wrote", IMG / "trace-overlay.png")


if __name__ == "__main__":
    main()
