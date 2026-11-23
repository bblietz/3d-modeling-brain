// Guitar neck rest: open-frame rocker for bench work on a guitar or bass. Design: 2026-11-23-guitar-neck-rest-design.md.
// mm. Standing frame: X along the neck, Y across the neck, Z up, bench at Z = 0.
//
//   MODE  part    the printable body lying on one face (print frame: x along the neck, y up the standing rocker with
//                 the cradle at the back of the plate, z from the plate)
//         scene   the body standing, with the cork pad and the grip tape drawn in
//   SOFT  true | false   scene only: draw the pad and the tape
//   FLIP  true | false   scene only: upside down, to show the grip tape channel
//
// The body is built the way it prints: as slices across the neck. Each slice is the side outline with its top at the
// height the cradle has there and its two top corners rounded R_END. The cradle's rims are rounded R_EDGE in that height
// curve, and at the two faces the outline shrinks through a quarter circle of R_EDGE. Hulls join neighbouring slices.
// A kernel fillet is not used: a 1/4 in ball cannot follow the 1/16 in rim round the cradle end without a crease.
MODE = "part";
SOFT = true;
FLIP = false;
CHANNEL = true;                    // false: the body before the grip tape channel is cut (build step 1)

IN = 25.4;
HIGH = 3.75 * IN;                  // bench to the top of the pad: where the back of the neck lies
CW = 64;                           // cradle width at the pad surface, 2-1/2 in
CR = 45.3;                         // cradle radius at the pad surface
PAD_T = 1.6;                       // pad seat: the cradle is cut this much deeper, for a 1/16 in cork sheet
RR = 130;                          // rocking curve radius
YC = 80;                           // width across the neck
XC_TOP = 110;                      // length over the top
C_HALF = 75;                       // half chord of the rocking curve
C_FR = 12;                         // frame thickness
CORNER_R = 5;                      // where the rocking curve meets the ends
WIN_R = 9;                         // corners of the opening
R_END = 6.35;                      // 1/4 in roundover on the two cradle ends (Brian 2026-11-23; the size is mine)
R_EDGE = 1.5875;                   // 1/16 in roundover on every other outside edge (Brian 2026-11-23; the size is mine)
STEPS = 8;                         // facets on a 1/16 in roundover

// Grip tape channel (Brian 2026-11-23: "Create a 2 in wide recessed channel in the bottom of the stand for me to put
// the grip tape in"; he has 2 in wide rubber grip tape). One channel, centred on the rocking curve, ends closed.
TAPE_W = 2 * IN;
TAPE_L = 5.5 * IN;                 // cut length of the tape, along the curve
TAPE_SIDE = 0.4;                   // clearance each side
TAPE_END = 1.6;                    // clearance each end
TAPE_D = 0.5;                      // channel depth: shallower than the tape, so the rest stands on rubber, not plastic
TAPE_T = 1.0;                      // tape thickness as drawn in the pictures (assumed, not measured)

// Cork pad as cut (scene only)
PAD_W = 2.75 * IN;
PAD_L = 4.125 * IN;

CD = CR - sqrt(CR * CR - CW * CW / 4);                            // cradle depth at the pad surface
ZC = HIGH + CD;                                                   // top of the shoulders
GR = CR + PAD_T;                                                  // radius of the cut
C_ZA = HIGH + CR;                                                 // axis of the cradle
C_SAG = RR - sqrt(RR * RR - C_HALF * C_HALF);
C_TM = asin(C_HALF / RR);
C_LEAN = atan((C_HALF - XC_TOP / 2) / (ZC - C_SAG));              // the ends lean this far from upright
FLOOR = HIGH - PAD_T;                                             // cradle floor on the centre plane
RIM_Y = sqrt(pow(GR + R_EDGE, 2) - pow(C_ZA - ZC + R_EDGE, 2));   // centre of the rim roundover, off the centre plane
RIM_YG = RIM_Y * GR / (GR + R_EDGE);                              // where the rim roundover leaves the cradle
FLAT = 2 * (C_HALF - (FLOOR - C_SAG) * tan(C_LEAN) - R_END * tan((90 - C_LEAN) / 2));   // level floor between the end roundovers
CH_W = TAPE_W + 2 * TAPE_SIDE;
CH_A = (TAPE_L / 2 + TAPE_END) / (RR - TAPE_D) * 180 / PI;        // half angle of the channel along the curve

C_BODY = "#4f83e6";
C_PAD = "#c9a26b";
C_TAPE = "#2a2e36";

// ---------------------------------------------------------------- side outline
module outline(n = 160) {          // the rocking curve under a tapered block; all four corners CORNER_R
  offset(r = CORNER_R) offset(delta = -CORNER_R) polygon(concat(
    [for (i = [0:n]) let(t = -C_TM + 2 * C_TM * i / n) [RR * sin(t), RR * (1 - cos(t))]],
    [[XC_TOP / 2, ZC], [-XC_TOP / 2, ZC]]));
}

function top_at(y) = y <= RIM_YG ? C_ZA - sqrt(GR * GR - y * y)                              // cradle,
                   : y < RIM_Y ? ZC - R_EDGE + sqrt(R_EDGE * R_EDGE - pow(y - RIM_Y, 2))     // rim roundover,
                   : ZC;                                                                     // shoulder
function inset_at(y) = y <= YC / 2 - R_EDGE ? 0 : R_EDGE - sqrt(R_EDGE * R_EDGE - pow(y - (YC / 2 - R_EDGE), 2));
YS = concat([for (i = [0:72]) RIM_YG * i / 72],
            [for (i = [1:STEPS]) RIM_YG + (RIM_Y - RIM_YG) * i / STEPS],
            [for (i = [0:STEPS]) YC / 2 - R_EDGE + R_EDGE * sin(90 * i / STEPS)]);

// Centre of the +X top corner's arc for a top at height h, and the upper part of the side outline from z0 up.
function corner(h) = let(s = (h - R_END - C_SAG + R_END * sin(C_LEAN)) / cos(C_LEAN))
  [C_HALF - s * sin(C_LEAN) - R_END * cos(C_LEAN), h - R_END];
function top_pts(h, z0 = 50, n = 20) = let(c = corner(h), x0 = C_HALF - (z0 - C_SAG) * tan(C_LEAN))
  concat([[x0, z0]],
         [for (i = [0:n]) let(a = C_LEAN + (90 - C_LEAN) * i / n) [c[0] + R_END * cos(a), c[1] + R_END * sin(a)]],
         [for (i = [n:-1:0]) let(a = C_LEAN + (90 - C_LEAN) * i / n) [-c[0] - R_END * cos(a), c[1] + R_END * sin(a)]],
         [[-x0, z0]]);

module side(h) {                   // side outline with its top at h
  intersection() { outline($fn = 72); translate([-200, -10]) square([400, 70]); }
  polygon(top_pts(h));
}

module slab(y) {                   // 0.02 thick, lying just inside y, so the last one ends exactly on the face
  translate([0, y, 0]) rotate([90, 0, 0]) linear_extrude(0.02) offset(delta = -inset_at(y)) side(top_at(y));
}

// One chain of slices from face to face. The far side is the near side mirrored; the centre slice exists once, because
// two centre slices 0.02 apart leave slivers that an STL's 32 bit vertices cannot keep closed.
N = len(YS);
module slice(k) { if (k < 0) mirror([0, 1, 0]) slab(YS[-k]); else slab(YS[k]); }
module shell() { for (k = [-(N - 1) : N - 2]) hull() { slice(k); slice(k + 1); } }

// ---------------------------------------------------------------- opening
module window() {
  offset(r = WIN_R) offset(delta = -WIN_R) intersection() {
    offset(delta = -C_FR) outline($fn = 72);
    translate([-200, 0]) square([400, FLOOR - C_FR]);
  }
}

module wslab(s, i, out = 0) {
  a = 90 * i / STEPS;
  translate([0, s * (YC / 2 - R_EDGE + R_EDGE * sin(a) + out), 0]) rotate([90, 0, 0]) linear_extrude(0.02, center = true)
    offset(delta = R_EDGE * (1 - cos(a))) window($fn = 72);
}

module window_cut() {              // the opening, flaring through a quarter circle of R_EDGE at each face
  rotate([90, 0, 0]) linear_extrude(YC - 2 * R_EDGE + 0.02, center = true, convexity = 4) window($fn = 72);
  for (s = [-1, 1]) {
    for (i = [0 : STEPS - 1]) hull() { wslab(s, i); wslab(s, i + 1); }
    hull() { wslab(s, STEPS); wslab(s, STEPS, 1); }
  }
}

// ---------------------------------------------------------------- grip tape channel
module curve_band(w, r0, r1, a, n = 96) {   // strip w wide on the rocking curve, between radii r0 and r1, +/- a degrees
  translate([0, 0, RR]) rotate([90, 0, 0]) linear_extrude(w, center = true, convexity = 4) polygon(concat(
    [for (i = [0:n]) let(t = -a + 2 * a * i / n) [r1 * sin(t), -r1 * cos(t)]],
    [for (i = [n:-1:0]) let(t = -a + 2 * a * i / n) [r0 * sin(t), -r0 * cos(t)]]));
}

module channel_cut() { curve_band(CH_W, RR - TAPE_D, RR + 1, CH_A); }

// ---------------------------------------------------------------- body and soft parts
module body() {
  difference() {
    shell();
    window_cut();
    if (CHANNEL) channel_cut();
  }
}

module pad() {                     // the cork as cut, stuck in the cradle
  a = PAD_W / 2 / (GR - PAD_T / 2) * 180 / PI;
  intersection() {
    translate([0, 0, C_ZA]) rotate([0, 90, 0]) difference() {
      cylinder(r = GR - 0.05, h = PAD_L, center = true, $fn = 240);
      cylinder(r = CR, h = PAD_L + 2, center = true, $fn = 240);
    }
    translate([0, 0, C_ZA]) rotate([0, 90, 0]) linear_extrude(PAD_L + 2, center = true)
      polygon([[0, 0], [2 * GR * cos(a), -2 * GR * sin(a)], [2 * GR, 0], [2 * GR * cos(a), 2 * GR * sin(a)]]);
  }
}

module tape() { curve_band(TAPE_W, RR - TAPE_D + 0.03, RR - TAPE_D + TAPE_T, TAPE_L / 2 / (RR - TAPE_D) * 180 / PI); }

module standing() {
  color(C_BODY) render(convexity = 6) body();
  if (SOFT) { color(C_PAD) pad(); if (CHANNEL) color(C_TAPE) tape(); }
}

if (MODE == "part") translate([0, 0, YC / 2]) rotate([-90, 0, 0]) body();
else if (FLIP) translate([0, 0, ZC]) rotate([180, 0, 0]) standing();
else standing();

echo(str("DERIVED CD=", CD, " ZC=", ZC, " GR=", GR, " FLOOR=", FLOOR, " C_LEAN=", C_LEAN, " FLAT=", FLAT, " RIM_Y=", RIM_Y,
         " RIM_YG=", RIM_YG, " CH_W=", CH_W, " CH_A=", CH_A, " R_END=", R_END, " R_EDGE=", R_EDGE, " PAD_T=", PAD_T,
         " HIGH=", HIGH, " CR=", CR, " YC=", YC, " RR=", RR, " TAPE_D=", TAPE_D, " TAPE_W=", TAPE_W, " TAPE_L=", TAPE_L,
         " PAD_W=", PAD_W, " PAD_L=", PAD_L, " C_FR=", C_FR, " XC_TOP=", XC_TOP, " C_HALF=", C_HALF, " C_SAG=", C_SAG));
