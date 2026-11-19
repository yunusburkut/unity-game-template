# The style-bible scripts end to end on a fixture, about 10 s, no references or game needed:
#
#   blender --background --factory-startup --python-exit-code 1 --python test_style_bible.py -- --out <empty dir>
#
# 1. extract_style finds the fixture screenshots' wood and red accent colours.
# 2. style_gate passes a bevelled palette crate, an accent-coloured one and a cutout texture (transparent texels off
#    palette), and fails the default material, a 1 cm loose part, an off-palette colour and a triangle count outside
#    its band (also one a Subdivision modifier makes), each by its own rule.
# 3. contact_sheet renders the crate's sheet (5 view rows plus a crops.json and a --refs reference), its json and the
#    game tile.
# Prints STYLE BIBLE PASS; any failed assert exits 1.

import json
import os
import sys

import bmesh
import bpy
import numpy as np
import OpenImageIO as oiio

SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
sys.dont_write_bytecode = True     # no __pycache__ beside the plugin's scripts
sys.path.insert(0, os.path.abspath(SCRIPTS))
import contact_sheet  # noqa: E402
import style_gate  # noqa: E402
from extract_style import metrics, pixels, read_rgb, srgb_to_lab  # noqa: E402

WOOD, RED = (0.78, 0.52, 0.30), (0.95, 0.15, 0.10)


def shot(path, h, w):
    img = np.zeros((h, w, 3), np.float32)
    img[:] = (0.35, 0.55, 0.30)
    img[: h // 3] = (0.55, 0.75, 0.95)
    img[h // 2: h // 2 + h // 6, w // 6: w // 2] = WOOD
    img[h // 8: h // 8 + h // 18, -w // 4: -w // 4 + h // 18] = RED
    buf = oiio.ImageBuf(oiio.ImageSpec(w, h, 3, oiio.UINT8))
    buf.set_pixels(oiio.ROI(), img)
    assert buf.write(path), buf.geterror()


def near(swatches, rgb, de=3.0):
    target = srgb_to_lab(np.array(rgb, float))
    return any(np.linalg.norm(np.array(s['lab']) - target) < de for s in swatches)


def crate(name, colour=None, tiny=False, subdiv=0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.6)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.03, segments=2, affect='EDGES', profile=0.5)
    if subdiv:
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=subdiv, use_grid_fill=True)
    if tiny:
        made = bmesh.ops.create_cube(bm, size=0.01)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.4), verts=made['verts'])
    bm.to_mesh(mesh)
    bm.free()
    if colour is None:
        mesh.materials.append(bpy.data.materials.new('Material'))
    else:
        role, rgb = colour
        mat = bpy.data.materials.new('M_' + role)
        mat.diffuse_color = (*contact_sheet.linear(rgb), 1.0)
        mesh.materials.append(mat)
    obj['style_class'] = 'prop'
    return obj


def cutout(name):
    """A crate whose texture is wood where opaque and magenta where alpha is 0: only the wood is ever seen."""
    obj = crate(name, ('Wood', WOOD))
    img = bpy.data.images.new('T_Cut', 64, 64, alpha=True)
    px = np.zeros((64, 64, 4), np.float32)
    px[:, :32] = (*WOOD, 1.0)
    px[:, 32:] = (1.0, 0.0, 1.0, 0.0)
    img.pixels.foreach_set(px.ravel())
    mat = bpy.data.materials.new('M_Cut')
    if mat.node_tree is None:            # Blender 5 gives new materials a node tree; 4.x needs use_nodes
        mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    obj.data.materials[0] = mat
    return obj


def main():
    out = sys.argv[sys.argv.index('--') + 1:][1]
    os.makedirs(out, exist_ok=True)

    shots = [os.path.join(out, 'shot%d.png' % i) for i in range(2)]
    shot(shots[0], 720, 1280)
    shot(shots[1], 1080, 1920)
    pooled = [pixels(read_rgb(p)) for p in shots]
    m = metrics(np.concatenate([p[0] for p in pooled]), np.concatenate([p[1] for p in pooled]))
    assert near(m['palette'], WOOD), 'extract_style: no wood swatch in %s' % m['palette']
    assert near(m['accents'], RED, 6.0), 'extract_style: no red accent in %s' % m['accents']

    style = {
        'shading': 'toon', 'camera': {'projection': 'ortho', 'pitch': 30, 'yaw': 45, 'asset_px': 64},
        'light': {'pitch': 50, 'yaw': -30, 'shadow_srgb': [0.55, 0.5, 0.65]},
        'palette': {'Wood': {'srgb': list(WOOD), 'smoothness': 0.15}}, 'accents': [list(RED)],
        'palette_de': 6, 'value_range': [20, 92], 'triangles': {'prop': [12, 800]}, 'detail_floor_m': 0.02,
        'texture_off_palette_max': 0.1,
    }
    style_path = os.path.join(out, 'style.json')
    with open(style_path, 'w', encoding='utf-8') as f:
        json.dump(style, f)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    good = crate('SM_Good', ('Wood', WOOD))
    bad = crate('SM_Bad', None, tiny=True)
    pink = crate('SM_Pink', ('Pink', (1.0, 0.2, 0.8)), subdiv=6)
    accent = crate('SM_Accent', ('Trim', RED))            # an accent colour is allowed though no role is named Trim
    dense = crate('SM_Dense', ('Wood', WOOD))
    dense.modifiers.new('Subdiv', 'SUBSURF').levels = 3   # the exported mesh, not the cage, is counted
    cut = cutout('SM_Cut')
    found, facts = {}, {}
    for obj in (good, bad, pink, accent, dense, cut):
        style_gate.check_object(obj, style, obj['style_class'],
                                lambda o, rule, msg: found.setdefault(o, set()).add(rule),
                                lambda o, k, v: facts.setdefault(o, {}).__setitem__(k, v))
    assert 'SM_Good' not in found, 'style_gate failed the palette crate: %s' % found.get('SM_Good')
    assert {'material', 'detail'} <= found.get('SM_Bad', set()), 'style_gate missed SM_Bad: %s' % found.get('SM_Bad')
    assert {'palette', 'triangles'} <= found.get('SM_Pink', set()), 'style_gate missed SM_Pink: %s' % found.get('SM_Pink')
    assert 'SM_Accent' not in found, 'style_gate failed the accent crate: %s' % found.get('SM_Accent')
    assert found.get('SM_Dense') == {'triangles'}, 'style_gate missed the modifier triangles: %s' % facts['SM_Dense']
    assert 'SM_Cut' not in found, 'style_gate counted transparent texels: %s' % facts['SM_Cut']

    crops = os.path.join(out, 'crops.json')
    with open(crops, 'w', encoding='utf-8') as f:
        json.dump([{'file': 'shot0.png', 'rect': [0, 300, 700, 400], 'note': 'wood block'}], f)
    sheet = os.path.join(out, 'SM_Good_sheet.png')
    sys.argv = ['blender', '--', '--style', style_path, '--out', sheet, '--objects', 'SM_Good', '--tile', '128',
                '--crops', crops, '--refs', shots[1]]
    contact_sheet.main()
    spec = oiio.ImageBuf(sheet).spec()
    assert (spec.width, spec.height) == (3 * 128, 6 * 128), 'sheet is %dx%d' % (spec.width, spec.height)
    with open(sheet[:-4] + '.json', encoding='utf-8') as f:
        rep = json.load(f)
    assert rep['layout']['references'] == ['shot0.png', 'shot1.png'], rep['layout']['references']
    assert oiio.ImageBuf(rep['game_tile']).spec().width == 128, 'no game tile at %s' % rep['game_tile']
    assert rep['against_style']['palette_coverage'] > 0.3, 'look pass is off-palette: %s' % rep['against_style']
    print('STYLE BIBLE PASS')


main()
