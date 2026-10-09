---
type: handoff
project: Built-in-bench
updated: 2026-10-07
---

# Built-in bench handoff

State: build123d model `built_in_bench.py` passes all asserts; `cutlist.md/.csv`, STEP, renders, `hero_shot.py`, `part_drawings.py`, `make_cutlist_page.py`, `cutlist.html` written 2026-10-07; shop page published at https://claude.ai/artifact/YQFcx4g5x64K83yhDHvGMf (republish the same file path to update). Waiting on Brian's look at the viewer and the three on-site measurements.

## Decisions already locked

- Picks from the options tool: A2 wood top at 16 in, B2 flush base, C2 frameless full overlay, D1 flat fronts, E1 8 in brass bar pull, F2 3/4 overhang eased edge, G2 solid glued-up maple top, H1 one full-depth cushion, I1 21 in Blum TANDEM 563H, J2 clear maple body.
- Brian 2026-10-07: fronts are 3/4 walnut veneer ply with maple around the outside on his tongue-and-groove router set; the rail tenon showing on the stile top is fine. The top's front edge is 3 in back from the pilaster faces.
- Fixed facts: opening 66 x 28; undermount slides; baseboard inside the alcove comes out; plumbing is in the wall; outlet is above bench height (photo shows a low receptacle, confirm on site).

## My calls (change via constants if Brian objects)

- STILE_W 1-1/2 in maple frame on the fronts.
- Case front edge at 23-1/2 from the wall; scribe strips 1-23/32 covering the end panels' front edges; fronts 31-3/32 x 11-1/8.
- Drawer boxes: 1/2 Baltic birch sides and bottom, 3/4 maple ply box front and back (back groove 3/16 so the Blum hook bores stay in wood).
- Nailer 3/4 x 2-1/2 solid maple on edge at the top back with 4 figure-8s; pocket screws at the front; no front stretcher (the box top is above it).
- Base is a 4 in ladder of any 3/4 ply; plinth 3-7/8 scribed, 1/8 reveal under the fronts.

## Next

1. Brian views the model (`SHOW=reset .venv/bin/python projects/Built-in-bench/built_in_bench.py` with `scripts/cad-viewer.sh` open) and OKs the frame width.
2. On-site measurements, then re-run `EXPORT=1`, `part_drawings.py`, `hero_shot.py`, `assembly_shots.py`, `make_cutlist_page.py`, `make_pdf.py` (cutlist.pdf), and republish cutlist.html to the same artifact URL with the images under images/parts and images/assembly.

## Update 2026-10-09 (late)

Decisions locked: 1/2 walnut ply panels inset 1/4 (back flush with the frame); frames, plinth, strips painted white (panels, top, shelves bare); every drawer box part is 1/2 9-ply Baltic birch (no back groove, bottom butts the back; locking-device screws #6 x 1/2). Pipeline rerun: EXPORT=1, part_drawings, hero_shot (CUSHION=0), assembly_shots, make_cutlist_page (now includes the alcove picture with shelves), make_pdf (20 pages), shop page republished as Version 4. Open: test-drill a scrap 1/2 BB back for the Blum hook bore (2 mm skin), site measurements, receptacle, the nook composite predates the inset.

Height lowered 2 in 2026-10-09 (top 14 in, base 3 in, box 8.5 in); pipeline rerun and shop page republished (Version 5). Osmo Natural (clear) on the maple top and shelves.
