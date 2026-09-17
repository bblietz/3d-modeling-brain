---
type: project
project: NACS-wall-holder
date: 2026-09-16
status: brief - spec and CAD retrieved; next, extract nose and lock-notch geometry, then the design plan
tags: [x2d, nacs, tesla, wall-mount]
---

# NACS wall holder (Tesla Wall Connector Gen 3, 48A)

Our own design for a wall-mounted dock for Brian's Tesla Gen 3 Wall Connector handle, with a cable wrap hook.

## Decisions already locked (2026-09-16)

- Handle: Tesla Wall Connector Gen 3 (AC, 48A).
- Docking: the handle goes in nose-down, angled, like a gas pump holster.
- Retention: a FIXED cleat (rigid tab) inside the socket, NO spring tab. The opening is oversized so the plug nose can pass over the cleat on the way in, then settle so the cleat holds it; the nose-down angle lets gravity keep it seated. Brian 2026-09-16: "do not use a spring tab... the tab should be fixed and the opening should be big enough to fit over the tab".
- Cable: include a cable wrap hook, sized for the 18 ft (5.5 m) Gen 3 cable.
- No geometry from the licensed Printables organizer (CC BY-NC-SA, [[NACS-organizer]]); it is a measurement reference only.

## Sources

- Face size, reference values only: Amphenol NACS datasheet (amphenol.co.jp/military/catalog/NACS.pdf), AC connector face 41 mm wide x 36 mm nose height, 52 mm at the front with the handle, 194 mm long.
- Full Tesla spec set, retrieved 2026-09-16 into `spec/` (Tesla unlinked it in 2024 when SAE J3400 replaced it):
  - `TS-0023666-NACS-Technical-Specification.pdf` (30 pages; section 7 is connector, inlet and system mechanics)
  - `NACS-AC-Charging-Connector-Datasheet.pdf`: the Tesla North American 48A AC connector, Brian's handle
  - `NACS-DC-Charging-Connector-Datasheet.pdf` and `NACS-AC-DC-Pin-Sharing-Appendix.pdf`
  - Official CAD: `NACS-500V-Connector-and-Inlet.stp`, `NACS-1kV-Connector.stp`, `NACS-1kV-Inlet.stp`
- How it was retrieved: the Wayback search API was blocked by the archive's bot protections (HTTP 429/503). The archived Oct 2023 `tesla.com/support/charging/product-guides` page still loads and gave the real links. The archive's STEP copies are Common Crawl captures truncated at 1 MiB, but `digitalassets.tesla.com/tesla-contents/raw/upload/v1681681730/<file>.stp` still serves the complete files.

## Reference socket measurements (organizer STL, measured only)

- Sideways socket, 40 mm deep to a square stop face; shield cross-section, widest just above center.
- Width 43.5 at the mouth, 41.2 at 8 deep, 40.9 at 16 deep, 39.7 at the stop.
- Height (square to the axis) about 38.5 at the mouth, 36.5, then 35.8 at 16 deep.
- About 2.5 mm clearance at the mouth, near line-to-line by 16 mm deep. The stop is narrower than Amphenol's 41 mm Ref width, so the nose likely tapers.
- Retention: a spring tab in the floor, about 12 wide x 2.7 thick x 22 long, with a 2 mm bump (rejected for our design: fixed cleat instead).
- Cable hook: trough 60 wide, lip 15 to 19 above the saddle.

## Open

- Cleat position and size: design it to engage the lock notch on the top of the connector nose (the one the car's charge-port lock pin enters), from the Tesla spec once retrieved. The cleat and the extra opening room both depend on that notch's location and depth.
- Cable diameter: unknown (Brian 2026-09-16). Working value about 18 mm (0.7 in, owner report on Tesla Motors Club thread 199159, not official). Size the hook generously for 16 to 22 mm cable (lip height and wrap width from a `CABLE_OD` constant set to 22) so an unmeasured cable still fits. Optional check: wrap a paper strip around the cable, mark the overlap, and divide that length by 3.14. The cable is 18 ft (5.5 m), so a hook loop about 300 mm around takes roughly 5 to 6 wraps side by side, about 100 mm of hook width.
- The Gen 3 handle has a button on top that opens the car's charge port; the holster must not press it.
