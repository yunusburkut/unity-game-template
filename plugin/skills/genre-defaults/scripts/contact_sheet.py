# The review sheet of a built asset, pinned so every iteration and every asset is judged the same way. Headless, on
# the saved .blend of the build (it never saves the file):
#
#   blender --background --factory-startup --python-exit-code 1 <asset>.blend --python contact_sheet.py -- \
#       --style Tools/Blender/Style/style.json --out <asset>_sheet.png [--crops crops.json] [--refs a.png b.png]
#       [--golden Tools/Blender/Style/golden.png] [--objects SM_A] [--tile 256]
#
# Rows: front, right, back, top (orthographic) and the game camera (style.json camera: pitch, yaw, projection).
# Columns: silhouette (black on white), clay (grey studio light, cavity) and look. Each view renders at the game's
# on-screen size (camera.asset_px) and is scaled up by whole pixels to the tile, so detail that is lost in the game is
# lost here too. A last row holds the reference crops (the rects of crops.json, or whole --refs images) and the golden
# asset, scaled to the tile height. <out>_game.png is the game-view look tile alone: the golden asset's one is golden.png.
#
# The look pass copies the Unity shading model from style.json "shading", with the light from "light":
#   toon    two bands: the colour, and colour x light.shadow_srgb where N.L falls under light.band (default 0.05,
#           Toon.shader's _RampOffset) or the asset shadows itself
#   flat    the colour unlit
#   lit, painted   Principled with the colour or image and the material's roughness, a sun and a grey ambient
# It is a Blender stand-in, not the Unity render: the final judgement is an in-engine screenshot.
#
# <out>.json beside the sheet: the layout, and extract_style's numbers measured on the game-view look render (asset
# pixels only) next to the style's value_range and palette, as palette_coverage (share within palette_de).

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
from extract_style import metrics, pixels, read_rgb, read_rgba, srgb_to_lab  # noqa: E402
from style_gate import LOD_CHILD, base_colour  # noqa: E402

VIEWS = [('front', 0.0, 0.0), ('right', 90.0, 0.0), ('back', 180.0, 0.0), ('top', 0.0, 90.0)]
GREY_BG = 0.55


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


def look_material(mat, shading, shadow, edge):
    """A render-only stand-in for mat that draws the style's shading model."""
    kind, val = base_colour(mat)
    m = bpy.data.materials.new('LOOK_' + mat.name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    if kind == 'image':
        col = nt.nodes.new('ShaderNodeTexImage')
        col.image = val
        colour = col.outputs['Color']
    else:
        col = nt.nodes.new('ShaderNodeRGB')
        col.outputs[0].default_value = (*linear(val if kind == 'rgb' else (1.0, 0.0, 1.0)), 1.0)
        colour = col.outputs[0]
    if shading == 'flat':
        em = nt.nodes.new('ShaderNodeEmission')
        nt.links.new(colour, em.inputs['Color'])
        nt.links.new(em.outputs[0], out.inputs['Surface'])
    elif shading == 'toon':
        diff = nt.nodes.new('ShaderNodeBsdfDiffuse')
        diff.inputs['Color'].default_value = (1, 1, 1, 1)
        to_rgb = nt.nodes.new('ShaderNodeShaderToRGB')
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'CONSTANT'
        ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
        ramp.color_ramp.elements[1].position = edge
        dark = nt.nodes.new('ShaderNodeMix')
        dark.data_type, dark.blend_type = 'RGBA', 'MULTIPLY'
        dark.inputs['Factor'].default_value = 1.0
        nt.links.new(colour, dark.inputs[6])          # the RGBA A and B (the float and vector ones come first)
        dark.inputs[7].default_value = (*linear(shadow), 1.0)
        band = nt.nodes.new('ShaderNodeMix')
        band.data_type = 'RGBA'
        nt.links.new(diff.outputs[0], to_rgb.inputs[0])
        nt.links.new(to_rgb.outputs['Color'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], band.inputs['Factor'])
        nt.links.new(dark.outputs[2], band.inputs[6])
        nt.links.new(colour, band.inputs[7])
        em = nt.nodes.new('ShaderNodeEmission')
        nt.links.new(band.outputs[2], em.inputs['Color'])
        nt.links.new(em.outputs[0], out.inputs['Surface'])
    else:
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        nt.links.new(colour, bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = mat.roughness
        nt.links.new(bsdf.outputs[0], out.inputs['Surface'])
    return m


def write_png(rgb, path):
    buf = oiio.ImageBuf(oiio.ImageSpec(rgb.shape[1], rgb.shape[0], 3, oiio.UINT8))
    buf.set_pixels(oiio.ROI(), np.clip(rgb, 0, 1).astype(np.float32))
    if not buf.write(path):
        raise SystemExit('cannot write %s: %s' % (path, buf.geterror()))


def ref_images(args):
    """sRGB images for the reference row: crops.json rects (paths relative to it), then whole --refs files."""
    out = []
    if args.crops:
        base = os.path.dirname(os.path.abspath(args.crops))
        with open(args.crops, encoding='utf-8') as f:
            for c in json.load(f):
                out.append((os.path.basename(c['file']), read_rgba(os.path.join(base, c['file']), c.get('rect'),
                                                                   long_side=None)[0]))
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
    ap.add_argument('--refs', nargs='*', default=[])
    ap.add_argument('--golden')
    ap.add_argument('--objects')
    ap.add_argument('--tile', type=int, default=256)
    args = ap.parse_args(argv)
    with open(args.style, encoding='utf-8') as f:
        style = json.load(f)
    cam_cfg, light = style.get('camera', {}), style.get('light', {})
    shading = style.get('shading', 'lit')
    px = int(cam_cfg.get('asset_px', 128))
    tile = max(args.tile, px)

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

    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = px
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
    looks = {}
    shadow = light.get('shadow_srgb', [0.55, 0.5, 0.65])
    # Shader to RGB of a white diffuse: world ambient 0.25 + sun 3 W/m2 x N.L / pi; the band edge sits at N.L = band
    edge = 0.25 + float(light.get('band', 0.05)) * 3.0 / math.pi
    tmp = tempfile.mkdtemp(prefix='contact_sheet_')
    views = VIEWS + [('game', cam_cfg.get('yaw', 45.0), cam_cfg.get('pitch', 30.0))]
    rows, game_look = [], None
    for vname, yaw, pitch in views:
        d = direction(yaw, pitch)
        persp = vname == 'game' and cam_cfg.get('projection', 'ortho') == 'persp'
        cam.data.type = 'PERSP' if persp else 'ORTHO'
        if persp:
            cam.data.angle = math.radians(cam_cfg.get('fov', 40.0))
            dist = radius / math.sin(cam.data.angle / 2) * 1.05
        else:
            cam.data.ortho_scale = radius * 2.1
            dist = radius * 4
        cam.data.clip_end = dist + radius * 4
        cam.location = centre + d * dist
        aim(cam, d)
        tiles = []
        for pass_name in ('clay', 'look'):
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
                            looks.setdefault(m.name, look_material(m, shading, shadow, edge))
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
                    write_png(upscale(shown, tile), re.sub(r'\.[^.]+$', '', args.out) + '_game.png')
            tiles.append(upscale(shown, tile))
        rows.append(np.concatenate(tiles, axis=1))
    shutil.rmtree(tmp, ignore_errors=True)

    refs_in = ref_images(args)
    extra = [fit(img, tile) for _, img in refs_in] + ([fit(read_rgb(args.golden), tile)] if args.golden else [])
    width = max(3, len(extra)) * tile
    sheet = [np.pad(r, ((0, 0), (0, width - r.shape[1]), (0, 0)), constant_values=1.0) for r in rows]
    if extra:
        ref_row = np.concatenate(extra, axis=1)
        sheet.append(np.pad(ref_row, ((0, 0), (0, width - ref_row.shape[1]), (0, 0)), constant_values=1.0))
    sheet = np.concatenate(sheet, axis=0)
    write_png(sheet, args.out)

    lab, g = pixels(*game_look)
    measured = metrics(lab, g, k=8)
    lo, hi = style.get('value_range', [0.0, 100.0])
    refs = [srgb_to_lab(np.array(v['srgb'], float)) for v in (style.get('palette') or {}).values()]
    refs += [srgb_to_lab(np.array(a, float)) for a in style.get('accents', [])]
    coverage = None
    if refs:
        dist = np.full(len(lab), np.inf)
        for r in refs:
            dist = np.minimum(dist, np.linalg.norm(lab - r, axis=1))
        coverage = round(float((dist <= float(style.get('palette_de', 6.0))).mean()), 3)
    report = {
        'sheet': os.path.abspath(args.out), 'objects': [o.name for o in objs], 'shading': shading,
        'layout': {'rows': [v[0] for v in views] + (['references'] if extra else []),
                   'columns': ['silhouette', 'clay', 'look'], 'tile_px': tile, 'asset_px': px,
                   'references': [n for n, _ in refs_in] + (['golden'] if args.golden else [])},
        'game_tile': re.sub(r'\.[^.]+$', '', os.path.abspath(args.out)) + '_game.png',
        'game_view': measured,
        'against_style': {'value_range': [lo, hi],
                          'inside_value_range': round(float(((lab[:, 0] >= lo) & (lab[:, 0] <= hi)).mean()), 3),
                          'palette_coverage': coverage},
    }
    with open(re.sub(r'\.[^.]+$', '', args.out) + '.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, indent=1)
    print('SHEET %s: %dx%d, game view L* %.0f-%.0f, inside value_range %.2f, palette coverage %s'
          % (args.out, sheet.shape[1], sheet.shape[0], measured['L_p2'], measured['L_p98'],
             report['against_style']['inside_value_range'], coverage))


if __name__ == '__main__':
    main()
