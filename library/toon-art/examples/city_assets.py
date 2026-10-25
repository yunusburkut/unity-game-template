# Builds every 3D model of the city theme and exports each one as an FBX for Unity, plus the palette texture they
# all share. Every face takes its color from one pixel of the palette, so the whole city draws with one material.
# The one exception is the "Paint" material on the truck and the bag: it stays a separate submesh, which the game
# tints with the picture's colors.
#
# blender -b --factory-startup -P Tools/Blender/city_assets.py -- <unity project folder> [preview.png]
#
# The style is a toy town: chunky proportions, every edge rounded off, smooth shading on the rounds and flat faces
# kept flat (weighted normals), so the toon shader draws clean bands instead of facets.
#
# Sizes are Unity world units: a board cell is 0.5. Blender is Z up; the FBX export turns that into Unity's Y up.
# Every model's front is Blender -Y.

import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

PALETTE = {
    "rubber": (0.17, 0.18, 0.22),
    "chassis": (0.26, 0.28, 0.34),
    "metal": (0.80, 0.83, 0.88),
    "metal_dark": (0.45, 0.48, 0.56),
    "white": (0.98, 0.98, 0.96),
    "glass": (0.55, 0.84, 0.98),
    "glass_dark": (0.33, 0.58, 0.86),
    "amber": (1.00, 0.72, 0.12),
    "headlight": (1.00, 0.97, 0.70),
    "taillight": (0.98, 0.26, 0.28),
    "mouth": (0.12, 0.12, 0.16),
    "trunk": (0.62, 0.40, 0.25),
    "leaf": (0.40, 0.80, 0.33),
    "leaf_dark": (0.24, 0.64, 0.33),
    "leaf_light": (0.62, 0.90, 0.36),
    "wall_cream": (1.00, 0.91, 0.74),
    "wall_coral": (1.00, 0.56, 0.48),
    "wall_mint": (0.55, 0.88, 0.74),
    "wall_sky": (0.58, 0.78, 0.98),
    "wall_lilac": (0.78, 0.68, 0.96),
    "wall_yellow": (1.00, 0.84, 0.36),
    "roof_dark": (0.44, 0.47, 0.58),
    "roof_red": (0.94, 0.38, 0.32),
    "roof_light": (0.84, 0.86, 0.90),
    "red": (0.96, 0.27, 0.25),
    "wood": (0.86, 0.58, 0.34),
    "green_bin": (0.25, 0.70, 0.46),
    "green_dark": (0.16, 0.50, 0.34),
    "orange": (1.00, 0.53, 0.14),
    "concrete": (0.86, 0.87, 0.90),
    "stripe_red": (0.98, 0.36, 0.38),
    "stripe_blue": (0.36, 0.56, 0.98),
}
NAMES = list(PALETTE)
CELLS = 8          # the texture is an 8 x 8 grid of colors
CELL_PIXELS = 4    # each color is a 4 x 4 block, so filtering never bleeds into the next one
PAINT = "Paint"
# edges sharper than this stay hard; anything rounder is shaded smooth
SHARP_ANGLE = math.radians(40)


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def material(name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        rgb = PALETTE.get(name, (0.95, 0.95, 0.95))
        mat.diffuse_color = (*[srgb_to_linear(c) for c in rgb], 1.0)
    return mat


# ---- mesh helpers: each one makes a separate object, and build() joins them into one model ----

def _object(name, bm, mat):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material(mat))
    return obj


def _place(bm, loc, axis='Z', rot=None, scale=None):
    """Scales, turns a Z-up shape onto another axis, tilts it and moves it into place."""
    if scale:
        bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    if axis == 'X':
        bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.radians(90), 3, 'Y'))
    elif axis == 'Y':
        bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
    if rot:
        bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.radians(rot[1]), 3, rot[0]))
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)


def box(size, loc, mat, bevel=0.0, segments=4, rot=None):
    """A box with every edge rounded off by bevel; a round profile, so it reads as a soft toy block."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, min(size) * 0.49), segments=segments,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    _place(bm, loc, rot=rot)
    return _object("box", bm, mat)


def slab(width, depth, height, radius, loc, mat, bevel=0.0, corners=5):
    """A rounded rectangle in plan, pushed up into a block: cornices, roofs, rims and bands."""
    bm = bmesh.new()
    w, d = width / 2 - radius, depth / 2 - radius
    outline = []
    for cx, cy, start in ((w, -d, -90), (w, d, 0), (-w, d, 90), (-w, -d, 180)):
        for i in range(corners + 1):
            a = math.radians(start + 90 * i / corners)
            outline.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    bottom = [bm.verts.new((x, y, -height / 2)) for x, y in outline]
    top = [bm.verts.new((x, y, height / 2)) for x, y in outline]
    bm.faces.new(bottom[::-1])
    bm.faces.new(top)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        rims = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-6]
        bmesh.ops.bevel(bm, geom=rims, offset=min(bevel, height * 0.49), segments=3, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    _place(bm, loc)
    return _object("slab", bm, mat)


def lathe(profile, mat, loc=(0, 0, 0), segments=20, axis='Z', scale=None, shape=None):
    """Spins a list of (radius, z) points round the Z axis. A radius of 0 closes that end with a single pole.
    shape(angle, z) can return a factor for the radius, for folds and lobes."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z))] * segments)
            continue
        ring = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            k = shape(a, z) if shape else 1.0
            ring.append(bm.verts.new((r * k * math.cos(a), r * k * math.sin(a), z)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(segments):
            j = (i + 1) % segments
            quad = [rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]]
            face = [v for n, v in enumerate(quad) if v is not quad[n - 1]]
            if len(face) >= 3:
                bm.faces.new(face)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _place(bm, loc, axis=axis, scale=scale)
    return _object("lathe", bm, mat)


def arc(cx, cz, r, start, end, steps):
    """Points along a circle in the (radius, z) plane, for the rounded corners of a lathe profile."""
    return [(cx + r * math.cos(math.radians(start + (end - start) * i / steps)),
             cz + r * math.sin(math.radians(start + (end - start) * i / steps))) for i in range(steps + 1)]


def puck(radius, depth, loc, mat, round_edge=0.0, axis='Z', segments=20):
    """A cylinder with its rims rounded off: wheels, hubs, lights, bases."""
    h = depth / 2
    b = min(round_edge, h * 0.99, radius * 0.99)
    if b <= 0:
        profile = [(0, -h), (radius, -h), (radius, h), (0, h)]
    else:
        profile = [(0, -h)] + arc(radius - b, -h + b, b, -90, 0, 3) + arc(radius - b, h - b, b, 0, 90, 3) + [(0, h)]
    return lathe(profile, mat, loc, segments, axis)


def dome(radius, height, loc, mat, segments=16):
    """Half a squashed sphere, sitting on its flat side."""
    profile = [(0, 0)] + [(radius * math.cos(math.radians(a)), height * math.sin(math.radians(a))) for a in range(0, 91, 15)]
    profile[-1] = (0, height)
    return lathe(profile, mat, loc, segments)


def ball(radius, loc, mat, scale=(1, 1, 1), subdivisions=2):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    _place(bm, loc, scale=scale)
    return _object("ball", bm, mat)


def prism(width, depth, height, loc, mat, bevel=0.0):
    """A gable roof: a triangle along X, pushed out along Y, its edges rounded off."""
    bm = bmesh.new()
    w, d = width / 2, depth / 2
    front = [bm.verts.new((-w, -d, 0)), bm.verts.new((w, -d, 0)), bm.verts.new((0, -d, height))]
    back = [bm.verts.new((-w, d, 0)), bm.verts.new((w, d, 0)), bm.verts.new((0, d, height))]
    bm.faces.new(front[::-1])
    bm.faces.new(back)
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((front[i], front[j], back[j], back[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=3, profile=0.5, affect='EDGES',
                        clamp_overlap=True)
    _place(bm, loc)
    return _object("prism", bm, mat)


def build(name, parts):
    """Joins the parts into one object, gives every face its palette UV, and leaves two materials at most:
    Paint first, then the shared palette. Then shades it: smooth across the rounds, hard on real corners, and
    each normal weighted by face area, so a big flat wall stays flat right up to its rounded edge."""
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    obj.data.name = name

    mesh = obj.data
    uv = mesh.uv_layers.new(name="UV")
    slot_names = [m.name for m in mesh.materials]
    has_paint = PAINT in slot_names
    slots = []
    for poly in mesh.polygons:
        color = slot_names[poly.material_index]
        if color == PAINT:
            u, v = 0.5, 0.5
            slots.append(0)
        else:
            index = NAMES.index(color)
            u = (index % CELLS + 0.5) / CELLS
            v = 1.0 - (index // CELLS + 0.5) / CELLS
            slots.append(1 if has_paint else 0)
        for loop in poly.loop_indices:
            uv.data[loop].uv = (u, v)

    # clearing the materials resets every face to the first slot, so the faces are sorted after it
    mesh.materials.clear()
    if has_paint:
        mesh.materials.append(material(PAINT))
    mesh.materials.append(palette_material())
    for poly, slot in zip(mesh.polygons, slots):
        poly.material_index = slot

    # Unity numbers the submeshes in the order their faces first come up, not by slot, so the Paint faces go first
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.sort_elements(type='MATERIAL', elements={'FACE'})
    bpy.ops.object.mode_set(mode='OBJECT')

    bm = bmesh.new()
    bm.from_mesh(mesh)
    for edge in bm.edges:
        edge.smooth = not (len(edge.link_faces) == 2 and edge.calc_face_angle(0.0) > SHARP_ANGLE)
    for face in bm.faces:
        face.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    weighted = obj.modifiers.new("Weighted", 'WEIGHTED_NORMAL')
    weighted.mode = 'FACE_AREA'
    weighted.weight = 50
    weighted.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    return obj


_palette_mat = None


def palette_material():
    global _palette_mat
    if _palette_mat is None:
        _palette_mat = bpy.data.materials.new("Palette")
        _palette_mat.diffuse_color = (0.8, 0.8, 0.8, 1)
    return _palette_mat


# ---- the models ----

def truck():
    p = []
    p.append(box((0.34, 0.64, 0.08), (0, 0, 0.125), "chassis", bevel=0.03))
    # big toy wheels: a soft tire and a hub that pokes out of it
    for y in (-0.22, 0.2):
        for x in (-0.18, 0.18):
            p.append(puck(0.1, 0.085, (x, y, 0.1), "rubber", round_edge=0.035, axis='X', segments=20))
            p.append(puck(0.05, 0.095, (x, y, 0.1), "metal", round_edge=0.015, axis='X', segments=14))
    # the cab: a round-cornered block with a windshield, side windows, mirrors and a beacon on the roof
    p.append(box((0.42, 0.25, 0.25), (0, -0.235, 0.27), PAINT, bevel=0.085))
    p.append(box((0.33, 0.04, 0.1), (0, -0.348, 0.3), "glass", bevel=0.018, segments=2))
    for side in (-1, 1):
        p.append(box((0.03, 0.12, 0.085), (side * 0.205, -0.22, 0.305), "glass", bevel=0.012, segments=2))
        p.append(ball(0.026, (side * 0.222, -0.33, 0.31), "chassis", scale=(0.7, 0.6, 1.2), subdivisions=1))
    p.append(puck(0.045, 0.02, (0, -0.24, 0.395), "chassis", round_edge=0.008, segments=14))
    p.append(dome(0.038, 0.04, (0, -0.24, 0.402), "amber", segments=14))
    # the face: a round bumper, a grille and two big round headlights
    p.append(box((0.44, 0.06, 0.06), (0, -0.37, 0.155), "metal", bevel=0.029))
    p.append(box((0.15, 0.02, 0.05), (0, -0.358, 0.215), "chassis", bevel=0.01, segments=2))
    for x in (-0.14, 0.14):
        p.append(puck(0.034, 0.03, (x, -0.352, 0.215), "headlight", round_edge=0.01, axis='Y', segments=14))
    # the body: a fat rounded box with a white band, the open hopper on top where the bags drop in
    p.append(box((0.44, 0.47, 0.3), (0, 0.125, 0.295), PAINT, bevel=0.09))
    p.append(slab(0.452, 0.43, 0.05, 0.07, (0, 0.13, 0.235), "white", bevel=0.012))
    p.append(slab(0.34, 0.25, 0.035, 0.06, (0, 0.19, 0.44), "metal_dark", bevel=0.012))
    p.append(slab(0.28, 0.19, 0.02, 0.04, (0, 0.19, 0.452), "mouth"))
    # the back: the tailgate and the taillights
    p.append(box((0.38, 0.04, 0.24), (0, 0.355, 0.29), "metal_dark", bevel=0.02, segments=3))
    for x in (-0.15, 0.15):
        p.append(puck(0.024, 0.02, (x, 0.378, 0.2), "taillight", round_edge=0.007, axis='Y', segments=12))
    return build("Truck", p)


def bag():
    # a plump sack that fills a unit cube: a round belly, gathered pleats up to the neck, a tie, and two floppy ears
    profile = [(0.0, -0.5), (0.2, -0.5), (0.33, -0.48), (0.43, -0.42), (0.49, -0.32), (0.515, -0.2), (0.515, -0.07),
               (0.49, 0.05), (0.43, 0.15), (0.34, 0.23), (0.23, 0.29), (0.13, 0.325), (0.075, 0.345),
               (0.068, 0.36), (0.1, 0.375), (0.108, 0.392), (0.088, 0.41), (0.0, 0.418)]

    def pleats(angle, z):
        # the plastic gathers into folds toward the neck; the belly below stays a clean round
        t = max(0.0, min(1.0, (z - 0.02) / 0.3))
        return 1.0 + 0.07 * t * t * math.sin(angle * 7)

    body = lathe(profile, PAINT, segments=28, shape=pleats)
    ears = []
    for side in (-1, 1):
        ear = ball(0.15, (0, 0, 0), PAINT, scale=(1.0, 0.45, 0.62), subdivisions=2)
        ear.data.transform(Matrix.Rotation(math.radians(34 * side), 4, 'Y'))
        ear.data.transform(Matrix.Translation((0.115 * side, 0, 0.45)))
        ears.append(ear)
    return build("Bag", [body] + ears)


def tree():
    # a lollipop tree: a tapered trunk and a cloud of three round puffs
    trunk = [(0, 0), (0.06, 0), (0.05, 0.02), (0.038, 0.06), (0.03, 0.3), (0, 0.3)]
    p = [lathe(trunk, "trunk", segments=10)]
    p.append(ball(0.21, (0, 0, 0.4), "leaf", scale=(1, 1, 0.92), subdivisions=3))
    p.append(ball(0.13, (0.07, -0.1, 0.5), "leaf_light", subdivisions=2))
    p.append(ball(0.13, (-0.12, 0.06, 0.32), "leaf_dark", subdivisions=2))
    return build("Tree", p)


def pine():
    p = [puck(0.032, 0.14, (0, 0, 0.07), "trunk", round_edge=0.01, segments=10)]
    for i, (r, z, h) in enumerate(((0.21, 0.1, 0.24), (0.17, 0.25, 0.22), (0.12, 0.39, 0.2))):
        tier = [(0, z), (r * 0.82, z), (r, z + 0.025), (r * 0.98, z + 0.045), (r * 0.55, z + h * 0.5),
                (r * 0.2, z + h * 0.86), (0, z + h)]
        p.append(lathe(tier, "leaf_dark" if i % 2 == 0 else "leaf", segments=14))
    return build("Pine", p)


def bush():
    p = [ball(0.16, (0, 0, 0.1), "leaf", scale=(1.2, 1, 0.8), subdivisions=3)]
    p.append(ball(0.11, (0.13, -0.04, 0.09), "leaf_light", subdivisions=2))
    p.append(ball(0.1, (-0.14, 0.03, 0.08), "leaf_dark", subdivisions=2))
    return build("Bush", p)


def lamp():
    p = [puck(0.05, 0.05, (0, 0, 0.025), "metal_dark", round_edge=0.018, segments=14)]
    p.append(lathe([(0, 0.04), (0.022, 0.04), (0.016, 0.2), (0.015, 0.7), (0, 0.7)], "metal_dark", segments=10))
    p.append(ball(0.026, (0, 0, 0.71), "metal_dark", subdivisions=2))
    p.append(box((0.026, 0.15, 0.026), (0, -0.075, 0.71), "metal_dark", bevel=0.012, segments=2))
    p.append(dome(0.065, 0.05, (0, -0.16, 0.68), "metal_dark", segments=16))
    p.append(puck(0.052, 0.012, (0, -0.16, 0.678), "headlight", segments=16))
    return build("Lamp", p)


def hydrant():
    profile = [(0, 0), (0.062, 0), (0.066, 0.012), (0.062, 0.026), (0.044, 0.032), (0.042, 0.14), (0.05, 0.148),
               (0.05, 0.165), (0.04, 0.172)] + arc(0, 0.172, 0.04, 0, 90, 4)[1:]
    p = [lathe(profile, "red", segments=16)]
    p.append(puck(0.022, 0.125, (0, 0, 0.1), "red", round_edge=0.008, axis='X', segments=12))
    p.append(puck(0.026, 0.06, (0, -0.04, 0.09), "metal", round_edge=0.01, axis='Y', segments=12))
    p.append(puck(0.012, 0.03, (0, 0, 0.222), "metal", round_edge=0.005, segments=10))
    return build("Hydrant", p)


def bench():
    p = []
    for y in (-0.04, 0.0, 0.04):
        p.append(box((0.38, 0.034, 0.022), (0, y, 0.115), "wood", bevel=0.01, segments=2))
    for z in (0.17, 0.215):
        p.append(box((0.38, 0.022, 0.034), (0, 0.065, z), "wood", bevel=0.01, segments=2))
    for x in (-0.15, 0.15):
        p.append(box((0.03, 0.11, 0.1), (x, 0.0, 0.05), "metal_dark", bevel=0.012, segments=2))
        p.append(box((0.03, 0.022, 0.13), (x, 0.065, 0.17), "metal_dark", bevel=0.01, segments=2))
    return build("Bench", p)


def dumpster():
    p = [box((0.38, 0.26, 0.21), (0, 0, 0.14), "green_bin", bevel=0.05)]
    p.append(box((0.4, 0.28, 0.035), (0, 0.0, 0.255), "green_dark", bevel=0.017, rot=('X', -6)))
    p.append(box((0.3, 0.025, 0.025), (0, -0.14, 0.2), "metal", bevel=0.012, segments=2))
    for x in (-0.13, 0.13):
        for y in (-0.08, 0.08):
            p.append(puck(0.03, 0.025, (x, y, 0.03), "rubber", round_edge=0.01, axis='X', segments=12))
    return build("Dumpster", p)


def cone():
    p = [slab(0.14, 0.14, 0.022, 0.03, (0, 0, 0.011), "orange", bevel=0.008)]
    p.append(lathe([(0, 0.02), (0.05, 0.02), (0.012, 0.19)] + arc(0, 0.19, 0.012, 0, 90, 3)[1:], "orange", segments=16))
    p.append(lathe([(0.041, 0.075), (0.0435, 0.08), (0.0355, 0.125), (0.033, 0.12)], "white", segments=16))
    return build("Cone", p)


def windows(p, width, depth, floors, floor_height, start, across, along, size, mat="glass", sill="white"):
    """Windows on the front and both sides (the back never shows), standing a little proud of the wall, each on a
    white sill."""
    ww, wh = size
    for f in range(floors):
        z = start + f * floor_height
        for i in range(across):
            x = -width / 2 + (i + 0.5) * width / across
            p.append(box((ww, 0.04, wh), (x, -depth / 2, z), mat, bevel=0.012, segments=1))
            if sill:
                p.append(box((ww + 0.04, 0.06, 0.025), (x, -depth / 2, z - wh / 2 - 0.012), sill, bevel=0.008, segments=1))
        for i in range(along):
            y = -depth / 2 + (i + 0.5) * depth / along
            for x in (-width / 2, width / 2):
                p.append(box((0.04, ww, wh), (x, y, z), mat, bevel=0.012, segments=1))
                if sill:
                    p.append(box((0.06, ww + 0.04, 0.025), (x, y, z - wh / 2 - 0.012), sill, bevel=0.008, segments=1))


def roof(p, width, depth, height, top_mat="roof_dark", rim="white"):
    """A fat rounded cornice and the flat roof inside it."""
    p.append(slab(width + 0.1, depth + 0.1, 0.1, 0.1, (0, 0, height + 0.02), rim, bevel=0.03))
    p.append(slab(width - 0.04, depth - 0.04, 0.04, 0.06, (0, 0, height + 0.08), top_mat))


def apartment():
    w, d, h = 1.2, 1.0, 1.8
    p = [box((w, d, h), (0, 0, h / 2), "wall_cream", bevel=0.07, segments=3)]
    p.append(box((w + 0.05, d + 0.05, 0.26), (0, 0, 0.13), "wall_coral", bevel=0.06, segments=3))
    roof(p, w, d, h)
    windows(p, w, d, 5, 0.3, 0.45, 3, 2, (0.2, 0.18))
    # the front door with a little canopy
    p.append(box((0.24, 0.05, 0.22), (0, -d / 2 - 0.01, 0.13), "glass_dark", bevel=0.02, segments=2))
    p.append(slab(0.34, 0.12, 0.03, 0.03, (0, -d / 2 - 0.05, 0.27), "wall_yellow", bevel=0.01))
    p.append(box((0.24, 0.18, 0.13), (0.26, 0.18, h + 0.16), "metal", bevel=0.04, segments=3))
    p.append(puck(0.12, 0.22, (-0.26, 0.2, h + 0.21), "wood", round_edge=0.03, segments=16))
    p.append(lathe([(0, h + 0.31), (0.14, h + 0.31), (0.13, h + 0.34), (0, h + 0.42)], "roof_red", segments=16))
    return build("Apartment", p)


def shop():
    w, d, h = 1.4, 1.0, 0.8
    p = [box((w, d, h), (0, 0, h / 2), "wall_coral", bevel=0.07, segments=3)]
    roof(p, w, d, h, top_mat="roof_light")
    # a big storefront, a door and a striped awning over them
    y = -d / 2
    p.append(box((w * 0.56, 0.04, 0.34), (w * 0.1, y, 0.25), "glass", bevel=0.02, segments=2))
    p.append(box((0.22, 0.05, 0.42), (-w * 0.32, y, 0.21), "glass_dark", bevel=0.02, segments=2))
    stripes = 8
    for i in range(stripes):
        x = -w * 0.42 + (i + 0.5) * w * 0.84 / stripes
        p.append(box((w * 0.84 / stripes, 0.2, 0.03), (x, y - 0.09, 0.53),
                     "stripe_red" if i % 2 == 0 else "white", rot=('X', 18)))
    for i in range(stripes):
        x = -w * 0.42 + (i + 0.5) * w * 0.84 / stripes
        p.append(ball(w * 0.42 / stripes, (x, y - 0.185, 0.495), "stripe_red" if i % 2 == 0 else "white",
                      scale=(1, 0.35, 0.6), subdivisions=1))
    p.append(box((w * 0.5, 0.06, 0.14), (0, y - 0.01, 0.7), "wall_yellow", bevel=0.05, segments=3))
    windows(p, w, d, 1, 0.3, 0.42, 0, 2, (0.28, 0.26))
    p.append(box((0.3, 0.2, 0.13), (0.35, 0.12, h + 0.15), "metal", bevel=0.04, segments=3))
    return build("Shop", p)


def tower():
    w, d, h = 1.0, 1.0, 2.5
    p = [box((w, d, h), (0, 0, h / 2), "wall_sky", bevel=0.08, segments=3)]
    # a ribbon of glass round every floor
    for f in range(8):
        z = 0.38 + f * 0.28
        p.append(box((w * 0.8, 0.04, 0.15), (0, -d / 2, z), "glass_dark", bevel=0.015, segments=1))
        for x in (-w / 2, w / 2):
            p.append(box((0.04, d * 0.8, 0.15), (x, 0, z), "glass_dark", bevel=0.015, segments=1))
    p.append(box((0.3, 0.05, 0.24), (0, -d / 2 - 0.01, 0.14), "glass", bevel=0.02, segments=2))
    roof(p, w, d, h)
    p.append(box((w * 0.56, d * 0.56, 0.3), (0, 0.05, h + 0.24), "wall_sky", bevel=0.07, segments=3))
    p.append(slab(w * 0.64, d * 0.64, 0.06, 0.08, (0, 0.05, h + 0.4), "white", bevel=0.02))
    p.append(puck(0.014, 0.36, (0.14, 0.12, h + 0.6), "metal_dark", segments=8))
    p.append(ball(0.032, (0.14, 0.12, h + 0.8), "taillight", subdivisions=2))
    return build("Tower", p)


def house():
    w, d, h = 1.0, 0.85, 0.75
    p = [box((w, d, h), (0, 0, h / 2), "wall_mint", bevel=0.06, segments=3)]
    p.append(prism(w + 0.16, d + 0.16, 0.44, (0, 0, h - 0.02), "roof_red", bevel=0.035))
    windows(p, w, d, 1, 0.3, 0.44, 2, 2, (0.2, 0.2))
    p.append(box((0.2, 0.05, 0.34), (0.28, -d / 2, 0.17), "wood", bevel=0.02, segments=2))
    p.append(ball(0.014, (0.22, -d / 2 - 0.03, 0.17), "amber", subdivisions=1))
    p.append(box((0.13, 0.13, 0.32), (-0.26, 0.15, h + 0.3), "wall_cream", bevel=0.03, segments=2))
    p.append(slab(0.17, 0.17, 0.04, 0.03, (-0.26, 0.15, h + 0.47), "roof_dark", bevel=0.01))
    return build("House", p)


def kiosk():
    w, d, h = 0.9, 0.7, 0.6
    p = [box((w, d, h), (0, 0, h / 2), "wall_lilac", bevel=0.07, segments=3)]
    p.append(slab(w + 0.18, d + 0.18, 0.07, 0.12, (0, 0, h + 0.02), "white", bevel=0.025))
    p.append(box((w * 0.7, 0.04, 0.24), (0, -d / 2, 0.34), "glass", bevel=0.02, segments=2))
    p.append(box((w * 0.8, 0.06, 0.04), (0, -d / 2 - 0.02, 0.21), "wood", bevel=0.015, segments=2))
    for x in (-w / 2, w / 2):
        p.append(box((0.04, d * 0.6, 0.22), (x, 0, 0.34), "glass", bevel=0.02, segments=2))
    p.append(box((0.52, 0.12, 0.17), (0, 0, h + 0.15), "wall_yellow", bevel=0.05, segments=3))
    return build("Kiosk", p)


MODELS = [truck, bag, tree, pine, bush, lamp, hydrant, bench, dumpster, cone, apartment, shop, tower, house, kiosk]


def write_palette(path):
    size = CELLS * CELL_PIXELS
    image = bpy.data.images.new("Palette", width=size, height=size, alpha=False)
    pixels = [1.0] * (size * size * 4)
    for index, name in enumerate(NAMES):
        col, row = index % CELLS, index // CELLS
        rgb = PALETTE[name]
        for py in range(CELL_PIXELS):
            for px in range(CELL_PIXELS):
                x = col * CELL_PIXELS + px
                # image rows run bottom up; palette rows run top down, like the UVs above
                y = size - 1 - (row * CELL_PIXELS + py)
                i = (y * size + x) * 4
                pixels[i:i + 4] = [*rgb, 1.0]
    # the values above are already sRGB; a non-color image saves them as they are
    image.colorspace_settings.name = 'Non-Color'
    image.pixels.foreach_set(pixels)
    image.update()
    image.filepath_raw = path
    image.file_format = 'PNG'
    image.save()


def export(obj, path):
    for other in bpy.context.scene.objects:
        other.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # this export lands Blender's +Y on Unity's +Z; turned half round, the model's front (Blender -Y) faces +Z,
    # which is where Unity's LookRotation points
    half_turn = Matrix.Rotation(math.pi, 4, 'Z')
    obj.data.transform(half_turn)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, use_mesh_modifiers=True,
                             mesh_smooth_type='FACE', apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                             axis_forward='-Z', axis_up='Y', bake_space_transform=True, add_leaf_bones=False,
                             bake_anim=False, path_mode='STRIP')
    obj.data.transform(half_turn)


def preview(objects, path):
    """A lineup of every model, rendered flat so the shapes and colors can be checked without Unity."""
    x = 0.0
    for obj in objects:
        size = obj.dimensions
        obj.location = (x + size.x / 2, 0, 0)
        x += size.x + 0.25
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.resolution_x, scene.render.resolution_y = 2400, 900
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("World")
    scene.world.color = (0.8, 0.85, 0.9)

    # palette faces show their own color in the preview: split them back out into per-color materials
    for obj in objects:
        mesh = obj.data
        uv = mesh.uv_layers[0]
        for poly in mesh.polygons:
            u, v = uv.data[poly.loop_indices[0]].uv
            if mesh.materials[poly.material_index].name == PAINT:
                continue
            index = int(u * CELLS) + int((1 - v) * CELLS) * CELLS
            name = NAMES[index]
            mat = material(name)
            if mat.name not in mesh.materials:
                mesh.materials.append(mat)
            poly.material_index = list(mesh.materials).index(mat)
        if PAINT in mesh.materials:
            material(PAINT).diffuse_color = (srgb_to_linear(0.25), srgb_to_linear(0.62), srgb_to_linear(0.95), 1)

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = x + 0.4
    cam = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (x / 2, -12 * math.cos(math.radians(30)) * 2, 12)
    look = Vector((x / 2, 0, 0.6)) - cam.location
    cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    project = argv[0]
    out = os.path.join(project, "Assets", "PixelVolley", "Art")
    models = os.path.join(out, "Models")
    os.makedirs(models, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    write_palette(os.path.join(out, "Palette.png"))

    objects = []
    for make in MODELS:
        obj = make()
        export(obj, os.path.join(models, obj.name + ".fbx"))
        objects.append(obj)
        print(f"[city_assets] {obj.name}: {len(obj.data.vertices)} verts, {obj.dimensions.x:.2f} x {obj.dimensions.y:.2f} x {obj.dimensions.z:.2f}")

    if len(argv) > 1:
        preview(objects, argv[1])


main()
