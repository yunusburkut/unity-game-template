# The review sheet of a built asset, pinned so every iteration and every asset is judged the same way. Headless, on
# the saved .blend of the build (it never saves the file):
#
#   blender --background --factory-startup --python-exit-code 1 <asset>.blend --python contact_sheet.py -- \
#       --style Tools/Blender/Style/style.json --out <asset>_sheet.png [--crops crops.json] [--class prop]
#       [--refs a.png b.png] [--golden Tools/Blender/Style/golden.png] [--objects SM_A] [--tile 256]
#
# Rows: front, right, back, top (orthographic) and the game camera (style.json camera: pitch, yaw, projection).
# Columns: silhouette (black on white), clay (grey studio light, cavity) and look. Each view renders at the game's
# 1080p scale, camera.asset_px pixels per camera.asset_m metres (the typical prop's height, default 1), so a hero
# draws larger than a prop (past 1024 px it shrinks to fit: layout.render_scale < 1 and a SHEET WARNING); the tile
# scales it up by whole pixels, so detail that is lost in the game is lost here too. A last row holds the references: the "kind": "object" crops of crops.json (those of
# --class, or with no class), else its surface crops, then whole --refs images, then the golden asset.
# <out>_game.png is the game-view look tile alone: the golden asset's one becomes golden.png.
#
# The look pass copies the Unity shading model from style.json "shading", with the light from "light":
#   toon    __GAME__/Toon's bands: the colour where N.L is over light.band (Toon.shader _RampOffset, default 0.05) and
#           the asset does not shadow itself, else lerp(luminance, colour, light.shade_saturation 1.3) x
#           light.shadow_srgb; both plus colour x light.ambient (the scene's SH level, default 0.5) x 0.18. No gloss
#           spot or rim (they follow smoothness and the view)
#   flat    the colour unlit
#   lit, painted   Principled with the colour or image and the material's roughness, a sun and a grey ambient
# "outline" (true, or {"px": 1.5, "srgb": [0.36, 0.30, 0.46]}, Toon.shader's defaults) adds the inverted-hull ink line
# at px 1080p pixels, coloured albedo x srgb. It is a Blender stand-in, not the Unity render: the final judgement is an
# in-engine screenshot.
#
# <out>.json beside the sheet: the layout; extract_style's numbers measured on the game tile (asset pixels one pixel
# in from the edge) next to style.json "look" (the reference numbers, same 1080p pixel scale); inside_value_range; and
# palette_coverage, the share of asset pixels within palette_de of a palette or accent colour as this shading draws it
# (lit band, shade band, ink). A toon or flat asset on palette reads 0.85 or more; lit and painted vary with the
# light, so compare with the golden asset's number.

import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile

import bpy
import numpy as np
import OpenImageIO as oiio
from mathutils import Vector

sys.dont_write_bytecode = True     # no __pycache__ beside the plugin's scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_style import SCREEN_H, linear_to_srgb, metrics, pixels, read_rgb, read_rgba, srgb_to_lab  # noqa: E402
from style_gate import LOD_CHILD, base_colour, is_cutout, root_of  # noqa: E402

VIEWS = [('front', 0.0, 0.0), ('right', 90.0, 0.0), ('back', 180.0, 0.0), ('top', 0.0, 90.0)]
GREY_BG = 0.55
AMBIENT_STRENGTH = 0.18          # Toon.shader _AmbientStrength
OUTLINE = {'px': 1.5, 'srgb': [0.36, 0.30, 0.46]}     # Toon.shader _OutlineWidth, _OutlineColor
LOOK_KEYS = ('detail_energy', 'dark_edge_share', 'chroma_mean', 'accent_share')


def direction(yaw, pitch):
    """Unit vector from the asset toward the eye; yaw 0, pitch 0 is Blender's Front view (from -Y)."""
    y, p = math.radians(yaw), math.radians(pitch)
    return Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))


def aim(obj, d):
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = (-d).to_track_quat('-Z', 'Z' if abs(d.z) < 0.999 else 'Y')


def linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def toon_params(light):
    return {'shadow': linear(light.get('shadow_srgb', [0.62, 0.62, 0.86])),     # Toon.shader _ShadeColor
            'saturation': float(light.get('shade_saturation', 1.3)),
            'ambient': float(light.get('ambient', 0.5)) * AMBIENT_STRENGTH,
            # Shader to RGB of a white diffuse: world 0.25 + sun 3 W/m2 x N.L / pi; the band edge sits at N.L = band
            'edge': 0.25 + float(light.get('band', 0.05)) * 3.0 / math.pi}


def outline_cfg(style):
    o = style.get('outline')
    if not o:
        return None
    return {**OUTLINE, **(o if isinstance(o, dict) else {})}


def colour_node(nt, mat):
    kind, val = base_colour(mat)
    if kind == 'image':
        col = nt.nodes.new('ShaderNodeTexImage')
        col.image = val.image
        col.interpolation = val.interpolation
        if not is_cutout(mat, val):
            # alpha is data here (the toon-art atlas keeps smoothness in it); with the Alpha output unlinked Blender
            # premultiplies Color by it, Unity does not
            col.image.alpha_mode = 'CHANNEL_PACKED'
        return col.outputs['Color']
    col = nt.nodes.new('ShaderNodeRGB')
    col.outputs[0].default_value = (*linear(val if kind == 'rgb' else (1.0, 0.0, 1.0)), 1.0)
    return col.outputs[0]


def mix(nt, blend, a, b, factor=1.0):
    """A Mix (Color) node: a and b are sockets or RGB tuples; the RGBA inputs are 6 and 7, after the float/vector ones."""
    m = nt.nodes.new('ShaderNodeMix')
    m.data_type, m.blend_type, m.clamp_factor = 'RGBA', blend, False
    if isinstance(factor, float):
        m.inputs['Factor'].default_value = factor
    else:
        nt.links.new(factor, m.inputs['Factor'])
    for sock, v in ((m.inputs[6], a), (m.inputs[7], b)):
        if isinstance(v, (tuple, list, np.ndarray)):
            sock.default_value = (*[float(x) for x in v], 1.0)
        else:
            nt.links.new(v, sock)
    return m.outputs[2]


def emit(nt, colour):
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(colour, em.inputs['Color'])
    nt.links.new(em.outputs[0], out.inputs['Surface'])


def look_material(mat, shading, toon):
    """A render-only stand-in for mat that draws the style's shading model."""
    m = bpy.data.materials.new('LOOK_' + mat.name)
    nt = m.node_tree
    nt.nodes.clear()
    colour = colour_node(nt, mat)
    if shading == 'flat':
        emit(nt, colour)
    elif shading == 'toon':
        diff = nt.nodes.new('ShaderNodeBsdfDiffuse')
        diff.inputs['Color'].default_value = (1, 1, 1, 1)
        to_rgb = nt.nodes.new('ShaderNodeShaderToRGB')
        nt.links.new(diff.outputs[0], to_rgb.inputs[0])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'CONSTANT'
        ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
        ramp.color_ramp.elements[1].position = toon['edge']
        nt.links.new(to_rgb.outputs['Color'], ramp.inputs['Fac'])
        lum = nt.nodes.new('ShaderNodeRGBToBW')
        nt.links.new(colour, lum.inputs[0])
        shade = mix(nt, 'MIX', lum.outputs[0], colour, toon['saturation'])     # lerp(luminance, colour, saturation)
        shade = mix(nt, 'MULTIPLY', shade, toon['shadow'])
        band = mix(nt, 'MIX', shade, colour, ramp.outputs['Color'])
        k = toon['ambient']
        emit(nt, mix(nt, 'ADD', band, mix(nt, 'MULTIPLY', colour, (k, k, k))))
    else:
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        nt.links.new(colour, bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = mat.roughness
        nt.links.new(bsdf.outputs[0], out.inputs['Surface'])
    return m


def ink_material(mat, tint):
    """The outline hull's material: albedo x tint, unlit, back faces only (the hull's normals are flipped)."""
    m = bpy.data.materials.new('INK_' + mat.name)
    m.use_backface_culling = True
    # the hull's sun-side faces are back faces too: culled from the shadow map, or the hull shades the whole asset
    m.use_backface_culling_shadow = True
    nt = m.node_tree
    nt.nodes.clear()
    emit(nt, mix(nt, 'MULTIPLY', colour_node(nt, mat), linear(tint)))
    return m


def add_outlines(objs, cfg, width):
    """An inverted hull per object (Solidify outward, flipped normals, ink materials after the originals); returns
    the modifiers so the clay pass can hide them."""
    mods, offsets = [], {}
    for o in objs:
        if o.data.name not in offsets:
            mats = list(o.data.materials)
            offsets[o.data.name] = len(mats)
            for m in mats:
                o.data.materials.append(ink_material(m, cfg['srgb']) if m else None)
        mod = o.modifiers.new('SHEET_Outline', 'SOLIDIFY')
        # Solidify works in object units: divide out an unapplied scale so every part draws the same world width
        mod.thickness, mod.offset = width / max(1e-6, float(np.mean(o.matrix_world.to_scale()))), 1.0
        mod.use_flip_normals, mod.use_rim, mod.use_even_offset = True, False, True
        mod.material_offset = offsets[o.data.name]
        mods.append(mod)
    return mods


def drawn_colours(style, shading, toon, ink):
    """CIELAB of every palette and accent colour as the look pass draws it: lit band, shade band and ink for toon."""
    srgb = [v['srgb'] for v in (style.get('palette') or {}).values()] + list(style.get('accents', []))
    out = []
    for c in srgb:
        lin = linear(c)
        if shading == 'toon':
            lum = float(lin @ np.array([0.2126, 0.7152, 0.0722]))
            variants = [lin * (1 + toon['ambient']),
                        (lum + toon['saturation'] * (lin - lum)) * toon['shadow'] + lin * toon['ambient']]
        else:
            variants = [lin]
        if ink:
            variants.append(lin * linear(ink['srgb']))
        out += [srgb_to_lab(linear_to_srgb(np.clip(v, 0.0, 1.0))) for v in variants]     # the render clamps too
    return out


def to8(rgb):
    """0-1 float to 8-bit: the sheet is assembled at a quarter of float32's memory (a 1024 px asset: ~50 MB)."""
    return (np.clip(rgb, 0.0, 1.0) * 255 + 0.5).astype(np.uint8)


def write_png(rgb, path):
    buf = oiio.ImageBuf(oiio.ImageSpec(rgb.shape[1], rgb.shape[0], 3, oiio.UINT8))
    buf.set_pixels(oiio.ROI(), rgb if rgb.dtype == np.uint8 else to8(rgb))
    if not buf.write(path):
        raise SystemExit('cannot write %s: %s' % (path, buf.geterror()))


def ref_images(args):
    """(name, sRGB image) for the reference row: object crops of the class (else surface crops), then --refs."""
    out = []
    if args.crops:
        base = os.path.dirname(os.path.abspath(args.crops))
        with open(args.crops, encoding='utf-8') as f:
            crops = json.load(f)
        objects = [c for c in crops if c.get('kind') == 'object' and c.get('class') in (None, args.cls)]
        for c in objects or [c for c in crops if c.get('kind', 'surface') == 'surface']:
            path = os.path.join(base, c['file'])
            out.append((os.path.basename(c['file']), read_rgba(path, c.get('rect'), long_side=None)[0]))
    out += [(os.path.basename(p), read_rgba(p, long_side=None)[0]) for p in args.refs]
    return out


def upscale(img, size):
    """Nearest-neighbour to size x size by whole pixels (pads the rest), so game-size pixels stay visible."""
    k = max(1, size // max(img.shape[:2]))
    big = np.repeat(np.repeat(img, k, axis=0), k, axis=1)
    tile = np.full((size, size, img.shape[2]), 1.0, np.float32)
    h, w = min(size, big.shape[0]), min(size, big.shape[1])
    tile[:h, :w] = big[:h, :w]
    return tile


def fit(rgb, size):
    """A reference image scaled to the tile height (keeps aspect, centred on white)."""
    h, w = rgb.shape[:2]
    s = size / float(max(h, w))
    ys = np.clip((np.arange(int(h * s)) / s).astype(int), 0, h - 1)
    xs = np.clip((np.arange(int(w * s)) / s).astype(int), 0, w - 1)
    small = rgb[ys][:, xs]
    tile = np.ones((size, size, 3), np.float32)
    oy, ox = (size - small.shape[0]) // 2, (size - small.shape[1]) // 2
    tile[oy:oy + small.shape[0], ox:ox + small.shape[1]] = small
    return tile


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser(prog='contact_sheet.py')
    ap.add_argument('--style', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--crops')
    ap.add_argument('--class', dest='cls')
    ap.add_argument('--refs', nargs='*', default=[])
    ap.add_argument('--golden')
    ap.add_argument('--objects')
    ap.add_argument('--tile', type=int, default=256)
    args = ap.parse_args(argv)
    with open(args.style, encoding='utf-8') as f:
        style = json.load(f)
    cam_cfg, light = style.get('camera', {}), style.get('light', {})
    shading = style.get('shading', 'lit')
    toon, ink = toon_params(light), outline_cfg(style)
    px = int(cam_cfg.get('asset_px', 128))
    px_per_m = px / float(cam_cfg.get('asset_m', 1.0))
    stem = re.sub(r'\.[^.]+$', '', args.out)

    names = args.objects.split(',') if args.objects else None
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and (o.name in names if names else
            not o.name.startswith('COL_') and not LOD_CHILD.search(o.name))]
    if not objs:
        raise SystemExit('no mesh objects to render')
    for o in bpy.data.objects:
        o.hide_render = o not in objs and o.type == 'MESH'
    corners = np.array([o.matrix_world @ Vector(c) for o in objs for c in o.bound_box])
    centre = Vector(((corners.min(0) + corners.max(0)) / 2).tolist())
    radius = float(np.linalg.norm(corners - np.array(centre), axis=1).max())
    # one render pixel is one 1080p screen pixel: n pixels frame the asset's bounding sphere with a margin. Past 1024
    # pixels (a building at prop scale) the render shrinks to fit and the report says so
    need = max(16, math.ceil(radius * 2.1 * px_per_m))
    n = min(1024, need)
    render_scale = n / need
    if render_scale < 1:
        print('SHEET WARNING: the asset needs %d px at game scale; drawn at %.2f x, so pixel detail reads coarser than '
              'in the game' % (need, render_scale))
        px_per_m *= render_scale
    tile = max(args.tile, n)

    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = n
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'Standard'
    cam = bpy.data.objects.new('SHEET_Cam', bpy.data.cameras.new('SHEET_Cam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    sun = bpy.data.objects.new('SHEET_Sun', bpy.data.lights.new('SHEET_Sun', 'SUN'))
    sun.data.energy = 3.0
    sc.collection.objects.link(sun)
    aim(sun, direction(light.get('yaw', -30.0), light.get('pitch', 50.0)))
    sc.world = sc.world or bpy.data.worlds.new('SHEET_World')
    sc.world.color = (0.25, 0.25, 0.25)
    if sc.world.node_tree:
        bg = next((n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if bg:
            bg.inputs['Color'].default_value = (0.25, 0.25, 0.25, 1)
            bg.inputs['Strength'].default_value = 1.0

    originals = {o.name: [s.material for s in o.material_slots] for o in objs}
    # an asset the game draws without the line (toon_prop's "outline": False, kit and level pieces) says so on its root
    inked = [o for o in objs if ink and root_of(o).get('outline', True)]
    hulls = add_outlines(inked, ink, ink['px'] / px_per_m) if inked else []
    looks = {}
    tmp = tempfile.mkdtemp(prefix='contact_sheet_')
    views = VIEWS + [('game', cam_cfg.get('yaw', 45.0), cam_cfg.get('pitch', 30.0))]
    rows, game_look = [], None
    for vname, yaw, pitch in views:
        d = direction(yaw, pitch)
        persp = vname == 'game' and cam_cfg.get('projection', 'ortho') == 'persp'
        cam.data.type = 'PERSP' if persp else 'ORTHO'
        if persp:
            # the distance where the game's fov shows px_per_m at the asset's centre; the render is that frame's
            # middle n pixels
            half = math.tan(math.radians(cam_cfg.get('fov', 40.0)) / 2)
            dist = max(SCREEN_H / (2 * px_per_m * half), radius * 1.2)
            cam.data.angle = 2 * math.atan(n / (2 * px_per_m * dist))
        else:
            cam.data.ortho_scale = n / px_per_m
            dist = radius * 4
        cam.data.clip_end = dist + radius * 4
        cam.location = centre + d * dist
        aim(cam, d)
        tiles = []
        for pass_name in ('clay', 'look'):
            for mod in hulls:
                mod.show_render = pass_name == 'look'
            if pass_name == 'clay':
                sc.render.engine = 'BLENDER_WORKBENCH'
                sh = sc.display.shading
                sh.light, sh.color_type, sh.single_color = 'STUDIO', 'SINGLE', (0.7, 0.7, 0.7)
                sh.show_cavity, sh.cavity_type, sh.show_shadows = True, 'WORLD', True
                for o in objs:
                    for s, m in zip(o.material_slots, originals[o.name]):
                        s.material = m
            else:
                sc.render.engine = 'BLENDER_EEVEE'
                for o in objs:
                    for s, m in zip(o.material_slots, originals[o.name]):
                        if m is not None:
                            looks.setdefault(m.name, look_material(m, shading, toon))
                            s.material = looks[m.name]
            path = os.path.join(tmp, '%s_%s.png' % (vname, pass_name))
            sc.render.filepath = path
            bpy.ops.render.render(write_still=True)
            rgb, alpha = read_rgba(path, long_side=None)     # straight alpha: composite once, here
            alpha = alpha[:, :, None]
            shown = rgb * alpha + GREY_BG * (1 - alpha)
            if pass_name == 'look':
                inside = alpha[:, :, 0] > 0.5
                tiles.insert(0, upscale(np.repeat(1.0 - inside[:, :, None].astype(np.float32), 3, axis=2), tile))
                if vname == 'game':
                    # one pixel in from the edge: anti-aliased rim pixels mix in the background and skew the numbers
                    core = inside.copy()
                    core[1:] &= inside[:-1]
                    core[:-1] &= inside[1:]
                    core[:, 1:] &= inside[:, :-1]
                    core[:, :-1] &= inside[:, 1:]
                    game_look = (rgb, core if core.any() else inside)
                    write_png(upscale(shown, tile), stem + '_game.png')
            tiles.append(upscale(shown, tile))
        rows.append(to8(np.concatenate(tiles, axis=1)))
    shutil.rmtree(tmp, ignore_errors=True)

    refs_in = ref_images(args)
    extra = [fit(img, tile) for _, img in refs_in] + ([fit(read_rgb(args.golden), tile)] if args.golden else [])
    width = max(3, len(extra)) * tile
    sheet = [np.pad(r, ((0, 0), (0, width - r.shape[1]), (0, 0)), constant_values=255) for r in rows]
    if extra:
        ref_row = to8(np.concatenate(extra, axis=1))
        sheet.append(np.pad(ref_row, ((0, 0), (0, width - ref_row.shape[1]), (0, 0)), constant_values=255))
    sheet = np.concatenate(sheet, axis=0)
    write_png(sheet, args.out)

    lab, g = pixels(*game_look)
    measured = metrics(lab, g, k=8)
    lo, hi = style.get('value_range', [0.0, 100.0])
    refs = drawn_colours(style, shading, toon, ink)
    coverage = None
    if refs:
        dist = np.full(len(lab), np.inf)
        for r in refs:
            dist = np.minimum(dist, np.linalg.norm(lab - r, axis=1))
        coverage = round(float((dist <= float(style.get('palette_de', 6.0))).mean()), 3)
    target = style.get('look') or {}
    report = {
        'sheet': os.path.abspath(args.out), 'objects': [o.name for o in objs], 'shading': shading,
        'outline': ink, 'outlined': [o.name for o in inked],
        'layout': {'rows': [v[0] for v in views] + (['references'] if extra else []),
                   'columns': ['silhouette', 'clay', 'look'], 'tile_px': tile, 'render_px': n, 'render_scale': round(render_scale, 3), 'asset_px': px,
                   'references': [n for n, _ in refs_in] + (['golden'] if args.golden else [])},
        'game_tile': os.path.abspath(stem + '_game.png'),
        'game_view': measured,
        'against_style': {'value_range': [lo, hi],
                          'inside_value_range': round(float(((lab[:, 0] >= lo) & (lab[:, 0] <= hi)).mean()), 3),
                          'palette_coverage': coverage,
                          'palette_coverage_expected': '>= 0.85' if shading in ('toon', 'flat')
                          else "the golden asset's number",
                          # a guide for the reviewers, not a gate: the references are whole frames, this is one asset
                          'look': {k: {'asset': measured[k], 'style': target[k]} for k in LOOK_KEYS if k in target}},
    }
    with open(stem + '.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, indent=1)
    print('SHEET %s: %dx%d, game view L* %.0f-%.0f, inside value_range %.2f, palette coverage %s'
          % (args.out, sheet.shape[1], sheet.shape[0], measured['L_p2'], measured['L_p98'],
             report['against_style']['inside_value_range'], coverage))


if __name__ == '__main__':
    main()
