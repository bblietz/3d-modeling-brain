---
name: weber-silver-bell-alnico-hemp
type: speaker
brand: Weber
model: Silver Bell, Alnico, hemp cone, 75 W
diameter_in: 12
impedance_ohm: [4, 8, 16]
power_w: 75
sensitivity_db: 98
magnet: alnico
fs_hz: 80
re_ohm: 13.0
le_mh: null
qts: null
qes: null
qms: null
vas_l: null
xmax_mm: null
sd_cm2: null
cutout_mm: 273.0
bolt_circle_mm: 297
bolt_count: 4
depth_mm: 146.0
frame_diameter_mm: 308.0
magnet_diameter_mm: 135
magnet_diameter_estimated: true
weight_kg: 3.2
data_status: missing
sources: [https://www.tedweber.com/slvr12a/]
status: unverified-starting-values
---

# Weber Silver Bell, Alnico, hemp cone, 75 W

## Character

- low_end: balanced. mids: forward. top: dark. breakup: not stated by the
  maker; alnico speakers are generally reputed to compress smoothly, but
  this is not a claim Weber makes for this specific model, so treat
  breakup as unconfirmed rather than "early."
- Weber (standard paper-cone Silver Bell): "standard low end with a
  midrange bump, and clear articulate high end," likened to "a classic
  Marshall stack."
- Weber on the hemp cone option specifically: "darker, warmer, foggy and
  less focused," hemp's longer fibers giving the treble "a sub-harmonic
  richness that warms the sound," a mellower top end and less immediate
  attack than paper.

## Best with

- Amp families: Boutique clean, per this order's Ceriatone Overtone
  Special 50 (a Dumble-style clone); Weber's own copy also likens the
  standard paper Silver Bell to "a classic Marshall stack," though the
  hemp cone shifts that warmer and darker than paper.
- Genres: indie-alternative, blues, classic-rock

Chosen for this order against a boutique-clean amp for the hemp cone's
warm, non-strident character. Families and genres per [[speaker-cab-voicing]].

## Data notes

- Weber does not publish Thiele-Small parameters (Fs, Qts, Vas, Xmax) for
  any Silver Bell variant (checked the product page directly and a
  TalkBass thread of speaker builders confirming the omission is
  deliberate, not just missing from the web copy); `data_status: missing`
  and every T/S field is null. The engine uses the open-back rule-of-thumb
  volume and predicts no response curve for this driver, so the missing
  T/S has no effect on this order's box sizing.
- `fs_hz` (80), `re_ohm` (13.0), and `sensitivity_db` (98) are **not**
  Weber-published numbers; they are round, category-typical placeholders
  for a 16 ohm alnico 12 inch guitar driver (anchored loosely against
  Celestion Blue's published 75 Hz Fs as a same-category alnico
  reference), filled in only because the engine's schema requires a
  number in these three fields regardless of `data_status`. They are
  echoed onto the voicing sheet for reference but feed no calculation for
  a driver with no T/S data. Do not treat them as real Weber specs.
- Physical dimensions (weight 7.05 lb / 3.2 kg, overall diameter 12.125 in
  / 308 mm, depth 5.75 in / 146 mm without the cover, cutout 10.75 in /
  273 mm, 40 oz alnico magnet) are read directly from the Alnico Silver
  Bell product page. Cutout is Weber's own figure, not the catalog's usual
  283 mm generic 12 inch assumption.
- `bolt_circle_mm` (297) and `bolt_count` (4) are **not** from Weber's
  page (not published there); assumed as the common 4-bolt, ~297 mm PCD
  pattern shared by most American 12 inch guitar speakers (matches this
  catalog's Celestion Blue note). Brian: verify the actual bolt circle
  against the physical speaker or Weber's paperwork before drilling the
  baffle.
- Weber sells the Silver Bell as a build-to-order combination of magnet
  (ceramic or alnico), cone (standard paper or hemp), and power handling
  (15/30/50/75/100 W); this note documents the Alnico, hemp, 75 W
  configuration chosen for `Cab-ElShaieb-1x12-hardwood` on 2026-09-15
  (Brian, at intake). A different wattage or magnet needs its own note.
- Magnet diameter not published (only magnet weight, 40 oz); 135 mm
  is estimated from typical alnico 12 inch guitar speaker structures
  in this weight class (Celestion's alnico magnets run about 128 mm;
  Weber's 40 oz structure is in the same range), `magnet_diameter_estimated: true`.
  Verify before designing a closed-back envelope check around it.
  See [[speaker-envelopes-and-port-stock]].

## Field notes

- none yet
