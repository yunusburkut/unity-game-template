# The smallest complete example of the art-pipeline chain, generic and runnable: it builds one toon prop (a banded
# barrel), checks it, exports it with the unity-export skill's FBX preset and writes the JSON manifest that
# PropBuilder.cs.txt turns into materials and a prefab. Copy it to Tools/Blender/<thing>.py and replace build().
#
# blender --background --factory-startup --python-exit-code 1 --python Tools/Blender/toon_prop.py -- <unity project> \
#     [check.png] [--export] [--style Tools/Blender/Style/style_a.json]
#
# Output: <project>/Assets/__GAME__/Game/Art/Models/SM_Barrel.fbx and SM_Barrel.json, inside the folder
# OutlineNormalsPostprocessor bakes, so the outline stays closed at the hard rim edges. With a style bible they wait
# for --export (after the review and the user's yes); every run saves Tools/Blender/checks/SM_Barrel.blend before the
# checks, so a failed run leaves the .blend style_gate.py names the cuts on. --style runs a decision-page reading
# (style_a.json, style_b.json): it saves SM_Barrel_<stem>.blend and never exports. Without --python-exit-code 1 a
# Python error exits 0 and the run looks green.
#
# Axes: authored in Blender metres, +Z up, the front toward -Y (Blender's Front view), the pivot at the base centre.
# With this preset and the importer's bakeAxisConversion the mesh keeps Blender X and negates Z; the prefab stands it
# up with a child turned Euler(90, 180, 0), so a Blender point (x, y, z) lands at Unity (-x, z, -y) in the prefab and
# the front faces transform.forward (+Z). to_unity() is that mapping, and every number in the manifest is already in
# Unity prefab space.

import json
import math
import os
import sys

import bmesh
import bpy

# role -> (sRGB colour, smoothness). The builder makes one __GAME__/Toon material per role and outline choice
# (M_<Role>, M_<Role>_Outline); a colour change happens here and nowhere else. Every script that uses a role gives it
# the same values (keep the shared palette in one module when there are several), or the rebuild fails on that role.
# A game with a style bible (genre-defaults references/style-bible.md) takes them from Tools/Blender/Style/style.json
# instead, in main(): its palette roles, its accents as roles Accent1..N, its class's triangle band and its outline.
PALETTE = {
    "Wood": ((0.78, 0.52, 0.30), 0.15),
    "WoodDark": ((0.55, 0.34, 0.20), 0.10),
    "Metal": ((0.62, 0.66, 0.74), 0.55),
}
TRIANGLE_BAND = (0, 600)    # a hand-sized prop on a phone; set it from the brief's screen size
ACCENT_SMOOTHNESS = 0.3     # style.json accents carry only a colour; a painted trim's gloss
NAME = "SM_Barrel"
STYLE_CLASS = "prop"        # the style bible's triangles key; the gate reads it off the root object
OUTLINE = True              # a prop the player reads; level pieces say False (and get M_<Role> without it)
ROLES = {"end": "WoodDark", "body": "Wood", "hoop": "Metal"}    # build()'s parts -> PALETTE keys
SEGMENTS = 16               # round parts' segments, the most main() starts from; with a style bible, from its asset_px
NARROWEST = 0.20            # build()'s narrowest ring (the heads' rim): the curve rule's radius for SEGMENTS
PX_PER_M = None             # the game camera's pixels a metre with a style bible (asset_px / asset_m)
BEVEL = 0.025               # the chimes' bevel; with a style bible, its bevel_m
HOOP_STEP = 0.025           # how far a hoop stands out; with a style bible, at least 2 px at game size
STYLE_PATH = None           # the style.json in use, which the over-budget message's gate run takes


class CheckError(Exception):
    pass


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def material(role):
    """A Blender material named after its palette role; Unity reads only the name (and the builder the role)."""
    name = "M_" + role
    if role not in PALETTE:
        raise CheckError("%s: role %s is not in the palette %s" % (NAME, role, sorted(PALETTE)))
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    rgb, smooth = PALETTE[role]
    linear = (*(srgb_to_linear(c) for c in rgb), 1.0)
    mat.diffuse_color = linear      # the check render shows the palette
    # the FBX carries the Principled Base Color: a flat or lit game's material reads it, and the style gate checks it
    next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = linear
    mat.roughness = 1.0 - smooth
    return mat


def lathe(bm, profile, segments):
    """Turns a (z, r) profile round the Z axis into one closed surface: a ring of quads per profile edge (returned in
    profile order) and an n-gon cap on each end; returns (bands, caps)."""
    angles = [2.0 * math.pi * i / segments for i in range(segments)]
    rings = [[bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in angles] for z, r in profile]
    bands = [[bm.faces.new((lo[i - 1], lo[i], hi[i], hi[i - 1])) for i in range(segments)]
             for lo, hi in zip(rings, rings[1:])]
    caps = [bm.faces.new(rings[0]), bm.faces.new(rings[-1])]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])    # closed, so outward is well defined
    return bands, caps


def build(segments):
    """The prop itself: a staved barrel, one closed surface turned from a profile (nothing buried inside it, the
    style gate's hidden rule). Every face gets a palette role through its material slot. This is the wiring example:
    a game's asset replaces build() with its own design from the brief (its proportions, the STYLE.md motif), never
    ships this barrel as it is."""
    roles = list(dict.fromkeys(ROLES.values()))     # one slot per role, in first-use order
    mesh = bpy.data.meshes.new(NAME)
    obj = bpy.data.objects.new(NAME, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj["style_class"] = STYLE_CLASS
    obj["outline"] = OUTLINE        # the contact sheet draws the ink line only where the game does
    for role in roles:
        mesh.materials.append(material(role))

    height, bilge, stave, recess = 0.80, 0.065, 0.03, 0.035
    chime = NARROWEST + stave
    bevel = min(BEVEL, stave / 2.0)     # a wider bible bevel would eat the stave end the head sits under

    def radius(z):      # the bilge: the staves bow out to their widest at mid height
        return chime + bilge * (1.0 - (2.0 * z / height - 1.0) ** 2)

    # the bulge's segments up the side: as many as the curve rule lets show (its chord error stays 0.25 px or more
    # at game size), the gate's curve rule fails finer
    side = max(2, int(2.0 * math.sqrt(bilge * PX_PER_M))) if PX_PER_M else 4
    hoops = [(0.13, 0.19), (0.61, 0.67)]
    # (z, r, the role of the edge up to the next point): the bottom head's rim down its recess, the stave end the
    # barrel stands on, the chime's bevel, the bowed side with each hoop stepping out and back at its own height, then
    # the same up top
    profile = [(recess, NARROWEST, "body"), (0.0, NARROWEST, "body"), (0.0, chime - bevel, "body")]
    staves = {bevel + (height - 2.0 * bevel) * i / side for i in range(side + 1)}
    for z in sorted(staves | {z for h in hoops for z in h}):
        hoop = next((h for h in hoops if h[0] <= z <= h[1]), None)
        if hoop is None:
            profile.append((z, radius(z), "body"))
        elif z == hoop[0]:
            profile += [(z, radius(z), "hoop"), (z, radius(z) + HOOP_STEP, "hoop")]
        elif z == hoop[1]:
            profile += [(z, radius(z) + HOOP_STEP, "hoop"), (z, radius(z), "body")]
    profile += [(height, chime - bevel, "body"), (height, NARROWEST, "body"), (height - recess, NARROWEST, None)]

    bm = bmesh.new()
    bands, caps = lathe(bm, [(z, r) for z, r, _ in profile], segments)
    for faces, (_, _, part) in zip(bands, profile):
        for f in faces:
            f.material_index = roles.index(ROLES[part])
    for f in caps:      # the heads are the dark end grain
        f.material_index = roles.index(ROLES["end"])
    # the game's STYLE.md Motif goes here: a part of this surface (a band, a stencil panel) in its role, never a
    # separate piece buried in the body
    bm.to_mesh(mesh)
    bm.free()

    # the bowed side shades smooth; heads, chime bevels and hoop rims keep their own flat toon band
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.set_sharp_from_angle(angle=math.radians(30.0))
    return obj


def triangles_of(obj):
    """The triangles Unity gets: the evaluated mesh, modifiers applied as the export applies them."""
    mesh = evaluated_mesh(obj)
    mesh.calc_loop_triangles()
    count = len(mesh.loop_triangles)
    obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    return count


def to_unity(p):
    """Blender (x, y, z) -> Unity prefab space (-x, z, -y), as the {x, y, z} object JsonUtility reads into a Vector3."""
    return {"x": round(-p[0], 5) + 0.0, "y": round(p[2], 5), "z": round(-p[1], 5) + 0.0}


def to_unity_size(s):
    """A Blender extent (x, y, z) -> Unity prefab space (x, z, y): sizes stay positive, the turn only reorders them."""
    return {"x": round(s[0], 5), "y": round(s[2], 5), "z": round(s[1], 5)}


def color(rgb):
    """An sRGB palette colour as the {r, g, b, a} object JsonUtility reads into a Color."""
    return {"r": rgb[0], "g": rgb[1], "b": rgb[2], "a": 1.0}


def evaluated_mesh(obj):
    return obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()


def check(obj, blend):
    """Every rule the asset must meet; a broken rule fails the run instead of exporting. blend: the .blend main()
    saved of this build, which the over-budget message sends to the style gate."""
    problems = []
    if obj.children:
        # PropBuilder makes one prefab from one mesh, and the export takes this object alone
        problems.append("parts %s under the root: join them into this mesh" % ", ".join(c.name for c in obj.children))
    if tuple(obj.location) != (0.0, 0.0, 0.0) or tuple(obj.rotation_euler) != (0.0, 0.0, 0.0) \
            or tuple(obj.scale) != (1.0, 1.0, 1.0):
        problems.append("transform is not identity: the vertices must already be in piece space")
    mesh = evaluated_mesh(obj)
    mesh.calc_loop_triangles()
    triangles = len(mesh.loop_triangles)
    if triangles > TRIANGLE_BAND[1]:
        problems.append("%d triangles, budget %d" % (triangles, TRIANGLE_BAND[1]) + (
            ": run style_gate.py on %s with --style %s, whose curve, waste and detail lines say what to cut"
            % (blend, STYLE_PATH) if STYLE_PATH else ""))
    elif triangles < TRIANGLE_BAND[0]:
        problems.append("%d triangles, under the %s band's %d: add the detail the references show at game size "
                        "(bevels, rims, planks), never subdivide flat faces" % (triangles, STYLE_CLASS, TRIANGLE_BAND[0]))
    used = sorted({p.material_index for p in mesh.polygons})
    if used != list(range(len(obj.data.materials))):
        problems.append("material slots %s, faces use %s: an unused slot becomes an empty submesh" %
                        (list(range(len(obj.data.materials))), used))
    for mat in obj.data.materials:
        if mat is None or not mat.name.startswith("M_") or mat.name[2:] not in PALETTE:
            problems.append("material %s is not a palette role" % (mat.name if mat else None))
    zs = [v.co.z for v in mesh.vertices]
    if abs(min(zs)) > 0.0005:
        problems.append("lowest point at z %.4f: the pivot must be the base centre" % min(zs))
    obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    if problems:
        raise CheckError(NAME + ": " + "; ".join(problems))
    return triangles


def export(obj, path):
    """The unity-export skill's preset, unchanged: copy it, never invent another."""
    bpy.context.view_layer.update()
    for other in bpy.context.view_layer.objects:
        other.select_set(other == obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True,
        object_types={'MESH'},
        apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', global_scale=1.0,
        axis_forward='-Z', axis_up='Y', bake_space_transform=False,
        use_mesh_modifiers=True, mesh_smooth_type='FACE',
        add_leaf_bones=False, use_armature_deform_only=True,
        bake_anim=False,
        path_mode='RELATIVE', embed_textures=False,
    )


def write_manifest(obj, triangles, path):
    """What Unity needs beyond the mesh, in Unity prefab space: JsonUtility field names, no dictionaries, no nulls."""
    # the evaluated mesh, the one check() measures and the export writes (use_mesh_modifiers), so a Bevel, Mirror or
    # Array modifier in a copied script moves the collider with it
    mesh = evaluated_mesh(obj)
    lo = [min(v.co[i] for v in mesh.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in mesh.vertices) for i in range(3)]
    obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    centre = [(a + b) / 2.0 for a, b in zip(lo, hi)]
    size = [b - a for a, b in zip(lo, hi)]
    manifest = {
        "mesh": NAME,
        "triangles": triangles,
        "roles": [m.name[2:] for m in obj.data.materials],      # submesh order
        "colors": [color(PALETTE[m.name[2:]][0]) for m in obj.data.materials],
        "smoothness": [PALETTE[m.name[2:]][1] for m in obj.data.materials],
        "outline": OUTLINE,
        "colliderCenter": to_unity(centre),
        "colliderSize": to_unity_size(size),
    }
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def check_render(obj, path):
    """A quick Workbench render for judging the shape and palette without Unity (Tools/Blender/checks/, gitignored)."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.color_type = 'MATERIAL'
    scene.render.resolution_x = scene.render.resolution_y = 768
    cam = bpy.data.objects.new("CheckCam", bpy.data.cameras.new("CheckCam"))
    scene.collection.objects.link(cam)
    cam.location = (1.6, -2.4, 1.5)
    target = obj.matrix_world.translation.copy()
    target.z += obj.dimensions.z / 2.0
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def use_style_bible(project, path=None):
    """The style bible's palette, accents, triangle band, outline, camera scale and bevel, when the game has one
    (path: another file, the decision page's two readings style_a.json and style_b.json, which must exist)."""
    global TRIANGLE_BAND, OUTLINE, SEGMENTS, PX_PER_M, BEVEL, HOOP_STEP, STYLE_PATH
    if path and not os.path.isfile(path):
        # a reading's build must never fall back to exporting the game's own FBX
        raise CheckError("--style %s is no file" % path)
    path = path or os.path.join(project, "Tools", "Blender", "Style", "style.json")
    if not os.path.isfile(path):
        return False
    with open(path, encoding="utf-8") as f:
        style = json.load(f)
    STYLE_PATH = path
    bands = style.get("triangles") or {}
    if STYLE_CLASS not in bands:
        raise CheckError("%s: STYLE_CLASS %r has no triangles band in %s (it has %s)"
                         % (NAME, STYLE_CLASS, path, ", ".join(sorted(bands)) or "none"))
    PALETTE.clear()
    PALETTE.update({r: (tuple(v["srgb"]), v["smoothness"]) for r, v in style["palette"].items()})
    PALETTE.update({"Accent%d" % (i + 1): (tuple(c), ACCENT_SMOOTHNESS) for i, c in enumerate(style.get("accents", []))})
    TRIANGLE_BAND = tuple(bands[STYLE_CLASS])
    # the bible's outline is the game's: none there, none on the prop (PropBuilder then makes M_<Role> without it)
    OUTLINE = OUTLINE and bool(style.get("outline", True))
    BEVEL = style.get("bevel_m", BEVEL)
    # the bible's roles when it renames them: the body takes the first palette role, the end grain the second, the
    # hoops a role named metal, else the shiniest one after the body (a palette role, not an accent: a band of
    # accent round a barrel takes more of its seen surface than accent_max_share allows)
    if not set(ROLES.values()) <= set(PALETTE):
        names = list(style["palette"])
        shiny = max(names[1:] or names, key=lambda r: style["palette"][r]["smoothness"])
        ROLES.update(body=names[0], end=names[min(1, len(names) - 1)],
                     hoop=next((r for r in names if "metal" in r.lower()), shiny))
    if len(set(ROLES.values())) < len(ROLES):
        # one role on two parts draws them one colour: the hoops vanish into the body, and every number still passes
        raise CheckError("%s: %s's palette has %d role(s) (%s); body, end grain and hoops need %d distinct ones: add "
                         "the swatches the references show (a dark wood, a metal)"
                         % (NAME, path, len(style["palette"]), ", ".join(style["palette"]), len(ROLES)))
    cam = style.get("camera") or {}
    if cam.get("asset_px"):
        PX_PER_M = cam["asset_px"] / (cam.get("asset_m") or 1.0)
        # the curve rule's count round the narrowest ring (finer is waste the gate fails); main() drops segments from
        # there until the triangles fit the band
        SEGMENTS = max(8, math.ceil(math.pi / math.acos(1 - 0.25 / (NARROWEST * PX_PER_M))) // 2 * 2)
        # a hoop 2 px proud reads as a rim at game size, not a painted line
        HOOP_STEP = max(style.get("detail_floor_m") or 0.0, 2.0 / PX_PER_M)
    return True


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    export_now = "--export" in argv
    argv = [a for a in argv if a != "--export"]
    style = None
    if "--style" in argv:
        at = argv.index("--style")
        style = argv[at + 1] if at + 1 < len(argv) else ""
        del argv[at:at + 2]
    if not argv or style == "":
        raise SystemExit("usage: blender ... --python toon_prop.py -- <unity project> [check.png] [--export] "
                         "[--style <style.json>]")
    models = os.path.join(argv[0], "Assets", "__GAME__", "Game", "Art", "Models")
    os.makedirs(models, exist_ok=True)
    bible = use_style_bible(argv[0], style)
    # with a style bible the FBX waits for the review: the .blend goes to the gate and the sheet, and --export (after
    # the user's yes) writes the FBX and manifest Unity imports; a decision-page reading (--style) never exports
    reading = os.path.splitext(os.path.basename(style or ""))[0]
    reading = "" if reading == "style" else reading     # --style naming the game's own style.json is no reading
    if export_now and reading:
        print("[toon_prop] --export ignored: --style names the decision-page reading %s" % reading)
    export_now = not bible or (export_now and not reading)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0

    # build, count, and drop segments until the triangles fit the band's top, so a rewritten build() needs no
    # per-segment cost; 8 is the floor (a coarser ring reads as a polygon), where check() reports what is over. Two at
    # a time: an even ring is symmetric both ways, so the bounds (the collider) stay centred on the pivot
    segments = SEGMENTS
    obj = build(segments)
    while triangles_of(obj) > TRIANGLE_BAND[1] and segments > 8:
        mesh = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(mesh)
        segments -= 2
        obj = build(segments)
    # the scene, saved before the checks for the style bible's style_gate and contact_sheet, so a failed run's gate
    # judges this build (checks/ is gitignored: the script is the source); one .blend per reading, so reading A's sheet
    # never draws reading B's build
    checks = os.path.join(argv[0], "Tools", "Blender", "checks")
    os.makedirs(checks, exist_ok=True)
    blend = os.path.join(checks, NAME + ("_" + reading if reading else "") + ".blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    triangles = check(obj, blend)
    if export_now:
        export(obj, os.path.join(models, NAME + ".fbx"))
        write_manifest(obj, triangles, os.path.join(models, NAME + ".json"))
    print("[toon_prop] %s: %d triangles, %.2f x %.2f x %.2f m" % (NAME, triangles, *obj.dimensions))
    if len(argv) > 1:
        check_render(obj, argv[1])


main()
