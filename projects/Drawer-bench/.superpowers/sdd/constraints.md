## Global Constraints

- All modeling in mm; `IN = 25.4`. Inches only appear in the cut list output.
- Coordinates: X = width (0 at the LEFT edge of the TOP), Y = depth (0 at the FRONT edge of the TOP), Z = height (0 at the floor). Posts start at (OH, OH).
- Provisional inputs, verbatim from design.md, as named constants: top 36 x 24 in, height 20 in, top thickness 1-3/4 in, overhang 1-1/4 in, 3/4 ply = 18.0 mm, 1/2 ply = 12.0 mm, slides 18 in. Nothing is cut from them.
- Locked design values: posts 3 in square, 3/8 in chamfer on all four vertical edges full length, no foot taper; panels 1/2 in behind the post faces in 3/4 (= T18) x 3/8 grooves stopped 1-1/2 in above the floor and open at the top; front frame 1 in behind the post faces, rails stub-tenoned 3/8 in; rails 1 / 1 / 1-1/2 in tall (top / mid / bottom); bottom 1/2 ply in 1/4 in grooves, top face 2-1/4 in above the floor; drawer fronts 3/4 in thick, 1/4 in behind the post faces, reveals 1/8 in to posts, 1/4 in between, 1/8 in under the top, 3/4 in floor gap, heights 5-3/4 and 11-3/8 in; undermount geometry per cabinet-bench (box width = opening - 10 mm, 12.7 mm recess, 20 mm tilt clearance, 9 mm rear clearance, 8 mm standoff).
- Resolutions the CAD forces (record in design.md in Task 9): top drawer opening is 4-1/2 in so BOX_TOP_H = 3-1/4 in and BOX_BOT_H = 8-1/4 in; the front-frame groove stops at the floor gap (3/4 in) so the bottom rail's tenon is housed; the rear top rail is 1-1/2 in tall, tenoned into the back groove line, and the back panel runs from the groove stop to the rail's underside (15-1/4 in); rails are milled to the measured ply thickness (RAIL_T = T18) so the stub tenons fill the same grooves.
- One named solid per registry part; qty > 1 copies are mirrored/placed for the assembly only. Exactly one solid per registry entry, no cross-part overlaps (volume of every pairwise intersection = 0).
- No git repository: there are no commit steps. The "commit" of each task is a passing run plus a viewed PNG.
- Run everything from the vault root `/home/brian/ClaudeProjects/3d-modeling-brain`. Scratch files go in `/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/9f86504f-96cd-4f66-8d18-d5c6b8b10a65/scratchpad` (call it `$SCRATCH` below).
- Do not touch Cabinet-bench files, `scripts/`, or `knowledge/woodworking-stock.md` (measured values are promoted only after a real build).

