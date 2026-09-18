---
name: feedback-verify-retention-features-closeup
description: Hooks, cleats, barbs and snap lips must be checked in a close-up section render before any print; a sign error made a "hook" a draft for five versions
metadata:
  type: feedback
---

On the NACS wall holder (2026-09-17) the cleat's "10 degree undercut" was built leaning the wrong way: the top of the holding face was set back toward the mouth, so it was a draft, not a hook. It passed five design rounds and a printed coupon because every section render was zoomed out to the whole cavity, where a 0.4 mm lean on a 2.2 mm bump is invisible. Brian found it on the printed part: "the cleat is too small ... so it can catch the wand better".

**Why:** a retention feature works or fails on the direction of one small face. Whole-part renders and watertight or clash checks cannot show that, and a coupon print costs him 1.5 hours.

**How to apply:** for any hook, cleat, barb, detent or snap lip, render a close-up section of just that feature with the mating part docked, before exporting anything, and state in words which way the holding face leans and where the contact point is. Size the feature from the mating pocket's measured section (spec plus CAD), not from a guess. Working example: `images/scad/cleat-detail.png` and the `cleat-detail` camera in projects/NACS-wall-holder/render.sh. Related: [[feedback-minimal-test-coupons]], [[feedback-openscad-for-complex-designs]], [[feedback-friction-fit-recipe]].
