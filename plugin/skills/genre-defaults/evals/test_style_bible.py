# The style-bible scripts end to end on a fixture, about 10 s, no references or game needed:
#
#   blender --background --factory-startup --python-exit-code 1 --python test_style_bible.py -- --out <empty dir>
#
# 1. extract_style finds the fixture screenshots' wood and red accent colours, scales a 720p shot to 1080p, reads an
#    EXR as linear, and its CLI measures crops.json's surface crop, not its object crop.
# 2. style_gate passes good assets (a bevelled palette crate, a two-part asset with an accent trim, an atlas keeping
#    smoothness in alpha whose UVs use only its wood cells, a cutout, an Edge Split crate) and fails each rule once
#    (default material, node colour, loose part, thin rod, off-palette, role mismatch, pure black, dim colour, stale
#    viewport colour, texture off palette and too dark, texel density, hard edges, accent share, triangles, also from
#    a modifier, flat waste) and measures striped texels' share; the CLI exits 1, skips COL_ and LOD1.
# 3. contact_sheet draws the toon band where Toon.shader puts it (a sphere against N.L), and the crate's sheet with
#    its outline, references, json and game tile; on-palette coverage is 0.85 or more, also through a perspective
#    camera into a folder not made yet with a golden not approved yet. Removing the flat and the straight waste the
#    gate counts leaves the game tile unchanged.
# 4. curve_waste fails a 64x32 smooth ball, a 64-sided cylinder and height loops on an open smooth tube at prop size
#    and passes 26 segments (the formula's count), also twisted and triangulated, a faceted ball and height loops
#    under hard caps (the baked outline normal needs them); the smooth crate's rounded corners count 0.
# Prints STYLE BIBLE PASS; any failed assert exits 1.

import json
import os
import sys

import bmesh
import bpy
import numpy as np
import OpenImageIO as oiio
from mathutils import Matrix

SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
sys.dont_write_bytecode = True     # no __pycache__ beside the plugin's scripts
sys.path.insert(0, os.path.abspath(SCRIPTS))
import contact_sheet  # noqa: E402
import extract_style  # noqa: E402
import style_gate  # noqa: E402
from extract_style import linear_to_srgb, metrics, pixels, read_rgb, read_rgba, srgb_to_lab  # noqa: E402

WOOD, RED, STONE = (0.78, 0.52, 0.30), (0.95, 0.15, 0.10), (0.55, 0.56, 0.58)
MAGENTA = (1.0, 0.0, 1.0)


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


def material(name, rgb=None, base=None):
    """A material with its colour in the viewport colour (the toon pipeline) and, with base, in the Base Color."""
    mat = bpy.data.materials.new(name)
    if rgb is not None:
        mat.diffuse_color = (*contact_sheet.linear(rgb), 1.0)
    if base is not None:
        bsdf = style_gate.principled(mat)
        bsdf.inputs['Base Color'].default_value = (*contact_sheet.linear(base), 1.0)
    return mat


def crate(name, colour=None, tiny=False, subdiv=0, bevel=True, size=0.6, touch=False, smooth=False, rod=False):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    if bevel:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=size / 20, segments=2, affect='EDGES', profile=0.5)
    if subdiv:
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=subdiv, use_grid_fill=True)
    if tiny:
        made = bmesh.ops.create_cube(bm, size=0.01)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.4), verts=made['verts'])
    if touch:           # a 1 cm cube whose corner sits on the crate's corner: one shared point, still a loose part
        made = bmesh.ops.create_cube(bm, size=0.01)
        bmesh.ops.translate(bm, vec=(size / 2 + 0.005,) * 3, verts=made['verts'])
    if rod:             # a 5 mm rod 0.3 m long, tilted: long enough, but under a pixel across at game size
        made = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.005, 0.005, 0.3), verts=made['verts'])
        bmesh.ops.rotate(bm, matrix=Matrix.Rotation(0.8, 3, 'Y'), verts=made['verts'])
        bmesh.ops.translate(bm, vec=(size, 0.0, 0.0), verts=made['verts'])
    for f in bm.faces:
        f.smooth = smooth
    bm.to_mesh(mesh)
    bm.free()
    if colour is None:
        mesh.materials.append(bpy.data.materials.new('Material'))
    elif isinstance(colour, bpy.types.Material):
        mesh.materials.append(colour)
    else:
        mesh.materials.append(material('M_' + colour[0], colour[1]))
    obj['style_class'] = 'prop'
    return obj


def atlas(name, v0, cutout=False, stripes=False, wood=WOOD):
    """A crate textured from a two-cell atlas: wood (alpha 0.15) in the bottom half, magenta in the top (alpha 1, or
    0 for a cutout); its UVs map into the half that starts at v0, so a wrong row order reads magenta. Alpha drives the
    material's Alpha only for a cutout; otherwise it is smoothness, as in the toon-art kit atlas."""
    img = bpy.data.images.new('T_' + name, 64, 64, alpha=True)
    px = np.zeros((64, 64, 4), np.float32)          # Blender's pixel rows run bottom first
    px[:32] = (*wood, 0.15 if not cutout else 1.0)
    px[32:] = (*MAGENTA, 0.0 if cutout else 1.0)
    if stripes:                                     # one texel row in 4 of the wood cell: about a quarter of each face
        px[:32:4] = (*MAGENTA, 1.0)
    img.pixels.foreach_set(px.ravel())
    mat = bpy.data.materials.new('M_' + name)
    bsdf = style_gate.principled(mat)
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = img
    mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    if cutout:
        mat.node_tree.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    obj = crate(name, mat)
    uv = obj.data.uv_layers.new(name='UVMap')
    for loop in obj.data.loops:
        co = obj.data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (0.05 + 0.9 * (co.x / 0.6 + 0.5), v0 + 0.05 + 0.4 * (co.z / 0.6 + 0.5))
    return obj


def waste(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.index_update()
    n = style_gate.flat_waste(mesh, bm)
    bm.to_mesh(mesh)
    bm.free()
    return n


def panel(name, inner):
    """A flat panel of 3 x 3 quads whose inner grid lines map to UV inner and 1 - inner (1/3: one affine map; 0.1: a
    9-slice keeping its trim narrow)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=3, y_segments=3, size=0.3)
    uv = bm.loops.layers.uv.new('UVMap')
    lines = np.linspace(min(v.co.x for v in bm.verts), max(v.co.x for v in bm.verts), 4)
    for f in bm.faces:
        for lp in f.loops:
            lp[uv].uv = tuple(np.interp(c, lines, [0, inner, 1 - inner, 1]) for c in lp.vert.co[:2])
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def sphere(name, colour, u=64, v=32, smooth=True, twist=0.0, cylinder=False, cuts=0, caps=True):
    """A 0.3 m radius ball, or a cylinder with flat caps (or none) and cuts height loops; twist turns each ring by
    twist x z / r and triangulates, so no quad stays planar (an imported mesh)."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    if cylinder:
        bmesh.ops.create_cone(bm, cap_ends=caps, segments=u, radius1=0.3, radius2=0.3, depth=0.6)
        if cuts:
            bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.1],
                                      cuts=cuts)
    else:
        bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=0.3)
    if twist:
        for vert in bm.verts:
            vert.co.rotate(Matrix.Rotation(twist * vert.co.z / 0.3, 3, 'Z'))
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.normal_update()
    for f in bm.faces:
        f.smooth = smooth and not (cylinder and abs(f.normal.z) > 0.99)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(colour)
    return obj


def sheet(style, out, name, objects, *extra, folder=''):
    path = os.path.join(out, 'style_%s.json' % name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(style, f)
    png = os.path.join(out, folder, '%s_sheet.png' % name)
    sys.argv = ['blender', '--', '--style', path, '--out', png, '--objects', objects, *extra]
    contact_sheet.main()
    with open(png[:-4] + '.json', encoding='utf-8') as f:
        return png, json.load(f)


def band_agreement(style, game_png):
    """Share of the sphere's pixels whose band (lit or shade, by the nearer drawn colour) matches N.L > band."""
    bpy.context.view_layer.update()
    cam, sun = bpy.data.objects['SHEET_Cam'], bpy.data.objects['SHEET_Sun']
    right, up, back = (np.array(cam.matrix_world.col[i].xyz) for i in range(3))
    to_sun = np.array(sun.matrix_world.col[2].xyz)
    toon = contact_sheet.toon_params(style['light'])
    lin = contact_sheet.linear(WOOD)
    lum = float(lin @ np.array([0.2126, 0.7152, 0.0722]))
    lit = srgb_to_lab(linear_to_srgb(lin * (1 + toon['ambient'])))
    shade = srgb_to_lab(linear_to_srgb((lum + toon['saturation'] * (lin - lum)) * toon['shadow'] + lin * toon['ambient']))
    img = srgb_to_lab(read_rgba(game_png, long_side=None)[0])
    n_px, ortho, r, band = img.shape[0], cam.data.ortho_scale, 0.3, style['light']['band']
    agree = total = 0
    for i in range(n_px):
        for j in range(n_px):
            a, b = ((j + 0.5) / n_px - 0.5) * ortho, (0.5 - (i + 0.5) / n_px) * ortho
            if a * a + b * b > (0.9 * r) ** 2:
                continue
            ndl = float((a * right + b * up + np.sqrt(r * r - a * a - b * b) * back) @ to_sun / r)
            if abs(ndl - band) < 0.06:      # a pixel straddles the edge
                continue
            drawn_lit = np.linalg.norm(img[i, j] - lit) < np.linalg.norm(img[i, j] - shade)
            agree += drawn_lit == (ndl > band)
            total += 1
    return agree / max(1, total), total


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
    assert read_rgb(shots[0], screen_h=1080).shape[:2] == (1080, 1920), 'extract_style: 720p not scaled to 1080p'
    srgb = read_rgb(shots[0], long_side=None)
    exr = oiio.ImageBuf(oiio.ImageSpec(1280, 720, 3, oiio.FLOAT))   # a float file holds linear values
    exr.set_pixels(oiio.ROI(), contact_sheet.linear(srgb).astype(np.float32))
    assert exr.write(os.path.join(out, 'shot0.exr')), exr.geterror()
    diff = np.abs(read_rgb(os.path.join(out, 'shot0.exr'), long_side=None) - srgb).max()
    assert diff < 2 / 255, 'extract_style read an EXR %.3f off its sRGB twin' % diff

    style = {
        'shading': 'toon', 'outline': True, 'camera': {'projection': 'ortho', 'pitch': 30, 'yaw': 45, 'asset_px': 64,
                                                       'asset_m': 0.6},
        'light': {'pitch': 50, 'yaw': -30, 'band': 0.05, 'shadow_srgb': [0.55, 0.5, 0.65]},
        'palette': {'Wood': {'srgb': list(WOOD), 'smoothness': 0.15}, 'Stone': {'srgb': list(STONE)}},
        'accents': [list(RED)], 'palette_de': 6, 'value_range': [20, 92], 'triangles': {'prop': [12, 800]},
        'detail_floor_m': 0.02, 'texture_off_palette_max': 0.1, 'accent_max_share': 0.3, 'hard_edges_max_share': 0.5,
        'flat_waste_max_share': 0.1, 'curve_waste_max_share': {'prop': 0.1},
    }

    bpy.ops.wm.read_factory_settings(use_empty=True)
    good = crate('SM_Good', ('Wood', WOOD))
    trimmed = crate('SM_Trimmed', ('Wood', WOOD))
    trim = crate('SM_Trimmed_Band', ('Trim', RED), size=0.2)            # an accent part of a two-part asset
    del trim['style_class']
    trim.parent = trimmed
    split = crate('SM_Split', ('Wood', WOOD))
    split.modifiers.new('Split', 'EDGE_SPLIT')                          # split edges are not loose parts
    shelf = bpy.data.objects.new('Props', None)                         # an Empty that only groups props
    bpy.context.scene.collection.objects.link(shelf)
    good.parent = split.parent = shelf
    # smooth shading interpolates across the cut's vertices, so they carry the look: not flat waste
    smooth = crate('SM_Smooth', ('Wood', WOOD), subdiv=1, smooth=True)
    # SM_Atlas reads only the bottom (wood) cell; SM_Cut's UVs span both: its magenta texels are transparent, so unseen
    passing = [good, trimmed, trim, split, smooth, atlas('SM_Atlas', 0.0), atlas('SM_Cut', 0.25, cutout=True)]
    node = material('M_Node')                                           # a base colour FBX cannot carry
    node.node_tree.links.new(node.node_tree.nodes.new('ShaderNodeRGB').outputs[0],
                             style_gate.principled(node).inputs['Base Color'])
    failing = {
        'SM_Bad': (crate('SM_Bad', None, tiny=True), {'material', 'detail'}),
        'SM_Pink': (crate('SM_Pink', ('Pink', (1.0, 0.2, 0.8)), subdiv=6), {'palette', 'triangles', 'waste'}),
        'SM_Accent': (crate('SM_Accent', ('Trim', RED)), {'accent'}),
        'SM_Dense': (crate('SM_Dense', ('Wood', WOOD)), {'triangles'}),     # subdivision curves every face: no waste
        'SM_Grid': (crate('SM_Grid', ('Wood', WOOD), subdiv=1), {'waste'}),     # flat faces cut in four, flat shaded
        'SM_Role': (crate('SM_Role', ('Wood', STONE)), {'palette'}),
        'SM_Black': (crate('SM_Black', ('Ink', (0.0, 0.0, 0.0))), {'value', 'palette'}),
        'SM_Stale': (crate('SM_Stale', material('M_Stale', WOOD, MAGENTA)), {'palette'}),
        'SM_Stain': (atlas('SM_Stain', 0.5), {'texture'}),
        'SM_Stripes': (atlas('SM_Stripes', 0.0, stripes=True), {'texture'}),
        'SM_Hard': (crate('SM_Hard', ('Wood', WOOD), bevel=False), {'edges'}),
        'SM_Touch': (crate('SM_Touch', ('Wood', WOOD), bevel=False, touch=True), {'edges', 'detail'}),
        'SM_Rod': (crate('SM_Rod', ('Wood', WOOD), rod=True), {'detail'}),
        'SM_Dim': (crate('SM_Dim', ('Dim', (0.08, 0.08, 0.08))), {'value', 'palette'}),     # L* 6: under value_range
        'SM_Node': (crate('SM_Node', node), {'material'}),
        'SM_Dark': (atlas('SM_Dark', 0.0, wood=(0.05, 0.035, 0.02)), {'texture'}),
    }
    failing['SM_Dense'][0].modifiers.new('Subdiv', 'SUBSURF').levels = 3   # the exported mesh is counted
    failures, facts = style_gate.gate(passing + [o for o, _ in failing.values()], style)
    found = {}
    for fl in failures:
        found.setdefault(fl['object'], set()).add(fl['rule'])
    for o in passing:
        assert o.name not in found, 'style_gate failed %s: %s %s' % (o.name, found.get(o.name), facts.get(o.name))
    for name, (_, rules) in failing.items():
        assert found.get(name) == rules, 'style_gate on %s: %s, expected %s' % (name, found.get(name), rules)
    assert facts['SM_Trimmed']['asset_triangles'] == facts['SM_Trimmed']['triangles'] + facts['SM_Trimmed_Band'][
        'triangles'], 'triangles are not summed per asset: %s' % facts['SM_Trimmed']
    assert facts['SM_Good']['asset_triangles'] == facts['SM_Good']['triangles'], 'the grouping Empty became an asset'
    _, part_facts = style_gate.gate([trimmed], style)
    assert part_facts['SM_Trimmed'].get('unchecked_parts') == ['SM_Trimmed_Band'], 'partial asset not reported: %s' \
        % part_facts['SM_Trimmed']
    assert any('outside value_range' in f['message'] for f in failures if f['object'] == 'SM_Dark'), \
        'a dark texture passed value_range: %s' % [f for f in failures if f['object'] == 'SM_Dark']
    stripes = facts['SM_Stripes']['texture_off_palette']
    assert 0.2 < stripes < 0.32, 'texture sampling missed the stripes: %.3f off-palette, about 0.27 drawn' % stripes
    # 9 quads of one plane and one UV map are one quad: 18 -> 2 triangles
    assert waste(panel('Panel', 1 / 3)) == 16, 'flat panel with one UV map: waste missed'
    assert waste(panel('Slice', 0.1)) == 0, 'a 9-slice UV counted as waste: dissolving it stretches the trim'
    # an unbevelled crate cut in four: each side loses its centre, keeps the edge midpoints the outline hull leans on
    assert waste(crate('SM_HardGrid', ('Wood', WOOD), bevel=False, subdiv=1).data) == 12, 'edge midpoints dissolved'
    # a 0.3 m ball at 64 px per 0.6 m has a 32 px radius: 26 x 13 segments (the style-bible formula) are needed, also
    # twisted and triangulated, 64 x 32 are not, nor a 64-sided cylinder, nor height loops on an open smooth tube;
    # faceted, the 64 x 32 facets are a look; under hard caps the loops hold the baked outline normal upright (the
    # rims tilt 45 degrees), so they stay
    wood = bpy.data.materials['M_Wood']
    balls = [sphere('SM_Fine', wood), sphere('SM_Lean', wood, 26, 13), sphere('SM_Facet', wood, smooth=False),
             sphere('SM_Twist', wood, 26, 13, twist=1.0), sphere('SM_Tube', wood, cylinder=True),
             sphere('SM_LeanTube', wood, 26, cylinder=True), sphere('SM_CapTube', wood, 26, cylinder=True, cuts=4),
             sphere('SM_CutTube', wood, 26, cylinder=True, cuts=4, caps=False)]
    curves, curve_facts = style_gate.gate(balls, style, 'prop')
    assert {f['object'] for f in curves if f['rule'] == 'curve'} == {'SM_Fine', 'SM_Tube', 'SM_CutTube'}, \
        'curve rule: %s %s' % (curves, {n: f.get('curve_waste_share') for n, f in curve_facts.items()})
    assert curve_facts['SM_CutTube']['curve_waste'] == 26 * 8, 'height loops: 26 columns of 10 triangles keep 2 each'
    assert curve_facts['SM_CapTube']['curve_waste'] == 0, 'height loops under hard caps counted: the outline needs them'
    for o in balls:
        bpy.data.objects.remove(o)
    texel, _ = style_gate.gate([bpy.data.objects['SM_Atlas']], dict(style, texel_density=10000))
    assert [f['rule'] for f in texel] == ['texel'], 'style_gate missed the texel density: %s' % texel

    for name in ('COL_SM_Good', 'SM_Good_LOD1'):           # default materials: failures if they were checked
        crate(name, None)
    report = os.path.join(out, 'gate.json')
    for objects, code in (('SM_Good,SM_Trimmed,SM_Trimmed_Band', 0), (None, 1)):
        sys.argv = ['blender', '--', '--style', os.path.join(out, 'style_gate.json'), '--report', report]
        sys.argv += ['--objects', objects] if objects else []
        with open(sys.argv[3], 'w', encoding='utf-8') as f:
            json.dump(style, f)
        try:
            style_gate.main()
            got = 0
        except SystemExit as e:
            got = e.code
        assert got == code, 'style_gate CLI --objects %s exited %s, expected %s' % (objects, got, code)
    with open(report, encoding='utf-8') as f:
        checked = json.load(f)['objects']
    assert 'COL_SM_Good' not in checked and 'SM_Good_LOD1' not in checked, 'the CLI checked COL_/LOD1: %s' % checked

    ball = sphere('SM_Ball', bpy.data.materials['M_Wood'])
    ball['outline'] = False                      # a piece the game draws without the line, as toon_prop says
    _, rep = sheet(style, out, 'SM_Ball', 'SM_Ball', '--tile', '64')
    assert rep['outlined'] == [], 'the root\'s "outline": False was ignored: %s' % rep['outlined']
    share, n = band_agreement(style, rep['game_tile'])
    assert n > 500 and share > 0.98, 'toon band off Toon.shader: %.3f of %d pixels agree' % (share, n)
    for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
        bpy.data.objects.remove(o)

    crops = os.path.join(out, 'crops.json')
    with open(crops, 'w', encoding='utf-8') as f:
        json.dump([{'file': 'shot0.png', 'rect': [0, 300, 700, 400], 'note': 'wood block'},
                   {'file': 'shot1.png', 'rect': [300, 500, 700, 250], 'kind': 'object', 'class': 'prop'}], f)
    found_json = os.path.join(out, 'style_metrics.json')
    sys.argv = ['blender', '--', '--crops', crops, '--out', found_json, '--swatches', os.path.join(out, 'palette.png')]
    extract_style.main()
    with open(found_json, encoding='utf-8') as f:
        found = json.load(f)
    assert [c['file'] for c in found['crops']] == ['shot0.png'], 'extract_style measured an object crop: %s' % [
        c['file'] for c in found['crops']]
    assert near(found['pooled']['palette'], WOOD), 'extract_style CLI: no wood in the crop: %s' % found['pooled']
    assert os.path.isfile(os.path.join(out, 'palette.png')), 'extract_style wrote no swatch strip'
    png, rep = sheet(style, out, 'SM_Good', 'SM_Good', '--tile', '128', '--crops', crops, '--class', 'prop',
                     '--refs', shots[1])
    spec = oiio.ImageBuf(png).spec()
    assert (spec.width, spec.height) == (3 * 128, 6 * 128), 'sheet is %dx%d' % (spec.width, spec.height)
    assert rep['layout']['references'] == ['shot1.png', 'shot1.png'], rep['layout']['references']
    game = srgb_to_lab(read_rgba(rep['game_tile'], long_side=None)[0]).reshape(-1, 3)
    ink = srgb_to_lab(linear_to_srgb(contact_sheet.linear(WOOD) * contact_sheet.linear(contact_sheet.OUTLINE['srgb'])))
    # a 1.5 px line round a 64 px asset is about 1.5% of the tile
    assert (np.linalg.norm(game - ink, axis=1) < 6).mean() > 0.005, 'no outline in the game tile'
    lit = srgb_to_lab(linear_to_srgb(contact_sheet.linear(WOOD) * (1 + contact_sheet.toon_params(style['light'])['ambient'])))
    assert (np.linalg.norm(game - lit, axis=1) < 6).mean() > 0.1, 'the outline hull shades the lit band away'
    assert rep['against_style']['palette_coverage'] >= 0.85, 'look pass is off-palette: %s' % rep['against_style']
    # the atlas keeps smoothness 0.15 in alpha: drawn premultiplied, its wood would read at 15% and fall off-palette
    _, rep = sheet(style, out, 'SM_Atlas', 'SM_Atlas')
    assert rep['against_style']['palette_coverage'] >= 0.85, 'atlas look pass is off-palette: %s' % rep['against_style']
    # a perspective game camera, framed from its fov to the same pixels per metre; no golden approved yet, no review
    # folder made yet: the sheet still comes out
    persp = dict(style, camera=dict(style['camera'], projection='persp', fov=40))
    _, rep = sheet(persp, out, 'SM_Split', 'SM_Split', '--tile', '64', '--golden', os.path.join(out, 'no_golden.png'),
                   folder='review')
    assert rep['against_style']['palette_coverage'] >= 0.85, 'persp look pass is off-palette: %s' % rep['against_style']
    assert 'golden' not in rep['layout']['references'], 'a missing golden got a tile'

    # the waste rule's claim: dissolving what it counts leaves the drawn asset as it was (a sheet changes the meshes it
    # draws, so each copy is drawn once)
    grid = bpy.data.objects['SM_Grid']
    flat = grid.copy()
    flat.data = grid.data.copy()
    flat.name = 'SM_GridFlat'
    bpy.context.scene.collection.objects.link(flat)
    removed = waste(flat.data)
    assert removed == facts['SM_Grid']['flat_waste'] > 0, 'dissolved %d, the gate counted %s' % (
        removed, facts['SM_Grid']['flat_waste'])
    # and the curve rule's straight part: a smooth side's height loops draw as the side without them
    sphere('SM_CutTube', wood, 26, cylinder=True, cuts=4, caps=False)
    sphere('SM_LeanTube', wood, 26, cylinder=True, caps=False)
    for pair in (('SM_Grid', 'SM_GridFlat'), ('SM_CutTube', 'SM_LeanTube')):
        tiles = []
        for name in pair:
            for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
                bpy.data.objects.remove(o)
            tiles.append(read_rgba(sheet(style, out, name, name, '--tile', '128')[1]['game_tile'], long_side=None)[0])
        diff = float(np.abs(tiles[0] - tiles[1]).max())
        assert diff <= 2 / 255, 'removing the waste %s counts changed the game tile by %.3f' % (pair[0], diff)
    print('STYLE BIBLE PASS')


main()
