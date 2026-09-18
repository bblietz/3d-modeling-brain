---
name: feedback-check-docking-and-hold-kinematics
description: For any fixed hook, cleat or latch, check the way in AND what the hanging load does; if docking is the load's own motion run backwards it cannot hold. A docked-pose clash check proves neither.
metadata:
  type: feedback
---

On the NACS wall holder (2026-09-18) six cavity versions passed a docked-pose clash check and close-up renders, yet the design could not work: the nose was meant to be lifted over a fixed cleat under a relieved roof, and the hanging weight (far out on the grip) levers the wand about the mouth's lip, tip up and pocket up, which is that same lift run backwards. A path search showed that any snug-roof length short enough to let the wand in also let its own weight take it out (load rise needed: 0.2 mm), and any longer one locked it out. Brian had reported "the cleat is too small" twice; the cleat was never the problem. His instinct that the snug section "should extend further out" was right.

**Why:** a retention feature is a mechanism, not a shape. The docked pose says nothing about whether the part can get there, or whether the service load can drive it back out. Friction is not a hold.

**How to apply:** before any coupon of a hook, cleat, bayonet or drop-in latch: (1) name the docking motion and the motion the service load produces, and make sure the load's motion is not the docking motion reversed; (2) run a pose-space check with the real mating geometry: a collision-free way in with the part grown about 0.2 mm, and the hold measured as how far the load must be raised against gravity to come off, frictionless; (3) use the mating part's real mesh, not an extruded outline (Tesla's nose tapers 0.75 mm toward the tip, which decided the answer). Working tool: `projects/NACS-wall-holder/pipeline/insertion.py` (side-view slices, slide/lift/tilt grid, WAY IN and HOLD). Shape the cavity as the swept room of the chosen docking motion (hull of the snug cavity with its tilted copies), not as a step relief. Related: [[feedback-verify-retention-features-closeup]], [[feedback-minimal-test-coupons]], [[feedback-openscad-for-complex-designs]].
