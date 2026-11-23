"""Bakes the seamless wear tile the Toon shader lays on in world space (its _WEAR keyword: rust chips, specks,
run-off streaks, grime):

blender --background --factory-startup --python-exit-code 1 --python Tools/Blender/wear_tile.py -- <unity project> [--game <Name>] [--seed N]

writes Assets/<Game>/Game/Art/Textures/Wear.png, 1024 px, linear, the raw noise fields (the shader thresholds them,
so the edges stay crisp up close): R chip noise, G specks, B run-off streaks (stretched along v, which the shader maps
to world up), A spots and grime. <Game> is --game, else the one folder under Assets that holds Game/Art. The tile
spans TILE_M metres (the material's Wear Tile Size), so the features keep their size. It is seamless because each
noise runs on a 4D torus: u and v each turn a circle. WearTilePostprocessor (Editor/Art/ToonShader.cs) pins its import.
"""
import math
import os
import sys

import bpy

# name -> (scale, detail, roughness or None, squash or None). The squash stretches the streak noise along the last
# axis (the tile's v).
NOISE = {
    "chip": (7.0, 10.0, 0.65, None),
    "spots": (4.5, 12.0, 0.7, None),
    "specks": (45.0, 2.0, None, None),
    "streak": (1.0, 4.0, None, (26.0, 26.0, 1.2)),
}
TILE_M = 2.5                            # the tile's side in metres
SIZE = 1024


def noise(nt, name, p, w):
    """The named wear noise node on the 4D torus (vector socket p and scalar w); returns its Fac."""
    scale, detail, rough, squash = NOISE[name]
    N, L = nt.nodes, nt.links
    if squash:
        sq = N.new("ShaderNodeVectorMath")
        sq.operation = "MULTIPLY"
        sq.inputs[1].default_value = squash
        L.new(p, sq.inputs[0])
        p = sq.outputs[0]
        sw = N.new("ShaderNodeMath")
        sw.operation = "MULTIPLY"
        sw.inputs[1].default_value = squash[2]
        L.new(w, sw.inputs[0])
        w = sw.outputs[0]
    n = N.new("ShaderNodeTexNoise")
    n.noise_dimensions = "4D"
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    if rough is not None:
        n.inputs["Roughness"].default_value = rough
    L.new(p, n.inputs["Vector"])
    L.new(w, n.inputs["W"])
    return n.outputs[0]


def torus(nt, seed):
    """The plane's UV (0-1) as a flat 4D torus TILE_M metres round: (vector, w) sockets, offset by the seed."""
    N, L = nt.nodes, nt.links
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["UV"], sep.inputs[0])
    r = TILE_M / (2 * math.pi)

    def circle(axis, fn, offset):
        a = N.new("ShaderNodeMath")
        a.operation = "MULTIPLY"
        a.inputs[1].default_value = 2 * math.pi
        L.new(sep.outputs[axis], a.inputs[0])
        t = N.new("ShaderNodeMath")
        t.operation = fn
        L.new(a.outputs[0], t.inputs[0])
        m = N.new("ShaderNodeMath")
        m.operation = "MULTIPLY_ADD"
        m.inputs[1].default_value = r
        m.inputs[2].default_value = offset
        L.new(t.outputs[0], m.inputs[0])
        return m.outputs[0]

    vec = N.new("ShaderNodeCombineXYZ")
    L.new(circle(0, "COSINE", seed * 3.1), vec.inputs[0])
    L.new(circle(0, "SINE", seed * 1.7), vec.inputs[1])
    L.new(circle(1, "COSINE", seed * 2.3), vec.inputs[2])
    return vec.outputs[0], circle(1, "SINE", seed * 1.3)


def bake_channel(plane, name, seed, size):
    """One noise baked (Cycles, an emission bake) into a linear float list of size*size values."""
    mat = bpy.data.materials.new("MW_" + name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    vec, w = torus(nt, seed)
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(noise(nt, name, vec, w), emit.inputs[0])
    nt.links.new(emit.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs[0])
    img = bpy.data.images.new("bake_" + name, size, size, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    target = nt.nodes.new("ShaderNodeTexImage")
    target.image = img
    nt.nodes.active = target
    plane.data.materials.clear()
    plane.data.materials.append(mat)
    bpy.ops.object.bake(type="EMIT")
    return img.pixels[:][0::4]


def bake_tile(path, size=SIZE, seed=7):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    plane = bpy.context.active_object
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 4
    scene.cycles.device = "CPU"
    scene.render.bake.margin = 0
    channels = [bake_channel(plane, n, seed, size) for n in ("chip", "specks", "streak", "spots")]
    out = bpy.data.images.new("Wear", size, size, alpha=True)
    out.colorspace_settings.name = "Non-Color"
    out.alpha_mode = "STRAIGHT"
    px = [0.0] * (size * size * 4)
    for c, values in enumerate(channels):
        px[c::4] = values
    out.pixels.foreach_set(px)
    out.filepath_raw = path
    out.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    out.save()
    lo = min(min(v) for v in channels)
    hi = max(max(v) for v in channels)
    if hi - lo < 0.3:
        raise SystemExit(f"Wear.png is nearly flat ({lo:.2f}-{hi:.2f}): the bake failed")
    print(f"[wear] {path}: {size} px, values {lo:.2f}-{hi:.2f}")


def textures_folder(project, game=None):
    """<project>/Assets/<Game>/Game/Art/Textures. <Game> is --game, else the one folder under Assets that holds
    Game/Art; none or several stops the run before it writes anything."""
    assets = os.path.join(project, "Assets")
    names = sorted(os.listdir(assets)) if os.path.isdir(assets) else []
    found = [d for d in names if os.path.isdir(os.path.join(assets, d, "Game", "Art"))]
    if game is None and len(found) != 1:
        raise SystemExit("wear_tile: %s under %s holds Game/Art, so the game's folder is not known: pass --game <Name>"
                         % ("more than one folder (%s)" % ", ".join(found) if found else "no folder", assets))
    game = game or found[0]
    if not os.path.isdir(os.path.join(assets, game, "Game", "Art")):
        raise SystemExit("wear_tile: --game %s has no Game/Art under %s (Game/Art is in: %s)"
                         % (game, assets, ", ".join(found) or "none"))
    return os.path.join(assets, game, "Game", "Art", "Textures")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not argv:
        raise SystemExit("usage: blender ... --python wear_tile.py -- <unity project> [--game <Name>] [--seed N]")

    def flag(name, default=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default

    folder = textures_folder(os.path.abspath(argv[0]), flag("--game"))
    os.makedirs(folder, exist_ok=True)
    bake_tile(os.path.join(folder, "Wear.png"), seed=int(flag("--seed", 7)))


if __name__ == "__main__":
    main()
