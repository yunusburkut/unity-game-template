# The style-bible scripts end to end on a fixture, about 20 s, no references or game needed:
#
#   blender --background --factory-startup --python-exit-code 1 --python test_style_bible.py -- --out <empty dir>
#
# 1. extract_style finds the fixture screenshots' wood and red accent colours, scales a 720p shot to 1080p, reads an
#    EXR as linear, and its CLI measures crops.json's surface crops, not its object crop, warns on a rect that runs off
#    its image and writes crops.png; the fixture's sky, brighter in blue than the default sun's lit band, gets the
#    albedo-over-1 STYLE WARNING and its "albedo_clipped" entry; a shot tagged with another colour profile than sRGB
#    gets one STYLE WARNING per file, and a --style whose light.color is a hex stops the CLI.
# 2. style_gate passes good assets (a bevelled palette crate, a two-part asset with an accent trim, an atlas keeping
#    smoothness in alpha whose UVs use only its wood cells, an Edge Split crate) and fails each rule once
#    (default material, node colour, loose part, thin rod, off-palette, role mismatch, pure black, dim colour, stale
#    viewport colour, texture off palette and too dark, texel density, hard edges, accent share, triangles, also from
#    a modifier, flat waste, a role in an accent colour, an empty mesh, unrealized instances, a cutout under toon,
#    which passes under lit, a box wound inside out, not a mirrored one, one flipped face, the inner wall a welded
#    lid leaves, a part hidden in the viewport, a Principled behind a Mix Shader) and measures striped
#    texels' share; it reads UV0 under an active lightmap UV, the object-linked slot over the mesh's, fails an image
#    material with no UV map, names where a detail failure is and gives a turned 12 mm cube its side as the size; the
#    CLI exits 1, skips COL_ and LOD1; the export set
#    leaves out a visible Boolean cutter and a render-hidden mesh, and keeps a hidden part under a classed root; a
#    curve part under a classed root fails (`mesh`), and so does an Empty instancing a collection (`instances`; beside
#    the asset it is the uncounted_instances fact). An
#    accent part buried inside another part counts 0 accent share until it shows, also mirrored, an open label quad
#    buries nothing, and a plank through a closed body hides nothing and counts about its visible area; a closed
#    cylinder buried in the mesh fails `hidden`, and so do the faces between a body and a flush lid in one mesh (two
#    closed parts sharing whole edges), two materials fail materials_max 1; a viewport-only colour off toon
#    fails, a Base Color typed as raw sRGB gets the srgb_to_linear hint, texels on a role skip value_range,
#    with no Principled at the output the viewport colour is judged off toon too,
#    principled() takes the wired node over a leftover, and a hex or 0-255 palette srgb, accent, light.color,
#    light.shadow_srgb or outline.srgb stops the CLI and the sheet with the field to copy, a bare-list role with the
#    form a role takes. An image behind a Reroute
#    fails `material` (the FBX export finds no texture there), a Mapping node on the image's Vector fails `texture` and
#    a UV Map node reading UV0 passes; a renamed material at Blender's grey is a light grey role (sRGB 0.906), not the
#    default, a coloured Material.NNN gets the default-name message, a near-white role is not pure white, a Boolean in
#    Transfer mode passes with the cutter's material, and under texel_density atlas a flat colour fails; an unclassed
#    part under the band gets the parenting hint, a classed root not; a half-size asset passes at the band floor scaled
#    by its size against camera.asset_m, and under it the message names the scaled floor; band_top_share is the count
#    over the band's top; the waste and materials messages name their remedies, the materials one the draws (twice
#    when outlined, the submeshes of separate parts); over the band, the message points at the asset's curve and
#    waste failures, or names a curve share over 0.1 that failed no limit (a class without one), or with none says
#    nothing is left to cut and names the largest parts; the CLI prints a STYLE FACTS line per asset with its
#    submeshes, on a pass too, a textured asset's ending with its texture_off_palette; flat_waste takes faces just
#    made with bm.faces.new.
# 3. contact_sheet aims its cameras upright (straight down = Blender Top, turned by the game camera's yaw: the ball's
#    lit side lands in the tile's bottom half at yaw 0, its top half at yaw 180), takes a Unity Euler (x, r, 0) as
#    pitch x, yaw 180 - r, draws a cutout under toon with one SHEET WARNING, the default line for a style with no
#    "outline" key, and the toon band where Toon.shader puts it (a sphere against N.L, also at band 0 and -0.1 under
#    a warm sun, with the glossy spot and the contact shade), defaults to the Main scene's sun (warm, pitch 50, yaw
#    210), stops on an unknown camera projection and a missing --crops file, notes a missing reference file and goes
#    on, draws UV0 under an active lightmap UV, an object-linked slot with its ink and a Boolean's transferred
#    material, the same ink on a box scaled (1, 1, 3) as on that box applied, carries a lit material's roughness,
#    exits on a missing --objects name, and draws the crate's sheet without --class with its outline, references,
#    json and game tile; on-palette coverage is 0.85 or more, also through a perspective camera into a folder not
#    made yet with a golden not approved yet, where an Edge Split crate keeps its outline. Removing the flat and the
#    straight waste the gate counts leaves the game tile unchanged, and so do a light, a bright world and a curve in
#    the .blend. Toon smoothness takes the M_<Role>'s palette smoothness, else a set Principled Roughness, else the
#    viewport one. silhouette_fill and the primitive-outline SHEET NOTE come for a box, not a ball; the Motif SHEET
#    WARNING and "motif" follow STYLE.md beside the style file; motif_px is null with a warning when no face carries
#    the "motif" attribute, 0 with the under 2 x 2 warning, which names the camera's yaw, for a tagged face the asset
#    hides, and a tagged lid reads
#    (motif_share, a fourth game tile); a tag on every face gets the covers-most SHEET WARNING, and a camera on the
#    sun's far side the lit-band SHEET NOTE; a mixed lineup's reference row takes every class's object crop, and the
#    golden tile keeps every step-th pixel, never scaled up, padded grey, with its golden_zoom and the note;
#    reference_zoom holds each reference tile's zoom, the golden's last; a look.chroma_mean far from the game view's
#    is a SHEET NOTE, not a warning; an atlas painted in memory and saved unpacked fails the gate reopened and gets
#    the sheet's warning, a packed one neither. extract_style's
#    toon_albedo is the swatch / TOON_LIT (the Main scene's sun) in linear, or / toon_lit(light) under a style's
#    light, also from its CLI.
# 4. curve_waste fails a 64x32 smooth ball, a 64-sided cylinder, also with 4 height loops under its hard caps (at a
#    higher share, not a thinner one), height loops on an open smooth tube and a flat
#    8-segment bevel 2 px wide at prop size and passes 26 segments (two merged leave the curve by 0.9 px), also
#    twisted and triangulated, faceted balls (26 x 13 count nothing) and height loops under hard caps (the baked
#    outline normal needs them; with the root's "outline" False they count); a 2 px bevel passes at 3 segments and
#    fails at 4, flat as smooth; the smooth crate's rounded corners count 0.
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
MAGENTA, SKY = (1.0, 0.0, 1.0), (0.55, 0.75, 0.95)


def shot(path, h, w):
    img = np.zeros((h, w, 3), np.float32)
    img[:] = (0.35, 0.55, 0.30)
    img[: h // 3] = SKY
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


def crate(name, colour=None, tiny=False, subdiv=0, bevel=True, size=0.6, touch=False, smooth=False, rod=False,
          turned=False):
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
    if turned:          # a 12 mm cube turned 30 and 45 degrees: 12 mm across its faces, 21 mm corner to corner
        bmesh.ops.create_cube(bm, size=0.012, matrix=Matrix.Translation((0.0, 0.0, 0.4))
                              @ Matrix.Rotation(0.5236, 4, 'Z') @ Matrix.Rotation(0.7854, 4, 'X'))
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


def tag_motif(obj, keep):
    """Tags the faces whose normal keep() takes with the boolean face attribute "motif", as a build marks its motif."""
    obj.data.attributes.new('motif', 'BOOLEAN', 'FACE').data.foreach_set(
        'value', [bool(keep(p.normal)) for p in obj.data.polygons])


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
    # the frame shows Toon's lit band under the Main scene's warm sun, albedo x TOON_LIT: the albedo that draws as the
    # wood swatch is that much darker
    sw = min(m['palette'], key=lambda s: np.linalg.norm(np.array(s['lab']) - srgb_to_lab(np.array(WOOD))))
    want = extract_style.hexcode(linear_to_srgb(contact_sheet.linear(sw['srgb']) / extract_style.TOON_LIT))
    assert sw['toon_albedo'] == want, 'toon_albedo %s, expected %s' % (sw['toon_albedo'], want)
    # under a style's light the lit band is its colour x intensity + its ambient: ambient 1 gives a different albedo
    warm = {'color': [1.0, 0.957, 0.839], 'ambient': 1.0}
    lit = extract_style.toon_lit(warm)
    assert np.allclose(extract_style.toon_lit({}), contact_sheet.linear([1.0, 0.957, 0.839]) + 0.09), \
        'toon_lit({}) is not the Main scene sun'
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
    # SM_Atlas reads only the bottom (wood) cell
    passing = [good, trimmed, trim, split, smooth, atlas('SM_Atlas', 0.0)]
    node = material('M_Node')                                           # a base colour FBX cannot carry
    node.node_tree.links.new(node.node_tree.nodes.new('ShaderNodeRGB').outputs[0],
                             style_gate.principled(node).inputs['Base Color'])
    failing = {
        'SM_Bad': (crate('SM_Bad', None, tiny=True), {'material', 'detail'}),
        'SM_Pink': (crate('SM_Pink', ('Pink', (1.0, 0.2, 0.8)), subdiv=6), {'palette', 'triangles', 'waste', 'curve'}),
        'SM_Accent': (crate('SM_Accent', ('Trim', RED)), {'accent'}),
        'SM_Dense': (crate('SM_Dense', ('Wood', WOOD)), {'triangles', 'curve'}),  # flat Subsurf 3: sub-pixel facets
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
        # SM_Cut's UVs span both cells: its magenta texels are transparent, so the texture rule does not see them, but
        # Toon.shader has no alpha clip and draws the card solid
        'SM_Cut': (atlas('SM_Cut', 0.25, cutout=True), {'material'}),
        'SM_Turned': (crate('SM_Turned', ('Wood', WOOD), turned=True), {'detail'}),
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
    assert any('Toon.shader has no alpha clip' in f['message'] for f in failures if f['object'] == 'SM_Cut'), \
        'a cutout under toon: %s' % [f for f in failures if f['object'] == 'SM_Cut']
    got, _ = style_gate.gate([failing['SM_Cut'][0]], dict(style, shading='lit'))
    assert not got, 'a cutout off toon, where the shader clips it: %s' % got
    # the size is the cube's side whichever way it is turned, not a diagonal
    assert [f['message'] for f in failures if f['object'] == 'SM_Turned'][0].endswith(', 0.012 m'), \
        'a turned 12 mm cube: %s' % [f for f in failures if f['object'] == 'SM_Turned']
    assert facts['SM_Trimmed']['asset_triangles'] == facts['SM_Trimmed']['triangles'] + facts['SM_Trimmed_Band'][
        'triangles'], 'triangles are not summed per asset: %s' % facts['SM_Trimmed']
    assert facts['SM_Good']['asset_triangles'] == facts['SM_Good']['triangles'], 'the grouping Empty became an asset'
    assert facts['SM_Good']['band_top_share'] == round(facts['SM_Good']['asset_triangles'] / 800, 3), \
        'band_top_share: %s' % facts['SM_Good']
    # over the band: the remedy starts with what the asset's other failures name (SM_Pink: curve and waste); with none,
    # nothing is left to cut, and the message says so and names the largest parts
    assert any('starting with what its curve and waste failures name' in f['message'] for f in failures
               if f['object'] == 'SM_Pink' and f['rule'] == 'triangles'), 'over the band with waste: %s' % failures
    got, _ = style_gate.gate([good], dict(style, triangles={'prop': [12, 100]}))
    assert [f['rule'] for f in got] == ['triangles'] and 'names anything to cut, so the design has more parts than ' \
        'the band affords (largest: SM_Good 108 triangles): drop parts' in got[0]['message'], \
        'over the band with nothing to cut: %s' % got
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
    # the bible's recipe on faces a build script just made (bm.faces.new leaves their normals unset): a 4 x 4 grid of
    # one plane is one quad, 32 -> 2 triangles
    fresh = bpy.data.meshes.new('Fresh')
    bm = bmesh.new()
    rows = [[bm.verts.new((x / 4, y / 4, 0.0)) for x in range(5)] for y in range(5)]
    for y in range(4):
        for x in range(4):
            bm.faces.new((rows[y][x], rows[y][x + 1], rows[y + 1][x + 1], rows[y + 1][x]))
    bm.to_mesh(fresh)
    got = style_gate.flat_waste(fresh, bm)
    bm.free()
    assert got == 30, 'flat_waste on bm.faces.new faces removed %d of 30' % got
    # a 0.3 m ball at 64 px per 0.6 m has a 32 px radius: 26 x 13 segments pass (two merged into one leave the curve
    # by 0.9 px, past CHORD_PX), also twisted and triangulated, 64 x 32 do not (0.15 px), nor a 64-sided cylinder, nor
    # height loops on an open smooth tube;
    # faceted, the 64 x 32 facets are a look; under hard caps the loops hold the baked outline normal upright (the
    # rims tilt 45 degrees), so they stay, and a 64-sided cylinder still fails with them (every piece of an over-fine
    # column counts, so the loops do not thin its share out); a flat 8-segment bevel 2 px wide cuts facets under a
    # pixel across, so it fails as a smooth curve would, while 26 x 13 facets, each pixels wide, count nothing
    wood = bpy.data.materials['M_Wood']
    bevel8 = crate('SM_Bevel8', ('Wood', WOOD), bevel=False)
    bevel8.modifiers.new('Bevel', 'BEVEL').segments = 8
    bevel8.modifiers['Bevel'].width = 2 / 64 * 0.6
    balls = [sphere('SM_Fine', wood), sphere('SM_Lean', wood, 26, 13), sphere('SM_Facet', wood, smooth=False),
             sphere('SM_Twist', wood, 26, 13, twist=1.0), sphere('SM_Tube', wood, cylinder=True),
             sphere('SM_LeanTube', wood, 26, cylinder=True), sphere('SM_CapTube', wood, 26, cylinder=True, cuts=4),
             sphere('SM_CutTube', wood, 26, cylinder=True, cuts=4, caps=False),
             sphere('SM_FineCapTube', wood, cylinder=True, cuts=4),
             sphere('SM_WideFacet', wood, 26, 13, smooth=False), bevel8]
    curves, curve_facts = style_gate.gate(balls, style, 'prop')
    assert {f['object'] for f in curves if f['rule'] == 'curve'} == {'SM_Fine', 'SM_Tube', 'SM_CutTube', 'SM_Bevel8',
                                                                     'SM_FineCapTube'}, \
        'curve rule: %s %s' % (curves, {n: f.get('curve_waste_share') for n, f in curve_facts.items()})
    assert curve_facts['SM_FineCapTube']['curve_waste_share'] > curve_facts['SM_Tube']['curve_waste_share'], \
        "height loops thinned an over-fine cylinder's share: %s" % curve_facts['SM_FineCapTube']
    assert curve_facts['SM_CutTube']['curve_waste'] == 26 * 8, 'height loops: 26 columns of 10 triangles keep 2 each'
    assert curve_facts['SM_CapTube']['curve_waste'] == 0, 'height loops under hard caps counted: the outline needs them'
    assert curve_facts['SM_WideFacet']['curve_waste'] == 0, 'wide facets counted: %s' % curve_facts['SM_WideFacet']
    # a piece the game draws without the ink line has no outline hull for height loops to hold: under hard caps they
    # count as on the open tube. A 2 px Bevel reads the same shaded flat or smooth (each strip is judged by its own
    # width, the outer one beside the wide flat too): 3 segments pass, 4 fail
    kit_tube = sphere('SM_KitTube', wood, 26, cylinder=True, cuts=4)
    kit_tube['outline'] = False
    balls.append(kit_tube)
    for seg in (3, 4):
        for shade in ('Flat', 'Smooth'):
            b = crate('SM_Bevel%d%s' % (seg, shade), ('Wood', WOOD), bevel=False, smooth=shade == 'Smooth')
            b.data.set_sharp_from_angle(angle=np.radians(30))
            b.modifiers.new('Bevel', 'BEVEL').segments = seg
            b.modifiers['Bevel'].width = 2 / 64 * 0.6
            balls.append(b)
    curves, more = style_gate.gate(balls[-5:], style, 'prop')
    assert more['SM_KitTube']['curve_waste'] == 26 * 8, 'height loops with no ink line: %s' % more['SM_KitTube']
    over_fine = {f['object'] for f in curves if f['rule'] == 'curve'}
    assert over_fine == {'SM_KitTube', 'SM_Bevel4Flat', 'SM_Bevel4Smooth'}, \
        'bevels flat and smooth: %s' % {n: f.get('curve_waste_share') for n, f in more.items()}
    for seg in (3, 4):
        flat_share, smooth_share = (more['SM_Bevel%d%s' % (seg, s)]['curve_waste_share'] for s in ('Flat', 'Smooth'))
        assert abs(flat_share - smooth_share) < 0.02, 'a %d-segment bevel reads %s flat, %s smooth' % (
            seg, flat_share, smooth_share)
    # over the band in a class with no curve limit: the curve share failed nothing, but it is named as where to cut,
    # not "more parts than the band affords"
    got, _ = style_gate.gate([balls[0]], dict(style, triangles={'hero': [12, 800]}), 'hero')
    assert [f['rule'] for f in got] == ['triangles'] and ' failed no limit for hero, but cut there first (fewer ' \
        'segments round curves)' in got[0]['message'] and 'curve_waste_share' in got[0]['message'], \
        'over the band with an unlimited curve share: %s' % got
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
    # a coloured material keeping Blender's name is named, not the default; a near-white role is confirmed, not pure
    # white; a Boolean in Transfer mode adds the cutter's material, which FBX ships, to the evaluated slots
    named = crate('SM_Named', material('Material', WOOD))
    snow = crate('SM_Snow', ('Snow', (0.99, 0.99, 0.99)))
    booled = crate('SM_Booled', ('Wood', WOOD))
    bool_cut = crate('SM_BoolCut', ('Stone', STONE), size=0.3)
    bool_cut.location = 0.3 * np.sign(contact_sheet.direction(45, 30))     # the corner the game camera sees
    cut = booled.modifiers.new('Cut', 'BOOLEAN')
    cut.object, cut.material_mode = bool_cut, 'TRANSFER'
    # a closed box wound inside out shows its far inside in the game (ForwardLit culls back faces); a mirrored
    # object's matrix turns the winding back, so it is not one
    inverted, mirrored = crate('SM_Inverted', ('Wood', WOOD)), crate('SM_Mirrored', ('Wood', WOOD))
    inverted.data.flip_normals()
    mirrored.scale.x = -1
    # one flipped face on a closed box (its volume stays positive) is culled the same way; a lid welded onto its body
    # (Merge by Distance) keeps the wall between them inside the mesh; a part hidden in the viewport is skipped by an
    # export by selection; a Principled behind a Mix Shader exports the viewport colour and no texture
    flipped = crate('SM_Flipped', ('Wood', WOOD))
    flipped.data.polygons[0].flip()
    welded = crate('SM_Welded', ('Wood', WOOD), bevel=False)
    bm = bmesh.new()
    bm.from_mesh(welded.data)
    made = bmesh.ops.create_cube(bm, size=0.6)['verts']
    bmesh.ops.scale(bm, vec=(1.0, 1.0, 1 / 6), verts=made)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.35), verts=made)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.to_mesh(welded.data)
    bm.free()
    ghost = crate('SM_Ghost', ('Wood', WOOD))
    behind = material('M_Behind', WOOD, WOOD)
    mix_shader = behind.node_tree.nodes.new('ShaderNodeMixShader')
    behind.node_tree.links.new(style_gate.principled(behind).outputs[0], mix_shader.inputs[1])
    behind.node_tree.links.new(mix_shader.outputs[0], next(
        n for n in behind.node_tree.nodes if n.type == 'OUTPUT_MATERIAL').inputs['Surface'])
    mixed_up = crate('SM_Behind', behind)
    bpy.context.view_layer.update()
    ghost.hide_set(True)
    roofed = dict(style, palette=dict(style['palette'], Roof={'srgb': list(RED)}, Grey={'srgb': [0.906] * 3},
                                      Snow={'srgb': [0.99] * 3}))
    extra, extra_facts = style_gate.gate([lightmapped, roof, empty, scatter, linked, no_uv, rerouted, mapped, uv_node,
                                          grey, named, snow, booled, inverted, mirrored, flipped, welded, ghost,
                                          mixed_up], roofed)
    rules = {}
    for fl in extra:
        rules.setdefault(fl['object'], set()).add(fl['rule'])
    said_of = {fl['object']: fl['message'] for fl in extra}
    for name, rule, words in (('SM_Flipped', 'mesh', 'edge(s) join faces wound opposite ways'),
                              ('SM_Welded', 'mesh', 'inner wall face(s) a weld, Mirror or Array merge left'),
                              ('SM_Ghost', 'mesh', 'SM_Ghost is hidden in the viewport'),
                              ('SM_Behind', 'material', 'reaches the output through Mix Shader')):
        assert [f['rule'] for f in extra if f['object'] == name and words in f['message']] == [rule], \
            '%s, expected [%s] "%s": %s' % (name, rule, words, [f for f in extra if f['object'] == name])
    assert rules['SM_Flipped'] == rules['SM_Ghost'] == {'mesh'} and rules['SM_Behind'] == {'material'}, \
        'a flipped face, a hidden part or a Principled behind a node failed another rule too: %s' % rules
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
    assert rules.get('SM_Named') == {'material'} and "carries Blender's default name" in said_of['SM_Named'], \
        'a coloured Material.NNN: %s' % [f for f in extra if f['object'] == 'SM_Named']
    assert 'SM_Snow' not in rules, 'a near-white role read as pure white: %s' % [f for f in extra
                                                                                if f['object'] == 'SM_Snow']
    assert 'SM_Booled' not in rules, 'a Boolean Transfer material: %s' % [f for f in extra
                                                                         if f['object'] == 'SM_Booled']
    assert rules.get('SM_Inverted') == {'mesh'} and 'inside out, recalc normals' in said_of['SM_Inverted'], \
        'an inside-out box: %s' % [f for f in extra if f['object'] == 'SM_Inverted']
    assert 'SM_Mirrored' not in rules, 'a mirrored box: %s' % [f for f in extra if f['object'] == 'SM_Mirrored']
    # a part with no classed root is an asset of its own: under the band, the remedy says to parent it; a classed root
    # under the band is not told to
    loose = crate('SM_Loose', ('Wood', WOOD))
    del loose['style_class']
    got, _ = style_gate.gate([loose, good], dict(style, triangles={'prop': [2000, 4000]}), 'prop')
    hint = {f['object'] for f in got if 'parent the asset\'s parts under one root' in f['message']}
    assert hint == {'SM_Loose'}, 'the parenting hint went to %s: %s' % (hint, got)
    # an asset smaller than the class's typical one (camera.asset_m 0.6) is held to a proportionally lower floor: the
    # 0.3 m crate's 108 triangles pass the band 150-800 at its own floor 75, where the 0.6 m crate fails unscaled;
    # under 300-800 the message names the scaled floor and where it comes from
    half = crate('SM_Half', ('Wood', WOOD), size=0.3)
    got, _ = style_gate.gate([half, good], dict(style, triangles={'prop': [150, 800]}))
    under = {f['object']: f['message'] for f in got if f['rule'] == 'triangles'}
    assert list(under) == ['SM_Good'] and under['SM_Good'].startswith(
        '108 triangles under the prop band 150-800: add the detail'), 'the band floor by size: %s' % under
    got, _ = style_gate.gate([half], dict(style, triangles={'prop': [300, 800]}))
    assert ["108 triangles under the prop band 150-800 (the band's 300 scaled by the asset's 0.30 m against asset_m "
            '0.6): add the detail' in f['message'] for f in got if f['rule'] == 'triangles'] == [True], \
        'the scaled floor is not named: %s' % got
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
    # the same Empty beside the asset is in no count either: a fact (the CLI's STYLE NOTE), not this asset's failure
    em.parent = None
    got, got_facts = style_gate.gate([host], style)
    assert not any(f['rule'] == 'instances' for f in got) and got_facts.get('EM_Bolts', {}).get(
        'uncounted_instances') == 1, 'a collection instance beside the asset: %s %s' % (got, got_facts.get('EM_Bolts'))
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
    # a 1.2 m accent plank through the 0.6 m body: no triangle of either is wholly inside the other, so none is hidden,
    # and the accent share is about the plank's visible area (0.26 of 2.40 m2)
    planked = crate('SM_Planked', ('Wood', WOOD))
    plank = crate('SM_Plank', ('Trim', RED), size=0.1)
    del plank['style_class']
    plank.parent, plank.scale = planked, (12.0, 1.0, 1.0)
    bpy.context.view_layer.update()
    _, got = style_gate.gate([planked, plank], dict(style, accent_max_share=None))
    assert got['SM_Planked']['hidden_share'] == 0 and abs(got['SM_Planked']['accent_share'] - 0.108) < 0.03, \
        'a plank through the body: %s' % got['SM_Planked']
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
    # a lid on the body's footprint, in the body's mesh: the two boxes share four whole edges and stay two closed
    # parts, so the body's top and the lid's bottom (4 of 24 triangles) are hidden
    lidded = crate('SM_Lidded', ('Wood', WOOD), bevel=False)
    bm = bmesh.new()
    bm.from_mesh(lidded.data)
    made = bmesh.ops.create_cube(bm, size=0.6)['verts']
    bmesh.ops.scale(bm, vec=(1.0, 1.0, 1 / 6), verts=made)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.35), verts=made)
    bm.faces.index_update()
    closed = style_gate.closed_parts(bm, *style_gate.loose_parts(bm), False)
    bm.to_mesh(lidded.data)
    bm.free()
    got, facts_l = style_gate.gate([lidded], dict(style, hidden_max_share=0.05))
    assert len(closed) == 2 and 'hidden' in {f['rule'] for f in got} and facts_l['SM_Lidded'][
        'hidden_share'] == 0.167, 'a flush lid: %d closed part(s), %s %s' % (len(closed), got, facts_l['SM_Lidded'])
    for most, fails in ((1, True), ({'prop': 2}, False)):
        got, _ = style_gate.gate([trimmed, trim], dict(style, materials_max=most))
        assert any(f['rule'] == 'materials' for f in got) == fails, 'materials_max %s: %s' % (most, got)
    # the remedy offers the palette atlas only to a game that has one
    for density, tail in ((None, 'read the same at game size'), ('atlas', 'or use the palette atlas')):
        got, _ = style_gate.gate([trimmed, trim], dict(style, materials_max=1, texel_density=density))
        assert [f['message'] for f in got if f['rule'] == 'materials'][0].endswith(tail), 'materials remedy: %s' % got
    # each material is a submesh per part, drawn twice only where the game draws the ink line
    for outline, draws in ((True, 'as this asset is (ForwardLit + Outline pass), and separate parts multiply the draws '
                                  '(2 submeshes in 2 parts: join them into one mesh)'),
                           (False, 'which this asset is not (one ForwardLit draw each)')):
        got, _ = style_gate.gate([trimmed, trim], dict(style, materials_max=1, outline=outline))
        assert draws in [f['message'] for f in got if f['rule'] == 'materials'][0], 'materials draws: %s' % got
    # and a game with the atlas maps every material to it: a flat colour fails
    got, _ = style_gate.gate([good], dict(style, texel_density='atlas'))
    assert any(f['rule'] == 'material' and 'texel_density is atlas' in f['message'] for f in got), \
        'a flat colour under the atlas: %s' % got
    # a leftover Principled ahead of the wired one is not the one judged
    leftover = bpy.data.materials.new('M_Leftover')
    wired = leftover.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output = next(n for n in leftover.node_tree.nodes if n.type == 'OUTPUT_MATERIAL')
    leftover.node_tree.links.new(wired.outputs['BSDF'], output.inputs['Surface'])
    assert style_gate.principled(leftover).name == wired.name, 'principled() took the leftover node'
    # a hex or 0-255 colour (palette, accent, the light's two, the ink's) stops the gate's CLI and the sheet's with the
    # key and the field to copy; a role written as a bare list stops them with the form a role takes
    hexed = os.path.join(out, 'style_hex.json')
    copy = 'toon_albedo_srgb'
    for key, bad, remedy in (
            ('palette.Wood.srgb', dict(style, palette={'Wood': {'srgb': '#C8854D'}}), copy),
            ('accents[0]', dict(style, accents=['#F22619']), copy),
            ('light.color', dict(style, light=dict(style['light'], color='#FFF4D6')), copy),
            ('light.shadow_srgb', dict(style, light=dict(style['light'], shadow_srgb=[140, 128, 166])), copy),
            ('outline.srgb', dict(style, outline={'px': 1.5, 'srgb': '#5C4D75'}), copy),
            ('palette.Wood', dict(style, palette={'Wood': list(WOOD)}), '{"srgb": [r, g, b], "smoothness": 0-1}')):
        with open(hexed, 'w', encoding='utf-8') as f:
            json.dump(bad, f)
        sys.argv = ['blender', '--', '--style', hexed, '--report', os.path.join(out, 'hex.json')]
        for run in (style_gate.main, lambda: sheet(bad, out, 'HexSheet', 'SM_Good')):
            try:
                run()
                raise AssertionError('%s ran with a bad %s' % ('style_gate' if run is style_gate.main else 'the sheet',
                                                               key))
            except SystemExit as e:
                assert key + ' is ' in str(e) and remedy in str(e), e
    # off toon, a colour only in the viewport colour never reaches Unity; a Base Color typed in sRGB gets the remedy;
    # a texture's palette texels are exempt from value_range as a flat palette colour is
    viewport, _ = style_gate.gate([good], dict(style, shading='lit'))
    assert any(f['rule'] == 'material' and 'viewport' in f['message'] for f in viewport), viewport
    # with no Principled at the output the viewport colour is the one FBX carries: judged as the colour, off toon too
    bare = material('M_Bare', WOOD)
    bare.node_tree.nodes.remove(style_gate.principled(bare))
    bare = crate('SM_Bare', bare)
    got, _ = style_gate.gate([bare], dict(style, shading='lit'))
    assert not got, 'a viewport colour with no Principled at the output: %s' % got
    typed = crate('SM_Typed', None)
    typed.data.materials[0] = bpy.data.materials.new('M_Wood')
    style_gate.principled(typed.data.materials[0]).inputs['Base Color'].default_value = (*WOOD, 1.0)
    got, _ = style_gate.gate([typed], style)
    assert any('srgb_to_linear' in f['message'] for f in got), 'no sRGB remedy: %s' % got
    got, _ = style_gate.gate([bpy.data.objects['SM_Atlas']], dict(style, value_range=[72, 92]))
    assert not [f for f in got if f['rule'] == 'texture'], 'palette texels judged by value_range: %s' % got
    for o in (lightmapped, roof, empty, scatter, linked, no_uv, host, cutter, hidden, part, rope, em, bolt, body, core,
              typed, label, labelled, buried, lidded, rerouted, mapped, uv_node, grey, named, snow, loose, planked,
              plank, inverted, mirrored, half, flipped, welded, ghost, mixed_up, bare):
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
        text = io.StringIO()
        try:
            with contextlib.redirect_stdout(text):
                style_gate.main()
            got = 0
        except SystemExit as e:
            got = e.code
        sys.stdout.write(text.getvalue())
        assert got == code, 'style_gate CLI --objects %s exited %s, expected %s' % (objects, got, code)
        # every run prints each asset's facts, a pass too: the numbers a rebuild steers by
        n = facts['SM_Good']['triangles']
        for want in ('STYLE FACTS SM_Good: %d triangles, band prop 12-800 (band_top_share %s), curve_waste_share 0.0, '
                     'flat_waste_share 0.0, hidden_share 0.0, largest parts: SM_Good %d; submeshes 1'
                     % (n, facts['SM_Good']['band_top_share'], n),
                     'STYLE GATE %s' % ('FAIL' if code else 'PASS')):
            assert want in text.getvalue(), 'style_gate CLI --objects %s did not print %r' % (objects, want)
    # a textured asset's line ends with the share of its texture off the palette (the last run checked every asset)
    want = 'submeshes 1; texture_off_palette %s' % facts['SM_Atlas']['texture_off_palette']
    assert any(ln.startswith('STYLE FACTS SM_Atlas: ') and ln.endswith(want) for ln in text.getvalue().splitlines()), \
        'SM_Atlas\'s STYLE FACTS line does not end with %r' % want
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
    # no light colour or direction set: the sheet's sun is the template Main scene's, warm, Unity Euler (50, -30, 0)
    default = contact_sheet.toon_params({})
    assert np.allclose(default['sun'], contact_sheet.linear([1.0, 0.957, 0.839])) and np.allclose(
        default['to_sun'], contact_sheet.direction(180 - -30, 50)), 'the default sun: %s' % default
    for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
        bpy.data.objects.remove(o)

    crops = os.path.join(out, 'crops.json')
    with open(crops, 'w', encoding='utf-8') as f:
        json.dump([{'file': 'shot0.png', 'rect': [0, 300, 700, 400], 'note': 'wood block'},
                   {'file': 'shot1.png', 'rect': [300, 500, 700, 250], 'kind': 'object', 'class': 'prop'},
                   {'file': 'shot1.png', 'rect': [1800, 900, 400, 300]}], f)     # runs off the 1920x1080 shot
    found_json, warm_json = os.path.join(out, 'style_metrics.json'), os.path.join(out, 'style_warm.json')
    with open(warm_json, 'w', encoding='utf-8') as f:
        json.dump(dict(style, light=warm), f)
    sys.argv = ['blender', '--', '--crops', crops, '--out', found_json, '--swatches', os.path.join(out, 'palette.png'),
                '--style', warm_json]
    _, text = said(extract_style.main)
    assert 'STYLE WARNING: crop 2 rect [1800, 900, 400, 300] runs off shot1.png (1920x1080): only ' \
        '[1800, 900, 120, 180] is measured' in text, 'no clipped-rect warning'
    assert '2 measured crop(s)' in text and os.path.isfile(os.path.join(out, 'crops.png')), 'no crops preview'
    with open(found_json, encoding='utf-8') as f:
        found = json.load(f)
    assert np.allclose(found['toon_lit'], lit, atol=1e-4), 'extract_style --style lit %s, expected %s' % (
        found['toon_lit'], lit)
    s0 = found['pooled']['palette'][0]
    want = linear_to_srgb(contact_sheet.linear(s0['srgb']) / lit)        # srgb is rounded to 3 places
    assert np.allclose(s0['toon_albedo_srgb'], want, atol=0.005), 'extract_style --style toon_albedo_srgb %s, ' \
        'expected %s' % (s0['toon_albedo_srgb'], want)
    measured = [c['file'] for c in found['crops']]
    assert measured == ['shot0.png', 'shot1.png'], 'extract_style measured an object crop: %s' % measured
    # a --style whose light.color is a hex stops the run with the form to write
    with open(hexed, 'w', encoding='utf-8') as f:
        json.dump(dict(style, light=dict(warm, color='#FFF4D6')), f)
    sys.argv[-1] = hexed
    try:
        extract_style.main()
        raise AssertionError('extract_style ran with a hex light.color')
    except SystemExit as e:
        assert 'light.color is ' in str(e) and 'write 3 numbers 0-1' in str(e), e
    assert near(found['pooled']['palette'], WOOD), 'extract_style CLI: no wood in the crop: %s' % found['pooled']
    assert os.path.isfile(os.path.join(out, 'palette.png')), 'extract_style wrote no swatch strip'
    # the lit band draws albedo x light, so no albedo reaches a swatch brighter than the light: the sky's blue (0.95)
    # is over the default warm sun's (about 0.89), so it is warned about and flagged with the colour the band draws;
    # the crops above hold no sky
    assert found['albedo_clipped'] == [], 'a wood crop flagged: %s' % found['albedo_clipped']
    sky_json = os.path.join(out, 'style_sky.json')
    sys.argv = ['blender', '--', '--images', shots[0], '--out', sky_json]
    _, text = said(extract_style.main)
    with open(sky_json, encoding='utf-8') as f:
        sky = json.load(f)
    clip = sky['albedo_clipped']
    assert len(clip) == 1 and clip[0]['channels'] == ['b'] and clip[0]['drawn_srgb'][2] < 0.9 and near(
        [(sky['pooled']['palette'] + sky['pooled']['accents'])[clip[0]['swatch'] - 1]], SKY), \
        'the sky swatch is not flagged: %s' % clip
    assert 'STYLE WARNING: swatch %d %s needs an albedo over 1 in b: the lit band under this light draws %s' % (
        clip[0]['swatch'], clip[0]['hex'], clip[0]['drawn_hex']) in text, 'no albedo warning for the sky'
    # a shot tagged with another colour profile than sRGB (Blender's own Display P3 one, as an iPhone screenshot
    # carries) is read as sRGB all the same: warned about once per file, an untagged shot not at all
    icc_file = os.path.join(bpy.utils.system_resource('DATAFILES'), 'colormanagement', 'icc', 'srgb_p3d65_display.icc')
    with open(icc_file, 'rb') as f:
        icc = f.read()
    p3 = os.path.join(out, 'shot_p3.png')
    spec = oiio.ImageSpec(64, 64, 3, oiio.UINT8)
    spec.attribute('ICCProfile', oiio.TypeDesc('uint8[%d]' % len(icc)), np.frombuffer(icc, np.uint8))
    buf = oiio.ImageBuf(spec)
    buf.set_pixels(oiio.ROI(), np.tile(np.float32(WOOD), (64, 64, 1)))
    assert buf.write(p3), buf.geterror()
    _, text = said(lambda: [read_rgb(p, long_side=None) for p in (p3, p3, shots[0])])
    assert text.count('STYLE WARNING: %s carries the colour profile ' % p3) == 1 and 'convert the shot to sRGB first' \
        in text and shots[0] not in text, 'the colour profile warning: %r' % text
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
    assert rep['motif_px'] is None and 'no face carries the boolean face attribute "motif"' in text, \
        'an untagged build: motif_px %s' % rep['motif_px']
    assert rep['motif_share'] is None and rep['layout']['game_row_extra'] == [], 'an untagged build: %s' % rep['layout']
    # the camera (yaw 45) stands on the sun's side (yaw -30): most of the view is in the lit band, no note
    assert rep['against_style']['lit_share'] >= contact_sheet.LIT_MIN and 'is in the lit band' not in text, \
        'a lit view got the shaded-side note: %s' % rep['against_style']
    spec = oiio.ImageBuf(png).spec()
    assert (spec.width, spec.height) == (3 * 128, 6 * 128), 'sheet is %dx%d' % (spec.width, spec.height)
    assert rep['layout']['references'] == ['shot1.png', 'shot1.png'], rep['layout']['references']
    # each reference tile's zoom: the object crop's own, none for the fitted --refs image
    assert rep['layout']['reference_zoom'][0] and rep['layout']['reference_zoom'][1:] == [None], \
        'reference_zoom %s' % rep['layout']['reference_zoom']
    game = srgb_to_lab(read_rgba(rep['game_tile'], long_side=None)[0]).reshape(-1, 3)
    # a one-pixel line round a 64 px asset is about 1% of the 128 px tile
    assert ink_share(style, rep['game_tile']) > 0.005, 'no outline in the game tile'
    lit = srgb_to_lab(linear_to_srgb(contact_sheet.toon_bands(contact_sheet.linear(WOOD),
                                                              contact_sheet.toon_params(style['light']))[0]))
    assert (np.linalg.norm(game - lit, axis=1) < 6).mean() > 0.1, 'the outline hull shades the lit band away'
    assert rep['against_style']['palette_coverage'] >= 0.85, 'look pass is off-palette: %s' % rep['against_style']
    # the atlas keeps smoothness 0.15 in alpha: drawn premultiplied, its wood would read at 15% and fall off-palette;
    # a STYLE.md with no "Motif:" line is warned about as a missing one is
    notes = os.path.join(out, 'STYLE.md')
    with open(notes, 'w', encoding='utf-8') as f:
        f.write('# Style\nMotifs come later.\n')
    tag_motif(bpy.data.objects['SM_Atlas'], lambda n: n.z < -0.99)     # its bottom: under the game camera
    (_, rep), text = said(lambda: sheet(style, out, 'SM_Atlas', 'SM_Atlas'))
    assert rep['against_style']['palette_coverage'] >= 0.85, 'atlas look pass is off-palette: %s' % rep['against_style']
    assert rep['motif'] is False and 'has no line starting "Motif:"' in text, 'a STYLE.md without Motif: passed'
    assert rep['motif_px'] == 0 and "the motif covers 0 px of the game view (under 2 x 2): the motif's faces are " \
        'hidden or face away from the game camera (yaw 45): put the motif on a side this camera sees, or set ' \
        'camera.yaw' in text, 'a hidden motif: motif_px %s' % rep['motif_px']
    # a cutout under toon is drawn solid, as the game draws it, with one warning for all its views
    _, text = said(lambda: sheet(style, out, 'SM_Cut', 'SM_Cut', '--tile', '64'))
    assert text.count('SHEET WARNING: M_SM_Cut is a cutout, and Toon.shader has no alpha clip') == 1, \
        'the cutout warning: %s' % [ln for ln in text.splitlines() if 'cutout' in ln]
    # a style.json with no "outline" key gets Toon.shader's default line, as the game does
    crate('SM_NoKey', bpy.data.materials['M_Wood'])
    no_key = {k: v for k, v in style.items() if k != 'outline'}
    _, rep = sheet(no_key, out, 'SM_NoKey', 'SM_NoKey', '--tile', '128')
    assert rep['outlined'] == ['SM_NoKey'] and ink_share(style, rep['game_tile']) > 0.005, \
        'no "outline" key drew no line: outlined %s' % rep['outlined']
    # a camera looking straight down turns by its yaw: the sun (yaw -30) stands at -Y, the tile's bottom at yaw 0
    # (Blender Top, +Y up) and its top at yaw 180 (a Unity camera at Euler (90, 0, 0)), so the ball's lit side and
    # glossy spot lie in that half
    for yaw, lit_half in ((0, 'bottom'), (180, 'top')):
        sphere('SM_Down%d' % yaw, bpy.data.materials['M_Wood'])['outline'] = False
        _, rep = sheet(dict(style, camera=dict(style['camera'], pitch=90, yaw=yaw)), out, 'SM_Down%d' % yaw,
                       'SM_Down%d' % yaw, '--tile', '64')
        light = srgb_to_lab(read_rgba(rep['game_tile'], long_side=None)[0])[:, :, 0]
        gap = light[len(light) // 2:].mean() - light[:len(light) // 2].mean()        # bottom half over top half, L*
        assert (gap if lit_half == 'bottom' else -gap) > 1, \
            'pitch 90, yaw %d: the lit side is not in the %s half (L* gap %.2f)' % (yaw, lit_half, gap)
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
    # a Boolean in Transfer mode draws its cut faces in the cutter's material (Stone)
    for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
        bpy.data.objects.remove(o)
    _, rep = sheet(style, out, 'SM_Booled', 'SM_Booled', '--tile', '128')
    toon = contact_sheet.toon_params(style['light'])
    bands = [srgb_to_lab(linear_to_srgb(b)) for b in contact_sheet.toon_bands(contact_sheet.linear(STONE), toon)]
    tile = srgb_to_lab(read_rgba(rep['game_tile'], long_side=None)[0]).reshape(-1, 3)
    got = (np.linalg.norm(tile[:, None] - np.array(bands)[None], axis=2).min(axis=1) < 4).mean()
    assert got > 0.003 and rep['against_style']['palette_coverage'] >= 0.85, \
        'the Boolean Transfer material is not drawn: %.4f of the tile, %s' % (got, rep['against_style'])
    for o in (booled, bool_cut):
        bpy.data.objects.remove(o)
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
    tag_motif(crate('SM_MixProp', bpy.data.materials['M_Wood']), lambda n: n.z > 0.99)     # its lid
    crate('SM_MixBarrel', bpy.data.materials['M_Wood'], size=0.3)['style_class'] = 'barrel'
    for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
        bpy.data.objects.remove(o)
    (png, rep), text = said(lambda: sheet(style, out, 'SM_Mix', 'SM_MixProp,SM_MixBarrel', '--tile', '64',
                                          '--crops', mixed, '--golden', golden))
    os.remove(notes)
    assert rep['layout']['references'] == ['shot1.png', 'shot0.png', 'golden'], rep['layout']['references']
    assert rep['motif'] is True and 'STYLE.md' not in text, 'a STYLE.md with a Motif: line, motif %s' % rep['motif']
    assert rep['motif_px'] >= contact_sheet.MOTIF_MIN_PX and 'SHEET WARNING' not in text, \
        'a tagged lid: motif_px %s' % rep['motif_px']
    t = rep['layout']['tile_px']                    # --tile 64 is widened to the asset's game-size pixels
    # the lid is a share of the asset's game-view pixels, and its mask is the game row's fourth tile
    assert 0 < rep['motif_share'] < contact_sheet.MOTIF_MAX_SHARE and rep['layout']['game_row_extra'] == ['motif'] \
        and oiio.ImageBuf(png).spec().width == 4 * t, 'a tagged lid: motif_share %s, %s' % (rep['motif_share'],
                                                                                           rep['layout'])
    step = -(-150 // t)
    want = cells[::step, ::step]            # never scaled up: the golden keeps the zoom of the sheet it came from
    o = (t - len(want)) // 2
    y = rep['layout']['rows'].index('references') * t
    drawn = read_rgb(png, long_side=None)[y:y + t, 2 * t:3 * t, 0]
    assert np.array_equal(drawn[o:o + len(want), o:o + len(want)] > 0.5, want == 1) and abs(
        drawn[0, 0] - contact_sheet.GREY_BG) < 0.01, 'the golden tile is not drawn by whole pixels, padded grey'
    # its zoom is read off its 3 px blocks, and a zoom other than the asset tiles' gets the note
    gz = rep['layout']['golden_zoom']
    assert gz == round(3 / step, 2) and ('the golden tile is drawn at' in text) == (gz != rep['layout']['zoom']), \
        'golden_zoom %s beside zoom %s' % (gz, rep['layout']['zoom'])
    assert len(rep['layout']['reference_zoom']) == 3 and rep['layout']['reference_zoom'][-1] == gz, \
        'reference_zoom %s, the golden last' % rep['layout']['reference_zoom']
    # a tag on every face marks the asset, not its motif; a camera on the sun's far side (yaw -30 + 180) sees the lit
    # top over two shaded sides: under a third of the view in the lit band
    tag_motif(crate('SM_AllTagged', bpy.data.materials['M_Wood']), lambda n: True)
    for o in [o for o in bpy.data.objects if o.name.startswith('SHEET_')]:
        bpy.data.objects.remove(o)
    # references far louder than the asset (look.chroma_mean 90): a note that sends the colour lens to look, no warning
    (_, rep), text = said(lambda: sheet(dict(style, camera=dict(style['camera'], yaw=150), look={'chroma_mean': 90.0}),
                                        out, 'SM_AllTagged', 'SM_AllTagged', '--tile', '64'))
    assert 'SHEET NOTE: game view chroma_mean ' in text and 'a lead for the colour lens' in text \
        and 'SHEET WARNING: game view' not in text, 'the chroma gap: %s' % [ln for ln in text.splitlines()
                                                                           if 'chroma' in ln]
    assert rep['motif_share'] > contact_sheet.MOTIF_MAX_SHARE and 'SHEET WARNING: the motif tag covers most of the ' \
        'asset (%.0f%% of its game-view pixels)' % (100 * rep['motif_share']) in text, \
        'a tag on every face: motif_share %s' % rep['motif_share']
    lit_share = rep['against_style']['lit_share']
    assert lit_share < contact_sheet.LIT_MIN and 'SHEET NOTE: %.0f%% of the game view is in the lit band (under a ' \
        'third): the camera (yaw 150) looks at the side the sun (yaw -30) leaves in shade' % (100 * lit_share) \
        in text, 'the shaded side: lit_share %s' % lit_share

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

    # an atlas painted in memory comes back blank from a .blend saved without packing it: the gate fails it with the
    # remedy and the sheet warns; packed first, it passes (last: opening a file drops this run's fixtures)
    blend = os.path.join(out, 'atlas.blend')
    for pack in (False, True):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        atlas('SM_Mem', 0.0)
        if pack:
            bpy.data.images['T_SM_Mem'].pack()
        bpy.ops.wm.save_as_mainfile(filepath=blend)
        bpy.ops.wm.open_mainfile(filepath=blend)
        got, _ = style_gate.gate([bpy.data.objects['SM_Mem']], style)
        _, text = said(lambda: sheet(style, out, 'SM_Mem', 'SM_Mem', '--tile', '64'))
        warned = 'SHEET WARNING: T_SM_Mem was made in memory' in text
        if pack:
            assert not got and not warned, 'a packed atlas reopened: %s' % got
        else:
            assert [f['rule'] for f in got] == ['texture'] and 'image.pack() before saving' in got[0]['message'] \
                and warned and 'this sheet draws it blank' in text, 'an unsaved atlas reopened: %s' % got
    print('STYLE BIBLE PASS')


main()
