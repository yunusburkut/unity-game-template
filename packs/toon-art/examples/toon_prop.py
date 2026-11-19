# The smallest complete example of the art-pipeline chain, generic and runnable: it builds one toon prop (a banded
# barrel), checks it, exports it with the unity-export skill's FBX preset and writes the JSON manifest that
# PropBuilder.cs.txt turns into materials and a prefab. Copy it to Tools/Blender/<thing>.py and replace build().
#
# blender --background --factory-startup --python-exit-code 1 --python Tools/Blender/toon_prop.py -- <unity project> \
#     [check.png] [--export] [--style Tools/Blender/Style/style_a.json] [--game <Name>]
#
# Output: <project>/Assets/<Game>/Game/Art/Models/SM_Barrel.fbx and SM_Barrel.json, inside the folder
# OutlineNormalsPostprocessor bakes, so the outline stays closed at the hard rim edges. <Game> is the one folder under
# Assets that holds Game/Art (the toon-art pack's), or --game <Name> when none or several do. With a style bible they
# wait for --export (after the review and the user's yes), which refuses the unchanged starter barrel; every run
# saves Tools/Blender/checks/SM_Barrel.blend before the checks, so a failed run leaves the .blend style_gate.py names
# the cuts on. --style runs a decision-page reading (style_a.json, style_b.json): it saves SM_Barrel_<stem>.blend and
# never exports. Without --python-exit-code 1 a Python error exits 0 and the run looks green.
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
# Toon smoothness: 0 is matte (wood, stone, cloth: no glossy spot, no rim), about 0.3 paint, 0.5-0.6 metal.
PALETTE = {
    "Wood": ((0.78, 0.52, 0.30), 0.0),
    "WoodDark": ((0.55, 0.34, 0.20), 0.0),
    "Metal": ((0.62, 0.66, 0.74), 0.55),
}
TRIANGLE_BAND = (0, 600)    # a hand-sized prop on a phone; set it from the brief's screen size
ACCENT_SMOOTHNESS = 0.3     # style.json accents carry only a colour; a painted trim's gloss
NAME = "SM_Barrel"
STYLE_CLASS = "prop"        # the style bible's triangles key; the gate reads it off the root object
OUTLINE = True              # a prop the player reads; level pieces say False (and get M_<Role> without it)
# build()'s parts -> PALETTE keys; a rewritten build names its roles from style.json's palette
ROLES = {"end": "WoodDark", "body": "Wood", "hoop": "Metal"}
SEGMENTS = 16               # round parts' segments, the most main() starts from; with a style bible, from its asset_px
NARROWEST = 0.175           # build()'s narrowest ring, the heads' rim
WIDEST = 0.29               # build()'s widest silhouette ring, the bilge: the chord rule's radius for SEGMENTS
PX_PER_M = None             # the game camera's pixels a metre with a style bible (asset_px / asset_m)
ASSET_M = 1.0               # the style bible's camera.asset_m, the typical asset: a smaller one's floor scales by it
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

    # heads well inside the bilge: a deep bow keeps the front and side silhouettes off a can's box (the sheet's
    # silhouette_fill about 0.90, where a primitive fills 0.93 or more)
    height, stave, recess = 0.80, 0.03, 0.035
    chime = NARROWEST + stave
    bilge = WIDEST - chime
    # 2 px at the game camera, in metres: profile detail under it (the chime bevel, the head's recess, a ring beside a
    # hoop) costs triangles nobody sees, so it is shed and the round keeps its segments; no bible, nothing is shed
    seen = 2.0 / PX_PER_M if PX_PER_M else 0.0
    bevel = min(BEVEL, stave / 2.0)     # a wider bible bevel would eat the stave end the head sits under
    bevel = bevel if bevel >= seen else 0.0

    def radius(z):      # the bilge: the staves bow out to their widest at mid height
        return chime + bilge * (1.0 - (2.0 * z / height - 1.0) ** 2)

    # the bulge's segments up the side: a parabola cut in n has bilge / n^2 of chord error, aimed at 0.5 px at game
    # size like SEGMENTS (the gate's curve rule fails only segments under about 0.06 px of their own)
    side = max(2, math.ceil(math.sqrt(2.0 * bilge * PX_PER_M))) if PX_PER_M else 4
    hoops = [(0.13, 0.19), (0.61, 0.67)]
    # (z, r, the role of the edge up to the next point): the bottom, one flat cap at z 0 (a prop standing on the
    # floor never shows it), the chime's bevel, the bowed side with each hoop stepping out and back at its own height,
    # the top chime's bevel, then the stave end and the top head's rim down its recess
    profile = [(0.0, chime - bevel, "body")] if bevel else []
    staves = {bevel + (height - 2.0 * bevel) * i / side for i in range(side + 1)}
    # a side ring under 2 px from a hoop's edge is a sliver: the hoop's own ring cuts the bow there
    staves = {z for z in staves if not any(h[0] - seen < z < h[1] + seen for h in hoops)}
    for z in sorted(staves | {z for h in hoops for z in h}):
        hoop = next((h for h in hoops if h[0] <= z <= h[1]), None)
        if hoop is None:
            profile.append((z, radius(z), "body"))
        elif z == hoop[0]:
            profile += [(z, radius(z), "hoop"), (z, radius(z) + HOOP_STEP, "hoop")]
        elif z == hoop[1]:
            profile += [(z, radius(z) + HOOP_STEP, "hoop"), (z, radius(z), "body")]
    if bevel:
        profile.append((height, chime - bevel, "body"))
    if recess >= seen:
        profile += [(height, NARROWEST, "body"), (height - recess, NARROWEST, None)]

    bm = bmesh.new()
    bands, caps = lathe(bm, [(z, r) for z, r, _ in profile], segments)
    # surface breakup at no triangle cost: every other stave (a face column) in the end grain's darker wood, so the
    # game tile shows planks, not a painted can; segments is always even, so the pattern closes round the back
    for faces, (_, _, part) in zip(bands, profile):
        for i, f in enumerate(faces):
            f.material_index = roles.index(ROLES["end" if part == "body" and i % 2 else part])
    for f in caps:      # the heads are the dark end grain
        f.material_index = roles.index(ROLES["end"])
    # the game's STYLE.md Motif goes here: a part of this surface (a band, a stencil panel) in its role, never a
    # separate piece buried in the body, its faces tagged in a boolean FACE attribute "motif" (after to_mesh:
    # mesh.attributes.new("motif", 'BOOLEAN', 'FACE')), which the contact sheet measures and FBX ignores. This
    # generic barrel has none, so its sheet warns
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
            ": run style_gate.py on %s with --style %s: its STYLE FACTS line and failures name what to cut, "
            "or it says the design has more parts than the band affords: drop parts in build() or take the "
            "band back to the decision page" % (blend, STYLE_PATH) if STYLE_PATH else ""))
    else:
        # the style gate's rule: an asset smaller than the typical one (asset_m) is held to a proportionally lower
        # floor; the band's top is a ceiling and stays
        size = round(max(obj.dimensions), 4)     # to 0.1 mm, as the gate: float noise must not lift the ceil
        floor = math.ceil(TRIANGLE_BAND[0] * min(1.0, size / ASSET_M))
        if triangles < floor:
            problems.append("%d triangles, under the %s band's %d%s: add the detail the references show at game size "
                            "(bevels, rims, planks), never subdivide flat faces" % (
                                triangles, STYLE_CLASS, floor,
                                " (the band's %d scaled by the asset's %.2f m against asset_m %g)"
                                % (TRIANGLE_BAND[0], size, ASSET_M) if floor < TRIANGLE_BAND[0] else ""))
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


def models_folder(project, game=None):
    """<project>/Assets/<Game>/Game/Art/Models, the folder OutlineNormalsPostprocessor bakes. <Game> is --game, else
    the one folder under Assets that holds Game/Art; none or several stops the run before it writes anywhere else."""
    assets = os.path.join(project, "Assets")
    names = sorted(os.listdir(assets)) if os.path.isdir(assets) else []
    found = [d for d in names if os.path.isdir(os.path.join(assets, d, "Game", "Art"))]
    if game is None and len(found) != 1:
        raise CheckError("%s: %s under %s holds Game/Art, so the game's folder is not known: pass --game <Name>"
                         % (NAME, "more than one folder (%s)" % ", ".join(found) if found else "no folder", assets))
    game = game or found[0]
    if not os.path.isdir(os.path.join(assets, game)):
        raise CheckError("%s: --game %s is no folder under %s (Game/Art is in: %s)"
                         % (NAME, game, assets, ", ".join(found) or "none"))
    return os.path.join(assets, game, "Game", "Art", "Models")


def use_style_bible(project, path=None):
    """The style bible's palette, accents, triangle band, outline, camera scale and bevel, when the game has one
    (path: another file, the decision page's two readings style_a.json and style_b.json, which must exist)."""
    global TRIANGLE_BAND, OUTLINE, SEGMENTS, PX_PER_M, ASSET_M, BEVEL, HOOP_STEP, STYLE_PATH
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

    def role(key, v):       # a palette role or an accent -> (sRGB, smoothness): style_gate.py check_colours' rule
        if key.startswith("palette.") and not isinstance(v, dict):
            raise CheckError('%s: %s is %r: write {"srgb": [r, g, b], "smoothness": 0-1}' % (path, key[:-5], v))
        c = v.get("srgb") if isinstance(v, dict) else v
        if not (isinstance(c, list) and len(c) == 3 and all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in c)):
            raise CheckError("%s: %s is %r: write 3 numbers 0-1 (style_metrics.json's toon_albedo_srgb or srgb), "
                             "not a hex or 0-255" % (path, key, c))
        return tuple(c), v.get("smoothness", ACCENT_SMOOTHNESS) if isinstance(v, dict) else ACCENT_SMOOTHNESS

    PALETTE.clear()
    PALETTE.update({r: role("palette.%s.srgb" % r, v) for r, v in style["palette"].items()})
    PALETTE.update({"Accent%d" % (i + 1): role("accents[%d]" % i, c) for i, c in enumerate(style.get("accents") or [])})
    TRIANGLE_BAND = tuple(bands[STYLE_CLASS])
    # the bible's outline is the game's: none there, none on the prop (PropBuilder then makes M_<Role> without it)
    OUTLINE = OUTLINE and bool(style.get("outline", True))
    BEVEL = style.get("bevel_m", BEVEL)
    if set(ROLES) == {"end", "body", "hoop"}:
        # the barrel's parts, when the bible renames its roles: the body takes the first palette role, the end grain
        # the second, the hoops a role named metal, else the shiniest one after the body (a palette role, not an
        # accent: a band of accent round a barrel takes more of its seen surface than accent_max_share allows)
        if not set(ROLES.values()) <= set(PALETTE):
            names = list(style["palette"])
            shiny = max(names[1:] or names, key=lambda r: PALETTE[r][1])
            ROLES.update(body=names[0], end=names[min(1, len(names) - 1)],
                         hoop=next((r for r in names if "metal" in r.lower()), shiny))
        if len(set(ROLES.values())) < len(ROLES):
            # one role on two parts draws them one colour: the hoops vanish into the body, and every number passes
            raise CheckError("%s: %s's palette has %d role(s) (%s); body, end grain and hoops need %d distinct ones: "
                             "add the swatches the references show (a dark wood, a metal)"
                             % (NAME, path, len(style["palette"]), ", ".join(style["palette"]), len(ROLES)))
    elif not set(ROLES.values()) <= set(PALETTE):
        raise CheckError("%s: ROLES values must be style.json palette roles: %s" % (NAME, ", ".join(sorted(PALETTE))))
    cam = style.get("camera") or {}
    ASSET_M = cam.get("asset_m") or 1.0
    if cam.get("asset_px"):
        PX_PER_M = cam["asset_px"] / ASSET_M
        # 0.5 px of chord error round the widest silhouette ring (where the ink line hides least), rounded up to even;
        # the gate's curve rule fails only under about 0.06 px a segment. main() drops segments while the triangles
        # are over the band's top, a ceiling and not a target
        n = math.ceil(math.pi / math.acos(1 - 0.5 / (WIDEST * PX_PER_M)))
        SEGMENTS = max(8, n + n % 2)
        # a hoop 2 px proud reads as a rim at game size, not a painted line
        HOOP_STEP = max(style.get("detail_floor_m") or 0.0, 2.0 / PX_PER_M)
    return True


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    export_now = "--export" in argv
    argv = [a for a in argv if a != "--export"]

    def option(name):       # --name <value>, taken out of argv; "" when the value is missing
        if name not in argv:
            return None
        at = argv.index(name)
        value = argv[at + 1] if at + 1 < len(argv) else ""
        del argv[at:at + 2]
        return value

    style, game = option("--style"), option("--game")
    if not argv or "" in (style, game):
        raise SystemExit("usage: blender ... --python toon_prop.py -- <unity project> [check.png] [--export] "
                         "[--style <style.json>] [--game <Name>]")
    # absolute before Blender takes them: it resolves a relative path against the drive root, not the working folder
    argv = [os.path.abspath(a) for a in argv]
    style = style and os.path.abspath(style)
    models = models_folder(argv[0], game)
    bible = use_style_bible(argv[0], style)
    # with a style bible the FBX waits for the review: the .blend goes to the gate and the sheet, and --export (after
    # the user's yes) writes the FBX and manifest Unity imports; a decision-page reading (--style) never exports
    reading = os.path.splitext(os.path.basename(style or ""))[0]
    reading = "" if reading == "style" else reading     # --style naming the game's own style.json is no reading
    if export_now and reading:
        print("[toon_prop] --export ignored: --style names the decision-page reading %s" % reading)
    export_now = not bible or (export_now and not reading)
    if bible and export_now and NAME == "SM_Barrel":
        # the shipped barrel is the wiring example, never a game's asset. Ceiling: it checks the name only, so a copy
        # that renames NAME and keeps this build() still exports; the art-reviewer's swap test catches that one
        raise CheckError("%s: --export refused: this is still the starter barrel; build() must come from the asset's "
                         "brief (its proportions, the STYLE.md motif) and NAME must name that asset" % NAME)

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
        os.makedirs(models, exist_ok=True)
        export(obj, os.path.join(models, NAME + ".fbx"))
        write_manifest(obj, triangles, os.path.join(models, NAME + ".json"))
    print("[toon_prop] %s: %d triangles, %.2f x %.2f x %.2f m" % (NAME, triangles, *obj.dimensions))
    if len(argv) > 1:
        check_render(obj, argv[1])


main()
