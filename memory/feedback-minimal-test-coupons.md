---
name: feedback-minimal-test-coupons
description: Test coupons must contain only the feature under test; Brian objected twice to coupons that reprint layers or islands that do not matter
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 744ff3b5-47ea-4284-a4c0-57fb6e3fdbcb
  modified: 2026-08-25T04:52:47.343Z
---

When building a physical test coupon, crop it to the feature being judged and the minimum substrate under it (thin slab, a few layers of the layer it sits on), and quote the print time from a real slice before offering it.

**Why:** On 2026-08-22 Brian pointed out that a "30 min comparison plate" was really 2h18m because it printed the full tag base ("could have printed the top half or less"), and on 2026-08-24 asked why a letters-only coupon reprinted a 1.0 mm slab, the navy banner, and three unrelated islands (about 20 of 27 layers below the letters). Print time is his scarce resource; representativeness of the surrounding layers is only worth keeping when it changes the feature under test.

**How to apply:** Default coupon = feature + 0.2-0.3 mm of its substrate + a 0.3 mm slab, nothing else on the plate except the prime tower if colors change. State explicitly what representativeness was traded away (layer time, color-change cadence). See [[project-sharks-nametag-coupons]] and [[feedback-agentic-os-conventions]].
