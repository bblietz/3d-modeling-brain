#!/usr/bin/env python
"""Lumber to buy for the freestanding bench, packed from the PARTS registry (Brian 2026-11-20: "add a section on
lumber I need to buy; assume 8 ft maple boards 1x6, full 4x8 sheets of plywood, no partial").

Stock: 1x6 x 8 ft S4S soft maple (3/4 x 5-1/2 x 96 actual) for every solid part (Brian 2026-11-20: "no hard maple,
all soft", and "i can't source 12/4 maple, so the legs will be made from 1x6") and 4 x 8 sheets for the ply. Parts
thicker than a board (the posts) become face-glued layers, each a planing allowance wider and an inch longer than
the part: four 3/4 layers make 3 in, planed to 2-1/2 square. Parts wider than a board (the top) become a glue-up
of strips, each a jointing allowance wider than its share and an inch longer for squaring the ends. Pieces are
shelf-packed onto each unit of stock, longest first, with a saw kerf between them: a shelf runs across the width
of the board or sheet and is as long as its longest piece. Solid parts keep their length along the board (grain);
sheet parts may turn. The 1/2 paint-grade ply panels come out of the 1/2 birch ply sheet with the back. Shelf packing wastes a little against
a careful layout, so a count here is safe, not minimal.

Run:  .venv/bin/python projects/Freestanding-bench/lumber_list.py   (prints the list; make_cutlist_page imports it)
"""
import math
import os
import sys

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
sys.path.insert(0, f"{VAULT}/projects/Freestanding-bench")
sys.path.insert(0, f"{VAULT}/scripts")
from cutlist import inch_frac  # noqa: E402

IN = 25.4
KERF = 0.125 * IN                # Brian 2026-11-20: all his circular blades are standard 1/8 in kerf
BOARD_T, BOARD_W, BOARD_L = 0.75 * IN, 5.5 * IN, 96 * IN   # 1x6 x 8 ft S4S
SHEET_W, SHEET_L = 48 * IN, 96 * IN
JOINT = 0.25 * IN                # lost per strip to jointing both edges in a glue-up
TRIM = 1.0 * IN                  # extra length on glue-up strips, for squaring the panel's ends
LAM_EXTRA = 0.125 * IN           # extra width on each post layer, planed off after the glue-up

# material -> (kind, stock name, note); kind "board" packs onto 1x6 boards, "sheet" onto 4 x 8 sheets;
# a material may point at another's stock to share it
STOCK = {
    "soft maple": ("board", "Soft maple 1x6 x 8 ft (3/4 x 5-1/2 actual)", "the top glue-up, the cleat, and the posts as four glued layers each"),
    "poplar": ("board", "Poplar 1x6 x 8 ft (3/4 x 5-1/2 actual)", "the drawer-front frames, painted white"),
    "3/4 birch ply": ("sheet", "3/4 birch plywood, paint grade, 4 x 8", "ends, bottom, partition"),
    "1/2 birch ply": ("sheet", "1/2 birch plywood, paint grade, 4 x 8", "the back and the two drawer-front panels"),
    "1/2 paint-grade ply": "1/2 birch ply",
    "1/2 Baltic birch": ("sheet", "1/2 Baltic birch, 4 x 8", "the four drawer boxes (a 5 x 5 sheet holds them too)"),
}


def fi(mm):
    return inch_frac(mm, 32)


def part_dims(solid):
    bb = solid.bounding_box()
    return sorted((bb.size.X, bb.size.Y, bb.size.Z))


def pieces_for(parts):
    """(material, name, w, l, turnable) per piece, qty expanded; wide solid parts become glue-up strips, thick ones layers"""
    out = []
    for p in parts:
        t, w, l = part_dims(p["solid"])
        stock = STOCK[p["material"]]
        mat = stock if isinstance(stock, str) else p["material"]
        kind = STOCK[mat][0]
        if kind == "board" and t > BOARD_T + 0.5:
            n = math.ceil(t / BOARD_T)
            for i in range(p["qty"] * n):
                out.append((mat, f"{p['name']} layer", w + LAM_EXTRA, l + TRIM, False))
            continue
        if kind == "board" and w > BOARD_W + 1e-6:
            n = math.ceil(w / (BOARD_W - JOINT))
            for i in range(p["qty"] * n):
                out.append((mat, f"{p['name']} strip", w / n + JOINT, l + TRIM, False))
        else:
            for i in range(p["qty"]):
                out.append((mat, p["name"], w, l, kind == "sheet"))
    return out


def pack(pieces, W, L):
    """shelf packing; returns a list of units, each a list of (name, w, l) placed on it"""
    units = []
    pieces = sorted(pieces, key=lambda x: (-max(x[2], x[3]), -min(x[2], x[3])))
    for name, w, l, turnable in pieces:
        orients = [(w, l)] + ([(l, w)] if turnable and w != l else [])
        placed = False
        for unit in units:
            for pw, pl in orients:
                if pw > W + 1e-6:
                    continue
                for shelf in unit["shelves"]:
                    if pl <= shelf["len"] + 1e-6 and shelf["used"] + KERF + pw <= W + 1e-6:
                        shelf["used"] += KERF + pw
                        shelf["pieces"].append((name, pw, pl))
                        placed = True
                        break
                if placed:
                    break
                if sum(s["len"] for s in unit["shelves"]) + KERF * len(unit["shelves"]) + pl <= L + 1e-6:
                    unit["shelves"].append({"len": pl, "used": pw, "pieces": [(name, pw, pl)]})
                    placed = True
                    break
            if placed:
                break
        if not placed:
            pw, pl = min(orients, key=lambda o: o[0]) if any(o[0] <= W for o in orients) else orients[0]
            for o in orients:
                if o[0] <= W + 1e-6 and o[1] <= L + 1e-6:
                    pw, pl = o
                    break
            assert pw <= W + 1e-6 and pl <= L + 1e-6, f"{name} {fi(w)} x {fi(l)} does not fit a {fi(W)} x {fi(L)} unit"
            units.append({"shelves": [{"len": pl, "used": pw, "pieces": [(name, pw, pl)]}]})
    for u in units:
        u["pieces"] = [p for s in u["shelves"] for p in s["pieces"]]
        u["yield"] = sum(pw * pl for _, pw, pl in u["pieces"]) / (W * L)
    return units


def lumber_lines(parts):
    """[(qty, stock, note, [unit descriptions])] in buying order"""
    pieces = pieces_for(parts)
    lines = []
    for mat, spec in STOCK.items():
        if isinstance(spec, str):
            continue
        kind, stock, what = spec
        mine = [(n, w, l, t) for m, n, w, l, t in pieces if m == mat]
        if not mine:
            continue
        W, L = (BOARD_W, BOARD_L) if kind == "board" else (SHEET_W, SHEET_L)
        units = pack(mine, W, L)
        descs = []
        for i, u in enumerate(units, 1):
            names = {}
            for n, pw, pl in u["pieces"]:
                names[n] = names.get(n, 0) + 1
            descs.append(f"{'board' if kind == 'board' else 'sheet'} {i}: " +
                         ", ".join(f"{c} {n}" if c > 1 else n for n, c in names.items()) +
                         f" ({u['yield']:.0%} of it)")
        lines.append((f"{len(units)} {'board' if len(units) == 1 else 'boards'}" if kind == "board"
                      else f"{len(units)} {'sheet' if len(units) == 1 else 'sheets'}", stock, what, descs))
    return lines


if __name__ == "__main__":
    import freestanding_bench as M
    for qty, stock, what, descs in lumber_lines(M.PARTS):
        print(f"{qty:>9}  {stock}: {what}")
        for d in descs:
            print(f"{'':>11}{d}")
