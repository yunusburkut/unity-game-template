"""
EXAMPLE FROM MIXTROL, read for its patterns (pieces, hosts, colliders, walk heights, a palette atlas, the manifest).
It does not run outside Mixtrol: it imports kit_palette.py, which is not included, and its paths (REPO two levels
up from Art/LevelKit, Assets/Mixtrol/..., FBX_DIR in Game/Art/LevelKit) and ticket numbers are Mixtrol's. In a game the
script lives in Tools/Blender and exports to Assets/__GAME__/Game/Art/Models (where OutlineNormalsPostprocessor bakes
the outline normals); toon_prop.py is the runnable starting point. Its export() call is the unity-export preset.
Its axis mapping (below: a Euler(90, 0, 0) child, Blender (x, y, z) -> Unity (x, z, y)) is Mixtrol's too; the template's
builder child is Euler(90, 180, 0) with (-x, z, -y), so take to_unity() from toon_prop.py, never from here.

Level kit - shared helpers for the headless Blender build (build_levelkit.py), whatever the theme.

Every piece is authored in piece space: Blender metres, +Z up, +X along the lane, -Y toward the camera, the origin at
the piece's pivot (Piece.pivot says which point that is). Every exported object sits at the world origin with an
identity transform, so its vertices are already in piece space. A part that moves (a spinner's bar, a plate's cap)
is exported in place too: the pivot it turns or slides about travels as metadata (Host.pivot), and the Unity builder
hangs the mesh under a host transform at that pivot, offset back by the same amount - the LaunchPad prefab's
Plate / PlateMesh shape.

Unity: an imported mesh keeps Blender X and negates Z (CLAUDE.md), and a child rotated Euler(90, 0, 0) stands it up,
so a Blender point (x, y, z) lands at Unity (x, z, y) inside the prefab. to_unity() is that mapping. It swaps two
axes, so it also flips handedness and every angle changes sign (Blender Rz(a) = Unity Ry(-a)). All of it is
computed here and written into the manifest; the C# side converts nothing.
"""
import bmesh
import bpy
import hashlib
import json
import math
import os
import re
from dataclasses import dataclass, field
from mathutils import Quaternion, Vector
from mathutils.bvhtree import BVHTree

import kit_palette as pal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CHECK_DIR = os.path.join(HERE, "checks")
BLEND_PATH = os.path.join(HERE, "LevelKit.blend")
FBX_DIR = os.path.join(REPO, "Assets", "Mixtrol", "Game", "Art", "LevelKit")

UNITY_ART = "Assets/Mixtrol/Game/Art/LevelKit"
UNITY_MATERIALS = "Assets/Mixtrol/Game/Materials/LevelKit"
UNITY_KIT_PREFABS = "Assets/Mixtrol/Game/Prefabs/LevelKit"
UNITY_VARIANTS = "Assets/Mixtrol/Game/Prefabs/Level/Parkur"
UNITY_BASE_PREFABS = "Assets/Mixtrol/Game/Prefabs/Level"

GRID = 1.25                 # level grid (LevelPalette.asset)
DEPTH = 5.0                 # every lane piece is four cells deep, like the device prefabs
HALF = DEPTH / 2.0
MM = 0.0005                 # tolerance of the geometric checks: half a millimetre

# (build key, family name used in files, folders and the palette category)
FAMILIES = [("structure", "Yapi"), ("devices", "Cihaz"), ("obstacles", "Engel"), ("decor", "Dekor")]

# The movement numbers the kit is sized against (PlayerMovement.asset, Player.prefab, docs/level-design-playbook.md).
CHARACTER = {"height": 1.8, "radius": 0.4, "stepOffset": 0.35, "slopeLimit": 50.0, "jump": 2.2,
             "doubleJump": 6.0, "gap": 6.5, "dash": 2.9, "crouchHeight": 0.95}
CAULDRON = {"maxStep": 0.35, "maxSlope": 27.0, "clearance": 1.84}

# Triangle budgets per role (soft, hard) for an Intel UHD 620 laptop at 1080p (refactor-pass low-end-pc.md).
BUDGETS = {"Play": (700, 1200), "Device": (1600, 3000), "Obstacle": (2500, 4000), "Decor": (2000, 4500)}

LANE = "Oynanis"


def log(*a):
    print("[levelkit]", *a, flush=True)


# ---------------------------------------------------------------------------------------------------------------------
# Scene and materials
# ---------------------------------------------------------------------------------------------------------------------

_materials = {}
_painted = set()


def use_palette(module):
    """Build with another palette module of kit_palette's shape: the theme's (build_levelkit.py --theme), or the
    Harabe look target's own (Art/Harabe). Call it after new_scene() and before the first piece."""
    global pal
    pal = module
    _materials.clear()


def painted():
    """Every role a face was given since new_scene(): what the built pieces actually wear."""
    return set(_painted)


def new_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _materials.clear()
    _painted.clear()
    sc = bpy.context.scene
    sc.name = "LevelKit"
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'
    # TEXTURE, not MATERIAL: the atlas roles share one material and keep their colours in its image. Untextured
    # materials (Tint, the stand-ins) still draw their own colour.
    sh.color_type = 'TEXTURE'
    sh.show_shadows = True
    sh.shadow_intensity = 0.35
    sh.show_cavity = True
    sh.cavity_type = 'WORLD'
    sh.background_type = 'WORLD'
    sc.display.render_aa = '8'
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'Standard'
    world = bpy.data.worlds.new("World")
    world.color = (0.20, 0.21, 0.26)
    sc.world = world
    return sc


def palette_texture():
    """T_Kit_Palette (kit_palette.ATLAS): one flat cell per atlas role, RGB its sRGB colour and alpha its smoothness.
    An unused cell is magenta at half smoothness, so a face mapped there by mistake is loud. Built in memory here;
    export_textures writes it with every family."""
    name = os.path.splitext(pal.TEXTURES[pal.ATLAS_ROLE])[0]
    image = bpy.data.images.get(name)
    if image is not None:
        return image
    width, height = pal.ATLAS_COLUMNS * pal.ATLAS_CELL, pal.ATLAS_ROWS * pal.ATLAS_CELL
    pixels, total = [], [0.0, 0.0, 0.0]
    for j in range(height):
        for i in range(width):
            cell = (j // pal.ATLAS_CELL) * pal.ATLAS_COLUMNS + i // pal.ATLAS_CELL
            if cell < len(pal.ATLAS):
                _, hx, smooth, _, _ = pal.role(pal.ATLAS[cell])
                rgb = pal.hex_to_srgb(hx)
            else:
                rgb, smooth = (1.0, 0.0, 1.0), 0.5
            pixels.extend((*rgb, smooth))
            for k in range(3):
                total[k] += rgb[k]
    image = bpy.data.images.new(name, width, height, alpha=True)
    image.colorspace_settings.name = 'sRGB'
    image.alpha_mode = 'STRAIGHT'
    image.pixels = pixels
    image["average"] = pal.srgb_to_linear(tuple(c / (width * height) for c in total))
    return image


def atlas_on_disk_matches():
    """Whether the T_Kit_Palette beside the FBX files is the atlas this palette makes. Every family's meshes and
    Bölüm 1's skin sample it at the cells they were built with, so a build that writes only some of them must find
    the same atlas there (a theme change moves the cells)."""
    path = os.path.join(FBX_DIR, pal.TEXTURES[pal.ATLAS_ROLE])
    if not os.path.exists(path):
        return False
    mine = palette_texture()
    disk = bpy.data.images.load(path, check_existing=False)
    try:
        return tuple(disk.size) == tuple(mine.size) and all(
            abs(a - b) < 1.5 / 255 for a, b in zip(disk.pixels[:], mine.pixels[:]))
    finally:
        bpy.data.images.remove(disk)


def material(role):
    """The kit material for a palette role, created once per scene: M_Kit_<Role>, or M_Kit_Atlas for the atlas."""
    if role in _materials:
        return _materials[role]
    if role == pal.ATLAS_ROLE:
        return _atlas_material()
    _, hx, smooth, ehx, eint = pal.role(role)
    lin = pal.srgb_to_linear(pal.hex_to_srgb(hx))
    mat = bpy.data.materials.new(pal.material_name(role))
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
        bsdf.inputs["Roughness"].default_value = 1.0 - smooth
        bsdf.inputs["Metallic"].default_value = 0.0
        if ehx:
            elin = pal.srgb_to_linear(pal.hex_to_srgb(ehx))
            bsdf.inputs["Emission Color"].default_value = (*elin, 1.0)
            bsdf.inputs["Emission Strength"].default_value = eint
    mat.diffuse_color = (*lin, 1.0)
    mat.roughness = 1.0 - smooth
    mat.metallic = 0.0
    # A textured role (kit_palette.TEXTURES) shows its image in EEVEE, and its average colour in the workbench sheets,
    # which draw material colours only. The image has to exist before the first piece using the role is built.
    tex = pal.TEXTURES.get(role)
    if tex:
        image = bpy.data.images.get(os.path.splitext(tex)[0])
        if image is None:
            raise CheckError("role %s: its texture %s has not been generated yet" % (role, tex))
        if bsdf:
            node = mat.node_tree.nodes.new("ShaderNodeTexImage")
            node.image = image
            mat.node_tree.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        mat.diffuse_color = (*image["average"], 1.0)
    _materials[role] = mat
    return mat


def _atlas_material():
    """M_Kit_Atlas: the palette image, sampled nearest so a cell is one flat colour, its alpha as smoothness."""
    image = palette_texture()
    mat = bpy.data.materials.new(pal.material_name(pal.ATLAS_ROLE))
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.interpolation = 'Closest'
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        rough = nodes.new("ShaderNodeMath")
        rough.operation = 'SUBTRACT'
        rough.inputs[0].default_value = 1.0
        links.new(tex.outputs["Alpha"], rough.inputs[1])
        links.new(rough.outputs["Value"], bsdf.inputs["Roughness"])
        bsdf.inputs["Metallic"].default_value = 0.0
    mat.diffuse_color = (*image["average"], 1.0)
    mat.metallic = 0.0
    _materials[pal.ATLAS_ROLE] = mat
    return mat


def plain_material(name, rgb):
    """A render-only material (stand-ins, labels); never exported."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        lin = pal.srgb_to_linear(rgb)
        mat.diffuse_color = (*lin, 1.0)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.5
    return mat


# ---------------------------------------------------------------------------------------------------------------------
# bmesh builders. Each returns a bmesh in piece space; paint() gives its faces a palette role.
# ---------------------------------------------------------------------------------------------------------------------

def translate(bm, v):
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(v))
    return bm


def rotate(bm, axis, degrees, origin=(0.0, 0.0, 0.0)):
    q = Quaternion(Vector(axis), math.radians(degrees))
    o = Vector(origin)
    for v in bm.verts:
        v.co = q @ (v.co - o) + o
    return bm


def orient(bm, axis):
    """Turn a mesh built along +Z so it runs along the given axis ('X', 'Y' or 'Z')."""
    if axis == 'X':
        rotate(bm, (0, 1, 0), 90)
    elif axis == 'Y':
        rotate(bm, (1, 0, 0), -90)
    return bm


def scale(bm, s, origin=(0.0, 0.0, 0.0)):
    o = Vector(origin)
    for v in bm.verts:
        d = v.co - o
        v.co = o + Vector((d.x * s[0], d.y * s[1], d.z * s[2]))
    return bm


def bevel(bm, edges, r, seg=3):
    if r <= 0 or not edges:
        return bm
    bmesh.ops.bevel(bm, geom=edges, offset=r, offset_type='OFFSET', segments=seg, profile=0.5, affect='EDGES',
                    clamp_overlap=True)
    return bm


def box(size, center=(0.0, 0.0, 0.0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts, vec=Vector(size))
    return translate(bm, center)


def _on(v, axis, value):
    return abs(v.co[axis] - value) < 1e-5


def block(size, center=(0.0, 0.0, 0.0), corner=0.0, top=0.0, bottom=0.0, seg=3, keep=()):
    """A box with its plan corners (vertical edges) rounded by `corner` and its top and bottom perimeters by `top` and
    `bottom`. `keep` names faces that stay flat and square: '-x', '+x', '-y', '+y'. Chainable floors keep both X ends,
    so modules laid end to end along the lane meet flush with no groove; an end cap keeps the side it joins."""
    bm = box(size, center)
    c = Vector(center)
    h = Vector(size) / 2
    planes = {'-x': (0, c.x - h.x), '+x': (0, c.x + h.x), '-y': (1, c.y - h.y), '+y': (1, c.y + h.y)}
    kept = [planes[k] for k in keep]

    def on_kept(e):
        return any(all(_on(v, a, val) for v in e.verts) for a, val in kept)

    if corner > 0:
        vertical = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1e-6 and not on_kept(e)]
        bevel(bm, vertical, corner, seg)
    if top > 0:
        bevel(bm, [e for e in bm.edges if all(_on(v, 2, c.z + h.z) for v in e.verts) and not on_kept(e)], top, seg)
    if bottom > 0:
        bevel(bm, [e for e in bm.edges if all(_on(v, 2, c.z - h.z) for v in e.verts) and not on_kept(e)], bottom, seg)
    return bm


def rounded_box(size, r, center=(0.0, 0.0, 0.0), seg=3):
    """Every edge rounded by r."""
    bm = box(size, center)
    return bevel(bm, list(bm.edges), r, seg)


def lathe(profile, u=24, center=(0.0, 0.0, 0.0), axis='Z', cap_bottom=True, cap_top=True, closed=False):
    """Revolve [(radius, z), ...], listed bottom to top, around +Z. A radius of 0 at an end closes it in a pole;
    otherwise that end gets an n-gon cap when asked for. `closed` joins the last point back to the first instead, for
    a cross-section that is a loop (a ring)."""
    bm = bmesh.new()
    rings = []
    for rad, z in profile:
        if rad <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((rad * math.cos(2 * math.pi * k / u), rad * math.sin(2 * math.pi * k / u), z))
                          for k in range(u)])
    if closed:
        rings.append(rings[0])
        cap_bottom = cap_top = False
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for k in range(u):
                bm.faces.new((a[0], b[k], b[(k + 1) % u]))
        elif len(b) == 1:
            for k in range(u):
                bm.faces.new((a[k], b[0], a[(k + 1) % u]))
        else:
            for k in range(u):
                k1 = (k + 1) % u
                bm.faces.new((a[k], a[k1], b[k1], b[k]))
    if cap_bottom and len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if cap_top and len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    orient(bm, axis)
    return translate(bm, center)


def cylinder(r, h, center=(0.0, 0.0, 0.0), u=24, top=0.0, bottom=0.0, seg=2, axis='Z', r_top=None):
    """Closed cylinder (a cone frustum when r_top is given), `h` long along `axis`, centred on `center`, its end
    rims rounded by `top` / `bottom`."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=u, radius1=r,
                          radius2=r if r_top is None else r_top, depth=h)
    if top > 0:
        bevel(bm, [e for e in bm.edges if all(_on(v, 2, h / 2) for v in e.verts)], top, seg)
    if bottom > 0:
        bevel(bm, [e for e in bm.edges if all(_on(v, 2, -h / 2) for v in e.verts)], bottom, seg)
    orient(bm, axis)
    return translate(bm, center)


def sphere(r, center=(0.0, 0.0, 0.0), u=16, v=10, stretch=(1.0, 1.0, 1.0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r)
    scale(bm, stretch)
    return translate(bm, center)


def capsule(r, length, center=(0.0, 0.0, 0.0), axis='Z', u=16, rings=4):
    """A cylinder `length` long capped by two hemispheres of radius r: `length + 2r` end to end."""
    prof = []
    for i in range(rings + 1):
        a = -math.pi / 2 + (math.pi / 2) * i / rings
        prof.append((r * math.cos(a), -length / 2 + r * math.sin(a)))
    for i in range(rings + 1):
        a = (math.pi / 2) * i / rings
        prof.append((r * math.cos(a), length / 2 + r * math.sin(a)))
    return lathe(prof, u, center, axis)


def torus(R, r, center=(0.0, 0.0, 0.0), arc=(0.0, 360.0), plane='XZ', u=32, v=12, caps=True):
    """A tube of radius r along an arc of a circle of radius R. The arc is in degrees from the plane's first axis
    toward its second: 'XZ' (faces the camera, 0 = +X, 90 = +Z) or 'YZ' (0 = +Y, 90 = +Z) or 'XY'."""
    axes = {'XZ': (Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0))),
            'YZ': (Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0))),
            'XY': (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))}[plane]
    e1, e2, n = axes
    full = abs(arc[1] - arc[0]) >= 359.999
    steps = u if full else u + 1
    bm = bmesh.new()
    rings = []
    for i in range(steps):
        t = math.radians(arc[0] + (arc[1] - arc[0]) * i / u)
        radial = e1 * math.cos(t) + e2 * math.sin(t)
        c = radial * R
        rings.append([bm.verts.new(c + r * (radial * math.cos(2 * math.pi * k / v) + n * math.sin(2 * math.pi * k / v)))
                      for k in range(v)])
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if full else [])
    for a, b in pairs:
        for k in range(v):
            k1 = (k + 1) % v
            bm.faces.new((a[k], a[k1], b[k1], b[k]))
    if caps and not full:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return translate(bm, center)


def tube(points, r, sides=10, caps=True):
    """A tube of radius r along a polyline, framed by parallel transport so it does not twist."""
    pts = [Vector(p) for p in points]
    bm = bmesh.new()
    tangents = []
    for i in range(len(pts)):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        tangents.append((b - a).normalized())
    ref = Vector((0, 0, 1)) if abs(tangents[0].z) < 0.9 else Vector((1, 0, 0))
    normal = tangents[0].cross(ref).normalized()
    rings = []
    for i, (p, t) in enumerate(zip(pts, tangents)):
        if i > 0:
            normal = (normal - t * normal.dot(t)).normalized()
        binormal = t.cross(normal)
        rings.append([bm.verts.new(p + r * (normal * math.cos(2 * math.pi * k / sides) +
                                             binormal * math.sin(2 * math.pi * k / sides))) for k in range(sides)])
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            k1 = (k + 1) % sides
            bm.faces.new((a[k], a[k1], b[k1], b[k]))
    if caps:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def prism(profile, depth, plane='XZ', offset=0.0, r=0.0, seg=2):
    """A closed 2D polygon extruded `depth` along the plane's normal, centred on `offset` along it.
    'XZ': profile (x, z), extruded along Y. 'XY': profile (x, y), extruded along Z. 'YZ': profile (y, z) along X."""
    bm = bmesh.new()
    lo = offset - depth / 2

    def place(a, b, w):
        if plane == 'XZ':
            return (a, w, b)
        if plane == 'XY':
            return (a, b, w)
        return (w, a, b)

    verts = [bm.verts.new(place(a, b, lo)) for a, b in profile]
    face = bm.faces.new(verts)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    moved = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    step = {'XZ': (0, depth, 0), 'XY': (0, 0, depth), 'YZ': (depth, 0, 0)}[plane]
    bmesh.ops.translate(bm, verts=moved, vec=Vector(step))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if r > 0:
        bevel(bm, list(bm.edges), r, seg)
    return bm


def cut(bm, normal, positions):
    """Slice the mesh with planes normal . p = d for every d in positions; nothing is removed, the faces just gain the
    edges a stripe or a band needs so paint() can give each side its own role."""
    n = Vector(normal).normalized()
    for d in positions:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=n * d, plane_no=n)
    return bm


def steps_between(lo, hi, step, origin=0.0):
    """Every origin + k * step strictly inside (lo, hi)."""
    k0 = math.floor((lo - origin) / step) + 1
    out = []
    k = k0
    while origin + k * step < hi - 1e-6:
        out.append(origin + k * step)
        k += 1
    return out


def paint(bm, rule):
    """Give every face a palette role: a role name, or a function(face) -> role name."""
    for f in bm.faces:
        role = rule if isinstance(rule, str) else rule(f)
        f.material_index = pal.ROLE_INDEX[role]
        _painted.add(role)
    return bm


def centre(f):
    return f.calc_center_median()


# ---------------------------------------------------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------------------------------------------------

@dataclass
class Look:
    """What a theme makes of one piece whose contract a family module holds (kit_structure, kit_devices, kit_obstacles,
    kit_decor): the meshes of its one part (`body`) or of each named part (`parts`), where the top probe may sample the
    visual walk surface (None: the contract's own rectangle), and a sentence for the catalogue note."""
    body: list = None
    walk_rect: tuple = None
    note: str = ""
    parts: dict = None


def notes(contract, look):
    """A catalogue note: the contract's sentences, then the look's."""
    return contract + (" " + look.note if look.note else "")


@dataclass
class Host:
    """A transform the Unity builder creates at `pivot` (piece space). Parts and colliders hang under it. `parent` is
    another host, or for a device variant the path of an existing child of the base prefab ("Visual", "Front"), which
    sits at the root's origin unless the variant's `anchors` says where (piece space): the seesaw's plank, 1.15 m up."""
    name: str
    pivot: tuple = (0.0, 0.0, 0.0)
    parent: str = ""
    layer: str = ""
    # What the Unity builder hangs on the host (docs/level-kit.md, "Obstacles"): with a kinematic body, Rotate /
    # Swing / Slide / Squash get an ObstacleDriver and Belt a ConveyorSurface; without one, Rotate is a cosmetic
    # SpinView. Updraft gets a LaunchPad on the host's trigger. Roll hosts of a device variant turn with the device's
    # travel (the chase wall's drums, ChaseDrumView). Grip is ice (MIX-205): nothing moves, the host gets an
    # IceSurface, and like a belt it needs the body a character finds its ground through. Still (MIX-254) is a part
    # that hits without moving on its own - a driver with no motion - so a treadmill can carry it as cargo. Tread
    # (MIX-258) is a treadmill's deck: a belt that stops for its inputs and carries the cargo placed on it. Mud
    # (MIX-259) is ice's opposite: nothing moves, the host gets a MudSurface whose drag (the range) slows the run. Tar
    # (MIX-253) is a tar pool's: the host gets a TarPool that lays its parts, one-cell modules, end to end. Chute
    # (MIX-287) is a slide's: nothing moves, the host gets a SlideSurface that measures its slope on the collider.
    motion: str = "None"            # None | Rotate | Swing | Slide | Squash | Belt | Updraft | Roll | Grip | Still | Tread | Mud | Tar | Chute
    axis: tuple = (0.0, 0.0, 0.0)   # Blender axis of the motion (Unity's own sense of rotation about its image)
    range: float = 0.0              # degrees (Rotate / Swing), metres (Slide, Updraft height, Roll radius), scale
                                    # (Squash), m/s (Belt), the share of grip taken away (Grip)
    period: float = 0.0             # seconds per cycle; for an Updraft, between two pushes; for a Belt, the
                                    # metres its chevron pattern repeats over
    kinematic: bool = False         # carries a kinematic Rigidbody (a door panel, a moving obstacle part)
    knock: tuple = ()               # (m/s along the lane, metres of lift) a hit throws with; empty = does not throw
    kills: bool = False             # a hit kills instead of throwing: the iron that cuts (MIX-254)
    reach: float = 0.0              # metres a hit reaches past the shapes; 0 leaves the config's default
    dwell: float = 0.0              # a slide's hold at each end, seconds; 0 leaves the builder's default
    share: float = 0.0              # a slide's share of moving time spent going out; 0 = the even split
    mouth: float = 0.0              # Tread (MIX-258): metres at each end where cargo sinks into the machine
    sink: float = 0.0               # Tread: how deep cargo sinks there, deeper than the tallest cargo


@dataclass
class Part:
    name: str
    host: str
    obj: object
    materials: list
    shadows: bool = True
    camera_side: bool = False


@dataclass
class Collider:
    host: str
    kind: str                       # Box | Capsule | Sphere
    center: tuple                   # piece space
    size: tuple = (0.0, 0.0, 0.0)   # Blender axes (box)
    tilt: float = 0.0               # degrees about the depth axis; positive raises the +X end
    radius: float = 0.0
    height: float = 0.0
    axis: str = 'Z'                 # Blender axis of a capsule
    trigger: bool = False
    walk: bool = False


@dataclass
class Piece:
    name: str
    family: str
    role: str                       # Play | Obstacle | Decor | Device
    pivot: str                      # TopCentre | BottomCentre | Underside | Axis | Attach | Contract
    cells: tuple = (0, 0, 0)        # Unity axes (lane, up, depth) in grid cells; zeros when off the grid
    top: object = None              # walk height in piece space, or None
    top_fn: object = None           # z(x, y) of a sloped walk surface
    slope: float = 0.0
    walk_rect: tuple = None         # (x0, x1, y0, y1) the top probe samples
    walkable: bool = False
    cauldron_safe: bool = False
    step_up: bool = False
    blocks_lane: bool = False
    depth_symmetric: bool = False
    chainable: bool = False
    static: bool = True
    shadows: bool = True
    layer: str = "Ground"
    budget: tuple = None
    notes: str = ""
    hosts: list = field(default_factory=list)
    parts: list = field(default_factory=list)
    colliders: list = field(default_factory=list)
    variant: dict = None
    frame_yaw: float = 0.0          # a variant authored in the lane frame inside a prefab that levels place at this yaw


class Kit:
    def __init__(self, key, family):
        self.key = key
        self.family = family
        self.coll = bpy.data.collections.new("Kit_" + family)
        bpy.context.scene.collection.children.link(self.coll)
        self.pieces = []

    def piece(self, name, **kw):
        p = Piece(name=name, family=self.family, **kw)
        self.pieces.append(p)
        return Builder(self, p)

    @property
    def fbx_path(self):
        return os.path.join(FBX_DIR, "Kit_%s.fbx" % self.family)

    @property
    def manifest_path(self):
        return os.path.join(FBX_DIR, "Kit_%s.json" % self.family)

    def objects(self):
        return [part.obj for p in self.pieces for part in p.parts]


class Builder:
    def __init__(self, kit, piece):
        self.kit = kit
        self.p = piece

    def host(self, name, pivot=(0.0, 0.0, 0.0), parent="", **kw):
        self.p.hosts.append(Host(name, tuple(pivot), parent, **kw))
        return self

    def part(self, name, bms, host="", shadows=None, camera_side=False, sharp=50.0, weighted=True):
        if not isinstance(bms, (list, tuple)):
            bms = [bms]
        full = "%s__%s" % (self.p.name, name)
        ob, roles = make_object(full, bms, self.kit.coll, sharp, weighted)
        self.p.parts.append(Part(name, host, ob, roles, self.p.shadows if shadows is None else shadows, camera_side))
        return ob

    def box(self, center, size, host="", tilt=0.0, walk=False, trigger=False):
        self.p.colliders.append(Collider(host, "Box", tuple(center), tuple(size), tilt, walk=walk, trigger=trigger))
        return self

    def capsule(self, center, radius, height, axis, host="", trigger=False):
        self.p.colliders.append(Collider(host, "Capsule", tuple(center), radius=radius, height=height, axis=axis,
                                         trigger=trigger))
        return self

    def sphere(self, center, radius, host="", trigger=False):
        self.p.colliders.append(Collider(host, "Sphere", tuple(center), radius=radius, trigger=trigger))
        return self


LIFT = 0.01             # m a coplanar face is pushed in along its normal
# Pieces whose faces the contract pins: a walkable top is probed to the millimetre and a depth-symmetric piece must
# match on both sides, so a one-sided nudge fails the check. Their coplanar pairs are fixed by hand in the theme.
LIFT_SKIP = ("Levha", "Kaydirak")
COPLANAR = 0.005        # m: two faces closer than this on one plane z-fight


def _tri_overlap(a, b):
    """True when one triangle's centroid lies inside the other (both coplanar, same facing): they share area."""
    def inside(p, t):
        n = t[2]
        v = [x.co for x in t[1].verts]
        return all((v[(k + 1) % 3] - v[k]).cross(p - v[k]).dot(n) > 1e-6 for k in range(3))
    return inside(a[4], b) or inside(b[4], a)


def lift_coplanar(bms, name):
    """Pushes the greater of two same-facing faces that share a plane and some area in by LIFT, so the pair stops
    z-fighting. Parts are the separate blocks a piece is made of (a decal block on a wall, a band over a body): the
    greater is the face of the bigger part, its own vertices moving with its neighbours shrinking 1 cm, never a
    gap. In rather than the lesser out so a piece's bounds, which its collider and contract checks pin, never grow.
    Rounds repeat for a stack of three. Run before the parts are joined, on triangulated parts."""
    vol = []
    for bm in bms:
        co = [v.co for v in bm.verts] or [Vector()]
        lo = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
        hi = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
        vol.append((hi - lo).x * (hi - lo).y * (hi - lo).z)
    lifted = 0
    for _ in range(3):
        buckets = {}
        for pi, bm in enumerate(bms):
            bm.normal_update()
            for f in bm.faces:
                if f.calc_area() < 1e-8:
                    continue
                n = f.normal
                cs = [v.co for v in f.verts]
                t = (pi, f, n.copy(), n.dot(cs[0]), f.calc_center_median(),
                     Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs))),
                     Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs))))
                buckets.setdefault((round(n.x, 2) + 0.0, round(n.y, 2) + 0.0, round(n.z, 2) + 0.0), []).append(t)
        push = {}
        for tl in buckets.values():
            tl.sort(key=lambda t: t[3])
            for i, a in enumerate(tl):
                for b in tl[i + 1:]:
                    if b[3] - a[3] > COPLANAR:
                        break
                    if any(a[5][k] > b[6][k] or b[5][k] > a[6][k] for k in range(3)) or not _tri_overlap(a, b):
                        continue
                    lose = b if (vol[a[0]], a[1].calc_area()) < (vol[b[0]], b[1].calc_area()) else a
                    push[(lose[0], lose[1].index)] = lose
        if not push:
            break
        for (pi, _), t in push.items():
            for v in t[1].verts:
                v.co -= t[2] * LIFT
            lifted += 1
    if lifted:
        log("  %s: sunk %d coplanar faces" % (name, lifted))


def make_object(name, bms, coll, sharp=50.0, weighted=True):
    """One mesh object out of several bmeshes: triangulated, smooth with edges sharper than `sharp` degrees split, the
    atlas roles folded into one slot through their UVs and the rest compacted into slots after it in palette order,
    and a weighted-normal modifier so a big flat face stays flat next to its rounded edge instead of shading into it."""
    for part in bms:
        bmesh.ops.triangulate(part, faces=list(part.faces), quad_method='BEAUTY', ngon_method='BEAUTY')
    if not name.startswith(LIFT_SKIP):
        lift_coplanar(bms, name)
    bm = bmesh.new()
    for part in bms:
        tmp = bpy.data.meshes.new("tmp")
        part.to_mesh(tmp)
        part.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method='BEAUTY', ngon_method='BEAUTY')
    limit = math.radians(sharp)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > limit:
            e.smooth = False
    # The palette atlas (kit_palette.ATLAS): an atlas role's face carries its colour in its UVs, every loop on the
    # centre of the role's cell, and joins slot key 0; any other role keeps a slot of its own after it (key 1 + its
    # palette index). A Belt face keeps the UVs its piece gave it.
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        role = pal.ROLE_NAMES[f.material_index]
        if role in pal.ATLAS:
            cell = pal.atlas_uv(role)
            for loop in f.loops:
                loop[uv].uv = cell
            f.material_index = 0
        else:
            f.material_index = 1 + pal.ROLE_INDEX[role]
    used = sorted({f.material_index for f in bm.faces})
    remap = {g: i for i, g in enumerate(used)}
    for f in bm.faces:
        f.material_index = remap[f.material_index]
    # Unity numbers submeshes in the order their material first turns up in the polygon list, not by slot. Sorting
    # the faces by slot makes the two agree, so the manifest's material order is the imported submesh order.
    bm.faces.sort(key=lambda f: f.material_index)
    bm.faces.index_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    roles = [pal.ATLAS_ROLE if g == 0 else pal.ROLE_NAMES[g - 1] for g in used]
    for r in roles:
        me.materials.append(material(r))
    if me.validate(verbose=False):
        log("WARNING %s: validate() changed the mesh" % name)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if weighted:
        mod = ob.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
        mod.mode = 'FACE_AREA'
        mod.weight = 50
        mod.keep_sharp = True
    return ob, roles


# ---------------------------------------------------------------------------------------------------------------------
# Unity mapping
# ---------------------------------------------------------------------------------------------------------------------

RX90 = Quaternion((1.0, 0.0, 0.0), math.radians(90.0))
AXIS_INDEX = {'X': 0, 'Y': 2, 'Z': 1}      # Blender axis -> Unity axis index


def to_unity(p):
    """Blender piece space -> Unity prefab space: (x, y, z) -> (x, z, y)."""
    return Vector((p[0], p[2], p[1]))


def yaw(deg):
    return Quaternion((0.0, 1.0, 0.0), math.radians(deg))


def frame(piece):
    """Rotation from the lane frame the piece was authored in to the prefab's own frame."""
    return yaw(-piece.frame_yaw)


def host_abs(piece, name):
    """A host's position in the prefab (or its anchor) frame. The root and a base-prefab anchor sit at zero."""
    for h in piece.hosts:
        if h.name == name:
            return frame(piece) @ to_unity(h.pivot)
    return Vector((0.0, 0.0, 0.0))


def mesh_bounds(ob):
    """Expected bounds of the imported mesh sub-asset: the importer keeps X and Y and negates Z."""
    vs = [v.co for v in ob.data.vertices]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), -max(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), -min(v.z for v in vs)))
    return lo, hi


def piece_vertices(piece):
    return [v.co.copy() for part in piece.parts for v in part.obj.data.vertices]


def bounds(points):
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi


def r5(x):
    v = round(float(x), 5)
    return 0.0 if v == 0 else v


def v3(v):
    return {"x": r5(v[0]), "y": r5(v[1]), "z": r5(v[2])}


def q4(q):
    return {"x": r5(q.x), "y": r5(q.y), "z": r5(q.z), "w": r5(q.w)}


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


# ---------------------------------------------------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------------------------------------------------

class CheckError(RuntimeError):
    pass


def check_piece(piece, errors, warnings):
    name = piece.name
    if not re.fullmatch(r"[A-Za-z0-9_]+", name):
        errors.append("%s: name must be ASCII letters, digits and underscores" % name)
    if not piece.parts:
        errors.append("%s: no parts" % name)
        return
    host_names = {h.name for h in piece.hosts}
    part_names = [p.name for p in piece.parts]
    if len(set(part_names)) != len(part_names):
        errors.append("%s: duplicate part names %s" % (name, part_names))
    if host_names & set(part_names):
        errors.append("%s: host and part share a name: %s" % (name, host_names & set(part_names)))
    for part in piece.parts:
        ob = part.obj
        if ob.name != ob.data.name or ob.name != "%s__%s" % (name, part.name):
            errors.append("%s: object %s / mesh %s were renamed" % (name, ob.name, ob.data.name))
        if part.host and part.host not in host_names:
            errors.append("%s: part %s hangs under unknown host %s" % (name, part.name, part.host))
        slots = [m.name for m in ob.data.materials]
        if len(set(slots)) != len(slots):
            errors.append("%s: duplicate material slots %s" % (ob.name, slots))
        used = {p.material_index for p in ob.data.polygons}
        if used != set(range(len(slots))):
            errors.append("%s: unused material slots" % ob.name)
        if any(abs(c) > 1e-9 for c in ob.location) or any(abs(c) > 1e-9 for c in ob.rotation_euler) \
                or any(abs(c - 1) > 1e-9 for c in ob.scale) or ob.parent is not None:
            errors.append("%s: object transform must be identity" % ob.name)
    for c in piece.colliders:
        if c.host and c.host not in host_names:
            errors.append("%s: collider under unknown host %s" % (name, c.host))
    for h in piece.hosts:
        if h.parent and h.parent not in host_names and piece.variant is None:
            errors.append("%s: host %s under unknown parent %s" % (name, h.name, h.parent))
        if piece.role != "Obstacle":
            continue
        # What the Unity builder will hang on this host has to be able to work.
        shapes = [c for c in piece.colliders if c.host == h.name]
        if h.motion == "Tread" and not (h.kinematic and any(c.walk for c in shapes) and h.mouth > 0 and h.sink > 0):
            errors.append("%s: treadmill %s needs a kinematic body, a walk collider, a mouth and a sink" % (name, h.name))
        if h.motion in ("Rotate", "Swing", "Slide", "Shoot", "Squash", "Belt", "Still", "Tread") and shapes and not h.kinematic:
            errors.append("%s: host %s moves colliders without a kinematic body" % (name, h.name))
        if h.motion == "Grip" and not (h.kinematic and shapes and 0.0 < h.range < 1.0):
            errors.append("%s: ice %s needs a kinematic body, a collider and a slip between 0 and 1" % (name, h.name))
        if h.motion == "Mud" and not (h.kinematic and shapes and 0.0 < h.range < 1.0):
            errors.append("%s: mud %s needs a kinematic body, a collider and a drag between 0 and 1" % (name, h.name))
        if h.motion == "Chute" and not (h.kinematic and any(c.walk and c.tilt for c in shapes)):
            errors.append("%s: slide %s needs a kinematic body and a tilted walk collider" % (name, h.name))
        if (h.knock or h.kills) and not shapes:
            errors.append("%s: host %s hits but has no collider to hit with" % (name, h.name))
        if h.motion == "Still" and not (h.kinematic and (h.knock or h.kills)):
            errors.append("%s: still host %s needs a kinematic body and a knock or a kill" % (name, h.name))
        if h.kills and h.knock:
            errors.append("%s: host %s both throws and kills; a kill wins, drop the knock" % (name, h.name))
        if h.motion == "Updraft" and not any(c.trigger for c in shapes):
            errors.append("%s: updraft %s has no trigger to push from" % (name, h.name))
    check_run(piece, errors)

    pts = piece_vertices(piece)
    lo, hi = bounds(pts)
    size = hi - lo

    # Grid: a lane piece's extents are whole cells, and four cells deep.
    cx, cy, cz = piece.cells
    if cx or cy or cz:
        want = Vector((cx * GRID, cz * GRID, cy * GRID))    # Blender axes
        for axis, label in ((0, "lane"), (1, "depth"), (2, "height")):
            if want[axis] > 0 and abs(size[axis] - want[axis]) > MM * 2:
                errors.append("%s: %s extent %.4f m, expected %.4f m (%g cells)" % (
                    name, label, size[axis], want[axis], want[axis] / GRID))

    # Pivot conventions.
    if piece.pivot == "TopCentre" and abs(hi.z) > MM:
        errors.append("%s: TopCentre pivot but the top is at z %.4f" % (name, hi.z))
    if piece.pivot in ("BottomCentre", "Underside") and abs(lo.z) > MM:
        errors.append("%s: %s pivot but the bottom is at z %.4f" % (name, piece.pivot, lo.z))
    if piece.depth_symmetric:
        key = {(round(p.x, 3), round(p.y, 3), round(p.z, 3)) for p in pts}
        mirrored = {(x, round(-y, 3) + 0.0, z) for x, y, z in key}
        if len({(x, y + 0.0, z) for x, y, z in key} ^ mirrored) > 0:
            errors.append("%s: flagged depth-symmetric but the -Y and +Y sides differ" % name)

    # Walk surface: probe the visual top with vertical rays, then the collider that is walked on.
    if piece.top is not None and piece.walk_rect:
        probe_top(piece, errors)
    for c in piece.colliders:
        if c.walk and c.kind == "Box" and abs(c.tilt) < 1e-9 and piece.top is not None:
            ctop = c.center[2] + c.size[2] / 2
            want = piece.top_fn(c.center[0], c.center[1]) if piece.top_fn else piece.top
            if abs(ctop - want) > MM:
                errors.append("%s: walk collider top %.4f, visual top %.4f" % (name, ctop, want))
    if piece.cauldron_safe and piece.slope > CAULDRON["maxSlope"]:
        errors.append("%s: flagged cauldron-safe at %.1f deg" % (name, piece.slope))
    if piece.walkable and piece.slope > 45.0 + 1e-6:
        errors.append("%s: flagged walkable at %.1f deg" % (name, piece.slope))
    if piece.step_up and piece.top is not None and piece.top > 0.33:
        errors.append("%s: a step-up piece %.2f m tall" % (name, piece.top))

    total = sum(tris(p.obj) for p in piece.parts)
    soft, hard = piece.budget or BUDGETS[piece.role]
    if total > hard:
        errors.append("%s: %d triangles, over the hard budget %d" % (name, total, hard))
    elif total > soft:
        warnings.append("%s: %d triangles, over the soft budget %d" % (name, total, soft))
    # A part is at most the atlas, Tint and Belt (MIX-190): anything more means a role escaped the atlas.
    subs = max(len(p.materials) for p in piece.parts)
    if subs > 3:
        errors.append("%s: %d materials on one part" % (name, subs))


RUN_MIDDLE, RUN_STRETCHED, RUN_ENDS = "Orta_", "Uzun_", ("Uc_Sol", "Uc_Sag")


def run_host(piece):
    """The host a run's modules hang under (MIX-290): the one whose parts include an Orta_ middle ("" for the root),
    or None for a piece that is no run. A tar pool lays its own (TarPool) and is none."""
    middles = [p for p in piece.parts if p.name.startswith(RUN_MIDDLE)]
    if not middles:
        return None
    host = next((h for h in piece.hosts if h.name == middles[0].host), None)
    return None if host is not None and host.motion == "Tar" else middles[0].host


def check_run(piece, errors):
    """A run's modules are what the Unity CellRun lays: every middle and every Uzun_ part exactly one cell long and
    centred on its host, each end inside that cell (it is laid over the first or the last one), all on one host. The
    run is laid centred on that host and the level editor takes the pivot for the run's centre, so the host sits at
    x 0 (an Uzun_ part is stretched about the piece's origin too); the lane is the prefab's X."""
    host = run_host(piece)
    if host is None:
        return
    name = piece.name
    hx = next((h.pivot[0] for h in piece.hosts if h.name == host), 0.0)
    if piece.cells[0] != 1:
        errors.append("%s: a run is one cell long in the manifest, its modules' length" % name)
    if piece.frame_yaw:
        errors.append("%s: a run is laid along the prefab's X; frame_yaw %g turns it" % (name, piece.frame_yaw))
    if abs(hx) > MM:
        errors.append("%s: run host %r at x %.4f; a run is centred on its pivot, so its host sits at x 0" % (
            name, host, hx))
    g = GRID / 2
    for part in piece.parts:
        if not (part.name.startswith((RUN_MIDDLE, RUN_STRETCHED)) or part.name in RUN_ENDS):
            continue
        if part.host != host:
            errors.append("%s: run part %s hangs under %r, not the run's host %r" % (name, part.name, part.host, host))
            continue
        xs = [v.co.x - hx for v in part.obj.data.vertices]
        lo, hi = min(xs), max(xs)
        if part.name in RUN_ENDS:
            if lo < -g - MM or hi > g + MM:
                errors.append("%s: run end %s spans x %.4f..%.4f, outside its cell" % (name, part.name, lo, hi))
        elif abs(hi - lo - GRID) > 2 * MM or abs(lo + hi) > 2 * MM:
            errors.append("%s: run module %s spans x %.4f..%.4f, not one cell centred on its host" % (
                name, part.name, lo, hi))


def probe_top(piece, errors):
    bm = bmesh.new()
    for part in piece.parts:
        bm.from_mesh(part.obj.data)
    bvh = BVHTree.FromBMesh(bm)
    x0, x1, y0, y1 = piece.walk_rect
    bad = 0
    for i in range(7):
        for j in range(5):
            x = x0 + (x1 - x0) * i / 6
            y = y0 + (y1 - y0) * j / 4
            want = piece.top_fn(x, y) if piece.top_fn else piece.top
            hit, normal, _, _ = bvh.ray_cast(Vector((x, y, want + 3.0)), Vector((0, 0, -1)), 10.0)
            if hit is None:
                bad += 1
                errors.append("%s: top probe found nothing at (%.2f, %.2f)" % (piece.name, x, y))
                continue
            if abs(hit.z - want) > MM:
                bad += 1
                errors.append("%s: top probe at (%.2f, %.2f) hit z %.4f, expected %.4f" % (
                    piece.name, x, y, hit.z, want))
            min_nz = math.cos(math.radians(piece.slope)) - 1e-4
            if normal.z < min_nz:
                bad += 1
                errors.append("%s: top probe at (%.2f, %.2f) found a %.1f deg face" % (
                    piece.name, x, y, math.degrees(math.acos(max(-1.0, min(1.0, normal.z))))))
            if bad > 3:
                bm.free()
                return
    bm.free()


def check_kit(kits):
    errors, warnings = [], []
    seen = {}
    for kit in kits:
        for piece in kit.pieces:
            if piece.name in seen:
                errors.append("%s: name used by both %s and %s" % (piece.name, seen[piece.name], kit.family))
            seen[piece.name] = kit.family
            check_piece(piece, errors, warnings)
    for w in warnings:
        log("WARNING", w)
    if errors:
        raise CheckError("%d check(s) failed:\n  %s" % (len(errors), "\n  ".join(errors)))
    log("checks passed: %d pieces, %d warnings" % (len(seen), len(warnings)))


# ---------------------------------------------------------------------------------------------------------------------
# Export and manifest
# ---------------------------------------------------------------------------------------------------------------------

def export_fbx(kit):
    os.makedirs(FBX_DIR, exist_ok=True)
    obs = kit.objects()
    # Objects linked since the last update are not in the view layer yet: selecting them would silently do nothing
    # and the first family would export an empty file.
    bpy.context.view_layer.update()
    for o in bpy.context.view_layer.objects:
        o.select_set(o in obs)
    bpy.context.view_layer.objects.active = obs[0]
    selected = [o for o in bpy.context.view_layer.objects if o.select_get()]
    if len(selected) != len(obs):
        raise CheckError("%s: %d of %d objects selected for export" % (kit.family, len(selected), len(obs)))
    bpy.ops.export_scene.fbx(
        filepath=kit.fbx_path,
        use_selection=True,
        object_types={'MESH'},
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        use_space_transform=True,
        bake_space_transform=False,
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        use_tspace=False,
        use_custom_props=False,
        bake_anim=False,
        path_mode='AUTO',
        embed_textures=False,
        batch_mode='OFF',
    )
    log("exported", kit.fbx_path, "%.1f KB, %d objects" % (os.path.getsize(kit.fbx_path) / 1024, len(obs)))


def export_textures(kit):
    """Writes the images the kit's textured roles use (kit_palette.TEXTURES) beside its FBX, with the FBX."""
    roles = {r for p in kit.pieces for part in p.parts for r in part.materials}
    for role in sorted(roles & set(pal.TEXTURES)):
        name = os.path.splitext(pal.TEXTURES[role])[0]
        image = bpy.data.images.get(name)
        if image is None:
            raise CheckError("%s: no image %s for the %s role" % (kit.family, name, role))
        path = os.path.join(FBX_DIR, pal.TEXTURES[role])
        image.filepath_raw = path
        image.file_format = 'PNG'
        image.save()
        log("texture", path, "%d x %d" % tuple(image.size))


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def collider_json(piece, c):
    f = frame(piece)
    base = host_abs(piece, c.host)
    center = f @ to_unity(c.center) - base
    tilt = Quaternion((0.0, 0.0, 1.0), math.radians(c.tilt))
    rot = f @ tilt
    out = {"host": c.host, "type": c.kind, "center": v3(center), "size": v3((0, 0, 0)),
           "rotation": q4(Quaternion()), "radius": r5(c.radius), "height": r5(c.height), "direction": 0,
           "isTrigger": c.trigger, "walkSurface": c.walk}
    if c.kind == "Box":
        size = to_unity(c.size)
        if abs(c.tilt) < 1e-9:
            # Only quarter turns of the frame: the box stays axis-aligned with its extents swapped.
            m = f.to_matrix()
            size = Vector([abs(x) for x in (m @ size)])
        else:
            out["rotation"] = q4(rot)
        out["size"] = v3(size)
    elif c.kind == "Capsule":
        axis = Vector((0, 0, 0))
        axis[AXIS_INDEX[c.axis]] = 1.0
        axis = f.to_matrix() @ axis
        out["direction"] = max(range(3), key=lambda i: abs(axis[i]))
    return out


def piece_json(piece, kit):
    f = frame(piece)
    lo, hi = bounds([f @ to_unity(p) for p in piece_vertices(piece)])
    hosts = []
    anchors = (piece.variant or {}).get("anchors", {})
    for h in piece.hosts:
        parent_abs = host_abs(piece, h.parent) if any(x.name == h.parent for x in piece.hosts) else \
            f @ to_unity(anchors.get(h.parent, (0.0, 0.0, 0.0)))
        axis = f @ to_unity(h.axis) if any(h.axis) else Vector()
        hosts.append({"name": h.name, "parent": h.parent, "position": v3(host_abs(piece, h.name) - parent_abs),
                      "layer": h.layer or piece.layer, "kinematicBody": h.kinematic, "motion": h.motion,
                      "axis": v3(axis), "range": r5(h.range), "period": r5(h.period),
                      "knockSpeed": r5(h.knock[0] if h.knock else 0.0), "knockHeight": r5(h.knock[1] if h.knock else 0.0),
                      "kills": h.kills, "reach": r5(h.reach), "dwell": r5(h.dwell), "outShare": r5(h.share),
                      "mouth": r5(h.mouth), "sink": r5(h.sink)})
    parts = []
    for part in piece.parts:
        mlo, mhi = mesh_bounds(part.obj)
        tint = part.materials.index("Tint") if "Tint" in part.materials else -1
        parts.append({"name": part.name, "host": part.host, "mesh": part.obj.name,
                      "position": v3(-host_abs(piece, part.host)), "rotation": q4(f @ RX90),
                      "materials": [pal.material_name(m) for m in part.materials], "tintSubmesh": tint,
                      "meshBoundsMin": v3(mlo), "meshBoundsMax": v3(mhi), "tris": tris(part.obj),
                      "castShadows": part.shadows, "cameraSide": part.camera_side})
    kind = "Variant" if piece.variant else "Kit"
    prefab = ("%s/%s.prefab" % (UNITY_VARIANTS, piece.name) if piece.variant else
              "%s/Parkur_%s/%s.prefab" % (UNITY_KIT_PREFABS, kit.family, piece.name))
    variant = piece.variant or {}
    return {
        "name": piece.name, "prefab": prefab, "kind": kind, "role": piece.role, "layer": piece.layer,
        "pivot": piece.pivot, "sizeCells": v3(piece.cells), "boundsMin": v3(lo), "boundsMax": v3(hi),
        "hasTop": piece.top is not None, "topY": r5(piece.top if piece.top is not None else 0.0),
        "slopeDeg": r5(piece.slope), "walkable": piece.walkable, "cauldronSafe": piece.cauldron_safe,
        "stepUp": piece.step_up, "blocksLane": piece.blocks_lane, "depthSymmetric": piece.depth_symmetric,
        "chainable": piece.chainable, "staticBatching": piece.static, "castShadows": piece.shadows,
        "tris": sum(tris(p.obj) for p in piece.parts), "notes": piece.notes,
        "hosts": hosts, "parts": parts, "colliders": [collider_json(piece, c) for c in piece.colliders],
        "variant": {
            "basePrefab": variant.get("base", ""),
            "frameYaw": r5(piece.frame_yaw),
            "expect": variant.get("expect", []),
            "deactivate": variant.get("deactivate", []),
            "repoint": [{"component": r[0], "field": r[1], "targets": r[2]} for r in variant.get("repoint", [])],
            "overrideRootBox": "rootBox" in variant,
            "rootBoxCenter": v3(variant["rootBox"][0] if "rootBox" in variant else (0, 0, 0)),
            "rootBoxSize": v3(variant["rootBox"][1] if "rootBox" in variant else (0, 0, 0)),
        },
    }


def write_manifest(kit):
    data = {"schema": 1, "family": kit.family, "fbx": "%s/Kit_%s.fbx" % (UNITY_ART, kit.family),
            "fbxSha1": sha1(kit.fbx_path), "pieces": [piece_json(p, kit) for p in kit.pieces]}
    with open(kit.manifest_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=True)
        fh.write("\n")
    log("manifest", kit.manifest_path, "%d pieces" % len(kit.pieces))


def write_root_manifest(kits):
    data = {
        "schema": 1,
        "generator": "Art/LevelKit/build_levelkit.py",
        "grid": {"cell": GRID, "laneDepth": DEPTH},
        "character": CHARACTER,
        "cauldron": CAULDRON,
        "materialFolder": UNITY_MATERIALS,
        "palette": [{"role": n, "material": pal.material_name(n), "hex": hx, "smoothness": s, "emissionHex": ehx,
                     "emission": e, "texture": "%s/%s" % (UNITY_ART, pal.TEXTURES[n]) if n in pal.TEXTURES else "",
                     "inAtlas": n in pal.ATLAS}
                    for n, hx, s, ehx, e in pal.ROLES],
        "atlas": {"material": pal.material_name(pal.ATLAS_ROLE),
                  "texture": "%s/%s" % (UNITY_ART, pal.TEXTURES[pal.ATLAS_ROLE]), "roles": list(pal.ATLAS)},
        "seats": [{"seat": n, "hex": hx} for n, hx in pal.SEATS],
        "families": [{"name": fam, "fbx": "%s/Kit_%s.fbx" % (UNITY_ART, fam),
                      "manifest": "%s/Kit_%s.json" % (UNITY_ART, fam)} for _, fam in FAMILIES],
    }
    path = os.path.join(FBX_DIR, "LevelKit.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=True)
        fh.write("\n")
    log("manifest", path)
