// NACS wall holder for the Tesla Gen 3 Wall Connector handle.
// A drum on a square backing plate; the wand comes out of the drum's right side
// 45 degrees down and leans away from the wall; the nose hangs on a fixed cleat
// in the connector's own lock notch, on the lower wall of the cavity.
// Docking: nose in with the grip raised dock_tilt, push to the stop, lower the grip; the nose pivots on its tip and
// the lock pocket comes down over the cleat. The roof is the snug size over the tip and opens only as far as that
// pivot needs. The hanging load turns the wand the other way (tip up), which the roof over the tip stops, so the
// load cannot undo the docking motion (pipeline/insertion.py checks both the way in and the hold).
//
// World frame (also the print orientation): the plate lies in XY with its back
// face on the wall at Z=0, +Z out from the wall, +X to the right as you face the
// wall, +Y up.
//
// Render views: render.sh.  Export: openscad -D display=false -D show_nose=false -D show_wall=false -o holder.stl holder.scad
// Coupon:       openscad -D display=false -D show_nose=false -D show_wall=false -D 'part="coupon"' -o coupon.stl holder.scad
//               (the nose cavity and cleat only, cut off just past the nose shoulder: coupon_cut)

include <nose_outline.scad>;
include <bell_sections.scad>;
include <rim_round.scad>;
include <nacs_face.scad>;

display = true;       // rotate so +Y is up on screen for renders
show_nose = true;     // ghost of the connector, docked
section = 0;          // 1: cut along the wand to show the cleat, 2: cut across the notch
pose_tilt = 0;        // ghost wand only: tilted up about its tip by this much, and pose_out further out along the tilted wand
pose_out = 0;
show_wall = true;     // faint wall plane behind the plate in renders
part = "holder";      // "coupon": the cavity and cleat with thin walls on a piece of the plate, print orientation unchanged
show_logo = true;     // the emblem recessed in the flange face (insertion.py turns it off for its export)
$fn = 96;

// connector facts (Tesla TS-0023666, STEP)
nose_len = 32.5;
nose_h = 35.52;
notch_a = 17.14; notch_b = 23.35;   // lock pocket walls at its base, from the nose tip (spec: 6.2 +-0.2 long, 9.71 +-0.2 wide at the base, 4 +-0.2 deep, 3 deg draft)
// the pocket across the wand, from Tesla's CAD: [half width, height above the nose's lowest line], mouth to crown.
// It opens to 11.6 at the mouth, its side walls lean 18 degrees, and its base is a dome 4.02 high at the centre.
pocket_x = [[5.78, 0.85], [5.57, 1.46], [5.41, 1.96], [5.25, 2.46], [5.10, 2.96], [4.65, 3.46], [3.73, 3.66], [2.46, 3.86], [1.46, 3.96], [0.42, 4.01], [0, 4.02]];
pocket_h = 4.02; pocket_len_mouth = 6.54;   // depth at the centre; length at the mouth (17.03 to 23.57 from the tip)
handle_len = 194.5;

// design
wand_down = 45;       // below horizontal, to the right, seen from the front
wand_lean = 15;       // away from the wall; 20 no longer fits between the plate and the flange with the deeper cavity (pipeline/zbudget.py)
clear = 0.5;
dock_tilt = 12;       // the roof opens this far for the wand coming in grip-up and pivoting down on its tip; at 10 there is no way in (pipeline/insertion.py)
dock_top = 0.1;       // roof clearance over the tilted nose (Tesla's nose tapers toward its tip, which adds about 0.5 there)
// The cleat is a wedge that fills the lock pocket: a ramp rising from the mouth side to a sharp edge at the back,
// and an overhanging back face, so the pocket's wall hangs on that edge, up near the pocket's base.
cleat_clear = 0.45;   // between the cleat and the pocket, sides and top
tip_gap = 2.5;        // nose tip to the cavity end wall when hanging: the travel left to push the pocket past the edge so the nose can drop
cleat_a = notch_a + tip_gap;                       // the holding edge, from the cavity end wall
cleat_h = pocket_h - cleat_clear;                  // edge height above the floor
cleat_b = cleat_a + pocket_len_mouth - 0.11 - cleat_clear - 0.1;   // foot of the ramp, just inside the pocket's mouth-side wall
undercut = 15;        // the back face overhangs by this much, so the contact is at the edge
cleat_depth = 44.45;  // the cleat's holding wall to the opening, along the cleat's wall: 1.75 in (Brian, 2026-10-08: cavity 1/2 in deeper; was 1.25 in)
grip_flare = 0.1;     // the sides and roof open by this much per mm from the nose shoulder to the outer edge, with no step: 1.6 by the end
                      // of Tesla's housing CAD (48.2 from the tip), where the grip is not modelled, and on at the same rate
floor_knee = 4;       // the floor carries the hanging wand, so it keeps Tesla's line to the end of that CAD, then falls to the flare over this length
plate_w = 101.6; plate_t = 5; plate_r = 10; hole_in = 10; hole_d = 5; csk_d = 10;   // corner radius = hole_in, so each countersink sits centred in its rounded corner
edge_r = 25.4 / 16;  // every outside edge is rounded at least 1/16 in (Brian, 2026-09-18), except the plate's back edge and the screw holes;
                     // the cleat keeps its sharp holding edge and the T its crisp outline. The mouth's rim: rim_round.scad, from pipeline/rim_round.py
drum_r = 45; drum_l = 100.4;                // plate front to flange front: 75 plus 1 in (Brian, 2026-10-08: "only be 1 in deeper", down from the 2 in first asked); drum 90 across
                                            // for the 1/2 in deeper cavity (Brian, 2026-10-08; 80 left 0.1 mm of wall at the cavity's far corner, 90 leaves 5)
flange_t = 8;                              // the flange is round (Brian, 2026-09-18: no point at the lower left)
fillet_flange = 7;                         // concave blend from the drum into the flange face (12 with the 80 drum; 7 keeps the flange at 104 on the 90 drum)
fillet_plate = 7;                          // concave blend from the drum into the plate (8 with the 80 drum; its foot must stay inside the screw countersinks, 52.7 off the axis)
flange_r = drum_r + fillet_flange;
// the top lip (Brian, 2026-10-08): a squared-off tab with rounded corners rising from the round flange, full width so its sides meet the flange's
// circle tangentially (his pick B over a narrower tab), 1.5 in above the flange's top (3 in was too tall). It hides the plate's top screws from a
// driver, hence top_mount.
tab_w = 104; tab_rise = 38.1; tab_r = 12.7;  // width (= flange diameter), rise above the flange's top, corner radius
tab_style = "crest";   // the lip's outline: "plain" flat top; "arch" crowned top; "shield" sides tapering to tab_top_w; "crest" shield sides with the arch's
                       // crowned top (Brian, 2026-10-08: "combine the top of the arch lip with the shield lip"); "gable" peaked top; "none" for the round flange alone
tab_top_w = 84;        // shield: width at the top
tab_crown = 10;        // arch: rise of the top's arc at the centre
tab_peak = 12;         // gable: rise of the apex above the eaves
tab_trim = "frame";    // "frame": a recessed line following the whole face's outline (Brian, 2026-10-08: yes)
frame_in = 6; frame_w = 2.5; frame_depth = 1;
top_mount = "none";    // reaching the top screws behind the lip: "keyhole" slots open at the plate's top edge (hang the holder on the top screws, drive the bottom two);
                       // "holes" driver holes through the lip; "none" plain holes (Brian, 2026-10-08: the crest's edge is 6 mm outside the top screw centres, driver goes in at a 6 degree tilt)
driver_d = 12;
logo_h = 59; logo_depth = 1;               // emblem height on the flange face (57% of the round part, as the T was), recess depth
emblem = "tesla";      // "tesla" the T (reference/tesla-t.svg, official artwork; Brian, 2026-10-08: back in after a look at generic ones); "bolt" a lightning bolt; "plug" a
                       // two-prong plug; "nacs" the connector's own face from Tesla's housing STEP (nacs_face.scad, pipeline/nacs_face.py); "ev" the letters EV; "none"
lip_text = true;       // the TESLA wordmark (reference/tesla-wordmark.svg, official artwork) recessed in the lip, bent along the crest's arch (Brian, 2026-10-08)
wordmark_w = 62;       // its width along the arc
wordmark_gap = 2;      // between the wordmark's top and the frame line's inner edge
coupon_wall = 3;                           // wall around the cavity in the fit coupon
coupon_slab = 0.9;                         // the coupon keeps only this much under the cavity's deepest corner (3 layers)
coupon_cut = tip_gap + nose_len + 1;       // the coupon ends here, just past the nose shoulder: the deeper opening gets no coupon (Brian, 2026-09-17)

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
mouth_z = 61.48;                                      // mouth centre out from the wall: the wand stays at the far end, mouth top 3.6 mm under the flange as validated (cut_top = flange underside - 3.6); the deepest corner is then 23 mm off the wall, pipeline/zbudget.py
M = [M0[0], M0[1], mouth_z];                         // mouth centre, on the drum surface
T = M - mouth * d;                                                     // cavity floor centre

module in_cavity_frame() multmatrix([[w[0], v[0], d[0], T[0]], [w[1], v[1], d[1], T[1]], [w[2], v[2], d[2], T[2]], [0, 0, 0, 1]]) children();

nb = len(bell_sections);
function bell_a(i) = bell_sections[i][0] + tip_gap;
far_a = mouth + 45;                       // well outside the drum
function flare(a) = grip_flare * max(0, a - bell_a(0));

module profile(grow = 0) offset(r = clear + grow) polygon(nose_outline);
module bell_profile(i, grow = 0, more = 0, drop = 0) intersection() {
    hull() {
        offset(r = clear + grow + more) polygon(bell_sections[i][1]);
        translate([0, more]) offset(r = clear + grow + more) polygon(bell_sections[i][1]);
    }
    translate([-100, min([for (q = bell_sections[i][1]) q[1]]) - clear - grow - drop]) square(200);   // the floor, lower by drop only
}
// the nose profile for the tilted wand: dock_top over its top line instead of clear
module tilt_profile(grow = 0) intersection() { profile(grow); translate([-50, -50]) square([100, 50 + half + dock_top + grow]); }
module slice(a) translate([0, 0, a]) linear_extrude(0.01) children();

// The cavity as convex pieces along the wand (grow > 0 gives the same shape with a wall around it, for the coupon).
// Each piece is the docked wand's room hulled with the same piece of the wand tilted up about its tip, so the union is
// what the docking pivot sweeps: snug roof over the tip, opening at dock_tilt toward the mouth, end wall leaning back.
nose_step = 2.5;                                          // short pieces keep the roof from being bridged flat over the tip
nose_pieces = ceil((nose_len + tip_gap) / nose_step);
cavity_segs = nose_pieces + nb + 1;
module piece(i, grow, tilted) {
    if (i < nose_pieces) {                                                                                               // the nose
        a0 = i == 0 ? -0.01 - grow : i * nose_step; a1 = min((i + 1) * nose_step, bell_a(0));
        translate([0, 0, a0]) linear_extrude(a1 - a0) if (tilted) tilt_profile(grow); else profile(grow);
    }
    else if (i < nose_pieces + nb - 1) { j = i - nose_pieces; hull() {                                                   // Tesla's housing behind the shoulder
        slice(bell_a(j)) bell_profile(j, grow, flare(bell_a(j))); slice(bell_a(j + 1)) bell_profile(j + 1, grow, flare(bell_a(j + 1))); } }
    else if (i == nose_pieces + nb - 1) { a0 = bell_a(nb - 1); a1 = a0 + floor_knee; hull() {                            // the grip beyond Tesla's CAD: the floor joins the flare
        slice(a0) bell_profile(nb - 1, grow, flare(a0)); slice(a1) bell_profile(nb - 1, grow, flare(a1), flare(a1)); } }
    else { a1 = bell_a(nb - 1) + floor_knee; hull() {                                                                    // and on out of the drum
        slice(a1) bell_profile(nb - 1, grow, flare(a1), flare(a1)); slice(far_a) bell_profile(nb - 1, grow, flare(far_a), flare(far_a)); } }
}
module tilt_about_tip(t) translate([0, floor_y, tip_gap]) rotate([-t, 0, 0]) translate([0, -floor_y, -tip_gap]) children();   // grip toward the roof by t
module cavity_seg(i, grow = 0) hull() {
    piece(i, grow, false);
    for (t = [dock_tilt / 2, dock_tilt]) intersection() {
        tilt_about_tip(t) piece(i, grow, true);
        translate([-500, floor_y - grow, -500]) cube(1000);                                                              // never below the floor
    }
}
module cavity(grow = 0) for (i = [0 : cavity_segs - 1]) cavity_seg(i, grow);

// the lock pocket's section across the wand, open downward; v = 0 is the nose's lowest line
module pocket_section() polygon(concat([[-pocket_x[0][0], -4]], [for (q = pocket_x) [-q[0], q[1]]],
                                       [for (i = [len(pocket_x) - 2 : -1 : 0]) pocket_x[i]], [[pocket_x[0][0], -4]]));

module cleat() intersection() {
    // the wedge along the wand: holding edge at cleat_a, back face overhanging, ramp down to cleat_b
    multmatrix([[0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]])
        linear_extrude(height = 14, center = true)
            polygon([[cleat_a + (cleat_h + 1.5) * tan(undercut), floor_y - 1.5], [cleat_b, floor_y - 1.5], [cleat_b, floor_y], [cleat_a, floor_y + cleat_h]]);
    // and across it: the pocket's own section, less the clearance
    translate([0, floor_y, cleat_a - 1]) linear_extrude(cleat_b - cleat_a + 2) offset(delta = -cleat_clear) pocket_section();
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
        translate([0, -half, notch_a]) linear_extrude(notch_b - notch_a) pocket_section();
    }
}

// drum and flange in one turned profile. The flange's underside is all blend, so its lower rim is an arc tangent to the blend and to the flange's edge.
module drum_profile() {
    zf = total_l - flange_t;
    a = [for (t = [0 : 5 : 90]) [drum_r + fillet_plate - fillet_plate * sin(t), plate_t + fillet_plate - fillet_plate * cos(t)]];
    tt = acos(edge_r / (fillet_flange + edge_r));                                       // where the blend hands over to the rim's arc
    zc = zf - fillet_flange + sqrt(fillet_flange * (fillet_flange + 2 * edge_r));       // that arc's centre height
    b = [for (t = concat([for (q = [0 : 5 : tt]) q], [tt])) [flange_r - fillet_flange * cos(t), zf - fillet_flange + fillet_flange * sin(t)]];
    c = [for (t = concat([for (q = [-tt + 10 : 10 : -1]) q], [0])) [flange_r - edge_r + edge_r * cos(t), zc + edge_r * sin(t)]];
    e = [for (t = [0 : 10 : 90]) [flange_r - edge_r + edge_r * cos(t), total_l - edge_r + edge_r * sin(t)]];
    polygon(concat([[0, plate_t - 0.01]], a, b, c, e, [[0, total_l]]));
}

// the plate: four turned corner posts with a rounded top edge, hulled
module plate() hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx, sy] * (plate_w / 2 - plate_r))
    rotate_extrude() polygon(concat([[0, 0], [plate_r, 0]], [for (t = [0 : 10 : 90]) [plate_r - edge_r + edge_r * cos(t), plate_t - edge_r + edge_r * sin(t)]], [[0, plate_t]]));

// the top lip's outline in the flange plane (+Y up). tab_raw: sharp corners, the sides meeting the flange's circle at their tangent points, the
// part below those points inside the flange. tab2d: the top corners rounded tab_r (offset in and out), the bottom ones put back sharp so the
// sides stay tangent to the circle. The lip itself: every edge rounded edge_r (sphere minkowski on the outline shrunk by edge_r).
y_top = flange_r + tab_rise;
module tab_raw() {
    if (tab_style == "plain") translate([-tab_w / 2, 0]) square([tab_w, y_top]);
    else if (tab_style == "arch") { R = (pow(tab_w / 2, 2) + pow(tab_crown, 2)) / (2 * tab_crown);
        intersection() { translate([-tab_w / 2, 0]) square([tab_w, y_top]); translate([0, y_top - R]) circle(R, $fn = 720); } }
    else if (tab_style == "shield") { P = [tab_top_w / 2, y_top]; a = atan2(P[1], P[0]) - acos(flange_r / norm(P)); Q = flange_r * [cos(a), sin(a)];
        polygon([[-Q[0], Q[1]], Q, P, [-P[0], P[1]]]); }
    else if (tab_style == "crest") { P = [tab_top_w / 2, y_top - tab_crown]; a = atan2(P[1], P[0]) - acos(flange_r / norm(P)); Q = flange_r * [cos(a), sin(a)];
        R = (pow(P[0], 2) + pow(tab_crown, 2)) / (2 * tab_crown); E = P + (P - Q) / norm(P - Q) * 30;   // the sides run on past P; the crown's arc through P cuts them back
        intersection() { polygon([[-Q[0], Q[1]], Q, E, [-E[0], E[1]]]); translate([0, y_top - R]) circle(R, $fn = 720); } }
    else if (tab_style == "gable") polygon([[-tab_w / 2, 0], [tab_w / 2, 0], [tab_w / 2, y_top - tab_peak], [0, y_top], [-tab_w / 2, y_top - tab_peak]]);
}
module tab2d() if (tab_style != "none") union() { offset(r = tab_r) offset(r = -tab_r) tab_raw(); intersection() { tab_raw(); translate([-100, -1]) square([200, 25]); } }
module tab() if (tab_style != "none") translate([0, 0, total_l - flange_t + edge_r]) minkowski() { linear_extrude(flange_t - 2 * edge_r) offset(r = -edge_r) tab2d(); sphere(edge_r, $fn = 24); }
module face2d() union() { circle(flange_r); tab2d(); }     // the whole front face's outline
// the wordmark bent along the crest's arch: the flat artwork cut into strips, each stood on the arc at its own angle (the arc's centre is the crown's)
wm_strip = 0.4;
module wordmark_flat() resize([wordmark_w, 0], auto = true) import("reference/tesla-wordmark.svg", center = true);
module wordmark_arc() if (tab_style == "crest" || tab_style == "arch") {
    Rc = (pow((tab_style == "crest" ? tab_top_w : tab_w) / 2, 2) + pow(tab_crown, 2)) / (2 * tab_crown);   // the crown's radius, as in tab_raw
    wh = wordmark_w * 36.249 / 278.672;                                                                   // the wordmark's height at this width
    Rt = Rc - frame_in - frame_w - wordmark_gap - wh / 2;                                                 // the text's centreline radius
    n = ceil(wordmark_w / wm_strip);
    translate([0, y_top - Rc]) for (i = [0 : n - 1]) { x0 = -wordmark_w / 2 + i * wm_strip;
        rotate(-(x0 + wm_strip / 2) / Rt * 180 / PI) translate([0, Rt]) translate([-(x0 + wm_strip / 2), 0]) intersection() { wordmark_flat(); translate([x0 - 0.01, -50]) square([wm_strip + 0.02, 100]); } }
}
module trim() {
    if (lip_text) translate([0, 0, total_l - logo_depth]) linear_extrude(logo_depth + 0.01) wordmark_arc();
    if (tab_trim == "frame") translate([0, 0, total_l - frame_depth]) linear_extrude(frame_depth + 0.01) difference() { offset(r = -frame_in) face2d(); offset(r = -frame_in - frame_w) face2d(); }
}

module body() {
    plate();
    rotate_extrude() drum_profile();
    tab();
}

// the emblem, logo_h tall, centred on the drum axis. The T: official emblem, two paths; the 0.05 mm closing heals a 0.02 mm self-crossing at the top of the stem
module bolt2d() translate([-0.275, -0.5]) polygon([[0.25, 1], [0, 0.42], [0.21, 0.42], [0.1, 0], [0.55, 0.58], [0.34, 0.58], [0.45, 1]]);   // 0.55 wide, 1 tall
module plug2d() translate([0, -30]) {                                                                                   // 60 tall: prongs, body, cord
    for (sx = [-1, 1]) hull() { translate([sx * 8 - 2.5, 44]) square([5, 1]); translate([sx * 8, 57.5]) circle(2.5); }
    hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx * 13, 34 + sy * 7]) circle(5);
    hull() { translate([-3, 22]) square([6, 1]); translate([0, 3]) circle(3); }
}
module nacs2d() { difference() { polygon(nacs_face_outer); offset(r = -2) polygon(nacs_face_outer); } for (h = nacs_face_holes) polygon(h); }   // outline band and pin holes
module emblem() if (emblem != "none") translate([0, 0, total_l - logo_depth]) linear_extrude(logo_depth + 0.01) {
    if (emblem == "tesla") resize([0, logo_h], auto = true) offset(r = -0.05) offset(r = 0.05) import("reference/tesla-t.svg", center = true);
    else if (emblem == "bolt") resize([0, logo_h], auto = true) bolt2d();
    else if (emblem == "plug") resize([0, logo_h], auto = true) plug2d();
    else if (emblem == "nacs") resize([0, logo_h * 0.9], auto = true) nacs2d();
    else if (emblem == "ev") text("EV", size = logo_h * 0.62, font = "DejaVu Sans:style=Bold", halign = "center", valign = "center");
}

module holes() {
    for (sx = [-1, 1], sy = [-1, 1]) translate([sx * (plate_w / 2 - hole_in), sy * (plate_w / 2 - hole_in), 0]) {
        slot = sy > 0 && top_mount == "keyhole" ? 20 : 0;   // the top holes run out through the plate's top edge, countersink and all
        hull() for (dy = [0, slot]) translate([0, dy, -1]) cylinder(h = plate_t + 2, d = hole_d);
        hull() for (dy = [0, slot]) translate([0, dy, plate_t - (csk_d - hole_d) / 2]) cylinder(h = (csk_d - hole_d) / 2 + 0.01, d1 = hole_d, d2 = csk_d);
    }
    if (top_mount == "holes") for (sx = [-1, 1]) translate([sx * (plate_w / 2 - hole_in), plate_w / 2 - hole_in, total_l - flange_t - 1]) {   // driver holes through the lip, in line with the top screws
        cylinder(h = flange_t + 2, d = driver_d);
        translate([0, 0, flange_t + 1 - edge_r]) cylinder(h = edge_r + 0.01, d1 = driver_d, d2 = driver_d + 2 * edge_r);
    }
}

// the cavity as cut from the body. It stops at cut_top, the height its top reaches inside the drum (pipeline/zbudget.py, mouth top). Above that the
// docking room's flared top corner ran on outside the drum as a narrow groove up the blend to the flange's rim, where no wand goes (insertion.py)
cut_top = 93.8;
module cavity_cut(grow = 0) intersection() { in_cavity_frame() cavity(grow); translate([-500, -500, -500]) cube([1000, 1000, 500 + cut_top + grow]); }

// the mouth's rim, rounded by a rolling ball of edge_r: between stations the sharp wedge is cut away back to where the ball touches, and the balls go back in
module dot(p) translate(p) cube(0.01, center = true);
module rim_cut() for (i = [0 : 1 : len(rim_O) - 1]) if (rim_next[i] >= 0) hull() for (k = [i, rim_next[i]]) { dot(rim_E[k]); dot(rim_TB[k]); dot(rim_O[k]); dot(rim_TC[k]); }
module rim_fill() for (i = [0 : 1 : len(rim_O) - 1]) if (rim_next[i] >= 0) hull() for (k = [i, rim_next[i]]) translate(rim_O[k]) sphere(r = edge_r, $fn = 20);

module holder() {
    difference() {
        body();
        cavity_cut();
        rim_cut();
        holes();
        if (show_logo) emblem();
        trim();
    }
    intersection() { rim_fill(); difference() { body(); cavity_cut(); } }
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
        in_cavity_frame() translate([-500, -500, -500]) cube([1000, 1000, 500 + coupon_cut]);   // nothing past the nose shoulder
    }
}

// the cavity inside the drum radius, for pipeline/zbudget.py
module probe() intersection() { in_cavity_frame() cavity(); cylinder(r = drum_r, h = 1000, center = true); }

// what the docked handle would cut out of the holder: must be empty
module clash() intersection() { holder(); in_cavity_frame() handle(); }

module part_body() { if (part == "coupon") coupon(); else if (part == "probe") probe(); else if (part == "cavity") in_cavity_frame() cavity(); else if (part == "clash") clash(); else holder(); }

module model() {
    if (section == 1) intersection() { part_body(); in_cavity_frame() translate([-500, -500, -500]) cube([500, 1000, 1000]); }
    else if (section == 2) intersection() { part_body(); in_cavity_frame() translate([-500, -500, -500]) cube([1000, 1000, 500 + cleat_a + 1.5]); }
    else part_body();
    if (show_nose) color(section == 0 ? "steelblue" : "gainsboro", section == 0 ? 0.55 : 0.85) in_cavity_frame() {
        if (section == 1) intersection() { tilt_about_tip(pose_tilt) translate([0, 0, pose_out]) handle(); translate([-500, -500, -500]) cube([500, 1000, 1000]); }
        else if (section == 2) intersection() { handle(); translate([-500, -500, -500]) cube([1000, 1000, 500 + cleat_a + 1.5]); }
        else handle();
    }
    if (show_wall) color("gray", 0.15) translate([-160, -200, -1]) cube([320, 320, 1]);
}

if (display) rotate([90, 0, 0]) model(); else model();

echo(str("wand direction d=", d, " up v=", v, " across w=", w, " mouth M=", M, " tip T=", T, " mouth depth=", mouth, " edge_r=", edge_r));
echo(str("cleat: edge at ", cleat_a, " height ", cleat_h, " ramp foot ", cleat_b, " ramp angle ", atan(cleat_h / (cleat_b - cleat_a))));
echo(str("lips from the cavity end wall: cleat wall ", mouth + lip_q(floor_y, 0), " roof ", mouth + lip_q(half + clear + (mouth - tip_gap) * tan(dock_tilt), 0),
         " flange side ", mouth + lip_q(0, 21.8), " wall side ", mouth + lip_q(0, -21.8)));
