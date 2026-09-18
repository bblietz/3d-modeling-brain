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
// Coupon:       coupon.stl / coupon-print.3mf are the PRINTED fit coupon, frozen at commit cb42b65 (shallow cavity, lean 20).
//               part="coupon" now gives the deep-cavity version, which Brian chose not to print (2026-09-17):
//               openscad -D display=false -D show_nose=false -D 'part="coupon"' -o coupon-deep.stl holder.scad

include <nose_outline.scad>;
include <bell_sections.scad>;

display = true;       // rotate so +Y is up on screen for renders
show_nose = true;     // ghost of the connector, docked
section = 0;          // 1: cut along the wand to show the cleat, 2: cut across the notch
show_wall = true;     // faint wall plane behind the plate in renders
part = "holder";      // "coupon": the cavity and cleat with thin walls on a piece of the plate, print orientation unchanged
show_logo = true;     // Tesla T recessed in the flange face (reference/tesla-t.svg, official artwork)
$fn = 96;

// connector facts (Tesla TS-0023666, STEP)
nose_len = 32.5;
nose_h = 35.52;
notch_a = 17.13; notch_b = 23.35; notch_d = 3.96; notch_w = 9.71;
handle_len = 194.5;

// design
wand_down = 45;       // below horizontal, to the right, seen from the front
wand_lean = 15;       // away from the wall; 20 no longer fits between the plate and the flange with the deeper cavity (pipeline/zbudget.py)
clear = 0.5;
roof_extra = 0.5;     // roof clearance over the tip zone is clear + roof_extra
roof_relief = 4;      // room over the nose to lift it over the cleat
tight_len = 5;        // the roof stays tight this far from the cavity floor
cleat_proud = 2.2; cleat_w = 8;
cleat_a = 18.3; cleat_c = 20.3; cleat_b = 22.5;   // load face, crown end, lead-in end, from the floor
undercut = 10;
cleat_depth = 31.75;  // the cleat's holding wall to the opening, along the cleat's wall (Brian: 1.25 in)
bell_extra = 2.5;     // more roof relief toward the mouth: a lifted handle swings higher the further out it is
grip_clear = 1.5;     // extra room past the end of Tesla's housing CAD (48.4 from the tip), where the grip is not modelled
grip_flare = 0.1;     // and this much more per mm beyond it
plate_w = 120; plate_t = 5; plate_r = 8; hole_in = 10; hole_d = 5; csk_d = 10;
drum_r = 50; drum_l = 75;                  // plate front to flange front
flange_t = 8; flange_point = 84; point_angle = -135;   // teardrop point to the lower left, clear of the wand
fillet_flange = 12;                        // concave blend from the drum into the flange face
fillet_plate = 8;                          // concave blend from the drum into the plate
flange_r = drum_r + fillet_flange;
logo_h = 70; logo_depth = 1;               // Tesla T height on the flange face (57% of the round part, as on the sample), recess depth
coupon_wall = 3;                           // wall around the cavity in the fit coupon
coupon_slab = 0.9;                         // the coupon keeps only this much under the cavity's deepest corner (3 layers)

half = nose_h / 2;
floor_y = -(half + clear);
total_l = plate_t + drum_l;
d = [cos(wand_lean) * cos(-wand_down), cos(wand_lean) * sin(-wand_down), sin(wand_lean)];   // along the wand, tip to grip
v0 = [0, 1, 0] - ([0, 1, 0] * d) * d;
v = v0 / norm(v0);                         // button side, up along the wand
w = cross(d, v);                           // across the wand, toward the flange
// where the cavity wall line at (up b, across c) leaves the drum surface, along the wand from the mouth centre
M0 = drum_r * [cos(-wand_down), sin(-wand_down)];
function lip_q(b, c) = let(p = M0 + b * [v[0], v[1]] + c * [w[0], w[1]], dxy = [d[0], d[1]],
                           A = dxy * dxy, B = 2 * (dxy * p), C = p * p - drum_r * drum_r)
    (-B + sqrt(B * B - 4 * A * C)) / (2 * A);
mouth = cleat_a + cleat_depth - lip_q(floor_y, 0);   // cavity end wall to the mouth centre, so the lip on the cleat's wall is cleat_depth from the holding wall
behind = 3;                                          // solid left between the wall and the cavity's deepest corner, which dips into the 5 mm plate
mouth_z = 36.3;                                      // mouth centre out from the wall that gives `behind` (pipeline/zbudget.py)
M = [M0[0], M0[1], mouth_z];                         // mouth centre, on the drum surface
T = M - mouth * d;                                                     // cavity floor centre

module in_cavity_frame() multmatrix([[w[0], v[0], d[0], T[0]], [w[1], v[1], d[1], T[1]], [w[2], v[2], d[2], T[2]], [0, 0, 0, 1]]) children();

tip_gap = cleat_a - notch_a;              // nose tip to the cavity end wall when the notch hangs on the cleat
nb = len(bell_sections);
function bell_a(i) = bell_sections[i][0] + tip_gap;
function bell_up(i) = roof_extra + roof_relief + bell_extra * (bell_sections[i][0] - bell_sections[0][0]) / (bell_sections[nb - 1][0] - bell_sections[0][0]);
far_a = mouth + 45;                       // well outside the drum

module profile(up = 0, grow = 0) hull() { offset(r = clear + grow) polygon(nose_outline); translate([0, up]) offset(r = clear + grow) polygon(nose_outline); }
module bell_profile(i, grow = 0, more = 0) hull() {
    offset(r = clear + grow + more) polygon(bell_sections[i][1]);
    translate([0, bell_up(i) + more]) offset(r = clear + grow + more) polygon(bell_sections[i][1]);
}
module slice(a) translate([0, 0, a]) linear_extrude(0.01) children();

// The cavity as convex segments along the wand (grow > 0 gives the same shape with a wall around it, for the coupon).
cavity_segs = nb + 2;
module cavity_seg(i, grow = 0) {
    if (i == 0) translate([0, 0, -0.01 - grow]) linear_extrude(bell_a(0) + 0.01 + grow) profile(roof_extra, grow);      // the nose; roof tight over the tip
    else if (i == 1) hull() {                                                                                            // roof relief to lift the nose over the cleat
        slice(tight_len) profile(roof_extra, grow);
        translate([0, 0, tight_len + roof_relief]) linear_extrude(bell_a(0) - tight_len - roof_relief) profile(roof_extra + roof_relief, grow);
    }
    else if (i <= nb) hull() { slice(bell_a(i - 2)) bell_profile(i - 2, grow); slice(bell_a(i - 1)) bell_profile(i - 1, grow); }   // Tesla's housing behind the shoulder
    else hull() {                                                                                                        // the grip beyond Tesla's CAD
        slice(bell_a(nb - 1)) bell_profile(nb - 1, grow, grip_clear);
        slice(far_a) bell_profile(nb - 1, grow, grip_clear + grip_flare * (far_a - bell_a(nb - 1)));
    }
}
module cavity(grow = 0) for (i = [0 : cavity_segs - 1]) cavity_seg(i, grow);

module cleat() {
    multmatrix([[0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]])
        linear_extrude(height = cleat_w, center = true)
            polygon([[cleat_a, floor_y - 1.5], [cleat_b, floor_y - 1.5], [cleat_b, floor_y], [cleat_c, floor_y + cleat_proud],
                     [cleat_a + cleat_proud * tan(undercut), floor_y + cleat_proud], [cleat_a, floor_y]]);
}

module handle() {
    translate([0, -clear, tip_gap]) difference() {
        union() {
            linear_extrude(nose_len) polygon(nose_outline);
            for (i = [0 : nb - 2]) hull() { slice(bell_sections[i][0]) polygon(bell_sections[i][1]); slice(bell_sections[i + 1][0]) polygon(bell_sections[i + 1][1]); }
            hull() {   // the grip is not in Tesla's CAD: a plain taper to the handle's overall size
                slice(bell_sections[nb - 1][0]) polygon(bell_sections[nb - 1][1]);
                translate([0, 3.5, handle_len]) linear_extrude(0.01) offset(r = 8) square([44 - 16, 46 - 16], center = true);
            }
        }
        translate([-notch_w / 2, -half - 1, notch_a]) cube([notch_w, notch_d + 1, notch_b - notch_a]);
    }
}

module drum_profile() {
    zf = total_l - flange_t;
    a = [for (t = [0 : 5 : 90]) [drum_r + fillet_plate - fillet_plate * sin(t), plate_t + fillet_plate - fillet_plate * cos(t)]];
    b = [for (t = [0 : 5 : 90]) [drum_r + fillet_flange - fillet_flange * cos(t), zf - fillet_flange + fillet_flange * sin(t)]];
    polygon(concat([[0, plate_t - 0.01]], a, b, [[drum_r + fillet_flange, zf + 0.01], [0, zf + 0.01]]));
}

module body() {
    linear_extrude(plate_t) offset(r = plate_r) offset(delta = -plate_r) square(plate_w, center = true);
    rotate_extrude() drum_profile();
    translate([0, 0, total_l - flange_t]) linear_extrude(flange_t) hull() {
        circle(r = flange_r);
        translate(flange_point * [cos(point_angle), sin(point_angle)]) circle(r = 6);
    }
}

// official emblem, two paths; the 0.05 mm closing heals a 0.02 mm self-crossing at the top of the stem in Tesla's outline
module logo() translate([0, 0, total_l - logo_depth]) linear_extrude(logo_depth + 0.01)
    resize([0, logo_h], auto = true) offset(r = -0.05) offset(r = 0.05) import("reference/tesla-t.svg", center = true);

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
        if (show_logo) logo();
    }
    color("limegreen") in_cavity_frame() cleat();
}

// Fit coupon: the real cavity, cleat and mouth cut out of the holder with coupon_wall of body around them,
// carried down to a thin slice of the plate so it prints in the same orientation (plate on the bed) with the
// same roof supports. Exported sitting on Z=0.
module coupon() translate([0, 0, coupon_slab - behind]) intersection() { coupon_core(); translate([-500, -500, behind - coupon_slab]) cube(1000); }

module coupon_core() {
    intersection() {
        holder();
        // the cavity with coupon_wall around it, each segment carried straight down to the plate
        for (i = [0 : cavity_segs - 1]) hull() {
            in_cavity_frame() cavity_seg(i, coupon_wall);
            linear_extrude(0.01) projection() in_cavity_frame() cavity_seg(i, coupon_wall);
        }
        cylinder(r = drum_r, h = 2 * total_l);                        // no plate outside the drum
    }
}

// the cavity inside the drum radius, for pipeline/zbudget.py
module probe() intersection() { in_cavity_frame() cavity(); cylinder(r = drum_r, h = 1000, center = true); }

// what the docked handle would cut out of the holder: must be empty
module clash() intersection() { holder(); in_cavity_frame() handle(); }

module part_body() { if (part == "coupon") coupon(); else if (part == "probe") probe(); else if (part == "clash") clash(); else holder(); }

module model() {
    if (section == 1) intersection() { part_body(); in_cavity_frame() translate([-500, -500, -500]) cube([500, 1000, 1000]); }
    else if (section == 2) intersection() { part_body(); in_cavity_frame() translate([-500, -500, -500]) cube([1000, 1000, 500 + 20.25]); }
    else part_body();
    if (show_nose) color(section == 0 ? "steelblue" : "gainsboro", section == 0 ? 0.55 : 0.85) in_cavity_frame() {
        if (section == 1) intersection() { handle(); translate([-500, -500, -500]) cube([500, 1000, 1000]); }
        else if (section == 2) intersection() { handle(); translate([-500, -500, -500]) cube([1000, 1000, 500 + 20.25]); }
        else handle();
    }
    if (show_wall) color("gray", 0.15) translate([-160, -200, -1]) cube([320, 320, 1]);
}

if (display) rotate([90, 0, 0]) model(); else model();

echo(str("wand direction d=", d, " up v=", v, " across w=", w, " mouth M=", M, " tip T=", T, " mouth depth=", mouth));
echo(str("lips from the cavity end wall: cleat wall ", mouth + lip_q(floor_y, 0), " roof ", mouth + lip_q(half + clear + bell_up(nb - 1), 0),
         " flange side ", mouth + lip_q(0, 21.8), " wall side ", mouth + lip_q(0, -21.8)));
