# Fails a built asset that leaves the game's style bible (style.json). Headless, on the saved .blend of the build:
#
#   blender --background --factory-startup --python-exit-code 1 <asset>.blend --python style_gate.py -- \
#       --style Tools/Blender/Style/style.json [--class prop] [--objects SM_A,SM_B] [--report gate.json]
#
# Exit 1 is a failed gate; every failure names the object, the rule and the number. Checked per mesh object (all of
# them, minus COL_ proxies and _LOD1+ children, unless --objects names some):
#   material  every used slot has a material; none is Blender's untouched default; the base colour is a flat colour
#             or an image texture (node-made colour does not reach Unity through FBX: bake it)
#   palette   a flat colour sits within palette_de (CIELAB distance) of a palette role; an M_<Role> material of the
#             toon pipeline matches its own role
#   value     every colour's L* is inside value_range, and nothing is pure black (L* < 3) or pure white (L* > 97)
#   texture   an image's L* p2/p98 stay inside value_range (5 L* slack), and at most texture_off_palette_max of its
#             pixels are farther than palette_de from every palette and accent colour
#   triangles the evaluated triangle count is inside triangles[<class>] (class from --class or the object's
#             "style_class" property)
#   detail    no loose part is smaller than detail_floor_m on its longest side: it vanishes at game size
#   texel     with a numeric texel_density (px/m), an image-textured object is within 10% of it
#   edges     with hard_edges_max_share set, the share of unbevelled edges sharper than 80 degrees stays under it
#             (a proxy for bevel_m: the bevel width itself is not measurable from the mesh; the review sheet judges it)

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
from extract_style import LONG_SIDE, linear_to_srgb, read_rgba, srgb_to_lab  # noqa: E402

DEFAULT_RGB = (0.8, 0.8, 0.8)
LOD_CHILD = re.compile(r'_LOD[1-9]\d*$')


def is_default(rgb):
    return all(abs(a - b) < 1e-4 for a, b in zip(rgb, DEFAULT_RGB))


def base_colour(mat):
    """('image', bpy image) | ('rgb', sRGB tuple) | ('nodes', node name) | ('default', None)."""
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if mat.node_tree else None
    if bsdf is not None and bsdf.inputs['Base Color'].is_linked:
        src = bsdf.inputs['Base Color'].links[0].from_node
        if src.type == 'TEX_IMAGE' and src.image is not None:
            return 'image', src.image
        return 'nodes', src.name
    # the toon pipeline (toon_prop.py) keeps the palette colour in the viewport colour; the manifest carries it
    for rgb in (tuple(mat.diffuse_color)[:3], tuple(bsdf.inputs['Base Color'].default_value)[:3] if bsdf else None):
        if rgb is not None and not is_default(rgb):
            return 'rgb', tuple(float(c) for c in linear_to_srgb(rgb))
    return 'default', None


def image_rgba(img):
    """(sRGB, alpha) of a texture at most LONG_SIDE on the long side, or None when it has no pixels."""
    path = bpy.path.abspath(img.filepath) if img.filepath else ''
    if path and os.path.isfile(path):
        return read_rgba(path)
    w, h = img.size
    if not w or not h:
        return None
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)      # a generated or packed image: its stored values, sRGB for byte images
    step = max(1, math.ceil(max(w, h) / LONG_SIDE))
    px = px.reshape(h, w, 4)[::step, ::step]
    return px[:, :, :3], px[:, :, 3]


def check_object(obj, style, cls, fail, info):
    """Every rule on the mesh as exported: the evaluated one, modifiers applied."""
    eval_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = eval_obj.to_mesh()
    try:
        check_mesh(obj.name, mesh, obj.matrix_world, style, cls, fail, info)
    finally:
        eval_obj.to_mesh_clear()


def check_mesh(name, mesh, matrix, style, cls, fail, info):
    pal = style.get('palette') or {}
    pal_lab = {r: srgb_to_lab(np.array(v['srgb'], float)) for r, v in pal.items()}
    accent_lab = [srgb_to_lab(np.array(a, float)) for a in style.get('accents', [])]
    allowed = list(pal_lab.items()) + [('accent', a) for a in accent_lab]
    de = float(style.get('palette_de', 6.0))
    lo, hi = style.get('value_range', [0.0, 100.0])
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.transform(matrix)
    world_area = sum(f.calc_area() for f in bm.faces)

    used = {p.material_index for p in mesh.polygons}
    for i in sorted(used):
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
                role = mat.name[2:] if mat.name.startswith('M_') else None
                if role in pal_lab:
                    d = float(np.linalg.norm(lab - pal_lab[role]))
                    if d > de:
                        fail(name, 'palette', '%s is %.1f from its role %s (palette_de %.0f)' % (mat.name, d, role, de))
                else:
                    near, d = min(((r, float(np.linalg.norm(lab - l))) for r, l in allowed), key=lambda t: t[1])
                    if d > de:
                        fail(name, 'palette', '%s is off-palette: nearest %s at %.1f (palette_de %.0f)'
                             % (mat.name, near, d, de))
        else:
            check_image(name, mesh, world_area, val, [a for _, a in allowed], de, lo, hi, style, fail, info)

    mesh.calc_loop_triangles()
    tris = len(mesh.loop_triangles)
    info(name, 'triangles', tris)
    bands = style.get('triangles') or {}
    if bands:
        if cls not in bands:
            fail(name, 'triangles', 'no class: pass --class or set the object\'s "style_class" to one of %s'
                 % ', '.join(sorted(bands)))
        elif not bands[cls][0] <= tris <= bands[cls][1]:
            fail(name, 'triangles', '%d triangles outside the %s band %d-%d' % (tris, cls, *bands[cls]))

    floor = style.get('detail_floor_m')
    if floor:
        seen, small = set(), 0
        for f in bm.faces:
            if f.index in seen:
                continue
            stack, part = [f], []
            seen.add(f.index)
            while stack:
                cur = stack.pop()
                part.append(cur)
                for e in cur.edges:
                    for nb in e.link_faces:
                        if nb.index not in seen:
                            seen.add(nb.index)
                            stack.append(nb)
            co = np.array([v.co for p in part for v in p.verts])
            if (co.max(0) - co.min(0)).max() < floor:
                small += 1
        if small:
            fail(name, 'detail', '%d loose part(s) smaller than detail_floor_m %.3f m' % (small, floor))
    inner = [e for e in bm.edges if len(e.link_faces) == 2]
    hard = sum(1 for e in inner if e.calc_face_angle(0.0) > math.radians(80))
    share = hard / max(1, len(inner))
    info(name, 'hard_edge_share', round(share, 3))
    limit = style.get('hard_edges_max_share')
    if limit is not None and share > limit:
        fail(name, 'edges', '%.0f%% of edges are unbevelled hard corners (max %.0f%%; bevel_m %s)'
             % (share * 100, limit * 100, style.get('bevel_m')))
    bm.free()


def check_image(name, mesh, area, img, refs, de, lo, hi, style, fail, info):
    got = image_rgba(img)
    if got is None:
        fail(name, 'texture', '%s has no pixels (file missing and not packed)' % img.name)
        return
    rgb, alpha = got
    opaque = alpha >= 0.5            # a cutout's transparent texels are never seen
    if not opaque.any():
        fail(name, 'texture', '%s is fully transparent' % img.name)
        return
    lab = srgb_to_lab(rgb[opaque])
    p2, p98 = np.percentile(lab[:, 0], [2, 98])
    if p2 < lo - 5 or p98 > hi + 5:
        fail(name, 'texture', '%s L* p2-p98 %.0f-%.0f outside value_range %s-%s' % (img.name, p2, p98, lo, hi))
    limit = style.get('texture_off_palette_max')
    if refs and limit is not None:
        d = np.full(len(lab), np.inf)
        for r in refs:                  # a running minimum: N x refs x 3 at once is hundreds of MB
            d = np.minimum(d, np.linalg.norm(lab - r, axis=1))
        off = float((d > de).mean())
        info(name, 'texture_off_palette', round(off, 3))
        if off > limit:
            fail(name, 'texture', '%s: %.0f%% of pixels off-palette (max %.0f%%)' % (img.name, off * 100, limit * 100))
    target = style.get('texel_density')
    if isinstance(target, (int, float)) and mesh.uv_layers.active:
        uv = mesh.uv_layers.active.data
        uv_area = 0.0
        for p in mesh.polygons:
            pts = [uv[li].uv for li in p.loop_indices]
            uv_area += abs(sum(pts[i].x * pts[i - 1].y - pts[i - 1].x * pts[i].y for i in range(len(pts)))) / 2
        w, h = img.size
        density = math.sqrt(uv_area * w * h / area) if area > 0 else 0.0
        info(name, 'texel_density', round(density, 1))
        if abs(density - target) > 0.1 * target:
            fail(name, 'texel', '%.0f px/m, style is %s px/m (10%% band)' % (density, target))


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
    else:
        objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('COL_')
                and not LOD_CHILD.search(o.name)]
    if not objs:
        raise SystemExit('no mesh objects to check')
    failures, facts = [], {}
    for obj in objs:
        check_object(obj, style, args.cls or obj.get('style_class'),
                     lambda o, rule, msg: failures.append({'object': o, 'rule': rule, 'message': msg}),
                     lambda o, k, v: facts.setdefault(o, {}).__setitem__(k, v))
    report = {'style': os.path.abspath(args.style), 'objects': [o.name for o in objs], 'facts': facts,
              'failures': failures, 'pass': not failures}
    if args.report:
        with open(args.report, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(report, f, indent=1)
    for fl in failures:
        print('STYLE FAIL %s [%s] %s' % (fl['object'], fl['rule'], fl['message']))
    print('STYLE GATE %s: %d object(s), %d failure(s)' % ('PASS' if not failures else 'FAIL', len(objs), len(failures)))
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
