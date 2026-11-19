# Fails a built asset that leaves the game's style bible (style.json). Headless, on the saved .blend of the build:
#
#   blender --background --factory-startup --python-exit-code 1 <asset>.blend --python style_gate.py -- \
#       --style Tools/Blender/Style/style.json [--class prop] [--objects SM_A,SM_B] [--report gate.json]
#
# Exit 1 is a failed gate; every failure names the object or asset, the rule and the number. Checked: every mesh
# object (minus COL_ proxies and _LOD1+ children, unless --objects names some), on its evaluated mesh (modifiers
# applied, as exported); faces sharing an edge's two end positions count as joined, so split edges (Edge Split, a
# hard-edge export) do not read as loose parts, while a part touching at one point stays its own:
#   material  every used slot has a material; none is Blender's untouched default; the base colour is a flat colour
#             or an image texture (node-made colour does not reach Unity through FBX: bake it). The colour judged is
#             the one FBX carries, the Principled Base Color, then the viewport colour the toon pipeline's manifest
#             carries
#   palette   a flat colour sits within palette_de (CIELAB distance) of a palette role or an accent; an M_<Role>
#             material of the toon pipeline matches its own role
#   value     every colour's L* is inside value_range, and nothing is pure black (L* < 3) or pure white (L* > 97)
#   texture   sampled through the mesh's UVs (the texels the asset shows, not the whole atlas), weighted by surface
#             area: L* p2/p98 inside value_range (5 L* slack), at most texture_off_palette_max of the samples farther
#             than palette_de from every palette and accent colour. Alpha hides a texel only when the material's
#             Alpha takes the texture's alpha (a cutout); an atlas keeping smoothness in alpha is measured whole
#   detail    no loose part is smaller than detail_floor_m on its longest side: it vanishes at game size
#   texel     with a numeric texel_density (px/m), an image-textured material is within 10% of it
#   edges     with hard_edges_max_share set, the share of edges sharper than 80 degrees stays under it (a proxy for
#             bevel_m: the bevel width itself is not measurable from the mesh; the review sheet judges it)
# and per asset: the topmost object up the parent chain with "style_class" (on the object, not its mesh) and every
# mesh under it; without one, the topmost mesh. Parent a multi-part asset's parts under one root; an Empty that only
# groups props is not an asset. With --objects naming only some parts, the report lists the rest as unchecked_parts:
#   triangles the summed triangle count is inside triangles[<class>] (class from --class or the root's "style_class")
#   accent    the share of the surface nearest an accent colour stays under accent_max_share
#   waste     with flat_waste_max_share set, the share of triangles that only split flat faces stays under it: those
#             Limited Dissolve removes with nothing on screen changing (shape, shading, outline, material and UV map
#             kept; see flat_waste)

import argparse
import json
import math
import os
import re
import sys

import bmesh
import bpy
import numpy as np

sys.dont_write_bytecode = True     # no __pycache__ beside the plugin's scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_style import linear_to_srgb, read_rgba, srgb_to_lab  # noqa: E402

DEFAULT_RGB = (0.8, 0.8, 0.8)
LOD_CHILD = re.compile(r'_LOD[1-9]\d*$')
TEXTURE_SIDE = 1024        # textures are sampled at most this size: an atlas cell stays pixels wide, a 4K map 16 MB
TRI_SAMPLES = (4, 4096)     # samples per triangle: about one per texel it covers, within these bounds
MAX_SAMPLES = 2_000_000     # per material; past it every triangle's count shrinks in proportion
FLAT_DEG = 0.1              # faces and normals this close count as the same plane: float noise, not modelled shape


def is_default(rgb):
    return all(abs(a - b) < 1e-4 for a, b in zip(rgb, DEFAULT_RGB))


def principled(mat):
    return next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if mat.node_tree else None


def base_colour(mat):
    """('image', image node) | ('rgb', sRGB tuple) | ('nodes', node name) | ('default', None)."""
    bsdf = principled(mat)
    if bsdf is not None and bsdf.inputs['Base Color'].is_linked:
        src = bsdf.inputs['Base Color'].links[0].from_node
        if src.type == 'TEX_IMAGE' and src.image is not None:
            return 'image', src
        return 'nodes', src.name
    # FBX carries the Principled Base Color; the toon pipeline (toon_prop.py) leaves it default and keeps the palette
    # colour in the viewport colour, which its manifest carries
    for rgb in (tuple(bsdf.inputs['Base Color'].default_value)[:3] if bsdf else None, tuple(mat.diffuse_color)[:3]):
        if rgb is not None and not is_default(rgb):
            return 'rgb', tuple(float(c) for c in linear_to_srgb(rgb))
    return 'default', None


def is_cutout(mat, tex):
    """True when the material's Alpha takes this texture's alpha: only then is a low-alpha texel unseen."""
    bsdf = principled(mat)
    if bsdf is None or not bsdf.inputs['Alpha'].is_linked:
        return False
    link = bsdf.inputs['Alpha'].links[0]
    return link.from_node == tex and link.from_socket.name == 'Alpha'


_IMAGES = {}     # (image name, side) -> pixels, for one gate() run: a kit's 20 parts share one atlas read


def image_rgba(img, side=TEXTURE_SIDE):
    """(sRGB (h, w, 3), alpha (h, w)) of a texture, top row first, at most side on the long side; None without
    pixels (file missing and not packed)."""
    if (img.name, side) not in _IMAGES:
        _IMAGES[img.name, side] = read_image(img, side)
    return _IMAGES[img.name, side]


def read_image(img, side):
    path = bpy.path.abspath(img.filepath) if img.filepath else ''
    if path and os.path.isfile(path):
        return read_rgba(path, long_side=side)
    w, h = img.size
    if not w or not h:
        return None
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)      # a generated or packed image; Blender keeps the bottom row first
    step = max(1, math.ceil(max(w, h) / side))
    px = px.reshape(h, w, 4)[::-1][::step, ::step]
    rgb = linear_to_srgb(px[:, :, :3]) if img.is_float else px[:, :, :3]    # float buffers hold linear values
    return np.clip(rgb, 0.0, 1.0), px[:, :, 3]


def mesh_arrays(mesh, matrix):
    """Per loop triangle: material index, world area, and UVs (n, 3, 2) or None."""
    mesh.calc_loop_triangles()
    n = len(mesh.loop_triangles)
    co = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get('co', co)
    m = np.array(matrix)
    co = co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
    tv = np.empty(n * 3, np.int32)
    tl = np.empty(n * 3, np.int32)
    mi = np.empty(n, np.int32)
    mesh.loop_triangles.foreach_get('vertices', tv)
    mesh.loop_triangles.foreach_get('loops', tl)
    mesh.loop_triangles.foreach_get('material_index', mi)
    p = co[tv.reshape(-1, 3)]
    area = np.linalg.norm(np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), axis=1) / 2
    uv = None
    if mesh.uv_layers.active:
        u = np.empty(len(mesh.loops) * 2, np.float32)
        mesh.uv_layers.active.data.foreach_get('uv', u)
        uv = u.reshape(-1, 2)[tl.reshape(-1, 3)]
    return mi, area, uv


def wpercentile(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return np.interp(np.asarray(q) / 100.0, c / c[-1], x[o])


def check_object(obj, style, fail, info):
    """Every per-object rule on the mesh as exported; returns its triangles, world area and accent-coloured area."""
    eval_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = eval_obj.to_mesh()
    try:
        return check_mesh(obj.name, mesh, obj.matrix_world, style, fail, info)
    finally:
        eval_obj.to_mesh_clear()


def check_mesh(name, mesh, matrix, style, fail, info):
    pal = style.get('palette') or {}
    pal_lab = {r: srgb_to_lab(np.array(v['srgb'], float)) for r, v in pal.items()}
    accent_lab = [srgb_to_lab(np.array(a, float)) for a in style.get('accents', [])]
    allowed = list(pal_lab.items()) + [('accent', a) for a in accent_lab]
    de = float(style.get('palette_de', 6.0))
    lo, hi = style.get('value_range', [0.0, 100.0])
    mi, area, uv = mesh_arrays(mesh, matrix)
    accent_area = 0.0

    for i in sorted(set(mi.tolist())):
        sel = mi == i
        mat = mesh.materials[i] if i < len(mesh.materials) else None
        if mat is None:
            fail(name, 'material', 'slot %d has no material' % i)
            continue
        kind, val = base_colour(mat)
        if kind == 'default' or re.match(r'^Material(\.\d+)?$', mat.name):
            fail(name, 'material', '%s is the untouched default material' % mat.name)
        elif kind == 'nodes':
            fail(name, 'material', '%s takes its base colour from node %s, which FBX does not carry: bake it to an '
                 'image' % (mat.name, val))
        elif kind == 'rgb':
            lab = srgb_to_lab(np.array(val))
            if lab[0] < 3 or lab[0] > 97:
                fail(name, 'value', '%s is pure %s (L* %.0f)' % (mat.name, 'black' if lab[0] < 3 else 'white', lab[0]))
            elif not lo <= lab[0] <= hi:
                fail(name, 'value', '%s L* %.0f outside value_range %s-%s' % (mat.name, lab[0], lo, hi))
            if allowed:
                # M_Wood.001 (Blender's duplicate name) is still the Wood role
                role = re.sub(r'\.\d+$', '', mat.name[2:]) if mat.name.startswith('M_') else None
                if role in pal_lab:
                    d = float(np.linalg.norm(lab - pal_lab[role]))
                    if d > de:
                        fail(name, 'palette', '%s is %.1f from its role %s (palette_de %.0f)' % (mat.name, d, role, de))
                else:
                    near, d = min(((r, float(np.linalg.norm(lab - l))) for r, l in allowed), key=lambda t: t[1])
                    if d > de:
                        fail(name, 'palette', '%s is off-palette: nearest %s at %.1f (palette_de %.0f)'
                             % (mat.name, near, d, de))
                    elif near == 'accent':
                        accent_area += float(area[sel].sum())
        else:
            accent_area += check_image(name, mat, val, area[sel], None if uv is None else uv[sel],
                                       [a for _, a in allowed], len(pal_lab), de, lo, hi, style, fail, info)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.transform(matrix)
    bm.normal_update()
    bm.faces.index_update()
    # an Edge Split modifier or a hard-edge export cuts faces apart along edges: faces join where an edge's two end
    # positions match (0.01 mm grid), which a part touching the body at one vertex does not
    pos = {v: tuple(int(round(c * 1e5)) for c in v.co) for v in bm.verts}
    shared = {}
    for e in bm.edges:
        shared.setdefault(frozenset((pos[e.verts[0]], pos[e.verts[1]])), []).extend(e.link_faces)
    floor = style.get('detail_floor_m')
    if floor:
        part = list(range(len(bm.faces)))

        def find(i):
            while part[i] != i:
                part[i] = part[part[i]]
                i = part[i]
            return i

        for faces in shared.values():
            for f in faces[1:]:
                part[find(f.index)] = find(faces[0].index)
        lo_co, hi_co = {}, {}
        for f in bm.faces:
            co = np.array([v.co for v in f.verts])
            r = find(f.index)
            lo_co[r] = np.minimum(lo_co.get(r, co.min(0)), co.min(0))
            hi_co[r] = np.maximum(hi_co.get(r, co.max(0)), co.max(0))
        small = sum(1 for r in lo_co if (hi_co[r] - lo_co[r]).max() < floor)
        if small:
            fail(name, 'detail', '%d loose part(s) smaller than detail_floor_m %.3f m' % (small, floor))
    inner = [faces for faces in shared.values() if len(faces) == 2]
    hard = sum(1 for a, b in inner if a.normal.angle(b.normal, 0.0) > math.radians(80))
    share = hard / max(1, len(inner))
    info(name, 'hard_edge_share', round(share, 3))
    limit = style.get('hard_edges_max_share')
    if limit is not None and share > limit:
        fail(name, 'edges', '%.0f%% of edges are unbevelled hard corners (max %.0f%%; bevel_m %s)'
             % (share * 100, limit * 100, style.get('bevel_m')))
    removable = flat_waste(mesh, bm)
    info(name, 'flat_waste', removable)
    bm.free()
    return {'triangles': int(len(mi)), 'area': float(area.sum()), 'accent_area': accent_area, 'removable': removable}


def same_uv_map(faces, layers, tol=0.5 / TEXTURE_SIDE):
    """True when one affine position-to-UV map carries every corner of faces in every UV layer, so dissolving them
    interpolates the UVs as before (a 9-slice panel's stretched middle and its trim are two maps)."""
    loops = [lp for f in faces for lp in f.loops]
    p = np.array([lp.vert.co for lp in loops])
    p -= p[0]
    for layer in layers:
        uv = np.array([lp[layer].uv for lp in loops])
        uv -= uv[0]
        if np.abs(p @ np.linalg.lstsq(p, uv, rcond=None)[0] - uv).max() > tol:
            return False
    return True


def flat_waste(mesh, bm):
    """Triangles Limited Dissolve removes with the look unchanged, counted after triangulating (Unity gets triangles,
    not the n-gons). Only faces whose every corner normal is the face normal take part, so shading interpolates as
    before; faces join only on one material and one affine UV map; a vertex goes only from inside one plane, so the
    corners and edge midpoints that steer Toon.shader's outline hull stay. Consumes bm: written back, it is that
    optimised mesh. Ceiling: a split hard edge (Edge Split) is a border whose vertices stay, so the count errs low."""
    if not len(mesh.polygons):
        return 0
    cn = np.empty(len(mesh.loops) * 3, np.float32)
    mesh.corner_normals.foreach_get('vector', cn)
    pn = np.empty(len(mesh.polygons) * 3, np.float32)
    mesh.polygon_normals.foreach_get('vector', pn)
    start, total = (np.empty(len(mesh.polygons), np.int32) for _ in range(2))
    mesh.polygons.foreach_get('loop_start', start)
    mesh.polygons.foreach_get('loop_total', total)
    same = (cn.reshape(-1, 3) * np.repeat(pn.reshape(-1, 3), total, axis=0)).sum(1) > math.cos(math.radians(FLAT_DEG))
    flat = set(np.flatnonzero(np.minimum.reduceat(same.astype(np.int8), start)).tolist())   # bm keeps face order
    uvs = bm.loops.layers.uv.values()
    edges = [e for e in bm.edges if len(e.link_faces) == 2 and all(f.index in flat for f in e.link_faces)
             and same_uv_map(e.link_faces, uvs)]
    verts = [v for v in bm.verts if v.link_faces and all(f.index in flat for f in v.link_faces)
             and all(f.normal.angle(v.link_faces[0].normal, 0.0) <= math.radians(FLAT_DEG) for f in v.link_faces)
             and same_uv_map(v.link_faces, uvs)]
    before = sum(len(f.verts) - 2 for f in bm.faces)
    region = bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(FLAT_DEG), use_dissolve_boundaries=False,
                                      verts=verts, edges=edges, delimit={'MATERIAL'})['region']
    # only the merged faces: re-splitting an untouched curved quad along another diagonal would change its shape
    bmesh.ops.triangulate(bm, faces=[f for f in region if f.is_valid], quad_method='BEAUTY', ngon_method='BEAUTY')
    return before - sum(len(f.verts) - 2 for f in bm.faces)


def check_image(name, mat, tex, area, uv, refs, n_pal, de, lo, hi, style, fail, info):
    """The texture rules on the texels the mesh shows; returns the accent-coloured world area."""
    img = tex.image
    got = image_rgba(img)
    if got is None:
        fail(name, 'texture', '%s has no pixels (file missing and not packed)' % img.name)
        return 0.0
    rgb, alpha = got
    uv_area = None
    if uv is not None and len(uv):
        e1, e2 = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
        uv_area = np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]) / 2
        h, w = alpha.shape
        k = np.clip(np.ceil(uv_area * w * h), *TRI_SAMPLES).astype(int)
        if k.sum() > MAX_SAMPLES:
            k = np.maximum(1, (k * MAX_SAMPLES / k.sum()).astype(int))
        tri = np.repeat(np.arange(len(uv)), k)
        r1, r2 = np.random.default_rng(7).random((2, len(tri)))     # uniform points inside each triangle
        s = np.sqrt(r1)
        pts = np.einsum('nk,nkd->nd', np.stack([1 - s, s * (1 - r2), s * r2], axis=1), uv[tri])
        x = np.clip(np.floor((pts[:, 0] % 1.0) * w).astype(int), 0, w - 1)
        y = np.clip(np.floor((1.0 - pts[:, 1] % 1.0) * h).astype(int), 0, h - 1)
        rgb, alpha, weight = rgb[y, x], alpha[y, x], (area / k)[tri]
    else:                                                           # no UVs: the whole image stands in
        rgb, alpha = rgb.reshape(-1, 3), alpha.ravel()
        weight = np.full(len(alpha), area.sum() / max(1, len(alpha)))
    if is_cutout(mat, tex):
        keep = alpha >= 0.5
        if not keep.any():
            fail(name, 'texture', '%s is transparent everywhere the mesh samples it' % img.name)
            return 0.0
        rgb, weight = rgb[keep], weight[keep]
    if weight.sum() <= 0:
        return 0.0
    lab = srgb_to_lab(rgb)
    p2, p98 = wpercentile(lab[:, 0], weight, [2, 98])
    if p2 < lo - 5 or p98 > hi + 5:
        fail(name, 'texture', '%s L* p2-p98 %.0f-%.0f outside value_range %s-%s' % (img.name, p2, p98, lo, hi))
    accent_area = 0.0
    if refs:
        d, nearest = np.full(len(lab), np.inf), np.zeros(len(lab), int)
        for k, r in enumerate(refs):        # a running minimum: N x refs x 3 at once is hundreds of MB
            dk = np.linalg.norm(lab - r, axis=1)
            nearest = np.where(dk < d, k, nearest)
            d = np.minimum(d, dk)
        off = float(weight[d > de].sum() / weight.sum())
        info(name, 'texture_off_palette', round(off, 3))
        limit = style.get('texture_off_palette_max')
        if limit is not None and off > limit:
            fail(name, 'texture', '%s: %.0f%% of the shown texels off-palette (max %.0f%%)'
                 % (img.name, off * 100, limit * 100))
        accent_area = float(weight[(nearest >= n_pal) & (d <= de)].sum())
    target = style.get('texel_density')
    if isinstance(target, (int, float)) and uv_area is not None:
        density = math.sqrt(uv_area.sum() * img.size[0] * img.size[1] / area.sum()) if area.sum() > 0 else 0.0
        info(name, 'texel_density', round(density, 1))
        if abs(density - target) > 0.1 * target:
            fail(name, 'texel', '%s: %.0f px/m, style is %s px/m (10%% band)' % (mat.name, density, target))
    return accent_area


def root_of(obj):
    """The asset obj belongs to: its topmost ancestor (or itself) with "style_class", else its topmost mesh ancestor.
    An Empty that only groups props in the .blend is not an asset."""
    chain = []
    while obj is not None:
        chain.append(obj)
        obj = obj.parent
    classed = [o for o in chain if o.get('style_class') is not None]
    return classed[-1] if classed else [o for o in chain if o.type == 'MESH'][-1]


def parts_of(root):
    """The mesh objects the gate sums into root's asset (COL_ proxies and LOD1+ children left out)."""
    return [o for o in [root, *root.children_recursive] if o.type == 'MESH' and not o.name.startswith('COL_')
            and not LOD_CHILD.search(o.name) and root_of(o) == root]


def gate(objs, style, cls=None):
    """Runs every rule; returns (failures [{object, rule, message}], facts {name: {key: value}})."""
    failures, facts, assets = [], {}, {}
    _IMAGES.clear()

    def fail(o, rule, msg):
        failures.append({'object': o, 'rule': rule, 'message': msg})

    def info(o, k, v):
        facts.setdefault(o, {})[k] = v

    for obj in objs:
        got = check_object(obj, style, fail, info)
        info(obj.name, 'triangles', got['triangles'])
        root = root_of(obj)
        a = assets.setdefault(root.name, {'cls': None, 'triangles': 0, 'area': 0.0, 'accent_area': 0.0, 'removable': 0})
        a['cls'] = a['cls'] or cls or root.get('style_class') or obj.get('style_class')
        for k in ('triangles', 'area', 'accent_area', 'removable'):
            a[k] += got[k]

    bands = style.get('triangles') or {}
    limit = style.get('accent_max_share')
    checked = {o.name for o in objs}
    for name, a in assets.items():
        info(name, 'asset_triangles', a['triangles'])
        unchecked = [o.name for o in parts_of(bpy.data.objects[name]) if o.name not in checked]
        if unchecked:       # --objects named only some parts: the sums below leave these out
            info(name, 'unchecked_parts', unchecked)
        if bands:
            if a['cls'] not in bands:
                fail(name, 'triangles', 'no class: pass --class or set "style_class" on the asset root to one of %s'
                     % ', '.join(sorted(bands)))
            elif not bands[a['cls']][0] <= a['triangles'] <= bands[a['cls']][1]:
                fail(name, 'triangles', '%d triangles outside the %s band %d-%d'
                     % (a['triangles'], a['cls'], *bands[a['cls']]))
        share = a['accent_area'] / a['area'] if a['area'] > 0 else 0.0
        info(name, 'accent_share', round(share, 3))
        if limit is not None and share > limit:
            fail(name, 'accent', '%.0f%% of the surface is accent colour (accent_max_share %.0f%%)'
                 % (share * 100, limit * 100))
        waste = a['removable'] / max(1, a['triangles'])
        info(name, 'flat_waste_share', round(waste, 3))
        if style.get('flat_waste_max_share') is not None and waste > style['flat_waste_max_share']:
            fail(name, 'waste', '%d of %d triangles only split flat faces (%.0f%%, flat_waste_max_share %.0f%%): '
                 'Limited Dissolve removes them with the look unchanged' % (a['removable'], a['triangles'], waste * 100,
                                                                             style['flat_waste_max_share'] * 100))
    return failures, facts


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser(prog='style_gate.py')
    ap.add_argument('--style', required=True)
    ap.add_argument('--class', dest='cls')
    ap.add_argument('--objects')
    ap.add_argument('--report')
    args = ap.parse_args(argv)
    with open(args.style, encoding='utf-8') as f:
        style = json.load(f)
    if args.objects:
        names = args.objects.split(',')
        missing = [n for n in names if n not in bpy.data.objects]
        if missing:
            raise SystemExit('no such object(s): %s' % ', '.join(missing))
        objs = [bpy.data.objects[n] for n in names]
        not_mesh = [o.name for o in objs if o.type != 'MESH']
        if not_mesh:
            raise SystemExit('not mesh object(s): %s (name the mesh parts, not their root)' % ', '.join(not_mesh))
    else:
        objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('COL_')
                and not LOD_CHILD.search(o.name)]
    if not objs:
        raise SystemExit('no mesh objects to check')
    failures, facts = gate(objs, style, args.cls)
    report = {'style': os.path.abspath(args.style), 'objects': [o.name for o in objs], 'facts': facts,
              'failures': failures, 'pass': not failures}
    if args.report:
        with open(args.report, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(report, f, indent=1)
    for fl in failures:
        print('STYLE FAIL %s [%s] %s' % (fl['object'], fl['rule'], fl['message']))
    for name, f in facts.items():
        if 'unchecked_parts' in f:
            print('STYLE NOTE %s: parts %s not named in --objects, so its triangle and accent sums leave them out'
                  % (name, ', '.join(f['unchecked_parts'])))
    print('STYLE GATE %s: %d object(s), %d failure(s)' % ('PASS' if not failures else 'FAIL', len(objs), len(failures)))
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
