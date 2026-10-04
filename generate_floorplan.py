"""
generate_floorplan.py
=====================
Draws the 2-bedroom UK terraced house floor plans exactly as specified in
floorplan_specification.md.

Both floors are drawn as FLAT plans side by side at the same Z level so one
top-down orthographic camera can see them. Room rectangles use the
coordinates from the specification unchanged; only the presentation differs
from a stacked 3D model (which cannot be read from directly above).

Run:  blender --background --python generate_floorplan.py
Out:  two_bed_terraced_house.blend, two_bed_house_floorplan_final.blend,
      C:/tmp/two_bed_house_floorplan_final.png
"""

import bpy
import math
import os

# ============================================================== clean the scene
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
             bpy.data.cameras, bpy.data.lights, bpy.data.images):
    for item in list(coll):
        try:
            coll.remove(item)
        except Exception:
            pass

scene = bpy.context.scene

# ============================================================== constants
EXT_W, EXT_D = 5.50, 10.00       # external footprint
T_EXT, T_INT = 0.20, 0.10         # wall thicknesses
XOFF = 7.80                       # first-floor plan sits to the right

# room plate colours (linear RGB)
C_LIV = (0.96, 0.91, 0.78)        # cream
C_KIT = (0.86, 0.86, 0.73)        # warm grey
C_HALL = (0.91, 0.89, 0.84)       # pale
C_STAIR = (0.72, 0.70, 0.66)      # grey
C_BED1 = (0.78, 0.86, 0.93)       # pale blue
C_BATH = (0.62, 0.86, 0.88)       # aqua
C_BED2 = (0.92, 0.82, 0.86)       # pale rose
C_GLASS = (0.45, 0.70, 0.88)      # window / rooflight blue
C_DARK = (0.06, 0.06, 0.06)       # walls and line work
C_TXT = (0.00, 0.00, 0.00)
C_TXT2 = (0.35, 0.35, 0.35)


# ============================================================== primitives
def rect(name, xa, ya, xb, yb, z, h, col, dx=0.0):
    """Flat box spanning (xa,ya)-(xb,yb), base at z, height h."""
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=((xa + xb) / 2.0 + dx, (ya + yb) / 2.0, z + h / 2.0))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = ((xb - xa) / 2.0, (yb - ya) / 2.0, h / 2.0)
    ob.color = (col[0], col[1], col[2], 1.0)
    return ob


def plate(name, xa, ya, xb, yb, col, dx=0.0):
    """A room floor plate, drawn just above the wall line-work."""
    return rect(name, xa, ya, xb, yb, -0.030, 0.02, col, dx=dx)


def wall_x(name, xa, xb, y, dx=0.0):
    """Internal horizontal wall, 0.10 m thick."""
    return rect(name, xa + dx, y - 0.05, xb + dx, y + 0.05, 0.0, 0.10, C_DARK)


def wall_y(name, x, ya, yb, dx=0.0):
    """Internal vertical wall, 0.10 m thick."""
    return rect(name, x - 0.05 + dx, ya, x + 0.05 + dx, yb, 0.0, 0.10, C_DARK)


def wall_ext_x(name, xa, xb, y, dx=0.0):
    """External horizontal wall, 0.20 m thick."""
    return rect(name, xa + dx, y - 0.10, xb + dx, y + 0.10, 0.0, 0.10, C_DARK)


def wall_ext_y(name, x, ya, yb, dx=0.0):
    """External vertical wall, 0.20 m thick."""
    return rect(name, x - 0.10 + dx, ya, x + 0.10 + dx, yb, 0.0, 0.10, C_DARK)


def open_x(name, xa, xb, y, col, dx=0.0):
    """Light reveal cut through a horizontal wall (door / window opening)."""
    return rect(name, xa + dx, y - 0.10, xb + dx, y + 0.10, 0.058, 0.02, col)


def open_y(name, x, ya, yb, col, dx=0.0):
    """Light reveal cut through a vertical wall."""
    return rect(name, x - 0.10 + dx, ya, x + 0.10 + dx, yb, 0.058, 0.02, col)


def win(name, xa, xb, y, dx=0.0):
    """Window symbol: glazing fill with a dark centre line."""
    rect(name + "_g", xa + dx, y - 0.080, xb + dx, y + 0.080, 0.072, 0.012, C_GLASS)
    rect(name + "_l", xa + dx, y - 0.012, xb + dx, y + 0.012, 0.088, 0.012, C_DARK)


def leaf(name, xa, ya, xb, yb, dx=0.0):
    """Door leaf line drawn across an opening."""
    return rect(name, xa + dx, ya, xb + dx, yb, 0.082, 0.012, C_DARK)


def label(name, body, x, y, size=0.25, rot=0.0, col=C_TXT, dx=0.0):
    bpy.ops.object.text_add(location=(x + dx, y, 0.12),
                            rotation=(0.0, 0.0, math.radians(rot)))
    ob = bpy.context.active_object
    ob.name = name
    ob.data.body = body
    ob.data.size = size
    ob.data.align_x = 'CENTER'
    ob.data.align_y = 'CENTER'
    ob.data.extrude = 0.0
    ob.color = (col[0], col[1], col[2], 1.0)
    return ob


def stair(name, xa, xb, ya, yb, risers, dx=0.0, up=True):
    """Tread lines plus a direction arrow drawn on the stair plate."""
    run = (yb - ya) / float(risers)
    for i in range(1, risers):
        rect("%s_t%02d" % (name, i), xa, ya + i * run, xb,
             ya + i * run + 0.022, 0.072, 0.012, C_DARK, dx=dx)
    cx = (xa + xb) / 2.0 + dx
    ya0, ya1 = (ya + 0.32, yb - 0.32) if up else (yb - 0.32, ya + 0.32)
    rect(name + "_shaft", cx - 0.020, min(ya0, ya1), cx + 0.020,
         max(ya0, ya1), 0.088, 0.012, C_DARK)
    hx, hy = cx, (ya1 if up else ya0)
    s = 1.0 if up else -1.0
    w = (xb - xa) * 0.24
    verts = [(hx, hy, 0.088),
             (hx - w, hy - 0.26 * s, 0.088),
             (hx + w, hy - 0.26 * s, 0.088)]
    me = bpy.data.meshes.new(name + "_head")
    me.from_pydata(verts, [], [(0, 1, 2)])
    me.update()
    ob = bpy.data.objects.new(name + "_head", me)
    scene.collection.objects.link(ob)
    ob.color = (C_DARK[0], C_DARK[1], C_DARK[2], 1.0)


def dim_h(name, xa, xb, y, txt, dx=0.0):
    """Horizontal dimension line with end ticks and a caption."""
    rect(name + "_t1", xa - 0.010 + dx, y - 0.07, xa + 0.010 + dx, y + 0.07, 0.05, 0.01, C_DARK)
    rect(name + "_t2", xb - 0.010 + dx, y - 0.07, xb + 0.010 + dx, y + 0.07, 0.05, 0.01, C_DARK)
    rect(name + "_b", xa + dx, y - 0.008, xb + dx, y + 0.008, 0.05, 0.01, C_DARK)
    label(name + "_c", txt, (xa + xb) / 2.0, y + 0.30, 0.24, dx=dx)


# ============================================================================
# GROUND FLOOR
# internal clear envelope 0.00..5.10 wide, 0.00..9.60 deep
# ============================================================================
# room plates
plate("g_living", 0.00, 0.00, 5.10, 3.20, C_LIV)
plate("g_stair", 0.00, 3.20, 1.00, 6.40, C_STAIR)
plate("g_hall", 1.00, 3.20, 5.10, 6.40, C_HALL)
plate("g_kitchen", 0.00, 6.40, 5.10, 9.60, C_KIT)

# external walls, 0.20 thick
wall_ext_y("g_ext_left", 0.00, 0.00, 10.00)
wall_ext_y("g_ext_right", 5.50, 0.00, 10.00)
for nm, xa, xb in [("a", 0.00, 0.50), ("b", 1.40, 2.60), ("c", 3.80, 5.30)]:
    wall_ext_x("g_ext_front_" + nm, xa, xb, 0.10)
for nm, xa, xb in [("a", 0.00, 0.30), ("b", 1.10, 2.60),
                   ("c", 3.80, 5.30), ("d", 4.30, 5.30)]:
    wall_ext_x("g_ext_rear_" + nm, xa, xb, 9.90)

# internal partitions
wall_x("g_liv_kit", 0.00, 5.10, 6.45)          # living / kitchen
wall_y("g_hall_stair", 1.00, 3.20, 6.40)      # stair / hall

# openings
open_x("g_front_door", 0.50, 1.40, 0.10, C_LIV)
open_x("g_liv_w1", 2.60, 3.80, 0.10, C_LIV)
open_x("g_rear_door", 1.10, 2.00, 9.90, C_KIT)
open_x("g_kit_w1", 2.60, 3.80, 9.90, C_KIT)
open_x("g_kit_w2", 4.10, 5.00, 9.90, C_KIT)
open_y("g_stair_door", 1.00, 3.90, 4.70, C_HALL)
open_y("g_liv_door", 5.10, 0.40, 1.20, C_LIV)
open_y("g_kit_door", 5.10, 7.00, 7.80, C_KIT)

leaf("g_fd_leaf", 0.50, 0.06, 1.40, 0.10)
leaf("g_rd_leaf", 1.10, 9.90, 2.00, 9.94)
leaf("g_sd_leaf", 0.96, 3.90, 1.00, 4.70)

win("g_liv_w2", 4.10, 5.00, 0.10)
win("g_stair_w", 0.30, 1.10, 9.90)

stair("g_st", 0.10, 0.90, 3.30, 6.30, 15, up=True)

label("g_title", "GROUND FLOOR", 2.75, 10.75, 0.50)
label("g_l_living", "LIVING ROOM\n5.1 x 3.2 m  =  16.3 sq m", 3.30, 1.70, 0.25)
label("g_l_kitchen", "KITCHEN / DINING\n5.1 x 3.2 m  =  16.3 sq m", 3.30, 8.00, 0.25)
label("g_l_hall", "HALL", 3.60, 4.30, 0.24)
label("g_l_stair", "STAIRS UP", 0.50, 4.80, 0.16, rot=90)
label("g_note", "front door + front windows in front wall   |   rear door + kitchen windows in rear wall",
      2.75, -0.60, 0.20, col=C_TXT2)

# ============================================================================
# FIRST FLOOR
# ============================================================================
F = XOFF

plate("f_bed1", 0.00, 0.00, 3.00, 3.20, C_BED1, dx=F)
plate("f_void", 0.00, 0.00, 1.00, 3.20, C_STAIR, dx=F)
plate("f_bath", 0.00, 3.20, 2.00, 5.40, C_BATH, dx=F)
plate("f_land1", 2.00, 3.20, 5.10, 5.40, C_HALL, dx=F)
plate("f_land2", 0.00, 5.40, 5.10, 6.40, C_HALL, dx=F)
plate("f_bed2", 0.00, 6.40, 5.10, 9.60, C_BED2, dx=F)
plate("f_stair2", 0.00, 3.20, 1.00, 6.40, C_STAIR, dx=F)

# external walls
wall_ext_y("f_ext_left", 0.00, 0.00, 10.00, dx=F)
wall_ext_y("f_ext_right", 5.50, 0.00, 10.00, dx=F)
for nm, xa, xb in [("a", 0.00, 2.60), ("b", 3.80, 5.30)]:
    wall_ext_x("f_ext_front_" + nm, xa, xb, 0.10, dx=F)
for nm, xa, xb in [("a", 0.00, 0.30), ("b", 1.10, 2.60),
                   ("c", 3.80, 5.30), ("d", 4.30, 5.30)]:
    wall_ext_x("f_ext_rear_" + nm, xa, xb, 9.90, dx=F)

# internal partitions
wall_y("f_bed1_land", 3.00, 1.20, 2.00, dx=F)      # bedroom 1 / landing
wall_x("f_bed1_bath", 0.00, 2.00, 3.25, dx=F)      # bedroom 1 / bathroom
wall_y("f_bath_land", 2.00, 3.20, 5.40, dx=F)      # bathroom / landing
wall_x("f_bath_bed2", 0.00, 2.00, 5.45, dx=F)      # bathroom / bedroom 2
wall_x("f_land_bed2", 0.00, 5.10, 6.45, dx=F)      # landing / bedroom 2

# openings
open_x("f_bed1_w1", 2.60, 3.80, 0.10, C_BED1, dx=F)
open_y("f_bed1_door", 3.00, 1.20, 2.00, C_BED1, dx=F)
open_y("f_bath_door", 2.00, 3.90, 4.70, C_BATH, dx=F)
open_y("f_bed2_door", 5.10, 6.60, 7.40, C_BED2, dx=F)
open_x("f_bed2_w1", 2.60, 3.80, 9.90, C_BED2, dx=F)
open_x("f_bed2_w2", 4.10, 5.00, 9.90, C_BED2, dx=F)
open_x("f_land_w", 0.30, 1.10, 9.90, C_HALL, dx=F)

leaf("f_b1d_leaf", 2.96, 1.20, 3.00, 2.00, dx=F)
leaf("f_bathd_leaf", 1.96, 3.90, 2.00, 4.70, dx=F)
leaf("f_b2d_leaf", 5.06, 6.60, 5.10, 7.40, dx=F)

win("f_bed1_w2", 4.10, 5.00, 0.10, dx=F)

# bathroom rooflight
rect("f_rooflight", 0.60, 4.00, 1.40, 4.80, 0.072, 0.012, C_GLASS, dx=F)
rect("f_rl_e1", 0.60, 4.00, 1.40, 4.12, 0.088, 0.012, C_DARK, dx=F)
rect("f_rl_e2", 0.60, 4.68, 1.40, 4.80, 0.088, 0.012, C_DARK, dx=F)

stair("f_st", 0.10, 0.90, 3.30, 6.30, 15, dx=F, up=False)

label("f_title", "FIRST FLOOR", 2.75 + F, 10.75, 0.50)
label("f_l_bed1", "BEDROOM 1\n3.0 x 3.2 m  =  9.6 sq m", 2.00 + F, 1.70, 0.24)
label("f_l_bath", "BATHROOM\n2.0 x 2.2 m  =  4.4 sq m", 1.00 + F, 4.60, 0.19)
label("f_l_bed2", "BEDROOM 2\n5.1 x 3.2 m  =  16.3 sq m", 2.55 + F, 8.00, 0.25)
label("f_l_land", "LANDING", 3.60 + F, 4.30, 0.22)
label("f_l_void", "STAIR VOID", 0.50 + F, 1.60, 0.15, rot=90)
label("f_note", "bathroom lit by rooflight   |   no side windows (mid-terrace)",
      2.75 + F, -0.60, 0.20, col=C_TXT2)

# ============================================================================
# TITLE BLOCK + DIMENSION LINES
# ============================================================================
label("tb_title", "2 BEDROOM UK TERRACED HOUSE   -   FLOOR PLANS",
      2.75 + F / 2.0, 11.95, 0.44)
label("tb_sub", "external footprint 5.50 x 10.00 m    |    external walls 0.20 m    "
                "|    partitions 0.10 m    |    metres",
      2.75 + F / 2.0, 11.45, 0.24, col=C_TXT2)

dim_h("dim_g_w", 0.00, 5.50, -1.15, "5.50 m")
dim_h("dim_f_w", 0.00, 5.50, -1.15, "5.50 m", dx=F)
label("dim_g_d", "10.00 m", -0.72, 5.00, 0.24, rot=90)
label("dim_f_d", "10.00 m", -0.72, 5.00, 0.24, rot=90, dx=F)

# ============================================================================
# CAMERA  - orthographic, straight down
# ============================================================================
cam_x = 2.75 + F / 2.0
bpy.ops.object.camera_add(location=(cam_x, 5.00, 30.0),
                         rotation=(0.0, 0.0, 0.0))
cam = bpy.context.active_object
cam.name = "PlanCamera"
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 15.4
scene.camera = cam

# ============================================================================
# RENDER SETTINGS - Workbench, flat lighting, object colours, WHITE background
# ============================================================================
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'FLAT'
scene.display.shading.color_type = 'OBJECT'
scene.display.shading.show_object_outline = False
scene.display.shading.show_cavity = False
scene.display.shading.show_specular_highlight = False
scene.display.shading.background_type = 'VIEWPORT'
scene.display.shading.background_color = (1.0, 1.0, 1.0)
try:
    scene.display.render_aa = '8'
except Exception:
    pass

# white world so nothing renders as black
world = bpy.data.worlds["World"]
world.use_nodes = True
wnodes = world.node_tree.nodes
wlinks = world.node_tree.links
for n in list(wnodes):
    wnodes.remove(n)
bgn = wnodes.new(type='ShaderNodeBackground')
bgn.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
bgn.inputs[1].default_value = 1.0
wout = wnodes.new(type='ShaderNodeOutputWorld')
wlinks.new(bgn.outputs['Background'], wout.inputs['Surface'])

scene.render.resolution_x = 2400
scene.render.resolution_y = 2000
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.view_settings.view_transform = 'Standard'

# ============================================================================
# SAVE + RENDER
# ============================================================================
os.makedirs("C:/tmp", exist_ok=True)
bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/Administrator/two_bed_terraced_house.blend")
bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/Administrator/two_bed_house_floorplan_final.blend")

scene.render.filepath = "C:/tmp/two_bed_house_floorplan_final.png"
bpy.ops.render.render(write_still=True)

print("OBJECTS -> %d" % len(bpy.data.objects))
print("RENDER_OK -> %s" % scene.render.filepath)