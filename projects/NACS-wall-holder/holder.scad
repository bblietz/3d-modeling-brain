// NACS wall holder for the Tesla Gen 3 Wall Connector handle.
// A drum on a square backing plate; the wand comes out of the drum's right side
// 45 degrees down and leans away from the wall; the nose hangs on a fixed cleat
// in the connector's own lock notch, on the lower wall of the cavity.
//
// World frame (also the print orientation): the plate lies in XY with its back
// face on the wall at Z=0, +Z out from the wall, +X to the right as you face the
// wall, +Y up.
//
// Render views: render.sh.  Export: openscad -D display=false -D show_nose=false -o holder.stl holder.scad

include <nose_outline.scad>;

display = true;       // rotate so +Y is up on screen for renders
show_nose = true;     // ghost of the connector, docked
section = 0;          // 1: cut along the wand to show the cleat, 2: cut across the notch
show_wall = true;     // faint wall plane behind the plate in renders
$fn = 96;

// connector facts (Tesla TS-0023666, STEP)
nose_len = 32.5;
nose_h = 35.52;
notch_a = 17.13; notch_b = 23.35; notch_d = 3.96; notch_w = 9.71;
handle_len = 194.5;

// design
wand_down = 45;       // below horizontal, to the right, seen from the front
wand_lean = 20;       // away from the wall
clear = 0.5;
roof_extra = 0.5;     // roof clearance over the tip zone is clear + roof_extra
roof_relief = 4;      // room over the nose to lift it over the cleat
tight_len = 5;        // the roof stays tight this far from the cavity floor
cleat_proud = 2.2; cleat_w = 8;
cleat_a = 18.3; cleat_c = 20.3; cleat_b = 22.5;   // load face, crown end, lead-in end, from the floor
undercut = 10;
mouth = 33;
plate_w = 120; plate_t = 5; plate_r = 8; hole_in = 10; hole_d = 5; csk_d = 10;
drum_r = 50; drum_l = 100;                 // plate front to flange front
flange_t = 8; flange_r = 62; flange_point = 84; flare_h = 15;
mouth_z = 41;                              // mouth centre out from the wall

half = nose_h / 2;
floor_y = -(half + clear);
total_l = plate_t + drum_l;
d = [cos(wand_lean) * cos(-wand_down), cos(wand_lean) * sin(-wand_down), sin(wand_lean)];   // along the wand, tip to grip
v0 = [0, 1, 0] - ([0, 1, 0] * d) * d;
v = v0 / norm(v0);                         // button side, up along the wand
w = cross(d, v);                           // across the wand, toward the flange
M = [drum_r * cos(-wand_down), drum_r * sin(-wand_down), mouth_z];   // mouth centre, on the drum surface
T = M - mouth * d;                                                     // cavity floor centre

module in_cavity_frame() multmatrix([[w[0], v[0], d[0], T[0]], [w[1], v[1], d[1], T[1]], [w[2], v[2], d[2], T[2]], [0, 0, 0, 1]]) children();

module profile(up = 0) hull() { offset(r = clear) polygon(nose_outline); translate([0, up]) offset(r = clear) polygon(nose_outline); }

module cavity() {
    translate([0, 0, -0.01]) linear_extrude(mouth + 40) profile(roof_extra);
    hull() {
        translate([0, 0, tight_len]) linear_extrude(0.01) profile(roof_extra);
        translate([0, 0, tight_len + roof_relief]) linear_extrude(mouth + 40) profile(roof_extra + roof_relief);
    }
}

module cleat() {
    multmatrix([[0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]])
        linear_extrude(height = cleat_w, center = true)
            polygon([[cleat_a, floor_y - 1.5], [cleat_b, floor_y - 1.5], [cleat_b, floor_y], [cleat_c, floor_y + cleat_proud],
                     [cleat_a + cleat_proud * tan(undercut), floor_y + cleat_proud], [cleat_a, floor_y]]);
}

module nose() {
    translate([0, -clear, cleat_a - notch_a]) difference() {
        union() {
            linear_extrude(nose_len) polygon(nose_outline);
            hull() {
                translate([0, 0, nose_len]) linear_extrude(0.01) polygon(nose_outline);
                translate([0, 3, 46]) linear_extrude(0.01) offset(r = 2) polygon(nose_outline);
            }
            hull() {
                translate([0, 3, 46]) linear_extrude(0.01) offset(r = 2) polygon(nose_outline);
                translate([0, -6, handle_len]) linear_extrude(0.01) offset(r = 8) square([44 - 16, 52 - 16], center = true);
            }
        }
        translate([-notch_w / 2, -half - 1, notch_a]) cube([notch_w, notch_d + 1, notch_b - notch_a]);
    }
}

module body() {
    linear_extrude(plate_t) offset(r = plate_r) offset(delta = -plate_r) square(plate_w, center = true);
    translate([0, 0, plate_t - 0.01]) cylinder(h = total_l - flange_t - flare_h - plate_t + 0.02, r = drum_r);
    translate([0, 0, total_l - flange_t - flare_h]) cylinder(h = flare_h + 0.01, r1 = drum_r, r2 = flange_r);
    translate([0, 0, total_l - flange_t]) linear_extrude(flange_t) hull() {
        circle(r = flange_r);
        translate(flange_point * [cos(-wand_down), sin(-wand_down)]) circle(r = 6);
    }
}

module holes() {
    for (sx = [-1, 1], sy = [-1, 1]) translate([sx * (plate_w / 2 - hole_in), sy * (plate_w / 2 - hole_in), 0]) {
        translate([0, 0, -1]) cylinder(h = plate_t + 2, d = hole_d);
        translate([0, 0, plate_t - (csk_d - hole_d) / 2]) cylinder(h = (csk_d - hole_d) / 2 + 0.01, d1 = hole_d, d2 = csk_d);
    }
}

module holder() {
    difference() {
        body();
        in_cavity_frame() cavity();
        holes();
    }
    color("limegreen") in_cavity_frame() cleat();
}

module model() {
    if (section == 1) intersection() { holder(); in_cavity_frame() translate([-500, -500, -500]) cube([500, 1000, 1000]); }
    else if (section == 2) intersection() { holder(); in_cavity_frame() translate([-500, -500, -500]) cube([1000, 1000, 500 + 20.25]); }
    else holder();
    if (show_nose) color("steelblue", section == 0 ? 0.55 : 0.3) in_cavity_frame() {
        if (section == 1) intersection() { nose(); translate([-500, -500, -500]) cube([500, 1000, 1000]); }
        else if (section == 2) intersection() { nose(); translate([-500, -500, -500]) cube([1000, 1000, 500 + 20.25]); }
        else nose();
    }
    if (show_wall) color("gray", 0.15) translate([-160, -200, -1]) cube([320, 320, 1]);
}

if (display) rotate([90, 0, 0]) model(); else model();

echo(str("wand direction d=", d, " up v=", v, " across w=", w, " mouth M=", M, " tip T=", T));
