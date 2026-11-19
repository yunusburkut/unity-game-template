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
#    a modifier, flat waste, a role in an accent colour, an empty mesh, unrealized instances) and measures striped
#    texels' share; it reads UV0 under an active lightmap UV, the object-linked slot over the mesh's, fails an image
#    material with no UV map, names where a detail failure is; the CLI exits 1, skips COL_ and LOD1; the export set
#    leaves out a visible Boolean cutter and a render-hidden mesh, and keeps a hidden part under a classed root; a
#    curve part under a classed root fails (`mesh`), and so does an Empty instancing a collection (`instances`). An
#    accent part buried inside another part counts 0 accent share until it shows, also mirrored, and an open label
#    quad buries nothing; a closed cylinder buried in the mesh fails `hidden`, two materials fail materials_max 1; a
#    viewport-only colour off toon fails, a Base Color typed as raw sRGB gets the srgb_to_linear hint, texels on a role
#    skip value_range, principled() takes the wired node over a leftover, and a hex palette srgb stops the CLI. An
#    image behind a Reroute fails `material` (the FBX export finds no texture there), a Mapping node on the image's
#    Vector fails `texture` and a UV Map node reading UV0 passes; a renamed material at Blender's grey is a light grey
#    role (sRGB 0.906), not the default; the waste and materials messages name their remedies.
# 3. contact_sheet aims its cameras upright (straight down = Blender Top), takes a Unity Euler (x, r, 0) as pitch x,
#    yaw 180 - r, draws the toon band where Toon.shader puts it (a sphere against N.L, also at band 0 and -0.1 under
#    a warm sun, with the glossy spot and the contact shade), stops on an unknown camera projection and a missing
#    --crops file, notes a missing
#    reference file and goes on, draws UV0 under an active lightmap UV and an object-linked slot with its ink, the same ink on a box
#    scaled (1, 1, 3) as on that box applied, carries a lit material's
#    roughness, exits on a missing --objects name, and draws the crate's sheet without --class with its outline,
#    references, json and game tile; on-palette coverage is 0.85 or more, also through a perspective camera into a
#    folder not made yet with a golden not approved yet, where an Edge Split crate keeps its outline. Removing the
#    flat and the straight waste the gate counts leaves the game tile unchanged, and so do a light, a bright world
#    and a curve in the .blend. Toon smoothness takes the M_<Role>'s palette smoothness, else a set Principled
#    Roughness, else the viewport one. silhouette_fill and the primitive-outline SHEET NOTE come for a box, not a ball;
#    the Motif SHEET WARNING and "motif" follow STYLE.md beside the style file; a mixed lineup's reference row takes
#    every class's object crop, and the golden tile keeps every step-th pixel, padded grey. extract_style's
#    toon_albedo is the swatch / 1.09 in linear, or / toon_lit(light) under a style's light, also from its CLI.
# 4. curve_waste fails a 64x32 smooth ball, a 64-sided cylinder and height loops on an open smooth tube at prop size
#    and passes 26 segments (the formula's count), also twisted and triangulated, a faceted ball and height loops
#    under hard caps (the baked outline normal needs them); the smooth crate's rounded corners count 0.
# Prints STYLE BIBLE PASS; any failed assert exits 1.

import contextlib
import io
import json
import os
import sys

import bmesh
import bpy
import numpy as np
import OpenImageIO as oiio
from mathutils import Matrix, Vector

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


def said(call):
    """call()'s result and what it printed (echoed too, so the run's log keeps it)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        got = call()
    sys.stdout.write(buf.getvalue())
    return got, buf.getvalue()


def ink_share(style, game_png):
    """Share of the game tile nearer the wood's ink than its lit band, its shade band or the backdrop: the game's line
    is 1.5 px pushed along the normal's screen part, so at an edge it is about one anti-aliased pixel wide."""
    img = srgb_to_lab(read_rgba(game_png, long_side=None)[0]).reshape(-1, 3)
    lit, shade = contact_sheet.drawn_colours({'palette': {'Wood': {'srgb': list(WOOD)}}}, 'toon',
                                             contact_sheet.toon_params(style['light']), None)[:2]
    ink = srgb_to_lab(linear_to_srgb(contact_sheet.linear(WOOD) * contact_sheet.linear(contact_sheet.OUTLINE['srgb'])))
    ref = np.array([ink, lit, shade, img[0]])
    return (np.linalg.norm(img[:, None] - ref[None], axis=2).argmin(axis=1) == 0).mean()


def band_agreement(style, game_png):
    """Share of the sphere's pixels whose band (lit or shade, by the nearer drawn colour) matches N.L > band."""
    bpy.context.view_layer.update()
    cam, sun = bpy.data.objects['SHEET_Cam'], bpy.data.objects['SHEET_Sun']
    right, up, back = (np.array(cam.matrix_world.col[i].xyz) for i in range(3))
    to_sun = np.array(sun.matrix_world.col[2].xyz)
    toon = contact_sheet.toon_params(style['light'])
    lin = contact_sheet.linear(WOOD)
    lum = float(lin @ np.array([0.2126, 0.7152, 0.0722]))
    lit = srgb_to_lab(linear_to_srgb(lin * (toon['sun'] + toon['ambient'])))
    shade = srgb_to_lab(linear_to_srgb((lum + toon['saturation'] * (lin - lum)) * toon['shadow'] * toon['sun']
                                       + lin * toon['ambient']))
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
    # the frame shows Toon's lit band, albedo x 1.09: the albedo that draws as the wood swatch is that much darker
    sw = min(m['palette'], key=lambda s: np.linalg.norm(np.array(s['lab']) - srgb_to_lab(np.array(WOOD))))
    want = extract_style.hexcode(linear_to_srgb(contact_sheet.linear(sw['srgb']) / 1.09))
    assert sw['toon_albedo'] == want, 'toon_albedo %s, expected %s' % (sw['toon_albedo'], want)
    # under a style's warm light the lit band is that light x its colour + the ambient: a different albedo
    warm = {'color': [1.0, 0.957, 0.839], 'ambient': 1.0}
    lit = extract_style.toon_lit(warm)
    assert np.allclose(extract_style.toon_lit({}), 1.09), 'toon_lit({}) is not Unity default 1.09'
    warm_sw = extract_style.swatches(np.array([sw['lab']]), np.array([1.0]), 0.0, lit)[0]
    want = extract_style.hexcode(linear_to_srgb(contact_sheet.linear(warm_sw['srgb']) / lit))
    assert warm_sw['toon_albedo'] == want != sw['toon_albedo'], 'warm toon_albedo %s, expected %s' % (
        warm_sw['toon_albedo'], want)
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
    assert any('a bare Limited Dissolve is not the same' in f['message'] for f in failures if f['rule'] == 'waste'), \
        'the waste remedy: %s' % [f['message'] for f in failures if f['rule'] == 'waste']
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
    assert any('at (' in f['message'] for f in failures if f['object'] == 'SM_Bad' and f['rule'] == 'detail'), \
        'the detail failure does not say where: %s' % [f for f in failures if f['object'] == 'SM_Bad']

    # a lightmap UV made active: the gate still reads UV0, the map the game's _BaseMap samples
    lightmapped = atlas('SM_Lightmap', 0.0)
    lm = lightmapped.data.uv_layers.new(name='Lightmap')
    for d in lm.data:
        d.uv = (d.uv.x, 0.5 + d.uv.y)               # the magenta cell
    lightmapped.data.uv_layers.active = lm
    lm.active_render = True
    # a palette role painted in an accent colour is accent surface; an empty mesh is checked, not a crash; geometry
    # node instances the counts cannot see fail
    roof = crate('SM_Roof', ('Roof', RED))
    empty = bpy.data.objects.new('SM_Empty', bpy.data.meshes.new('SM_Empty'))
    bpy.context.scene.collection.objects.link(empty)
    empty['style_class'] = 'prop'
    scatter = crate('SM_Scatter', ('Wood', WOOD))
    ng = bpy.data.node_groups.new('GN_Scatter', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    pts, cube = ng.nodes.new('NodeGroupInput'), ng.nodes.new('GeometryNodeMeshCube')
    inst = ng.nodes.new('GeometryNodeInstanceOnPoints')
    ng.links.new(pts.outputs[0], inst.inputs['Points'])
    ng.links.new(cube.outputs['Mesh'], inst.inputs['Instance'])
    ng.links.new(inst.outputs['Instances'], ng.nodes.new('NodeGroupOutput').inputs[0])
    scatter.modifiers.new('Scatter', 'NODES').node_group = ng
    # a slot linked to the object is the material FBX ships; an image material on a mesh with no UV map samples one
    # texel in Unity
    linked = crate('SM_Linked', ('Wood', WOOD))
    linked.material_slots[0].link = 'OBJECT'
    linked.material_slots[0].material = material('M_Magenta', MAGENTA)
    no_uv = atlas('SM_NoUV', 0.0)
    no_uv.data.uv_layers.remove(no_uv.data.uv_layers[0])
    # the FBX export finds no texture behind a Reroute; Unity samples UV0 as is, so a Mapping node on the image's
    # Vector is lost, a UV Map node reading UV0 is not; a renamed material at Blender's 0.8 grey is a light grey role
    rerouted, mapped, uv_node = atlas('SM_Reroute', 0.0), atlas('SM_Mapped', 0.0), atlas('SM_UVNode', 0.0)
    for obj, kind in ((rerouted, 'NodeReroute'), (mapped, 'ShaderNodeMapping'), (uv_node, 'ShaderNodeUVMap')):
        nt = obj.data.materials[0].node_tree
        tex, made = next(n for n in nt.nodes if n.type == 'TEX_IMAGE'), nt.nodes.new(kind)
        if obj is rerouted:
            nt.links.new(tex.outputs['Color'], made.inputs[0])
            nt.links.new(made.outputs[0], style_gate.principled(obj.data.materials[0]).inputs['Base Color'])
        else:
            nt.links.new(made.outputs[0], tex.inputs['Vector'])
    mapped_node = next(n for n in mapped.data.materials[0].node_tree.nodes if n.type == 'MAPPING')
    mapped_node.inputs['Scale'].default_value = (4.0, 4.0, 4.0)
    next(n for n in uv_node.data.materials[0].node_tree.nodes if n.type == 'UVMAP').uv_map = 'UVMap'
    grey = crate('SM_Grey', material('M_Grey'))
    roofed = dict(style, palette=dict(style['palette'], Roof={'srgb': list(RED)}, Grey={'srgb': [0.906] * 3}))
    extra, extra_facts = style_gate.gate([lightmapped, roof, empty, scatter, linked, no_uv, rerouted, mapped, uv_node,
                                          grey], roofed)
    rules = {}
    for fl in extra:
        rules.setdefault(fl['object'], set()).add(fl['rule'])
    said_of = {fl['object']: fl['message'] for fl in extra}
    assert rules.get('SM_Reroute') == {'material'} and 'from node Reroute' in said_of['SM_Reroute'], \
        'an image behind a Reroute: %s' % [f for f in extra if f['object'] == 'SM_Reroute']
    assert rules.get('SM_Mapped') == {'texture'} and 'through node Mapping on its Vector' in said_of['SM_Mapped'], \
        'a Mapping node on the image: %s' % [f for f in extra if f['object'] == 'SM_Mapped']
    assert 'SM_UVNode' not in rules, 'a UV Map node reading UV0 failed: %s' % rules.get('SM_UVNode')
    assert 'SM_Grey' not in rules, 'a light grey role read as the default: %s' % [f for f in extra
                                                                                 if f['object'] == 'SM_Grey']
    assert 'SM_Lightmap' not in rules, 'the active lightmap UV was read, not UV0: %s' % extra_facts.get('SM_Lightmap')
    assert rules.get('SM_Roof') == {'accent'}, 'a role in an accent colour: %s' % rules.get('SM_Roof')
    assert 'triangles' in rules.get('SM_Empty', set()), 'an empty mesh: %s' % rules.get('SM_Empty')
    assert 'instances' in rules.get('SM_Scatter', set()), 'unrealized instances passed: %s' % rules.get('SM_Scatter')
    assert rules.get('SM_Linked') == {'palette'}, 'the object-linked slot was not checked: %s' % rules.get('SM_Linked')
    assert rules.get('SM_NoUV') == {'texture'}, 'an image material without UVs: %s' % rules.get('SM_NoUV')
    # the export set: a Boolean cutter left visible and a render-hidden mesh are not exported, so not checked; a part
    # hidden from render under a classed root ships with an export by selection, so it is
    host, cutter, hidden = crate('SM_Host', ('Wood', WOOD)), crate('SM_Cutter', None), crate('SM_Hidden', None)
    host.modifiers.new('Cut', 'BOOLEAN').object = cutter
    hidden.hide_render = True
    part = crate('SM_HiddenPart', None)
    del part['style_class']
    part.parent, part.hide_render = host, True
    exported = {o.name for o in style_gate.exported_meshes()}
    assert {'SM_Host', 'SM_HiddenPart'} <= exported and not exported & {'SM_Cutter', 'SM_Hidden'}, \
        'export set: %s' % sorted(exported)
    # a curve part under a classed root renders in Blender, but the FBX export takes meshes only
    rope = bpy.data.objects.new('CU_Rope', bpy.data.curves.new('CU_Rope', 'CURVE'))
    bpy.context.scene.collection.objects.link(rope)
    rope.parent = host
    roped, _ = style_gate.gate([host], style)
    assert any(f['rule'] == 'mesh' and 'CU_Rope' in f['message'] for f in roped), 'a curve part passed: %s' % roped
    # an Empty under the root instancing a collection: the FBX export ships its meshes, no count sees them
    bolts = bpy.data.collections.new('Bolts')
    bolt = crate('SM_Bolt', ('Wood', WOOD), size=0.05)
    bpy.context.scene.collection.objects.unlink(bolt)
    bolts.objects.link(bolt)
    em = bpy.data.objects.new('EM_Bolts', None)
    em.instance_type, em.instance_collection, em.parent = 'COLLECTION', bolts, host
    bpy.context.scene.collection.objects.link(em)
    bolted, _ = style_gate.gate([host], style)
    assert any(f['rule'] == 'instances' and 'EM_Bolts' in f['message'] for f in bolted), \
        'a collection instance under the root passed: %s' % bolted
    # an accent box buried inside the body is never on screen: no accent share; outside it, it counts
    body = crate('SM_Body', ('Wood', WOOD))
    core = crate('SM_Core', ('Trim', RED), size=0.4)
    del core['style_class']
    core.parent = body
    for mirror, z, share in ((1, 0.0, 0.0), (1, 1.0, 0.31), (-1, 0.0, 0.0), (-1, 1.0, 0.31)):   # -1: winding flips
        body.scale.x, core.location.z = mirror, z
        bpy.context.view_layer.update()
        _, got = style_gate.gate([body, core], dict(style, accent_max_share=None))
        assert abs(got['SM_Body']['accent_share'] - share) < 0.03, 'accent share %s with the core at z %s, scale x %s' \
            % (got['SM_Body']['accent_share'], z, mirror)
    # an open label quad on the face buries nothing: only a closed part has an inside
    label = bpy.data.objects.new('SM_Label', bpy.data.meshes.new('SM_Label'))
    bpy.context.scene.collection.objects.link(label)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.1)
    bmesh.ops.rotate(bm, matrix=Matrix.Rotation(1.5708, 3, 'Y'), verts=bm.verts)     # facing +X
    bmesh.ops.translate(bm, vec=(0.302, 0.0, 0.0), verts=bm.verts)
    bm.to_mesh(label.data)
    bm.free()
    label.data.materials.append(material('M_Label', RED))
    labelled = crate('SM_Labelled', ('Wood', WOOD))
    label.parent = labelled
    _, got = style_gate.gate([labelled, label], dict(style, accent_max_share=None))
    assert got['SM_Labelled']['accent_share'] < 0.1 and got['SM_Labelled']['hidden_share'] == 0, \
        'an open label hid the body: %s' % got['SM_Labelled']
    # a closed cylinder buried in the body's own mesh: unseen triangles; two materials over materials_max 1
    buried = crate('SM_Buried', ('Wood', WOOD))
    bm = bmesh.new()
    bm.from_mesh(buried.data)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.1, radius2=0.1, depth=0.3)
    bm.to_mesh(buried.data)
    bm.free()
    got, facts_b = style_gate.gate([buried], dict(style, hidden_max_share=0.05))
    assert 'hidden' in {f['rule'] for f in got} and facts_b['SM_Buried']['hidden_share'] > 0.05, \
        'a buried cylinder passed: %s %s' % (got, facts_b['SM_Buried'])
    for most, fails in ((1, True), ({'prop': 2}, False)):
        got, _ = style_gate.gate([trimmed, trim], dict(style, materials_max=most))
        assert any(f['rule'] == 'materials' for f in got) == fails, 'materials_max %s: %s' % (most, got)
    # the remedy offers the palette atlas only to a game that has one
    for density, tail in ((None, 'read the same at game size'), ('atlas', 'or use the palette atlas')):
        got, _ = style_gate.gate([trimmed, trim], dict(style, materials_max=1, texel_density=density))
        assert [f['message'] for f in got if f['rule'] == 'materials'][0].endswith(tail), 'materials remedy: %s' % got
    # a leftover Principled ahead of the wired one is not the one judged
    leftover = bpy.data.materials.new('M_Leftover')
    wired = leftover.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output = next(n for n in leftover.node_tree.nodes if n.type == 'OUTPUT_MATERIAL')
    leftover.node_tree.links.new(wired.outputs['BSDF'], output.inputs['Surface'])
    assert style_gate.principled(leftover).name == wired.name, 'principled() took the leftover node'
    # a hex palette colour stops the CLI with the field to copy
    hexed = os.path.join(out, 'style_hex.json')
    with open(hexed, 'w', encoding='utf-8') as f:
        json.dump(dict(style, palette={'Wood': {'srgb': '#C8854D'}}), f)
    sys.argv = ['blender', '--', '--style', hexed, '--report', os.path.join(out, 'hex.json')]
    try:
        style_gate.main()
        raise AssertionError('style_gate ran with a hex srgb')
    except SystemExit as e:
        assert 'toon_albedo_srgb' in str(e), e
    # off toon, a colour only in the viewport colour never reaches Unity; a Base Color typed in sRGB gets the remedy;
    # a texture's palette texels are exempt from value_range as a flat palette colour is
    viewport, _ = style_gate.gate([good], dict(style, shading='lit'))
    assert any(f['rule'] == 'material' and 'viewport' in f['message'] for f in viewport), viewport
    typed = crate('SM_Typed', None)
    typed.data.materials[0] = bpy.data.materials.new('M_Wood')
    style_gate.principled(typed.data.materials[0]).inputs['Base Color'].default_value = (*WOOD, 1.0)
    got, _ = style_gate.gate([typed], style)
    assert any('srgb_to_linear' in f['message'] for f in got), 'no sRGB remedy: %s' % got
    got, _ = style_gate.gate([bpy.data.objects['SM_Atlas']], dict(style, value_range=[72, 92]))
    assert not [f for f in got if f['rule'] == 'texture'], 'palette texels judged by value_range: %s' % got
    for o in (lightmapped, roof, empty, scatter, linked, no_uv, host, cutter, hidden, part, rope, em, bolt, body, core,
              typed, label, labelled, buried, rerouted, mapped, uv_node, grey):
        bpy.data.objects.remove(o)
    # the lit and painted look pass takes the gloss FBX carries, the Principled one
    gloss = material('M_Gloss', base=WOOD)
    style_gate.principled(gloss).inputs['Roughness'].default_value = 0.1
    got = style_gate.principled(contact_sheet.look_material(gloss, 'lit', None)).inputs['Roughness'].default_value
    assert abs(got - 0.1) < 1e-6, 'lit look pass roughness %.2f, the material has 0.1' % got
    # Toon smoothness in the game's order: the M_<Role>'s palette smoothness over a viewport roughness, then a set
    # Principled Roughness over the viewport one, then 1 - viewport roughness (Blender's 0.4)
    gloss.roughness = 0.4
    for mat, want in ((bpy.data.materials['M_Wood'], 0.15), (gloss, 0.9), (material('M_Plain'), 0.6)):
        got = contact_sheet.toon_smoothness(mat, style['palette'])
        assert abs(got - want) < 1e-6, 'toon smoothness of %s %.2f, expected %.2f' % (mat.name, got, want)

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

    # cameras stand upright (local Y up, X level) and look along -d; straight down is Blender's Top view; a Unity
    # camera at Euler (x, r, 0) is pitch x, yaw 180 - r through the toon-art axes
    # (Blender (x, y, z) = Unity (-x, z, -y))
    probe = bpy.data.objects.new('Probe', None)
    for yaw, pitch in ((45, 30), (-30, 50), (180, 10), (0, 90)):
        d = contact_sheet.direction(yaw, pitch)
        contact_sheet.aim(probe, d)
        rot = probe.rotation_quaternion.to_matrix()
        right, up, back = rot.col[0], rot.col[1], rot.col[2]
        assert (back - d).length < 1e-4, 'aim(%s, %s) looks along %s' % (yaw, pitch, -back)
        assert abs(right.z) < 1e-4 and (up.z > 0 or pitch == 90), \
            'aim(%s, %s) rolls the camera: right %s up %s' % (yaw, pitch, right, up)
    assert (rot.col[0] - Vector((1, 0, 0))).length < 1e-4 and (up - Vector((0, 1, 0))).length < 1e-4, 'top view'
    for x, r in ((30, 45), (50, -150), (10, 0)):
        xr, rr = np.radians(x), np.radians(r)
        to_eye = Vector((np.sin(rr) * np.cos(xr), np.cos(rr) * np.cos(xr), np.sin(xr)))    # -forward, in Blender axes
        assert (contact_sheet.direction(180 - r, x) - to_eye).length < 1e-6, 'Unity Euler (%s, %s, 0)' % (x, r)
    bpy.data.objects.remove(probe)

    ball = sphere('SM_Ball', bpy.data.materials['M_Wood'])
    ball['outline'] = False                      # a piece the game draws without the line, as toon_prop says
    (_, rep), text = said(lambda: sheet(style, out, 'SM_Ball', 'SM_Ball', '--tile', '64'))
    assert rep['outlined'] == [], 'the root\'s "outline": False was ignored: %s' % rep['outlined']
    # a ball fills about pi/4 of its box: no primitive's-outline note (a box's comes with the crate's sheet below)
    assert rep['silhouette_fill']['front'] < contact_sheet.BOX_FILL and 'silhouettes fill' not in text, \
        'a ball read as a box: %s' % rep['silhouette_fill']
    share, n = band_agreement(style, rep['game_tile'])
    assert n > 500 and share > 0.98, 'toon band off Toon.shader: %.3f of %d pixels agree' % (share, n)
    # the glossy spot at M_Wood's smoothness (the Wood role's 0.15, as the builder sets it) and the contact shade under
    # the floor (the ball's lower half sits below light.ground_y): Toon.shader's colours, drawn
    toon = contact_sheet.toon_params(style['light'])
    lit_lin = contact_sheet.toon_bands(contact_sheet.linear(WOOD), toon)[0]
    tile = srgb_to_lab(read_rgba(rep['game_tile'], long_side=None)[0]).reshape(-1, 3)
    for what, lin in (('spot', lit_lin + toon['sun'] * 0.15 * contact_sheet.SPOT),
                      ('contact', lit_lin * (1 - toon['contact']))):
        got = (np.linalg.norm(tile - srgb_to_lab(linear_to_srgb(np.clip(lin, 0, 1))), axis=1) < 4).mean()
        assert got > 0.001, 'the %s is not drawn: %.4f of the tile' % (what, got)     # the spot: about 30 px
    # a band at or under 0 (Toon.shader takes -1 to 1) and Unity's default warm sun, which tints both bands
    # (a sheet changes the meshes it draws, so each band draws a fresh ball)
    for band in (0.0, -0.1):
        for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_') or o.name.startswith('SM_Ball')]:
            bpy.data.objects.remove(o)
        sphere('SM_Ball', bpy.data.materials['M_Wood'])['outline'] = False
        edge = dict(style, light=dict(style['light'], band=band, color=[1.0, 0.957, 0.839]))
        _, rep = sheet(edge, out, 'SM_Ball', 'SM_Ball', '--tile', '64')
        share, n = band_agreement(edge, rep['game_tile'])
        assert n > 500 and share > 0.98, 'band %s off Toon.shader: %.3f of %d pixels agree' % (band, share, n)
    for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
        bpy.data.objects.remove(o)

    crops = os.path.join(out, 'crops.json')
    with open(crops, 'w', encoding='utf-8') as f:
        json.dump([{'file': 'shot0.png', 'rect': [0, 300, 700, 400], 'note': 'wood block'},
                   {'file': 'shot1.png', 'rect': [300, 500, 700, 250], 'kind': 'object', 'class': 'prop'}], f)
    found_json, warm_json = os.path.join(out, 'style_metrics.json'), os.path.join(out, 'style_warm.json')
    with open(warm_json, 'w', encoding='utf-8') as f:
        json.dump(dict(style, light=warm), f)
    sys.argv = ['blender', '--', '--crops', crops, '--out', found_json, '--swatches', os.path.join(out, 'palette.png'),
                '--style', warm_json]
    extract_style.main()
    with open(found_json, encoding='utf-8') as f:
        found = json.load(f)
    assert np.allclose(found['toon_lit'], lit, atol=1e-4), 'extract_style --style lit %s, expected %s' % (
        found['toon_lit'], lit)
    s0 = found['pooled']['palette'][0]
    want = linear_to_srgb(contact_sheet.linear(s0['srgb']) / lit)        # srgb is rounded to 3 places
    assert np.allclose(s0['toon_albedo_srgb'], want, atol=0.005), 'extract_style --style toon_albedo_srgb %s, ' \
        'expected %s' % (s0['toon_albedo_srgb'], want)
    assert [c['file'] for c in found['crops']] == ['shot0.png'], 'extract_style measured an object crop: %s' % [
        c['file'] for c in found['crops']]
    assert near(found['pooled']['palette'], WOOD), 'extract_style CLI: no wood in the crop: %s' % found['pooled']
    assert os.path.isfile(os.path.join(out, 'palette.png')), 'extract_style wrote no swatch strip'
    try:
        sheet(style, out, 'SM_Typo', 'SM_Good,SM_Gud')
        raise AssertionError('contact_sheet drew SM_Good alone for --objects SM_Good,SM_Gud')
    except SystemExit as e:
        assert 'SM_Gud' in str(e), e
    try:
        sheet(dict(style, camera=dict(style['camera'], projection='fisheye')), out, 'SM_Fish', 'SM_Good')
        raise AssertionError('contact_sheet drew an unknown projection')
    except SystemExit as e:
        assert 'persp' in str(e), e
    try:
        sheet(style, out, 'SM_NoCrops', 'SM_Good', '--crops', os.path.join(out, 'gone.json'))
        raise AssertionError('contact_sheet drew without the --crops file')
    except SystemExit as e:
        assert 'no such file' in str(e), e
    # no --class: the root's style_class picks the object crops; a screenshot left on another machine is skipped
    with open(crops, encoding='utf-8') as f:
        listed = json.load(f) + [{'file': 'gone.png', 'kind': 'object', 'class': 'prop'}]
    crops_gone = os.path.join(out, 'crops_gone.json')
    with open(crops_gone, 'w', encoding='utf-8') as f:
        json.dump(listed, f)
    (png, rep), text = said(lambda: sheet(style, out, 'SM_Good', 'SM_Good', '--tile', '128', '--crops', crops_gone,
                                          '--refs', shots[1]))
    # a crate fills its front and side boxes: the primitive's-outline note; no STYLE.md beside the style: no Motif
    assert min(rep['silhouette_fill']['front'], rep['silhouette_fill']['right']) >= contact_sheet.BOX_FILL \
        and 'SHEET NOTE: front and side silhouettes fill' in text, "a box's outline passed: %s" % rep['silhouette_fill']
    assert rep['motif'] is False and 'STYLE.md is missing' in text, 'no STYLE.md, motif %s' % rep['motif']
    spec = oiio.ImageBuf(png).spec()
    assert (spec.width, spec.height) == (3 * 128, 6 * 128), 'sheet is %dx%d' % (spec.width, spec.height)
    assert rep['layout']['references'] == ['shot1.png', 'shot1.png'], rep['layout']['references']
    game = srgb_to_lab(read_rgba(rep['game_tile'], long_side=None)[0]).reshape(-1, 3)
    # a one-pixel line round a 64 px asset is about 1% of the 128 px tile
    assert ink_share(style, rep['game_tile']) > 0.005, 'no outline in the game tile'
    lit = srgb_to_lab(linear_to_srgb(contact_sheet.linear(WOOD) * (1 + contact_sheet.toon_params(style['light'])['ambient'])))
    assert (np.linalg.norm(game - lit, axis=1) < 6).mean() > 0.1, 'the outline hull shades the lit band away'
    assert rep['against_style']['palette_coverage'] >= 0.85, 'look pass is off-palette: %s' % rep['against_style']
    # the atlas keeps smoothness 0.15 in alpha: drawn premultiplied, its wood would read at 15% and fall off-palette;
    # a STYLE.md with no "Motif:" line is warned about as a missing one is
    notes = os.path.join(out, 'STYLE.md')
    with open(notes, 'w', encoding='utf-8') as f:
        f.write('# Style\nMotifs come later.\n')
    (_, rep), text = said(lambda: sheet(style, out, 'SM_Atlas', 'SM_Atlas'))
    assert rep['against_style']['palette_coverage'] >= 0.85, 'atlas look pass is off-palette: %s' % rep['against_style']
    assert rep['motif'] is False and 'has no line starting "Motif:"' in text, 'a STYLE.md without Motif: passed'
    # a perspective game camera, framed from its fov to the same pixels per metre; no golden approved yet, no review
    # folder made yet: the sheet still comes out
    persp = dict(style, camera=dict(style['camera'], projection='Perspective', fov=40))     # Unity's word
    _, rep = sheet(persp, out, 'SM_Split', 'SM_Split', '--tile', '64', '--golden', os.path.join(out, 'no_golden.png'),
                   folder='review')
    assert rep['against_style']['palette_coverage'] >= 0.85, 'persp look pass is off-palette: %s' % rep['against_style']
    assert 'golden' not in rep['layout']['references'], 'a missing golden got a tile'
    # Edge Split cuts the crate at every bevel: the game's averaged outline normals keep its line closed, so must the
    # sheet's
    assert ink_share(persp, rep['game_tile']) > 0.005, 'the split crate lost its outline'
    # the look pass draws UV0 under an active lightmap UV (on the magenta cell), and the object-linked slot's colour
    # and ink over a magenta mesh slot
    lightmapped = atlas('SM_LightmapSheet', 0.0)
    lm = lightmapped.data.uv_layers.new(name='Lightmap')
    for d in lm.data:
        d.uv = (d.uv.x, 0.5 + d.uv.y)
    lightmapped.data.uv_layers.active = lm
    lm.active_render = True
    _, rep = sheet(style, out, 'SM_LightmapSheet', 'SM_LightmapSheet')
    assert rep['against_style']['palette_coverage'] >= 0.85, 'the sheet drew the lightmap UV: %s' % rep['against_style']
    linked = crate('SM_LinkedSheet', material('M_MagentaSheet', MAGENTA))
    linked.material_slots[0].link = 'OBJECT'
    linked.material_slots[0].material = bpy.data.materials['M_Wood']
    _, rep = sheet(style, out, 'SM_LinkedSheet', 'SM_LinkedSheet', '--tile', '64')
    assert rep['against_style']['palette_coverage'] >= 0.85, 'linked slot look: %s' % rep['against_style']
    assert ink_share(style, rep['game_tile']) > 0.005, 'the object-linked slot lost its ink'
    # an object scaled (1, 1, 3) draws the ink of the same box with the scale applied: the hull pushes in world space
    inks = []
    for name, applied in (('SM_TallScaled', False), ('SM_TallApplied', True)):
        tall = crate(name, bpy.data.materials['M_Wood'])
        if applied:
            tall.data.transform(Matrix.Diagonal((1.0, 1.0, 3.0, 1.0)))
        else:
            tall.scale = (1.0, 1.0, 3.0)
        for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
            bpy.data.objects.remove(o)
        inks.append(ink_share(style, sheet(style, out, name, name, '--tile', '128')[1]['game_tile']))
    assert inks[1] > 0.005 and abs(inks[0] - inks[1]) < 0.25 * inks[1], 'scaled box ink %.4f, applied %.4f' % tuple(inks)
    # a mixed lineup's reference row takes each class's object crop; a 150 px golden larger than the tile keeps every
    # step-th pixel, drawn by whole pixels and padded grey (a resize would smear its 3 px checker); a STYLE.md naming
    # a Motif: no warning
    with open(notes, 'w', encoding='utf-8') as f:
        f.write('# Style\n  Motif: brass rivets on every corner\n')
    cells = (np.indices((150, 150)) // 3).sum(axis=0) % 2
    golden = os.path.join(out, 'golden.png')
    buf = oiio.ImageBuf(oiio.ImageSpec(150, 150, 3, oiio.UINT8))
    buf.set_pixels(oiio.ROI(), np.repeat(cells[:, :, None], 3, axis=2).astype(np.float32))
    assert buf.write(golden), buf.geterror()
    mixed = os.path.join(out, 'crops_mixed.json')
    with open(mixed, 'w', encoding='utf-8') as f:
        json.dump([{'file': 'shot1.png', 'rect': [300, 500, 700, 250], 'kind': 'object', 'class': 'prop'},
                   {'file': 'shot0.png', 'rect': [0, 300, 300, 200], 'kind': 'object', 'class': 'barrel'}], f)
    crate('SM_MixProp', bpy.data.materials['M_Wood'])
    crate('SM_MixBarrel', bpy.data.materials['M_Wood'], size=0.3)['style_class'] = 'barrel'
    for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
        bpy.data.objects.remove(o)
    (png, rep), text = said(lambda: sheet(style, out, 'SM_Mix', 'SM_MixProp,SM_MixBarrel', '--tile', '64',
                                          '--crops', mixed, '--golden', golden))
    os.remove(notes)
    assert rep['layout']['references'] == ['shot1.png', 'shot0.png', 'golden'], rep['layout']['references']
    assert rep['motif'] is True and 'STYLE.md' not in text, 'a STYLE.md with a Motif: line, motif %s' % rep['motif']
    t = rep['layout']['tile_px']                    # --tile 64 is widened to the asset's game-size pixels
    step = -(-150 // t)
    want = cells[::step, ::step]
    k = t // len(want)
    want = np.repeat(np.repeat(want, k, axis=0), k, axis=1)
    o = (t - len(want)) // 2
    y = rep['layout']['rows'].index('references') * t
    drawn = read_rgb(png, long_side=None)[y:y + t, 2 * t:3 * t, 0]
    assert np.array_equal(drawn[o:o + len(want), o:o + len(want)] > 0.5, want == 1) and abs(
        drawn[0, 0] - contact_sheet.GREY_BG) < 0.01, 'the golden tile is not drawn by whole pixels, padded grey'

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
    # the sheet lights the asset with its own sun and world only, and draws meshes only: a light, a bright world and a
    # curve poking out of the crate change nothing
    tiles = []
    for name in ('SM_LitA', 'SM_LitB'):
        crate(name, bpy.data.materials['M_Wood'])
        for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
            bpy.data.objects.remove(o)
        tiles.append(read_rgba(sheet(style, out, name, name, '--tile', '128')[1]['game_tile'], long_side=None)[0])
        stray = bpy.data.objects.new('Stray', bpy.data.lights.new('Stray', 'POINT'))
        stray.data.energy, stray.location = 5000.0, (0.0, -1.0, 1.0)
        bpy.context.scene.collection.objects.link(stray)
        world = bpy.data.worlds.new('Bright')
        world.color = (1.0, 0.0, 0.0)
        bpy.context.scene.world = world
        wire = bpy.data.curves.new('Stray', 'CURVE')
        wire.bevel_depth = 0.05
        spline = wire.splines.new('POLY')
        spline.points.add(1)
        spline.points[1].co = (0.0, 0.0, 1.0, 1.0)
        bpy.context.scene.collection.objects.link(bpy.data.objects.new('Stray', wire))
    diff = float(np.abs(tiles[0] - tiles[1]).max())
    assert diff <= 2 / 255, 'a light or world in the .blend changed the game tile by %.3f' % diff
    print('STYLE BIBLE PASS')


main()
