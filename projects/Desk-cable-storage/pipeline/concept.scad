// Desk cable storage: to-scale concept scene for brainstorming.
// Parameters in inches (from the high-res photos, about +-10%); geometry in mm.
function in(x) = x * 25.4;
$fn = 40;

// ----- closet and desk -----
W   = 45;     // closet interior width, side wall to side wall
OPN = 32;     // door opening width, centred: the slab runs behind both jamb returns
JL  = (W - OPN) / 2;   // left jamb return at x = 6.5
D   = 24;     // slab front edge to the back wall
HT  = 27.5;   // top surface height above the floor
T   = 0.75;   // slab thickness (reads 5/8 in the photo; measure)
U   = HT - T; // underside height, 26.75
CLW = 1.5; CLH = 0.75;   // 1x2 cleats on the flat along both side walls

// power strip screwed flat to the underside, 12 in behind the front edge
SX0 = 4; SL = 34; SY0 = 12; SW = 2.0; ST = 1.9;
NOUT = 9; OPITCH = 3.4;
function ox(i) = SX0 + 1.6 + i * OPITCH;       // outlet centres, x = 5.6 .. 32.8
PW = 1.4; PT = 0.9; PH = 1.5;                   // plug head size
PZ = U - ST - PH;                               // plug bottoms at 23.35
TODAY = [1, 2, 3, 4, 7];                        // outlets used today

// things on the floor
TOWER  = [7.5, 17, 15];  TOWER_AT  = [JL + 2.5, 0.5];
SHRED  = [11, 12, 11];   SHRED_AT  = [W - JL - 1.5 - 11, D - 12];
BASKET = [12, 10, 8];    BASKET_AT = [W - JL - 1.5 - 12, 1];

// ----- concepts -----
option = "today";   // today | A | B | C | D
highlight = true;   // orange for design views; false renders the new part in black PETG for the hidden checks
view   = "persp";   // persp | section (cut at an outlet, seen from the right) | front (cut at y = 8, seen from the front)

// A: low shelf trough hung from the slab behind the strip, open top and back
A_L = 16; A_D = 9.5; A_HF = 3; A_HB = 5.5; A_LIP = 0.6; A_WALL = 0.16; A_X0 = W/2 - A_L/2;
A_SLOPE = atan((A_HB - A_HF) / A_D);
function a_floor(y) = U - A_HF - (A_HB - A_HF) * (y - (D - A_D)) / A_D;   // floor height at depth y
// B: box in the hidden pocket behind the left jamb return, fed by a raceway behind the strip
B_X0 = CLW + 0.25; B_XW = JL - 0.5 - B_X0; B_Y0 = 1.5; B_L = 20; B_H = 7; B_LIP = 2; B_WALL = 0.16;
RW_Y = SY0 + SW + 0.3; RW_H = 1.1; RW_W = 1.3;   // raceway just behind the strip
// C: rail of coil hooks behind the strip; bricks go on the desk through a grommet
C_X0 = 8; C_L = 28; C_Y = 21; C_DROP = 2.4; C_COIL_R = 1.5;
// D: trough shelf screwed to the back wall. D_TOP is its top edge: PZ - 0.5 puts it
// just under the plug heads (as first drawn); override to U to raise it to the underside.
D_L = 10; D_D = 6; D_H = 6; D_TOP = PZ - 0.5; D_X0 = W/2 - D_L/2;   // 254 mm, one piece across the 256 mm bed; 6 in front to back; 6 in deep
use_stl = true;      // true: place the real part (trough.stl from trough.py) instead of the concept box
D_LIP_FRAC = 0.75;   // front wall height as a fraction of the box height (Brian: 75%)
D_LIP = D_H * D_LIP_FRAC;

BRICK = [6, 2.4, 1.2];

col_wall  = [0.87, 0.84, 0.77];
col_floor = [0.36, 0.26, 0.18];
col_ply   = [0.85, 0.72, 0.50];
col_top   = [0.12, 0.12, 0.12];
col_dark  = [0.16, 0.16, 0.17];
col_cord  = [0.10, 0.10, 0.10];
col_new   = highlight ? [0.95, 0.52, 0.15] : [0.09, 0.09, 0.09];   // every new part is orange, or black PETG as built

module box(size, at, c) { color(c) translate([in(at[0]), in(at[1]), in(at[2])]) cube([in(size[0]), in(size[1]), in(size[2])]); }

module room() {
    box([W + 80, D + 80, 1], [-40, -50, -1], col_floor);              // floor
    box([W + 80, 4, 96], [-40, D, 0], col_wall);                      // back wall
    box([W + 8, 0.5, 3], [-4, D - 0.5, 0], [0.97, 0.97, 0.95]);      // baseboard
    box([4, D + 4, 96], [-4, 0, 0], col_wall);                        // side walls
    box([4, D + 4, 96], [W, 0, 0], col_wall);
    box([JL + 40, 4.5, 96], [-40, -4.5, 0], col_wall);                // front wall left of the opening
    box([JL + 40, 4.5, 96], [W - JL, -4.5, 0], col_wall);             // front wall right of the opening
    box([W + 80, 4.5, 16], [-40, -4.5, 80], col_wall);                // header
    box([3.5, 0.75, 83.5], [JL - 3.5, -5.25, 0], [1, 1, 1]);          // casings
    box([3.5, 0.75, 83.5], [W - JL, -5.25, 0], [1, 1, 1]);
    box([OPN + 7, 0.75, 3.5], [JL - 3.5, -5.25, 80], [1, 1, 1]);
}

module desk() {
    box([W, D, T - 0.05], [0, 0, U], col_ply);                        // plywood slab
    box([W, D, 0.05], [0, 0, HT - 0.05], col_top);                    // black top
    box([CLW, D, CLH], [0, 0, U - CLH], [0.62, 0.45, 0.28]);          // cleats
    box([CLW, D, CLH], [W - CLW, 0, U - CLH], [0.62, 0.45, 0.28]);
    box([SL, SW, ST], [SX0, SY0, U - ST], col_dark);                  // power strip
    for (i = [0 : NOUT - 1])                                          // outlet faces
        box([1.2, 1.2, 0.02], [ox(i) - 0.6, SY0 + SW/2 - 0.6, U - ST - 0.02], [0.3, 0.3, 0.3]);
}

module plugs(list) { for (i = list) box([PW, PT, PH], [ox(i) - PW/2, SY0 + SW/2 - PT/2, PZ], col_cord); }

module floor_stuff() {
    box(TOWER, [TOWER_AT[0], TOWER_AT[1], 0], [0.20, 0.20, 0.22]);
    box(SHRED, [SHRED_AT[0], SHRED_AT[1], 0], [0.26, 0.26, 0.27]);
    box(BASKET, [BASKET_AT[0], BASKET_AT[1], 0], [0.62, 0.50, 0.34]);
}

module torus(R, r) { rotate_extrude($fn = 48) translate([in(R), 0]) circle(r = in(r), $fn = 12); }
module seg(a, b, r = 0.14) { hull() { translate([in(a[0]), in(a[1]), in(a[2])]) sphere(r = in(r), $fn = 12);
                                      translate([in(b[0]), in(b[1]), in(b[2])]) sphere(r = in(r), $fn = 12); } }
function py() = SY0 + SW/2;

// today: five cords drop from the strip, a brick hangs in mid air, slack lies on the floor
module cords_today() {
    plugs(TODAY);
    color(col_cord) for (i = TODAY) {
        x = ox(i);
        if (i == 2) {
            seg([x, py(), PZ], [x, py() + 1, U - 10]);
            box(BRICK, [x - BRICK[0]/2, py() - 0.5, U - 10 - BRICK[2]], col_cord);
            seg([x, py() + 1, U - 10 - BRICK[2]], [x + 1, py() + 4, 0.2]);
        } else if (i == 7) {
            seg([x, py(), PZ], [x, py() + 2, SHRED[2]]);
        } else {
            seg([x, py(), PZ], [x + 2, py() + 5, 0.2]);
        }
        if (i != 7) translate([in(x + 1), in(py() + 7), in(0.2)]) torus(3.5, 0.14);
    }
}

// ---------- A: wedge shelf behind the strip ----------
module a_profile(inset) {   // side-wall profile in the (y, z) plane, inches
    polygon([[D - A_D + inset, U - A_HF + inset], [D + 1, U - A_HB + inset + (A_HB - A_HF) / A_D],
             [D + 1, U + 1], [D - A_D + inset, U + 1]]);
}
module optionA() {
    color(col_new) difference() {
        union() {
            translate([in(A_X0), 0, 0]) rotate([90, 0, 90]) linear_extrude(in(A_L)) scale(25.4) a_profile(0);
            for (sx = [A_X0 - 1, A_X0 + A_L]) for (y = [D - A_D + 0.5, D - 2.5])              // screw ears
                translate([in(sx), in(y), in(U - 0.25)]) cube([in(1), in(1.5), in(0.25)]);
        }
        // hollow: open top against the slab, open back against the wall
        translate([in(A_X0 + A_WALL), 0, 0]) rotate([90, 0, 90]) linear_extrude(in(A_L - 2 * A_WALL)) scale(25.4) a_profile(A_WALL);
        // front open above a short lip
        translate([in(A_X0 - 1), in(D - A_D - 1), in(U - A_HF + A_LIP)]) cube([in(A_L + 2), in(1 + A_WALL + 0.01), in(A_HF)]);
        translate([in(-10), in(-10), in(U)]) cube([in(W + 20), in(D + 20), in(10)]);           // trim anything above the underside
        for (sx = [A_X0 - 0.5, A_X0 + A_L + 0.5]) for (y = [D - A_D + 1.25, D - 1.75])
            translate([in(sx), in(y), in(U - 1)]) cylinder(d = in(0.2), h = in(2));
    }
    plugs([0 : NOUT - 1]);
    color(col_cord) for (i = [0 : NOUT - 1]) {
        x = ox(i); xin = min(max(x, A_X0 + 2.5), A_X0 + A_L - 2.5);
        yc = D - 4.2; zc = a_floor(yc) + A_WALL + 0.35 + (i % 2) * 0.45;
        seg([x, py(), PZ], [x, py() + 1.2, PZ - 1.2]);
        seg([x, py() + 1.2, PZ - 1.2], [xin, D - A_D + 1.5, a_floor(D - A_D + 1.5) + 0.5]);
        translate([in(xin), in(yc), in(zc)]) rotate([-A_SLOPE, 0, 0]) torus(1.8, 0.14);
    }
    translate([in(A_X0 + 1), in(D - A_D + 1.2), in(a_floor(D - A_D + 1.2) + A_WALL)]) rotate([-A_SLOPE, 0, 0])
        color(col_cord) cube([in(BRICK[0]), in(BRICK[1]), in(BRICK[2])]);
}

// ---------- B: box in the pocket behind the left jamb return ----------
module optionB() {
    zb = U - B_H;
    color(col_new) difference() {
        union() {
            translate([in(B_X0), in(B_Y0), in(zb)]) cube([in(B_XW), in(B_L), in(B_H)]);
            for (y = [B_Y0 + 1, B_Y0 + B_L - 2.5])                                               // screw ears, inboard side
                translate([in(B_X0 + B_XW), in(y), in(U - 0.25)]) cube([in(1), in(1.5), in(0.25)]);
            translate([in(SX0), in(RW_Y), in(U - RW_H)]) cube([in(SL - 2), in(RW_W), in(RW_H)]);  // raceway behind the strip
        }
        translate([in(B_X0 + B_WALL), in(B_Y0 + B_WALL), in(zb + B_WALL)])                       // open top
            cube([in(B_XW - 2*B_WALL), in(B_L - 2*B_WALL), in(B_H + 1)]);
        translate([in(B_X0 + B_XW - 1), in(B_Y0 - 1), in(zb + B_LIP)]) cube([in(2), in(B_L + 2), in(B_H)]);  // inboard side open above the lip
        translate([in(SX0 - 1), in(RW_Y + 0.2), in(U - RW_H - 1)]) cube([in(SL), in(RW_W - 0.4), in(RW_H + 1 - 0.2)]);  // raceway channel, open at the bottom
        for (y = [B_Y0 + 1.75, B_Y0 + B_L - 1.75])
            translate([in(B_X0 + B_XW + 0.5), in(y), in(U - 1)]) cylinder(d = in(0.2), h = in(2));
    }
    plugs([0 : NOUT - 1]);
    color(col_cord) for (i = [0 : NOUT - 1]) {
        x = ox(i); zr = U - RW_H/2; yr = RW_Y + RW_W/2;
        yc = B_Y0 + 2.5 + i * (B_L - 5) / (NOUT - 1); zc = zb + B_WALL + 0.4 + (i % 3) * 0.45;
        seg([x, py(), PZ], [x, yr, zr]);                                  // up behind the strip into the raceway
        seg([x, yr, zr], [B_X0 + B_XW - 0.5, yr, zr]);                     // along the raceway to the pocket
        seg([B_X0 + B_XW - 0.5, yr, zr], [B_X0 + B_XW/2, yc, zc]);        // down into the box
        translate([in(B_X0 + B_XW/2), in(yc), in(zc)]) rotate([0, 90, 0]) torus(1.6, 0.14);   // coil lying flat against the wall side
    }
    box([BRICK[1], BRICK[0], BRICK[2]], [B_X0 + 0.5, B_Y0 + 8, zb + B_WALL], col_cord);
}

// ---------- C: coil hooks behind the strip ----------
module optionC() {
    color(col_new) {
        translate([in(C_X0), in(C_Y - 0.6), in(U - 0.25)]) cube([in(C_L), in(1.2), in(0.25)]);
        for (i = [0 : NOUT - 1]) {
            x = C_X0 + 1 + i * (C_L - 2) / (NOUT - 1);
            translate([in(x), in(C_Y), in(U - C_DROP)]) cylinder(d = in(0.45), h = in(C_DROP));
            hull() { translate([in(x), in(C_Y), in(U - C_DROP)]) sphere(d = in(0.45));
                     translate([in(x), in(C_Y + 1.4), in(U - C_DROP + 0.35)]) sphere(d = in(0.45)); }   // prong points to the wall
        }
    }
    plugs([0 : NOUT - 1]);
    color(col_cord) for (i = [0 : NOUT - 1]) {
        x = C_X0 + 1 + i * (C_L - 2) / (NOUT - 1);
        seg([ox(i), py(), PZ], [x, C_Y + 0.8, U - C_DROP + C_COIL_R]);
        translate([in(x), in(C_Y + 0.8), in(U - C_DROP - 0.1)]) rotate([90, 0, 90]) torus(C_COIL_R, 0.14);
    }
    box(BRICK, [W/2 + 6, D - 4.5, HT], col_cord);                                             // brick on the desk
    color(col_cord) translate([in(W/2 + 5.4), in(D - 3.25), in(HT - 0.3)]) cylinder(d = in(2), h = in(0.35));   // grommet
}

// ---------- D: trough on the back wall under the plugs (PICKED), front wall 75% of the height ----------
module optionD() {
    zb = D_TOP - D_H;
    if (use_stl)
        color(col_new) translate([in(W/2), in(D) - in(D_D)/2, in(zb)]) import("../trough.stl", convexity = 4);
    else color(col_new) difference() {
        union() {
            translate([in(D_X0), in(D - D_D), in(zb)]) cube([in(D_L), in(D_D), in(D_H)]);
            translate([in(D_X0 - 1.25), in(D - 0.25), in(zb)]) cube([in(D_L + 2.5), in(0.25), in(min(D_H + 1.25, U - zb))]);   // wall plate never enters the slab
        }
        translate([in(D_X0 + A_WALL), in(D - D_D + A_WALL), in(zb + A_WALL)]) cube([in(D_L - 2*A_WALL), in(D_D - 2*A_WALL), in(D_H + 1)]);   // open top
        translate([in(D_X0 - 1), in(D - D_D - 1), in(zb + D_LIP)]) cube([in(D_L + 2), in(1 + A_WALL + 0.01), in(D_H)]);   // front open above the wall
        for (sx = [D_X0 - 0.6, D_X0 + D_L + 0.6]) for (z = [zb + 0.6, zb + D_H + 0.6])   // wall anchors
            translate([in(sx), in(D - 1), in(z)]) rotate([-90, 0, 0]) cylinder(d = in(0.2), h = in(2));
    }
    plugs([0 : NOUT - 1]);
    color(col_cord) for (i = [0 : NOUT - 1]) {
        x = ox(i); xin = min(max(x, D_X0 + 2.5), D_X0 + D_L - 2.5); zc = zb + 0.6 + (i % 2) * 0.5;
        seg([x, py(), PZ], [x, D - D_D - 0.4, D_TOP + 0.25]);          // down and back, over the front wall
        seg([x, D - D_D - 0.4, D_TOP + 0.25], [xin, D - 3, zc]);        // drop through the open top
        translate([in(xin), in(D - 3), in(zc)]) torus(1.6, 0.14);
    }
    box(BRICK, [D_X0 + 1, D - D_D + 0.8, zb + A_WALL], col_cord);
}

module scene() {
    room(); desk(); floor_stuff();
    if (option == "today") cords_today();
    if (option == "A") optionA();
    if (option == "B") optionB();
    if (option == "C") optionC();
    if (option == "D") optionD();
}

CUT_X = ox(4);      // section through outlet 5
if (view == "section")
    intersection() { scene(); color([0.45, 0.45, 0.45]) translate([-in(60), -in(200), -in(20)]) cube([in(60 + CUT_X), in(400), in(150)]); }
else if (view == "front")
    intersection() { scene(); color([0.45, 0.45, 0.45]) translate([-in(60), in(8), -in(20)]) cube([in(W + 120), in(100), in(150)]); }
else
    scene();
