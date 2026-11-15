# The smallest complete example of the art-pipeline chain, generic and runnable: it builds one toon prop (a banded
# barrel), checks it, exports it with the unity-export skill's FBX preset and writes the JSON manifest that
# PropBuilder.cs.txt turns into materials and a prefab. Copy it to Tools/Blender/<thing>.py and replace build().
#
# blender --background --factory-startup --python-exit-code 1 --python Tools/Blender/toon_prop.py -- <unity project> [check.png]
#
# Output: <project>/Assets/__GAME__/Game/Art/Models/SM_Barrel.fbx and SM_Barrel.json, inside the folder
# OutlineNormalsPostprocessor bakes, so the outline stays closed at the hard rim edges. Without --python-exit-code 1
# a Python error exits 0 and the run looks green.
#
# Axes: authored in Blender metres, +Z up, the front toward -Y, the pivot at the base centre. With this preset and
# the importer's bakeAxisConversion the mesh keeps Blender X and negates Z; the prefab stands it up with a child
# turned Euler(90, 0, 0), so a Blender point (x, y, z) lands at Unity (x, z, y) in the prefab. to_unity() is that
# mapping, and every number in the manifest is already in Unity prefab space.

import json
import os
import sys

import bmesh
import bpy

# role -> (sRGB colour, smoothness). The builder makes one __GAME__/Toon material per role, M_<Role>; a colour
# change happens here and nowhere else.
PALETTE = {
    "Wood": ((0.78, 0.52, 0.30), 0.15),
    "WoodDark": ((0.55, 0.34, 0.20), 0.10),
    "Metal": ((0.62, 0.66, 0.74), 0.55),
}
TRIANGLE_BUDGET = 600       # a hand-sized prop on a phone; set it from the brief's screen size
NAME = "SM_Barrel"


class CheckError(Exception):
    pass


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def material(role):
    """A Blender material named after its palette role; Unity reads only the name (and the builder the role)."""
    name = "M_" + role
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    rgb, smooth = PALETTE[role]
    mat.diffuse_color = (*(srgb_to_linear(c) for c in rgb), 1.0)    # the check render shows the palette
    mat.roughness = 1.0 - smooth
    return mat


def ring(bm, radius, z0, z1, segments):
    """A closed cylinder band from z0 to z1, as new faces in bm; returns them."""
    made = bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius, radius2=radius,
                                 depth=z1 - z0)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, (z0 + z1) / 2.0), verts=made["verts"])
    return list({f for v in made["verts"] for f in v.link_faces})


def build():
    """The prop itself: a body with two metal hoops. Every face gets a palette role through its material slot."""
    roles = ["WoodDark", "Wood", "Metal"]
    mesh = bpy.data.meshes.new(NAME)
    obj = bpy.data.objects.new(NAME, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for role in roles:
        mesh.materials.append(material(role))

    bm = bmesh.new()
    body = ring(bm, 0.30, 0.0, 0.80, 16)
    for f in body:
        # the lids are the dark end grain, the staves the light wood
        f.material_index = roles.index("WoodDark" if abs(f.normal.z) > 0.9 else "Wood")
    bevel_edges = [e for e in bm.edges if len(e.link_faces) == 2
                   and abs(e.link_faces[0].normal.dot(e.link_faces[1].normal)) < 0.5]
    bmesh.ops.bevel(bm, geom=bevel_edges, offset=0.025, segments=2, affect='EDGES', profile=0.5)
    for z in (0.16, 0.64):
        for f in ring(bm, 0.315, z - 0.03, z + 0.03, 16):
            f.material_index = roles.index("Metal")
    bm.to_mesh(mesh)
    bm.free()

    # flat faces stay flat next to their rounded edges, so the toon bands stay clean
    for poly in mesh.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    return obj


def to_unity(p):
    """Blender (x, y, z) -> Unity prefab space (x, z, y), as the {x, y, z} object JsonUtility reads into a Vector3."""
    return {"x": round(p[0], 5), "y": round(p[2], 5), "z": round(p[1], 5)}


def color(rgb):
    """An sRGB palette colour as the {r, g, b, a} object JsonUtility reads into a Color."""
    return {"r": rgb[0], "g": rgb[1], "b": rgb[2], "a": 1.0}


def evaluated_mesh(obj):
    return obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()


def check(obj):
    """Every rule the asset must meet; a broken rule fails the run instead of exporting."""
    problems = []
    if tuple(obj.location) != (0.0, 0.0, 0.0) or tuple(obj.rotation_euler) != (0.0, 0.0, 0.0) \
            or tuple(obj.scale) != (1.0, 1.0, 1.0):
        problems.append("transform is not identity: the vertices must already be in piece space")
    mesh = evaluated_mesh(obj)
    mesh.calc_loop_triangles()
    triangles = len(mesh.loop_triangles)
    if triangles > TRIANGLE_BUDGET:
        problems.append("%d triangles, budget %d" % (triangles, TRIANGLE_BUDGET))
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
    lo = [min(v.co[i] for v in obj.data.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in obj.data.vertices) for i in range(3)]
    centre = [(a + b) / 2.0 for a, b in zip(lo, hi)]
    size = [b - a for a, b in zip(lo, hi)]
    manifest = {
        "mesh": NAME,
        "triangles": triangles,
        "roles": [m.name[2:] for m in obj.data.materials],      # submesh order
        "colors": [color(PALETTE[m.name[2:]][0]) for m in obj.data.materials],
        "smoothness": [PALETTE[m.name[2:]][1] for m in obj.data.materials],
        "outline": True,                                        # a prop the player reads; level pieces say False
        "colliderCenter": to_unity(centre),
        "colliderSize": to_unity(size),     # sizes are positive: the swap only reorders them
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


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not argv:
        raise SystemExit("usage: blender ... --python toon_prop.py -- <unity project> [check.png]")
    models = os.path.join(argv[0], "Assets", "__GAME__", "Game", "Art", "Models")
    os.makedirs(models, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0

    obj = build()
    triangles = check(obj)
    export(obj, os.path.join(models, NAME + ".fbx"))
    write_manifest(obj, triangles, os.path.join(models, NAME + ".json"))
    print("[toon_prop] %s: %d triangles, %.2f x %.2f x %.2f m" % (NAME, triangles, *obj.dimensions))
    if len(argv) > 1:
        check_render(obj, argv[1])


main()
