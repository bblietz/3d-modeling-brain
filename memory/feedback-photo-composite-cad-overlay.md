---
name: feedback-photo-composite-cad-overlay
description: "Client-facing room composites must be dimensionally true; project the CAD into the photo through a matched camera and let Gemini only add materials, then measure the output"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d3e73073-5ff1-4cf2-8b88-f1fd6660abc7
  modified: 2026-10-23T20:07:55.094Z
---

Brian signs clients off on the generated room picture, not on CAD drawings, so the picture has to show the design at its true size. Gemini cannot hold a dimension given in words ("the top is 14 inches") and drew the alcove bench about 6 in too tall from a prompt, twice (2026-10-23). What works: camera-match the room photo from known geometry (the alcove's four floor corners gave distance, focal length, height and lateral offset in closed form, verified against the 8 ft ceiling), z-buffer the CAD solids into the photo flat-shaded at true scale, and prompt Gemini to photorealize that overlay without moving an edge. Verify by drawing the projected outline over the output and measuring a distinctive feature (the walnut panels) in inches.

**Why:** a composite that misstates the height by 6 in on a 14 in seat is a false sign-off; Brian: "I want the generated image to realistically represent the design. The client will sign off on the generated image."

**How to apply:** for any photo composite of a design, reach for `projects/Built-in-bench/photo_match.py` (overlay + `check` mode) and the `guided` job in `render_in_room.py` as the template; never ask Gemini for sizes in words; never show Brian a composite without the overlay check; state the measured error in the reply. See [[project-built-in-bench]] and [[feedback-nanobanana-report-cost]].
