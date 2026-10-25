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

## Update 2026-10-23

Height is 14 in top / 17 in seat (2026-10-09). Brian wants the room picture dimensionally true because the client signs off on it. Done: `photo_match.py` (camera match from the alcove's floor corners, CAD z-buffered into the photo at true scale, `check` mode measures Gemini's output against the projection) and the `guided` job in `render_in_room.py`; `images/bench-in-nook-guided.png` verified (edges on the projection, panel bottoms within 1/4 in); shop page Version 8 and the PDF carry it. The earlier wrong-height composites (`bench-in-nook-low*.png`) were deleted. Later the same day the client asked for the dog and the reference picture's items in the sign-off image: the `styled` job (`render_in_room.py styled`, edits the guided picture with `concept-ai-bench-web.jpg` as reference) made `images/bench-in-nook-styled.png`, re-checked within 1/4 in; shop page Version 9 carried it. Then the client's own dogs replaced the golden retriever: `render_in_room.py dogs` (edits the styled picture with `images/maizy.jpg` and `images/franco.jpg`) made `images/bench-in-nook-dogs.png`, re-checked within 1/4 in; shop page Version 10 carried it. Then the concept's dropped soffit with two downlights went in (picture only; final form 2026-10-24: a bulkhead flush with the pilaster faces, one band 12 in below the ceiling running from the left pilaster's outer edge across the alcove and both pilaster tops and on over the hallway opening past the frame edge, 28 in deep, as the concept draws it; the photo's ceiling measures 98.5 in through the camera, so the alcove ceiling becomes about 7 ft 2-1/2 in; constants SOFFIT_DROP, PILASTER_W, HALL_RUN, LIGHT_X in photo_match.py). Two wrong versions came first, a box between the pilasters (Version 11) and the same box set back 3 in (Version 12, invisible from this camera; Brian: "i dont see a change"); his note "flush with the front and then extends over the hallway" described the concept. `photo_match.py soffit images/bench-in-nook-dogs.png` makes the overlay, `render_in_room.py soffit` photorealizes it, `render_in_room.py soffit-paint` repaints the underside white (Gemini keeps it blue-grey otherwise, every time); `images/bench-in-nook-soffit-paint.png` checked within 1/4 in; shop page Version 13 and the PDF carry it. The picture is a chain guided -> styled -> dogs -> soffit -> soffit-paint -> walnut-shelves; any change reruns from the stage it touches, then `photo_match.py check` before showing it. 2026-10-24: Brian made the shelves walnut (picture only, matching the drawer panels, still Osmo Natural): `render_in_room.py walnut-shelves` edits the soffit-paint picture (`images/bench-in-nook-walnut-shelves.png`, checked within 1/4 in, compared side by side with the maple version); `photo_match.py` renders the shelves walnut in the overlay and the guided/styled/soffit prompts say walnut, so a rerun from guided needs no extra pass; shop page Version 14 and the PDF carry it. Then Brian made the top walnut too ("the benchtop should also be walnut"), a real design change: WALNUT_S ("solid walnut") on the top in `built_in_bench.py`, EXPORT=1 rerun (cut list: top 3/4 x 24-5/8 x 66 solid walnut), `part_drawings.py`, `hero_shot.py` (CUSHION=0) and `assembly_shots.py` rerun with "solid walnut" in their color maps, page intro and labels updated (solid walnut group first in the case list); `render_in_room.py walnut-top` edits the walnut-shelves picture (`images/bench-in-nook-walnut-top.png`; the top's front edge is only about 7 px tall from this camera, so it was verified by pixel sampling and a zoomed crop as well as `check`); shop page Version 15 and the PDF carry it. Chain: guided -> styled -> dogs -> soffit -> soffit-paint -> walnut-shelves -> walnut-top. Still open: site measurements, the receptacle, the Blum hook-bore scrap test, Brian's look at STILE_W, and the plinth (3 in) meeting the 4 in pilaster baseboards.

Height lowered 2 in 2026-10-09 (top 14 in, base 3 in, box 8.5 in); pipeline rerun and shop page republished (Version 5). Osmo Natural (clear) on the maple top and shelves.
