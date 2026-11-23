// Concept solids for the guitar neck rest options page.
// mm. X along the neck (nut toward -X, body toward +X), Y across the neck, Z up, bench at Z = 0.
// Every number comes from params.scad, which concepts.py writes from its one parameter set.
//
//   PART  a | b | c | d_base | d_cradle | e | f_base | f_head          round 1: six base shapes
//         c1 | c2 | c2_lid | c3                                       round 2: three rocker bodies
//         c1a | c1b | c1c                                             round 3: the open frame with a longer cradle (LONG)
//         c1r                                                         the kept body: c1 with its edges rounded over
//   MODE  part   the bare printable solid in its print orientation (for STL export)
//         scene  on the bench with its pad and the neck stand-in (for the pictures)
//   VIEW  shape  the bare rest with its pad
//         use    with the neck stand-in on it
//         extra  the other height, the parts apart, or the range
//         pad    round 2: the rocker close up, pad and tread in PADMAT (cork | felt | tpu)
//         end    c1r: one cradle end close up
include <params.scad>

PART = "a";
MODE = "part";
VIEW = "shape";
NECK = "bass";
PADMAT = "cork";

CD = CR - sqrt(CR * CR - CW * CW / 4);        // cradle depth at the pad surface
GR = CR + PAD_T;                              // groove radius cut into the body (pad sits in it)
GW = sqrt(GR * GR - (CR - CD) * (CR - CD));   // half width of the groove cut at the rim

C_BODY = "#4f83e6";
C_BODY2 = "#89aef2";
C_PAD = "#c9a26b";
C_MAT = "#44584f";
C_GRID = "#6f867b";
C_NECK = "#e6c992";
C_BOARD = "#4b3023";
C_FRET = "#d9d9d9";
C_NUT = "#f5f1e6";
C_FILL = "#8d949e";
C_SOFT = PADMAT == "felt" ? "#3f6b52" : PADMAT == "tpu" ? "#2a2e36" : C_PAD;

// ---------------------------------------------------------------- helpers
module cbox(s, c = 3) {   // centred box with all edges chamfered by c
  hull() {
    cube([s.x - 2 * c, s.y - 2 * c, s.z], center = true);
    cube([s.x - 2 * c, s.y, s.z - 2 * c], center = true);
    cube([s.x, s.y - 2 * c, s.z - 2 * c], center = true);
  }
}

// Groove for a cradle on a +Z face, running along X, pad surface lowest at Z = zb.
module groove(len, zb) {
  translate([0, 0, zb + CR]) rotate([0, 90, 0]) cylinder(r = GR, h = len + 2, center = true, $fn = 200);
}

// The stick-on pad that lines that groove.
module pad(len, zb) {
  intersection() {
    translate([0, 0, zb + CR]) rotate([0, 90, 0]) difference() {
      cylinder(r = GR - 0.06, h = len - 6, center = true, $fn = 200);   // just shy of the groove: coincident faces speckle in preview
      cylinder(r = CR, h = len, center = true, $fn = 200);
    }
    translate([-len / 2 + 1, -CW / 2 + 1, zb - PAD_T - 1]) cube([len - 2, CW - 2, CD + PAD_T + 1]);   // short of the body's end faces: coplanar faces speckle in preview
  }
}

// ---------------------------------------------------------------- neck stand-in
function neck_w(x) = NECK_W0 + (NECK_W1 - NECK_W0) * x / NECK_L12;
function neck_d(x) = NECK_D0 + (NECK_D1 - NECK_D0) * x / NECK_L12;

module neck_profile(w, d) {   // 2D, back lowest point at the origin
  fb = 6.35;
  translate([-w / 2, d - fb]) square([w, fb]);
  translate([0, d - fb]) scale([w / 2, d - fb]) difference() {
    circle(1, $fn = 96);
    translate([-2, 0]) square([4, 2]);
  }
}

module neck_slice(x) {
  translate([x, 0, 0]) rotate([90, 0, 90]) linear_extrude(0.1) neck_profile(neck_w(x), neck_d(x));
}

// Nut at x = 0, back of the neck along z = 0, drawn out to l with a cut-off headstock stub.
module neck(l = NECK_DRAW) {
  color(C_NECK, 0.92) {
    hull() { neck_slice(0); neck_slice(l); }
    hull() {   // headstock stub, cut off
      translate([-2, -neck_w(0) / 2, neck_d(0) - 4.5 - 14.5]) cube([2, neck_w(0), 14.5]);
      translate([-HEAD_STUB, -neck_w(0) / 2 - 12, neck_d(0) - 4.5 - 14.5]) cube([2, neck_w(0) + 24, 14.5]);
    }
  }
  color(C_BOARD) hull() {
    translate([0, -neck_w(0) / 2 + 0.3, neck_d(0) - 0.4]) cube([0.1, neck_w(0) - 0.6, 0.7]);
    translate([l, -neck_w(l) / 2 + 0.3, neck_d(l) - 0.4]) cube([0.1, neck_w(l) - 0.6, 0.7]);
  }
  color(C_NUT) translate([-3.2, -neck_w(0) / 2, neck_d(0) - 2]) cube([3.2, neck_w(0), 4.5]);
  for (x = FRETS) if (x < l - 2)
    color(C_FRET) translate([x - 1.2, -neck_w(x) / 2, neck_d(x)]) cube([2.4, neck_w(x), 1.3]);
}

// A neck on a fixed, level cradle: it slopes down toward the body, so it bears on the body-side end of the pad.
module neck_on_fixed(len, zb, tilt) {
  translate([len / 2 - 3, 0, zb]) rotate([0, tilt, 0]) translate([-(X_REST + len / 2 - 3), 0, 0]) neck();
}

// A neck lying along a cradle that has turned to meet it.
module neck_aligned(zb, xr = X_REST, l = NECK_DRAW) {
  translate([-xr, 0, zb]) neck(l);
}

module bench(l = 300, x0 = 0, w = 250) {   // cutting mat with a 1 in grid, for scale
  color(C_MAT) translate([x0, 0, -2.01]) cube([l, w, 4], center = true);
  color(C_GRID) {
    for (i = [ceil((x0 - l / 2) / IN) : floor((x0 + l / 2) / IN)]) translate([i * IN - 0.35, -w / 2, 0]) cube([0.7, w, 0.12]);
    for (j = [ceil(-w / 2 / IN) : floor(w / 2 / IN)]) translate([x0 - l / 2, j * IN - 0.35, 0]) cube([l, 0.7, 0.12]);
  }
}

// ---------------------------------------------------------------- A: two-height frame block
XA = 95;
YA = LOW + CD;
ZA = HIGH + CD;

module a_grooved(pads = false) {
  if (pads) {
    pad(XA, HIGH);
    translate([0, 0, ZA / 2]) rotate([-90, 0, 0]) pad(XA, -YA / 2 + LOW);
  } else {
    groove(XA, HIGH);
    translate([0, 0, ZA / 2]) rotate([-90, 0, 0]) groove(XA, -YA / 2 + LOW);
  }
}

module a_body() {
  wy0 = -YA / 2 + 11;
  wy1 = YA / 2 - CD - PAD_T - 9;
  wz0 = 11;
  wz1 = HIGH - PAD_T - 9;
  difference() {
    translate([0, 0, ZA / 2]) cbox([XA, YA, ZA]);
    a_grooved();
    translate([0, (wy0 + wy1) / 2, (wz0 + wz1) / 2]) rotate([0, 90, 0])
      linear_extrude(XA + 2, center = true) offset(r = 8) square([wz1 - wz0 - 16, wy1 - wy0 - 16], center = true);
  }
}

module a_low() {   // lying on its -Y face: the +Y cradle is up, at LOW
  translate([0, ZA / 2, YA / 2]) rotate([90, 0, 0]) children();
}

// ---------------------------------------------------------------- B: three-height block
BA = LOW + CD;     // local x
BB = HIGH + CD;    // local y
BC = TALL + CD;    // local z
M_B_ON_B = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]];     // module X -> local z, module Z -> local +y
M_B_ON_A = [[0, 0, 1, 0], [0, -1, 0, 0], [1, 0, 0, 0]];    // module X -> local z, module Z -> local +x

module b_local(pads = false) {
  if (pads) {
    pad(BA, -BC / 2 + TALL);
    multmatrix(M_B_ON_B) pad(BC, -BB / 2 + HIGH);
    multmatrix(M_B_ON_A) pad(BC, -BA / 2 + LOW);
  } else {
    difference() {
      cbox([BA, BB, BC], 4);
      groove(BA, -BC / 2 + TALL);
      multmatrix(M_B_ON_B) groove(BC, -BB / 2 + HIGH);
      multmatrix(M_B_ON_A) groove(BC, -BA / 2 + LOW);
    }
  }
}

module b_up_b() { multmatrix([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, BB / 2]]) children(); }    // HIGH cradle up
module b_up_a() { multmatrix([[0, 0, 1, 0], [0, -1, 0, 0], [1, 0, 0, BA / 2]]) children(); }   // LOW cradle up
module b_up_c() { translate([0, 0, BC / 2]) children(); }                                      // TALL cradle up

// ---------------------------------------------------------------- C: rocker
XC_TOP = 110;
ZC = HIGH + CD;
C_HALF = 75;                                   // half chord of the rocking arc
C_SAG = RR - sqrt(RR * RR - C_HALF * C_HALF);

// Side view: the rocking arc under a tapered block. With deck > 0 the cradle beam keeps square ends that deep
// and the sides run to its lower corners (round 3, where the cradle is longer than the rocker).
module c_outline(n = 40, top = XC_TOP, half = C_HALF, deck = 0) {
  tm = asin(half / RR);
  offset(r = 5) offset(delta = -5) polygon(concat(
    [for (i = [0:n]) let(t = -tm + 2 * tm * i / n) [RR * sin(t), RR * (1 - cos(t))]],
    deck > 0 ? [[top / 2, ZC - deck], [top / 2, ZC], [-top / 2, ZC], [-top / 2, ZC - deck]]
             : [[top / 2, ZC], [-top / 2, ZC]]));
}

module c_profile() {
  difference() {
    c_outline();
    hull() for (x = [-26, 26]) for (z = [C_SAG + 22, HIGH - PAD_T - 22]) translate([x, z]) circle(r = 10, $fn = 48);
  }
}

module c_body() {
  difference() {
    rotate([90, 0, 0]) linear_extrude(YC, center = true, convexity = 4) c_profile();
    groove(XC_TOP + 60, HIGH);
  }
}

module c_rolled(t) { translate([0, 0, RR]) rotate([0, t, 0]) translate([0, 0, -RR]) children(); }

// ---------------------------------------------------------------- C, round 2: three rocker bodies
// c1  open frame.
// c2  closed, with a ballast pocket under a lid on the -Y face and a hang slot above it.
// c3  closed, with a second, fixed cradle on the -Y face: lay the rocker on its +Y face and the neck
//     sits at C3_LOW on a cradle that already slopes C3_SLOPE toward the body.
// All three carry two recessed tread strips on the rocking curve.
C_FR = 12;                         // frame thickness of the open body
TR_W = 14;                         // tread strip width
TR_IN = 3;                         // lip left outside each strip
TR_D = 1.2;                        // recess depth: a 1.6 mm strip stands 0.4 proud
C2_PX = 22;                        // ballast pocket: half spacing of the obround's centres
C2_PR = 17;                        //   radius
C2_PZ = 30;                        //   height of its centre line
C2_PD = 64;                        //   depth from the -Y face
C2_LID = 3;                        // lid plate thickness, let into a rebate C2_LIP wide
C2_LIP = 2.5;
C2_SKIRT = 6;                      // lid skirt, inside the pocket
C2_SLOT_Z = 67;                    // hang slot above the pocket
C2_SLOT_R = 9;
C2_VOL = (4 * C2_PX * C2_PR + PI * C2_PR * C2_PR) * (C2_PD - C2_LID - C2_SKIRT) / 1000;   // cm3 behind the skirt
C3_ZS = 62;                        // side cradle centre line, measured up the upright rocker
C3_Y0 = YC / 2 - CD;               // its pad surface, measured from the rocker's centre plane
C3_LOW = YC / 2 + C3_Y0;           // neck height on the fixed cradle
C3_LEN = 116;                      // pad length on the fixed cradle

module tread(out = 0.4, half = C_HALF) {   // the two strips on the rocking curve, reaching `out` past the curve
  tm = asin(half / RR) - 4;
  n = 80;
  for (s = [-1, 1]) translate([0, s * (YC / 2 - TR_IN - TR_W / 2), RR]) rotate([90, 0, 0])
    linear_extrude(TR_W, center = true, convexity = 4) polygon(concat(
      [for (i = [0:n]) let(t = -tm + 2 * tm * i / n) [(RR + out) * sin(t), -(RR + out) * cos(t)]],
      [for (i = [n:-1:0]) let(t = -tm + 2 * tm * i / n) [(RR - TR_D) * sin(t), -(RR - TR_D) * cos(t)]]));
}

module c1_body(top = XC_TOP, half = C_HALF, deck = 0) {
  difference() {
    rotate([90, 0, 0]) linear_extrude(YC, center = true, convexity = 6) difference() {
      c_outline(160, top, half, deck);
      offset(r = 9) offset(delta = -9) intersection() {
        offset(delta = -C_FR) c_outline(160, top, half, deck);
        translate([-200, 0]) square([400, HIGH - PAD_T - C_FR]);
      }
    }
    groove(top + 60, HIGH);
    tread(1, half);
  }
}

// Obround prism opening on the -Y face: starts y0 in from that face and runs d deep.
module c2_pocket(r, y0, d) {
  translate([0, -YC / 2 + y0 + d, 0]) rotate([90, 0, 0]) linear_extrude(d, convexity = 4)
    hull() for (x = [-C2_PX, C2_PX]) translate([x, C2_PZ]) circle(r = r, $fn = 72);
}

module c2_body() {
  difference() {
    rotate([90, 0, 0]) linear_extrude(YC, center = true, convexity = 6) difference() {
      c_outline(160);
      hull() for (x = [-C2_PX, C2_PX]) translate([x, C2_SLOT_Z]) circle(r = C2_SLOT_R, $fn = 48);
    }
    groove(XC_TOP + 60, HIGH);
    tread(1);
    c2_pocket(C2_PR, -1, C2_PD + 1);
    c2_pocket(C2_PR + C2_LIP, -1, C2_LID + 1);
  }
}

module c2_lid(clear = 0.15) {      // in place on the body: plate in the rebate, skirt in the pocket
  c2_pocket(C2_PR + C2_LIP - clear, 0, C2_LID);
  difference() {
    c2_pocket(C2_PR - clear, C2_LID - 0.01, C2_SKIRT);
    c2_pocket(C2_PR - clear - 2, C2_LID - 1, C2_SKIRT + 2);
  }
}

module c2_fill() { c2_pocket(C2_PR - 0.6, C2_LID + C2_SKIRT + 0.5, C2_PD - C2_LID - C2_SKIRT - 1); }

// Puts a +Z-face groove or pad on the -Y face at C3_ZS, sloped for the laid-down rocker (lower toward +X).
module c3_place() {
  translate([0, -C3_Y0, C3_ZS]) rotate([0, 0, C3_SLOPE]) translate([0, C3_Y0, 0]) rotate([90, 0, 0]) children();
}

module c3_body() {
  difference() {
    rotate([90, 0, 0]) linear_extrude(YC, center = true, convexity = 6) c_outline(160);
    groove(XC_TOP + 60, HIGH);
    tread(1);
    c3_place() groove(190, C3_Y0);
  }
}

module c3_lying() { translate([0, -C3_ZS, YC / 2]) rotate([-90, 0, 0]) children(); }   // on its +Y face, fixed cradle up

module c_any(n) {                  // rocker body n with its pad and tread
  color(C_BODY) { if (n == 1) c1_body(); if (n == 2) c2_body(); if (n == 3) c3_body(); }
  color(C_SOFT) { pad(XC_TOP, HIGH); tread(0.4); if (n == 3) c3_place() pad(C3_LEN, C3_Y0); }
}

// ---------------------------------------------------------------- C1, round 3: a longer cradle
// LONG (params.scad) lists the variants: [name, cradle length, half chord of the rocking arc, rest centre from the nut,
// roll under the bass]. Same curve radius, cradle section, frame and tread as c1; only the two lengths change.
function lv(p) = [for (v = LONG) if (v[0] == p) v][0];
LV = lv(PART);
C_DECK = CD + PAD_T + C_FR;        // the cradle beam: groove, pad allowance and the frame under them
NECK_DRAW_LONG = 330;

module long_body(v) { c1_body(v[1], v[2], C_DECK); }

module long_any(v) {               // long-cradle body with its pad and tread
  color(C_BODY) long_body(v);
  color(C_SOFT) { pad(v[1], HIGH); tread(0.4, v[2]); }
}

// ---------------------------------------------------------------- C1 with its edges rounded over (Brian, 2026-11-23)
// "the front and back edges closest to the neck should be rounded over": the two cradle ends (confirmed by a question).
// "all edges should have a slight roundover": every other outside edge.
// Same body as c1, built the way it prints (on its side, one slice per layer): each slice across the neck is the side
// outline with its top at the height the cradle has there and its two top corners rounded R_END. The cradle's rims are
// rounded R_EDGE in that height curve, and the outline shrinks through a quarter circle of R_EDGE at the two faces.
// The window flares through the same quarter circle. The tread recesses stay square: the strips seat in them.
R_END = 6.35;                      // 1/4 in: the two cradle ends
R_EDGE = 1.5875;                   // 1/16 in: every other outside edge
C_LEAN = atan((C_HALF - XC_TOP / 2) / (ZC - C_SAG));              // the end faces lean this far from upright
C_ZA = HIGH + CR;                                                 // axis of the groove
RIM_Y = sqrt(pow(GR + R_EDGE, 2) - pow(C_ZA - ZC + R_EDGE, 2));   // centre of the rim roundover, off the centre plane
RIM_YG = RIM_Y * GR / (GR + R_EDGE);                              // where that roundover leaves the groove
C1R_FLAT = 2 * (C_HALF - (HIGH - PAD_T - C_SAG) * tan(C_LEAN) - R_END * tan((90 - C_LEAN) / 2));   // level floor between the end roundovers
C1R_STEPS = 8;                     // facets on a 1/16 in roundover

function c1r_top(y) = y <= RIM_YG ? C_ZA - sqrt(GR * GR - y * y)                             // top of the body at y: groove,
                    : y < RIM_Y ? ZC - R_EDGE + sqrt(R_EDGE * R_EDGE - pow(y - RIM_Y, 2))    // rim roundover,
                    : ZC;                                                                    // shoulder
function c1r_inset(y) = y <= YC / 2 - R_EDGE ? 0 : R_EDGE - sqrt(R_EDGE * R_EDGE - pow(y - (YC / 2 - R_EDGE), 2));
c1r_ys = concat([for (i = [0:72]) RIM_YG * i / 72],
                [for (i = [1:C1R_STEPS]) RIM_YG + (RIM_Y - RIM_YG) * i / C1R_STEPS],
                [for (i = [0:C1R_STEPS]) YC / 2 - R_EDGE + R_EDGE * sin(90 * i / C1R_STEPS)]);

// Centre of the +X top corner's arc for a top at height h, and the upper part of the side outline from z0 up.
function c1r_corner(h) = let(s = (h - R_END - C_SAG + R_END * sin(C_LEAN)) / cos(C_LEAN))
  [C_HALF - s * sin(C_LEAN) - R_END * cos(C_LEAN), h - R_END];
function c1r_top_pts(h, z0 = 50, n = 20) = let(c = c1r_corner(h), x0 = C_HALF - (z0 - C_SAG) * tan(C_LEAN))
  concat([[x0, z0]],
         [for (i = [0:n]) let(a = C_LEAN + (90 - C_LEAN) * i / n) [c[0] + R_END * cos(a), c[1] + R_END * sin(a)]],
         [for (i = [n:-1:0]) let(a = C_LEAN + (90 - C_LEAN) * i / n) [-c[0] - R_END * cos(a), c[1] + R_END * sin(a)]],
         [[-x0, z0]]);

module c1r_side(h) {               // side outline with its top at h
  intersection() { c_outline(160, $fn = 72); translate([-200, -10]) square([400, 70]); }
  polygon(c1r_top_pts(h));
}

module c1r_slab(y) {               // 0.02 thick, lying just inside y, so the last one ends exactly on the face
  translate([0, y, 0]) rotate([90, 0, 0]) linear_extrude(0.02)
    offset(delta = -c1r_inset(y)) c1r_side(c1r_top(y));
}

module c1r_half() { for (i = [0 : len(c1r_ys) - 2]) hull() { c1r_slab(c1r_ys[i]); c1r_slab(c1r_ys[i + 1]); } }

module c1_window() {               // the opening of the open frame, as c1_body() cuts it
  offset(r = 9) offset(delta = -9) intersection() {
    offset(delta = -C_FR) c_outline(160);
    translate([-200, 0]) square([400, HIGH - PAD_T - C_FR]);
  }
}

module c1r_wslab(s, i, out = 0) {
  a = 90 * i / C1R_STEPS;
  translate([0, s * (YC / 2 - R_EDGE + R_EDGE * sin(a) + out), 0]) rotate([90, 0, 0]) linear_extrude(0.02, center = true)
    offset(delta = R_EDGE * (1 - cos(a))) c1_window($fn = 72);
}

module c1r_window_cut() {
  rotate([90, 0, 0]) linear_extrude(YC - 2 * R_EDGE + 0.02, center = true, convexity = 4) c1_window($fn = 72);
  for (s = [-1, 1]) {
    for (i = [0 : C1R_STEPS - 1]) hull() { c1r_wslab(s, i); c1r_wslab(s, i + 1); }
    hull() { c1r_wslab(s, C1R_STEPS); c1r_wslab(s, C1R_STEPS, 1); }
  }
}

module c1r_body() {
  difference() {
    union() { c1r_half(); mirror([0, 1, 0]) c1r_half(); }
    c1r_window_cut();
    tread(1);
  }
}

module c1r_any() {                 // the kept body with its pad and tread
  color(C_BODY) render(convexity = 6) c1r_body();
  color(C_SOFT) { pad(XC_TOP, HIGH); tread(0.4); }
}

// ---------------------------------------------------------------- D: hanging cradle on a yoke
XD = 124;
YD = 116;
D_PLATE = 8;
D_UP_T = 12;
D_GAP = 88;                 // between the uprights
D_CR_L = 100;
D_CR_W = D_GAP - 4;
D_ZP = HIGH + 4;            // pivot axis: just above the line the neck bears on, so the cradle hangs
D_PIN = 12;
D_ZU = D_ZP + 9;

module d_base() {
  translate([0, 0, D_PLATE / 2]) cbox([XD, YD, D_PLATE], 2);
  for (s = [-1, 1]) translate([0, s * (D_GAP / 2 + D_UP_T / 2), 0]) difference() {
    rotate([90, 0, 0]) linear_extrude(D_UP_T, center = true)
      polygon([[-34, D_PLATE - 1], [34, D_PLATE - 1], [15, D_ZU], [-15, D_ZU]]);
    translate([0, 0, D_ZP]) rotate([90, 0, 0]) cylinder(d = D_PIN + 0.8, h = D_UP_T + 2, center = true, $fn = 64);
    translate([-(D_PIN + 0.8) / 2, -D_UP_T / 2 - 1, D_ZP]) cube([D_PIN + 0.8, D_UP_T + 2, 20]);
  }
}

module d_cradle() {
  h = CD + PAD_T + 9;
  difference() {
    translate([0, 0, HIGH + CD - h / 2]) cbox([D_CR_L, D_CR_W, h], 2.5);
    groove(D_CR_L, HIGH);
  }
  for (s = [-1, 1]) translate([0, s * (D_CR_W / 2 - 3), D_ZP]) rotate([-s * 90, 0, 0])
    cylinder(d = D_PIN, h = D_UP_T + 5, $fn = 64);
}

module d_swung(t) { translate([0, 0, D_ZP]) rotate([0, t, 0]) translate([0, 0, -D_ZP]) children(); }

// ---------------------------------------------------------------- E: long low trough
XE = 9 * IN;
ZE = FLAT + CD;
E_CORE = 2 * GW + 8;
E_FOOT = E_CORE + 40;

module e_body() {
  difference() {
    rotate([90, 0, 90]) linear_extrude(XE, center = true)
      polygon([[-E_FOOT / 2, 0], [E_FOOT / 2, 0], [E_FOOT / 2, 7], [E_CORE / 2, 19], [E_CORE / 2, ZE],
               [-E_CORE / 2, ZE], [-E_CORE / 2, 19], [-E_FOOT / 2, 7]]);
    groove(XE, FLAT);
  }
}

// ---------------------------------------------------------------- F: screw-adjustable pedestal
F_DISC_D = 130;
F_DISC_T = 10;
F_RM = 20.75;      // mean thread radius
F_E = 1.25;        // thread amplitude: 44.5 degree flank at this pitch, prints without support
F_P = 8;           // pitch
F_LS = 46;         // sleeve length = post length
F_SLEEVE_D = 66;
F_FLOOR = 6;
XF = 100;
YF = 2 * GW + 8;
F_ZB0 = F_LS + F_FLOOR + PAD_T;     // pad surface above the sleeve's bottom end
F_MIN = F_DISC_T + F_ZB0;
F_ENGAGE = 16;
F_MAX = F_MIN + F_LS - F_ENGAGE;

module f_thread(h, clear = 0) {
  linear_extrude(height = h, twist = -360 * h / F_P, slices = ceil(h * 3), convexity = 4)
    translate([F_E, 0]) circle(r = F_RM + clear, $fn = 72);
}

module f_base() {
  cylinder(d = F_DISC_D, h = F_DISC_T - 3, $fn = 128);
  translate([0, 0, F_DISC_T - 3]) cylinder(d1 = F_DISC_D, d2 = F_DISC_D - 6, h = 3, $fn = 128);
  translate([0, 0, F_DISC_T - 0.01]) f_thread(F_LS);
}

module f_head() {   // z = 0 at the sleeve's bottom end
  top = F_ZB0 + CD;
  difference() {
    union() {
      cylinder(d = F_SLEEVE_D, h = F_LS, $fn = 128);
      hull() {
        translate([0, 0, F_LS - 32]) cylinder(d = F_SLEEVE_D, h = 0.1, $fn = 128);
        translate([0, 0, F_LS + (top - F_LS) / 2]) cbox([XF, YF, top - F_LS], 2.5);
      }
    }
    translate([0, 0, -1]) f_thread(F_LS + 1, 0.45);
    groove(XF, F_ZB0);
  }
}

// ---------------------------------------------------------------- output
module body() { color(C_BODY) children(); }

if (MODE == "part") {
  if (PART == "a") translate([0, 0, XA / 2]) rotate([0, -90, 0]) translate([0, 0, -ZA / 2]) a_body();   // standing on end
  if (PART == "b") b_up_a() b_local();
  if (PART == "c") translate([0, 0, YC / 2]) rotate([90, 0, 0]) c_body();                               // on its side
  if (PART == "c1") translate([0, 0, YC / 2]) rotate([90, 0, 0]) c1_body();                             // on its side
  if (PART == "c2") translate([0, 0, YC / 2]) rotate([-90, 0, 0]) c2_body();                            // on its side, pocket up
  if (PART == "c2_lid") translate([0, 0, YC / 2]) rotate([90, 0, 0]) c2_lid();                          // plate down, skirt up
  if (PART == "c3") c3_lying() c3_body();                                                               // on its side, fixed cradle up
  if (!is_undef(LV)) translate([0, 0, YC / 2]) rotate([90, 0, 0]) long_body(LV);                        // on its side
  if (PART == "c1r") translate([0, 0, YC / 2]) rotate([90, 0, 0]) c1r_body();                           // on its side
  if (PART == "d_base") d_base();
  if (PART == "d_cradle") translate([0, 0, -(HIGH - PAD_T - 9)]) d_cradle();
  if (PART == "e") e_body();
  if (PART == "f_base") f_base();
  if (PART == "f_head") f_head();
} else {
  if (!is_undef(LV)) bench(VIEW == "use" ? 470 : 300, VIEW == "use" ? 25 : 0);
  else if (VIEW == "use" || (VIEW == "extra" && PART == "c3")) bench(430, 50);
  else if (VIEW == "extra" && PART == "b") bench(480, 0);
  else if (VIEW == "extra" && (PART == "f" || PART == "a")) bench(VIEW == "extra" && PART == "a" ? 430 : 360, PART == "a" ? 50 : 0);
  else bench();

  if (PART == "a") {
    if (VIEW == "extra") {   // lying on its side: the low cradle is up
      a_low() { body() a_body(); color(C_PAD) a_grooved(pads = true); }
      neck_on_fixed(XA, LOW, TILT_LOW);
    } else {
      body() a_body();
      color(C_PAD) a_grooved(pads = true);
      if (VIEW == "use") neck_on_fixed(XA, HIGH, TILT_HIGH);
    }
  }
  if (PART == "b") {
    if (VIEW == "extra") {   // the three ways up, side by side
      translate([-160, 0, 0]) b_up_a() { body() b_local(); color(C_PAD) b_local(pads = true); }
      translate([0, 0, 0]) b_up_b() { body() b_local(); color(C_PAD) b_local(pads = true); }
      translate([150, 0, 0]) b_up_c() { body() b_local(); color(C_PAD) b_local(pads = true); }
    } else {
      b_up_b() { body() b_local(); color(C_PAD) b_local(pads = true); }
      if (VIEW == "use") neck_on_fixed(BC, HIGH, TILT_HIGH);
    }
  }
  if (PART == "c") c_rolled(VIEW == "use" ? TILT_HIGH : 0) {
    body() c_body();
    color(C_PAD) pad(XC_TOP, HIGH);
    if (VIEW == "use") neck_aligned(HIGH);
  }
  if (PART == "c1" || PART == "c2" || PART == "c3") {
    n = PART == "c1" ? 1 : PART == "c2" ? 2 : 3;
    if (VIEW == "use") c_rolled(TILT_HIGH) { c_any(n); if (n == 2) color(C_BODY2) c2_lid(); neck_aligned(HIGH); }
    else if (VIEW == "extra" && n == 1) translate([0, 0, ZC]) rotate([180, 0, 0]) c_any(1);   // upside down: the tread
    else if (VIEW == "extra" && n == 2) {   // lid off, ballast in the pocket
      c_any(2);
      color(C_FILL) c2_fill();
      translate([0, -70, 0]) color(C_BODY2) c2_lid();
    }
    else if (VIEW == "extra" && n == 3) {   // laid down: the fixed cradle is up
      c3_lying() c_any(3);
      translate([0, 0, C3_LOW]) rotate([0, C3_SLOPE, 0]) translate([-X_REST, 0, 0]) neck();
    }
    else { c_any(n); if (n == 2) color(C_BODY2) c2_lid(); }
  }
  if (!is_undef(LV)) {
    if (VIEW == "use") c_rolled(LV[4]) { long_any(LV); neck_aligned(HIGH, LV[3], NECK_DRAW_LONG); }
    else long_any(LV);
  }
  if (PART == "c1r") {
    if (VIEW == "use") c_rolled(TILT_HIGH) { c1r_any(); neck_aligned(HIGH); }
    else if (VIEW == "extra") translate([0, 0, ZC]) rotate([180, 0, 0]) c1r_any();   // upside down: the tread
    else c1r_any();
  }
  if (PART == "d") {
    body() d_base();
    translate([0, 0, VIEW == "extra" ? 45 : 0]) d_swung(VIEW == "use" ? TILT_HIGH : 0) {
      color(C_BODY2) d_cradle();
      color(C_PAD) pad(D_CR_L, HIGH);
      if (VIEW == "use") neck_aligned(HIGH);
    }
  }
  if (PART == "e") {
    body() e_body();
    color(C_PAD) pad(XE, FLAT);
    if (VIEW == "use") neck_on_fixed(XE, FLAT, 0);
  }
  if (PART == "f") {
    if (VIEW == "extra") {   // lowest and highest, side by side
      for (k = [0, 1]) translate([k == 0 ? -85 : 85, 0, 0]) {
        body() f_base();
        translate([0, 0, F_DISC_T + (k == 0 ? 0 : F_LS - F_ENGAGE)]) { color(C_BODY2) f_head(); color(C_PAD) pad(XF, F_ZB0); }
      }
    } else {
      body() f_base();
      translate([0, 0, F_DISC_T + F_LIFT]) { color(C_BODY2) f_head(); color(C_PAD) pad(XF, F_ZB0); }
      if (VIEW == "use") neck_on_fixed(XF, F_MIN + F_LIFT, TILT_F);
    }
  }
}

echo(str("DERIVED CD=", CD, " GW=", GW, " XA=", XA, " YA=", YA, " ZA=", ZA, " BA=", BA, " BB=", BB, " BC=", BC,
         " YC=", YC, " ZC=", ZC, " C_CHORD=", 2 * C_HALF, " XD=", XD, " YD=", YD, " D_ZU=", D_ZU,
         " XE=", XE, " ZE=", ZE, " E_FOOT=", E_FOOT, " F_MIN=", F_MIN, " F_MAX=", F_MAX, " F_DISC_D=", F_DISC_D,
         " XF=", XF, " YF=", YF, " XC_TOP=", XC_TOP, " C_FR=", C_FR, " TR_W=", TR_W, " C2_VOL=", C2_VOL,
         " C3_LOW=", C3_LOW, " C3_ZS=", C3_ZS, " R_END=", R_END, " R_EDGE=", R_EDGE, " C_LEAN=", C_LEAN,
         " C1R_FLAT=", C1R_FLAT, " RIM_Y=", RIM_Y, " TR_IN=", TR_IN, " TR_D=", TR_D));
