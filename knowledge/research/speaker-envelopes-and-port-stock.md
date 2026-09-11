---
name: speaker-envelopes-and-port-stock
description: Web research (2026-09-10) on 12 inch guitar speaker frame and magnet diameters for the catalog, purchasable round port tube stock, and common hardware cutout sizes
type: reference
status: research
created: 2026-09-10
tags: [knowledge, speaker-cab, speakers, hardware, research]
---

# Speaker envelopes, port tube stock, hardware cutouts

Research run for the Plan 2 brainstorm ([[2026-09-10-plan-2-generator-design]]). The cabinet generator needs a magnet and frame envelope for its interference checks, a table of purchasable tube inside diameters for port rounding, and hardware cutout starting values. Every estimate is marked; "not published" means the maker prints nothing.

## Part A: frame and magnet envelope

Frame outer diameter is published by every maker. Magnet outer diameter is published only by Celestion (product pages plus the chassis drawing on page 33 of the Guitar Speaker Catalogue PDF) and Jensen (dimensional drawings served as SVG). Eminence spec sheets carry no mechanical drawing and give magnet weight only. WGS publishes no magnet data.

| Slug | Frame OD mm | Magnet OD mm | Magnet depth mm | Overall depth mm | Status |
|---|---|---|---|---|---|
| celestion-blue | 309 | 128 (alnico can) | 73 | 165 | published |
| celestion-cream | 309 | 128 (alnico can) | 73 | 165 | published |
| celestion-gold | 309 | 128 (alnico can) | 73 | 165 | published |
| celestion-g12-65-heritage | 309 | 145 | 34 | 128 | published |
| celestion-g12m-25-greenback | 309 | 150 | 39 | 130 | published |
| celestion-g12m-65-creamback | 309 | 150 | 39 | 130 | published |
| celestion-vintage-30 | 309 | 156 | 38 | 135 | published |
| celestion-g12h-30-anniversary | 309 | 156 | 38 | 135 | published |
| celestion-g12h-75-creamback | 309 | 168 | 44 | 138 | published (catalogue misprints 188 mm; 6.6 in is 168) |
| celestion-heritage-g12h55 | 309 | 168 | not published | 135 | published |
| jensen-c12n | 307.0 | 134.0 | 30.0 | 121.0 | published |
| jensen-p12n | 307.0 | 160.0 (bell), bare slug 98.0 | 81.4 | 169.4 | published |
| eminence-cannabis-rex | 305.6 | 135 to 150 | not published | 129.5 | estimated |
| eminence-red-white-and-blues | 305.6 | 135 to 150 | not published | 129.5 | estimated |
| eminence-texas-heat | 305.6 | 135 to 150 | not published | 129.5 | estimated |
| eminence-swamp-thang | 305.6 | 163 to 181 | not published | 132.1 | estimated |
| eminence-tonker | 305.6 | 163 to 181 | not published | 132.1 | estimated |
| wgs-et65 | 309.6 | 145 to 150 | not published | 128.6 | estimated |
| wgs-green-beret | 309.6 | 145 to 150 | not published | 128.6 | estimated |
| wgs-veteran-30 | 309.6 | about 156 | not published | 131.8 | estimated |

Sources: celestion.com product pages for each model and celestion.com/wp-content/uploads/2020/03/Guitar_Speaker_Catalogue.pdf; jensentone.com dimensional drawing SVGs (c12n_drawing.svg, p12n_drawing.svg); Eminence PDFs on cdn.shopify.com (Cannabis_Rex.pdf, Red_White_and_Blues.pdf, Texas_Heat.pdf, Swamp_Thang.pdf, Tonker.pdf); wgsusa.com product pages.

Basis of the Eminence estimates: sintered ferrite at 4.85 g/cm3, the published magnet weight, a ring bore of about 60 mm, ring height 15 to 19 mm, calibrated against Celestion's published pairs (35 oz reads 150 mm, 50 oz reads 156 to 168 mm). WGS estimates are by analogy to the Celestion model each clones (weight and depth within a few percent); they are the weakest rows.

Cover caveat: Celestion's figure is the bare ceramic ring. A covered model (the green-cover G12H family) is wider by an unpublished 4 to 12 mm on diameter. The generator adds a 12 mm cover allowance to every magnet diameter.

Data corrections for the catalog notes: the catalogue misprint above, and celestion.com/wp-content/uploads/2019/10/141.pdf is Voice Coil magazine (February 2015), not a Celestion spec sheet.

Recommended envelope (adopted in the design): a frame disc at the note's frame diameter for the first 100 mm behind the baffle front face (Celestion chassis depths run 91 to 97 mm, Jensen 88 to 91), then the magnet cylinder at the note's magnet diameter plus 12 mm, 185 mm where the note has none, total length the note's depth. A single 185 mm full-depth cylinder overstates the alnico Celestions and the Jensen C12N four to eight times by swept volume, which is why the two-step form is used.

## Part B: round port tube stock (US)

ASTM D2661 ABS DWV is made to Schedule 40 iron pipe sizes, so ABS DWV and PVC Schedule 40 share wall and inside diameter. Charlotte's PVC DWV pipe is dual-marked D1785 and D2665 solid-wall Schedule 40. Thin-wall sewer and drain pipe is D2729 on a different outside-diameter series.

| Nominal | Standard | OD mm | ID mm | Wall mm |
|---|---|---|---|---|
| 2 in | PVC Sch 40 and ABS DWV | 60.3 | 52.0 | 3.9 |
| 3 in | same | 88.9 | 77.3 | 5.5 |
| 4 in | same | 114.3 | 101.5 | 6.0 |
| 6 in | same | 168.3 | 153.2 | 7.1 |
| 3 in | PVC thin-wall D2729 | 82.6 | 79.0 (derived) | 1.8 |
| 4 in | PVC thin-wall D2729 | 107.1 | 103.3 (derived) | 1.9 |
| 6 in | PVC thin-wall D2729 | 159.4 | 154.3 (derived) | 2.5 |

Schedule 40 inside diameters are published averages; D2729 inside diameters are derived from OD minus twice the minimum wall. Sources: charlottepipe.com PVC DWV submittal and DC-DWV catalog, jmeagle.com ABS sheet, piping-world.com D1785 table.

Precision Port flared kits (Parts Express 268-348, 268-350, 268-352; inch values converted):

| Spec | 2 in | 3 in | 4 in |
|---|---|---|---|
| Tube ID mm | 50.80 | 76.20 | 101.60 |
| Tube OD mm | 53.98 | 79.38 | 104.78 |
| Face flange OD mm | 133.35 | 158.75 | 184.15 |
| Inner flare max OD mm | 108.0 | 133.35 | 158.75 |
| Baffle cutout mm | 107.95 | 133.35 | 158.75 |
| Flare part overall length mm | 63.50 | 76.20 | 76.20 |
| Minimum assembled length mm | 101.60 | 127.00 | 127.00 |
| Maximum assembled length as shipped mm | 279.40 | 431.80 | 431.80 |

Model the inner flare's clearance as a cylinder of the inner-flare OD over the flare's overall length inward from the panel. Flange thickness is not published.

Parts Express straight flanged tubes (ID x length, mm): 260-402 38.1 x 101.6; 260-406 44.45 x 57.15; 260-407 44.45 x 101.6; 260-409 69.85 x 120.65; 260-404 76.2 x 114.3; 260-411 tapered 100.0 to 98.4 x 114.3; 260-478 63.5 x 215.9; 260-480 95.25 x 193.68; adjustable 260-388 34.93 x 109.5 to 219.1, 260-387 50.8 x 152.4 to 279.4, 260-386 63.5 x 109.5 to 219.1, 260-329 109.54 x 158.75 to 298.45.

What builders use: round rear port tubes are a bass-cab convention, not a guitar-cab one. Avatar's guitar cabs are closed with no port while its bass cabs are front slot ported; Mesa's 1x12 Boogie Thiele is closed-back and front ported; the EV TL806 builders' plan (the canonical vented 1x12 for the EVM12L) uses a rectangular slot at the bottom of the front baffle with the depth set by a 3/4 x 3.5 in strip; Friedman's 212 cabs are "rear-ported, closed-back" with no published geometry; the only round-tube precedent with a stated size is a bass-cab spreadsheet author on TalkBass using 3 in Schedule 40 PVC (77.3 mm ID). Sources: avatarspeakers.com G212 and B410, mesaboogie.com Boogie Thiele, nexp.pt TL806_Builders_Plans.pdf, friedmanamplification.com, talkbass.com thread 707950.

Adopted starting tube table: Schedule 40 inside diameters 52.0, 77.3, 101.5, 153.2 mm, flagged unverified until Brian buys stock.

## Part C: hardware cutouts

| Item | Key dimensions | Cutout or recess | Screw pattern | Source |
|---|---|---|---|---|
| Marshall style rectangular jack dish (CJP-1) | plate not published | cutout 76.2 x 87.3 mm; depth not published | not published | amprepairparts.com jackpanel |
| Steel jack dish JP-028 / JP-322 | plate 101.6 x 111.1 mm, 1.2 mm steel | not published | not published | same |
| Steel jack plate JP-344 | 88.9 x 130.2 mm | flat plate | 4 x #8 | same |
| Round recessed jack cup JP-104 | OD 95.25 mm | inner 55.6 mm | 2 holes at 53.98 mm | same |
| Plastic dual-jack plate JP-225 | 85.7 mm square | fits a 76.2 mm round hole | not published | same |
| Penn Elcom medium recessed dish D0941K | not published | dish depth 13 mm, 1.2 mm steel | not published | penn-elcom.com D0941K |
| Marshall strap handle (Mojotone) | not published | surface mount | 228.6 mm inner (t-nuts), 254 mm outer | mojotone.com |
| Fender strap handle, chrome caps (Mojotone) | not published | surface mount | 203.2 mm | mojotone.com |
| Fender OEM FAH-332 / FAH-944 | 234.95 mm long without caps | surface mount | 196.85 mm | amprepairparts.com handles |
| Generic GAH-1 / GAH-271C | 260.35 mm mounted, strap 22.2 mm wide | surface mount | 209.55 mm, 10-32 t-nut | same |
| Penn Elcom recessed handle H7115Z (small) | flange 115 x 107 mm | dish depth 8.5 mm; cutout not published | 8 holes | penn-elcom.com |
| Penn Elcom H7154Z (medium) | flange 161 x 107 mm, grip 19 mm | dish depth 8.5 mm; cutout not published | 10 holes | penn-elcom.com |
| Penn Elcom H7165Z (large) | flange 178 x 127 mm, 150 kg | dish depth 16 mm; cutout not published | 14 holes | penn-elcom.com |
| Penn Elcom H7165-10Z (large shallow) | flange 178 x 127 mm | dish depth 10 mm | 14 holes | penn-elcom.com |
| Rubber feet, Penn Elcom | 9106 dia 64 h 25.4; F1615 43 / 20; F1686 40 / 16; FG-9620 35 / 33; 9112 32.5 / 12.7 | | one central screw | penn-elcom.com feet |
| Two-leg corners C1824K / C1270K | leg length not published; 0.8 / 1.2 mm steel | | 2 holes | penn-elcom.com |
| Three-leg corners C0670Z, C1083Z, C1340K | leg length not published | | 3 to 6 holes | penn-elcom.com |
| Marshall corners MC-1091 / MC-1090 | leg length not published; 19.05 mm radius | | rivets, 3 front, 4 rear | amprepairparts.com |

Caveats: no US supplier publishes metal-corner leg length, so the corner allowance stays a measured parameter (starting value 50 mm keep-out from external corners). Penn Elcom never publishes the panel cutout for recessed handles or dishes; the free STEP models on 3DContentCentral are where a cutout must come from, and the metric figures on the UK site are the truer ones. The construction note's 110 x 70 mm jack plate cutout is close to the Marshall CJP-1's 76.2 x 87.3 mm but not the same part; reconcile against the plate actually purchased. Amplified Parts, CE Distribution, and Antique Electronic Supply refused automated fetches.
