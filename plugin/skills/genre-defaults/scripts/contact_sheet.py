# The review sheet of a built asset, pinned so every iteration and every asset is judged the same way. Headless, on
# the saved .blend of the build (it never saves the file):
#
#   blender --background --factory-startup --python-exit-code 1 <asset>.blend --python contact_sheet.py -- \
#       --style Tools/Blender/Style/style.json --out <asset>_sheet.png [--crops crops.json] [--class prop]
#       [--refs a.png b.png] [--golden Tools/Blender/Style/golden.png] [--objects SM_A] [--tile 256]
#
# Rows: front, right, back, top (orthographic) and the game camera (style.json camera: pitch, yaw, projection). Yaw 0,
# pitch 0 looks from Blender's front (-Y); a Unity camera or sun at Euler (x, r, 0) is pitch x, yaw 180 - r (the
# toon-art axes: Blender (x, y, z) is Unity (-x, z, -y)).
# Columns: silhouette (black on white), clay (grey studio light, cavity) and look. Each view renders at the game's
# 1080p scale, camera.asset_px pixels per camera.asset_m metres (the typical prop's height, default 1), so a hero
# draws larger than a prop (past 1024 px it shrinks to fit: layout.render_scale < 1 and a SHEET WARNING); the tile
# scales it up by whole pixels, centred, so detail that is lost in the game is lost here too. Cameras stand upright
# (the top view is Blender's Top: +Y up). Rendered: the meshes an export takes (style_gate's exported_meshes) or
# --objects (a missing name exits), lit only by the sheet's sun and a fresh grey world. A last row holds the references:
# the "kind": "object" crops of crops.json (those of --class, default every style_class among the objects' roots, or
# with no class) at the same 1080p scale and zoom as the asset, else its surface crops, then whole --refs images, then
# the golden asset (by whole pixels, padded grey).
# <out>_game.png is the game-view look tile alone: the golden asset's one becomes golden.png.
#
# The look pass copies the Unity shading model from style.json "shading", with the light from "light":
#   toon    __GAME__/Toon's bands: the colour where N.L is over light.band (Toon.shader _RampOffset, default 0.05;
#           blended over light.softness 0.035 either side, _RampSoftness) and the asset does not shadow itself, else lerp(luminance, colour, light.shade_saturation 1.3) x
#           light.shadow_srgb; both times the main light (light.color x light.intensity) plus colour x light.ambient
#           (the scene's SH level, default 0.5) x light.ambient_strength 0.18; darker toward the floor
#           (light.contact_shade 0.3 under light.ground_y -0.06 m, fading out over light.contact_height 0.25 m of world
#           z, with the .blend's z = 0 as the game's floor); plus the glossy spot (light.spot 0.85) and the rim
#           (light.rim 0.5 past light.rim_edge 0.62) at the smoothness the game gets: an M_<Role> material's palette
#           role smoothness, else 1 - a set Principled Roughness, else 1 - the viewport roughness (toon_smoothness).
#           SH ambient is one level, not sampled by the normal
#   flat    the colour unlit
#   lit, painted   Principled with the colour or image and the Roughness and Metallic FBX carries, a sun and a grey
#           ambient
# "outline" (true, or {"px": 1.5, "srgb": [0.36, 0.30, 0.46]}, Toon.shader's defaults) adds the inverted-hull ink line
# at px 1080p pixels, coloured albedo x srgb, pushed along each position's distinct corner normals summed, as
# OutlineNormalsPostprocessor bakes them (a split or hard edge keeps a closed line). It is a Blender stand-in, not the
# Unity render: the final judgement is an in-engine screenshot.
#
# <out>.json beside the sheet: the layout; extract_style's numbers measured on the game tile (asset pixels one pixel
# in from the edge) next to style.json "look" (the reference numbers, same 1080p pixel scale); inside_value_range; and
# palette_coverage, the share of asset pixels (inside the silhouette's ink ring) within palette_de of a palette or
# accent colour as this shading draws it (lit band, shade band, ink, contact, spot, rim, and the blends between one
# colour's variants); a SHEET WARNING when the game view's chroma_mean sits more than CHROMA_GAP from look's. A toon or
# flat asset on palette reads 0.85 or more at asset_px 64 and up (under that, the edge
# pixels between two colours weigh more: compare with the golden asset's number); lit and painted vary with the light,
# so compare with the golden asset's number. silhouette_fill: per view, the asset's pixels over its bounding box's;
# front and right both at BOX_FILL or more print a SHEET NOTE (a primitive's outline). motif: STYLE.md beside --style
# has a line starting "Motif:"; false prints a SHEET WARNING.

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
from mathutils import Quaternion, Vector

sys.dont_write_bytecode = True     # no __pycache__ beside the plugin's scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_style import (SCREEN_H, linear_to_srgb, metrics, pixels, read_rgb, read_rgba, srgb_to_lab,  # noqa: E402
                           srgb_to_linear as linear)
from style_gate import base_colour, exported_meshes, is_cutout, named_meshes, principled, root_of  # noqa: E402

VIEWS = [('front', 0.0, 0.0), ('right', 90.0, 0.0), ('back', 180.0, 0.0), ('top', 0.0, 90.0)]
GREY_BG = 0.55
AMBIENT_STRENGTH = 0.18          # Toon.shader _AmbientStrength
SUN_E = 3.0                      # the sheet's sun, W/m2
OUTLINE = {'px': 1.5, 'srgb': [0.36, 0.30, 0.46]}     # Toon.shader _OutlineWidth, _OutlineColor
LOOK_KEYS = ('detail_energy', 'dark_edge_share', 'chroma_mean', 'accent_share')
SPOT, RIM, RIM_EDGE = 0.85, 0.5, 0.62     # Toon.shader _SpecularStrength, _RimStrength, _RimEdge
CHROMA_GAP = 10                           # chroma_mean this far from the references' is a lead for the colour lens
BOX_FILL = 0.95                           # front and side both filling their boxes this much: a primitive's outline


def direction(yaw, pitch):
    """Unit vector from the asset toward the eye; yaw 0, pitch 0 is Blender's Front view (from -Y)."""
    y, p = math.radians(yaw), math.radians(pitch)
    return Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))


def aim(obj, d):
    """Turns obj's -Z along -d, upright (its local Y toward world +Z); straight down it is Blender's Top view (X right,
    Y up)."""
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = (-d).to_track_quat('-Z', 'Y') if abs(d.z) < 0.999 else Quaternion()


def toon_params(light):
    """style.json light as Toon.shader's values; each field defaults to the shader's default."""
    return {'shadow': linear(light.get('shadow_srgb', [0.62, 0.62, 0.86])),     # Toon.shader _ShadeColor
            'saturation': float(light.get('shade_saturation', 1.3)),
            'ambient': float(light.get('ambient', 0.5)) * float(light.get('ambient_strength', AMBIENT_STRENGTH)),
            'band': float(light.get('band', 0.05)),                             # Toon.shader _RampOffset
            'softness': max(1e-3, float(light.get('softness', 0.035))),         # _RampSoftness
            'spot': float(light.get('spot', SPOT)),                             # _SpecularStrength
            'rim': float(light.get('rim', RIM)),                                # _RimStrength
            'rim_edge': float(light.get('rim_edge', RIM_EDGE)),                 # _RimEdge
            # the main light's colour x intensity: Toon.shader multiplies both bands by it, never the ambient
            'sun': linear(light.get('color', [1.0, 1.0, 1.0])) * float(light.get('intensity', 1.0)),
            'to_sun': tuple(direction(light.get('yaw', -30.0), light.get('pitch', 50.0))),
            # Toon.shader _ContactShade, _GroundY, _ContactHeight: darker toward the floor, Blender z = Unity y
            'contact': float(light.get('contact_shade', 0.3)),
            'ground': float(light.get('ground_y', -0.06)),
            'contact_h': max(1e-4, float(light.get('contact_height', 0.25)))}


ACCENT_SMOOTHNESS = 0.3                  # style.json accents carry only a colour (toon_prop's value)


def toon_smoothness(mat, palette):
    """Toon.shader's _Smoothness in the order the game sets it: an M_<Role> material takes its palette role's
    smoothness (the builder makes it from style.json, as drawn_colours does), else 1 - the Principled Roughness FBX
    carries when it is wired and set (not Blender's 0.5), else 1 - the viewport roughness (toon_prop keeps it there)."""
    role = re.sub(r'\.\d+$', '', mat.name[2:]) if mat.name.startswith('M_') else None
    if role in palette:
        return float(palette[role].get('smoothness', ACCENT_SMOOTHNESS))
    bsdf = principled(mat)
    rough = bsdf.inputs['Roughness'] if bsdf is not None else None
    if rough is not None and not rough.is_linked and abs(rough.default_value - 0.5) > 1e-4:
        return min(1.0, max(0.0, 1.0 - rough.default_value))
    return min(1.0, max(0.0, 1.0 - mat.roughness))


def outline_cfg(style):
    o = style.get('outline')
    if not o:
        return None
    return {**OUTLINE, **(o if isinstance(o, dict) else {})}


def colour_node(nt, mat, viewport=True):
    kind, val = base_colour(mat, viewport)    # a viewport-only colour off toon draws magenta: Unity gets grey
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


def look_material(mat, shading, toon, palette=None):
    """A render-only stand-in for mat that draws the style's shading model (palette: style.json's, for toon)."""
    m = bpy.data.materials.new('LOOK_' + mat.name)
    nt = m.node_tree
    nt.nodes.clear()
    colour = colour_node(nt, mat, shading == 'toon')
    if shading == 'flat':
        emit(nt, colour)
    elif shading == 'toon':
        # Toon.shader: lit = smoothstep(band -+ softness, N.L) x unshadowed, colour = (lerp(shade, albedo, lit) x sun + albedo x ambient)
        # x contact, + sun x smoothness x (spot x lit + rim)
        def math_node(op, a, b, vector=False):
            n = nt.nodes.new('ShaderNodeVectorMath' if vector else 'ShaderNodeMath')
            n.operation = op
            for sock, v in ((n.inputs[0], a), (n.inputs[1], b)):
                if isinstance(v, (float, tuple)):
                    sock.default_value = v
                else:
                    nt.links.new(v, sock)
            return n.outputs['Value' if vector and op == 'DOT_PRODUCT' else 0]

        def smoothstep(v, lo, hi):
            n = nt.nodes.new('ShaderNodeMapRange')
            n.interpolation_type = 'SMOOTHSTEP'
            nt.links.new(v, n.inputs['Value'])
            n.inputs['From Min'].default_value, n.inputs['From Max'].default_value = lo, hi
            return n.outputs['Result']
        geo = nt.nodes.new('ShaderNodeNewGeometry')
        normal, view = geo.outputs['Normal'], geo.outputs['Incoming']
        facing = nt.nodes.new('ShaderNodeVectorMath')
        facing.operation = 'DOT_PRODUCT'
        nt.links.new(normal, facing.inputs[0])
        facing.inputs[1].default_value = toon['to_sun']
        band = smoothstep(facing.outputs['Value'], toon['band'] - toon['softness'], toon['band'] + toon['softness'])
        # the cast shadow: the look pass has a black world, so a white diffuse reads the sun alone, SUN_E x N.L / pi
        # where nothing blocks it; Toon.shader cuts its shadow at half attenuation. A face turned away reads 0 > a
        # negative half, unshadowed, so a band under 0 still draws its lit strip there
        diff = nt.nodes.new('ShaderNodeBsdfDiffuse')
        diff.inputs['Color'].default_value = (1, 1, 1, 1)
        to_rgb = nt.nodes.new('ShaderNodeShaderToRGB')
        nt.links.new(diff.outputs[0], to_rgb.inputs[0])
        sunlit = nt.nodes.new('ShaderNodeRGBToBW')
        nt.links.new(to_rgb.outputs['Color'], sunlit.inputs[0])
        half = math_node('MULTIPLY', facing.outputs['Value'], 0.5 * SUN_E / math.pi)
        unshadowed = math_node('GREATER_THAN', sunlit.outputs[0], half)
        lit = math_node('MULTIPLY', band, unshadowed)
        lum = nt.nodes.new('ShaderNodeRGBToBW')
        nt.links.new(colour, lum.inputs[0])
        shade = mix(nt, 'MIX', lum.outputs[0], colour, toon['saturation'])     # lerp(luminance, colour, saturation)
        shade = mix(nt, 'MULTIPLY', shade, toon['shadow'])
        bands = mix(nt, 'MULTIPLY', mix(nt, 'MIX', shade, colour, lit), toon['sun'])
        k = toon['ambient']
        lighted = mix(nt, 'ADD', bands, mix(nt, 'MULTIPLY', colour, (k, k, k)))
        # contact: smoothstep(ground, ground + height, world z), from 1 - contact_shade up to 1
        z = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(geo.outputs['Position'], z.inputs[0])
        near = smoothstep(z.outputs['Z'], toon['ground'], toon['ground'] + toon['contact_h'])
        shaded = mix(nt, 'MULTIPLY', lighted,
                     math_node('ADD', math_node('MULTIPLY', near, toon['contact']), 1.0 - toon['contact']))
        # the glossy spot (on the lit band) and the rim (fading to 0.3 in a cast shadow), as strong as the surface
        # is smooth; view is the direction to the eye, perspective or not
        s = toon_smoothness(mat, palette or {})
        halfway = math_node('NORMALIZE', math_node('ADD', view, toon['to_sun'], vector=True), (0.0, 0.0, 0.0),
                            vector=True)
        ndh = math_node('MAXIMUM', math_node('DOT_PRODUCT', normal, halfway, vector=True), 0.0)
        spot = smoothstep(math_node('POWER', ndh, 2.0 ** (s * 9.0 + 1.0)), 0.45, 0.55)
        ndv = math_node('MAXIMUM', math_node('DOT_PRODUCT', normal, view, vector=True), 0.0)
        sunward = math_node('MINIMUM', math_node('MAXIMUM', math_node('ADD', facing.outputs['Value'], 0.3), 0.0), 1.0)
        side = math_node('ADD', math_node('MULTIPLY', sunward, 0.6), 0.4)
        edge = toon['rim_edge']
        rim = smoothstep(math_node('MULTIPLY', math_node('SUBTRACT', 1.0, ndv), side), edge - 0.04, edge + 0.04)
        sr = s * toon['rim']
        glow = math_node('ADD', math_node('MULTIPLY', math_node('MULTIPLY', spot, lit), s * toon['spot']),
                         math_node('MULTIPLY', rim, math_node('ADD', math_node('MULTIPLY', unshadowed, 0.7 * sr),
                                                             0.3 * sr)))
        emit(nt, mix(nt, 'ADD', shaded, mix(nt, 'MULTIPLY', glow, toon['sun'])))
    else:
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        nt.links.new(colour, bsdf.inputs['Base Color'])
        # the gloss FBX carries: the Principled values, then the viewport ones (the toon pipeline keeps 1 - smoothness
        # there)
        src = principled(mat)
        for name, fallback in (('Roughness', mat.roughness), ('Metallic', mat.metallic)):
            own = src is not None and not src.inputs[name].is_linked
            bsdf.inputs[name].default_value = src.inputs[name].default_value if own else fallback
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


OUTLINE_NORMAL = 'outline_normal'


def bake_outline_normals(mesh, grid):
    """OutlineNormalsPostprocessor's bake as the point attribute OUTLINE_NORMAL: per position (rounded to grid object
    units, the postprocessor's 0.1 mm), the sum of its distinct corner normals (dot over 0.999 counts once, so a seam's
    duplicate does not pull a cube corner off its diagonal), normalised; a sum near zero keeps the vertex normal.
    Every vertex at one position gets one direction, so a hard or split edge keeps a closed line unwelded."""
    cn = np.empty(len(mesh.loops) * 3, np.float32)
    mesh.corner_normals.foreach_get('vector', cn)
    lv = np.empty(len(mesh.loops), np.int32)
    mesh.loops.foreach_get('vertex_index', lv)
    co = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get('co', co)
    vn = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get('normal', vn)
    positions, key = np.unique(np.round(co.reshape(-1, 3) / grid).astype(np.int64), axis=0, return_inverse=True)
    key = key.ravel()
    sums, seen = np.zeros((len(positions), 3)), [[] for _ in positions]
    for k, n in zip(key[lv], cn.reshape(-1, 3)):
        if not any(float(n @ m) > 0.999 for m in seen[k]):
            seen[k].append(n)
            sums[k] += n
    out = sums[key]
    size = np.linalg.norm(out, axis=1, keepdims=True)
    out = np.where(size ** 2 > 1e-6, out / np.maximum(size, 1e-12), vn.reshape(-1, 3))
    attr = mesh.attributes.new(OUTLINE_NORMAL, 'FLOAT_VECTOR', 'POINT')
    attr.data.foreach_set('vector', out.astype(np.float32).ravel())


def hull_nodes(width, offset):
    """Geometry nodes that add the inverted ink hull to a mesh the way the game builds it: a copy pushed out width
    metres along OUTLINE_NORMAL's world part (bake_outline_normals) across the active camera's view (Toon.shader
    normalises the world normal's screen part, so a cube corner moves the full width, not width x cos, and an
    unapplied non-uniform scale bends the normal, not the width), faces flipped, material index moved to the ink
    slots."""
    ng = bpy.data.node_groups.new('SHEET_Hull', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes, link = ng.nodes, ng.links.new
    src, out = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    push = nodes.new('GeometryNodeSetPosition')
    baked = nodes.new('GeometryNodeInputNamedAttribute')
    baked.data_type = 'FLOAT_VECTOR'
    baked.inputs['Name'].default_value = OUTLINE_NORMAL

    def vmath(op, a, b=None):
        n = nodes.new('ShaderNodeVectorMath')
        n.operation = op
        link(a, n.inputs[0])
        if b is not None:
            link(b, n.inputs[1])
        return n

    def info(obj_socket):
        n = nodes.new('GeometryNodeObjectInfo')
        n.transform_space = 'ORIGINAL'
        link(obj_socket, n.inputs['Object'])
        return n

    def transform(matrix, vector):
        n = nodes.new('FunctionNodeTransformDirection')
        link(vector, n.inputs['Direction'])
        link(matrix, n.inputs['Transform'])
        return n.outputs[0]
    to_object = nodes.new('FunctionNodeInvertMatrix')
    link(info(nodes.new('GeometryNodeSelfObject').outputs[0]).outputs['Transform'], to_object.inputs[0])
    normal_matrix = nodes.new('FunctionNodeTransposeMatrix')
    link(to_object.outputs['Matrix'], normal_matrix.inputs[0])
    normal = vmath('NORMALIZE', transform(normal_matrix.outputs[0], baked.outputs['Attribute'])).outputs[0]
    # the view axis in world space: the active camera's -Z
    view = nodes.new('FunctionNodeRotateVector')
    view.inputs['Vector'].default_value = (0, 0, -1)
    link(info(nodes.new('GeometryNodeInputActiveCamera').outputs[0]).outputs['Rotation'], view.inputs['Rotation'])
    # the normal's screen part: N - (N.V) V, normalised (zero where a face looks straight at the camera)
    along_view = vmath('SCALE', view.outputs[0])
    link(vmath('DOT_PRODUCT', normal, view.outputs[0]).outputs['Value'], along_view.inputs['Scale'])
    screen = vmath('NORMALIZE', vmath('SUBTRACT', normal, along_view.outputs[0]).outputs[0])
    along = vmath('SCALE', screen.outputs[0])
    along.inputs['Scale'].default_value = width
    shift = nodes.new('ShaderNodeMath')
    shift.inputs[1].default_value = offset
    link(nodes.new('GeometryNodeInputMaterialIndex').outputs[0], shift.inputs[0])
    flip, ink = nodes.new('GeometryNodeFlipFaces'), nodes.new('GeometryNodeSetMaterialIndex')
    join = nodes.new('GeometryNodeJoinGeometry')
    link(src.outputs[0], push.inputs['Geometry'])
    link(transform(to_object.outputs['Matrix'], along.outputs['Vector']), push.inputs['Offset'])
    link(push.outputs['Geometry'], flip.inputs['Mesh'])
    link(flip.outputs['Mesh'], ink.inputs['Geometry'])
    link(shift.outputs[0], ink.inputs['Material Index'])
    link(ink.outputs['Geometry'], join.inputs[0])
    link(src.outputs[0], join.inputs[0])
    link(join.outputs[0], out.inputs[0])
    return ng


def add_outlines(objs, cfg, width):
    """An inverted hull per object (hull_nodes, ink materials after the originals, from the object's slots: an
    object-linked slot is the material that ships); returns the modifiers so the clay pass can hide them. Each object
    takes its evaluated mesh (what FBX exports, the viewport evaluation) as its own data with the modifiers dropped,
    so the outline normal is baked on the vertices the game gets; the sheet never saves the file. That drops what
    the evaluated mesh leaves out (a modifier's instances, which FBX keeps): add a realize step here if one ships."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mods = []
    for o in objs:
        slots = [(s.link, s.material) for s in o.material_slots]
        # a mesh of its own: linked duplicates may link other materials to their objects, so each gets its own ink
        o.data = bpy.data.meshes.new_from_object(o.evaluated_get(depsgraph), preserve_all_data_layers=True,
                                                 depsgraph=depsgraph)
        o.modifiers.clear()
        for s, (lnk, m) in zip(o.material_slots, slots):
            s.link, s.material = lnk, m
        for _, m in slots:
            o.data.materials.append(ink_material(m, cfg['srgb']) if m else None)
        # the grid is in object units (a millimetre's tenth, as the postprocessor's); the width is in metres
        bake_outline_normals(o.data, 1e-4 / max(1e-6, float(np.mean(o.matrix_world.to_scale()))))
        mod = o.modifiers.new('SHEET_Outline', 'NODES')
        mod.node_group = hull_nodes(width, len(slots))
        mods.append(mod)
    return mods


def toon_bands(lin, toon):
    """Linear lit and shade band of an albedo, as Toon.shader draws them."""
    lum = float(lin @ np.array([0.2126, 0.7152, 0.0722]))
    return (lin * (toon['sun'] + toon['ambient']),
            (lum + toon['saturation'] * (lin - lum)) * toon['shadow'] * toon['sun'] + lin * toon['ambient'])


def drawn_colours(style, shading, toon, ink):
    """CIELAB of every palette and accent colour as the look pass draws it: lit band, shade band and ink for toon, and
    the anti-aliased blends between one colour's variants (a band edge, the ink against its own colour). Toon adds each
    band darkened by the contact shade, the glossy spot on the lit band and the rim on both, at the role's
    smoothness."""
    roles = [(v['srgb'], v.get('smoothness', ACCENT_SMOOTHNESS)) for v in (style.get('palette') or {}).values()]
    roles += [(c, ACCENT_SMOOTHNESS) for c in style.get('accents', [])]
    out = []
    for c, s in roles:
        lin = linear(c)
        if shading == 'toon':
            lit, shade = toon_bands(lin, toon)
            glow = toon['sun'] * float(s)
            spot, rim = toon['spot'], toon['rim']
            variants = [lit, shade, lit * (1 - toon['contact']), shade * (1 - toon['contact']), lit + glow * spot,
                        lit + glow * rim, shade + glow * rim, shade + glow * 0.3 * rim]
        else:
            variants = [lin]
        if ink:
            variants.append(lin * linear(ink['srgb']))
        variants += [a + t * (b - a) for i, a in enumerate(variants) for b in variants[i + 1:]
                     for t in (0.25, 0.5, 0.75)]
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


def ref_images(args, tile, k):
    """(name, tile) for the reference row: object crops of the class at the game's 1080p scale, zoomed k times like
    the asset (else surface crops, fitted), then --refs fitted."""
    out = []
    if args.crops:
        base = os.path.dirname(os.path.abspath(args.crops))
        with open(args.crops, encoding='utf-8') as f:
            crops = json.load(f)
        # the screenshots stay on the machine that made the bible (reference/ is gitignored): a missing one is noted
        missing = sorted({c['file'] for c in crops if not os.path.isfile(os.path.join(base, c['file']))})
        if missing:
            print('SHEET NOTE: reference %s missing (copy Tools/Blender/Style/reference/ from the machine that made '
                  'the bible); the row goes without it' % ', '.join(missing))
        crops = [c for c in crops if c['file'] not in missing]
        objects = [c for c in crops if c.get('kind') == 'object' and c.get('class') in {None, *args.classes}]
        for c in objects:
            img = read_rgba(os.path.join(base, c['file']), c.get('rect'), screen_h=SCREEN_H)[0]
            out.append((os.path.basename(c['file']), upscale(img, tile, 1.0, k)))
        surfaces = [] if objects else [c for c in crops if c.get('kind', 'surface') == 'surface']
        if surfaces:
            print('SHEET NOTE: no object crop of class %s in %s (style-bible step 1.3); the row shows %d surface crops'
                  % ('/'.join(sorted(map(str, args.classes))), args.crops, min(3, len(surfaces))))
        for c in surfaces[:3]:
            img = read_rgba(os.path.join(base, c['file']), c.get('rect'), long_side=None)[0]
            out.append((os.path.basename(c['file']), fit(img, tile)))
    out += [(os.path.basename(p), fit(read_rgba(p, long_side=None)[0], tile)) for p in args.refs]
    return out


def upscale(img, size, bg, k=None):
    """Nearest-neighbour by whole pixels (k, else the most that fits size), centred on a size x size tile of bg and cut
    to it, so game-size pixels stay visible."""
    k = k or max(1, size // max(img.shape[:2]))
    big = np.repeat(np.repeat(img, k, axis=0), k, axis=1)
    cy, cx = max(0, (big.shape[0] - size) // 2), max(0, (big.shape[1] - size) // 2)
    big = big[cy:cy + size, cx:cx + size]
    tile = np.full((size, size, img.shape[2]), bg, np.float32)
    oy, ox = (size - big.shape[0]) // 2, (size - big.shape[1]) // 2
    tile[oy:oy + big.shape[0], ox:ox + big.shape[1]] = big
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
    projection = {'ortho': 'ortho', 'orthographic': 'ortho', 'persp': 'persp', 'perspective': 'persp'}.get(
        str(cam_cfg.get('projection', 'ortho')).lower())
    if projection is None:
        raise SystemExit('camera.projection %r: use "ortho" or "persp"' % cam_cfg.get('projection'))
    shading = style.get('shading', 'lit')
    toon, ink = toon_params(light), outline_cfg(style)
    px = int(cam_cfg.get('asset_px', 128))
    px_per_m = px / float(cam_cfg.get('asset_m') or 1.0)
    stem = re.sub(r'\.[^.]+$', '', args.out)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    if args.crops and not os.path.isfile(args.crops):       # before ten renders, not after
        raise SystemExit('--crops %s: no such file (style-bible step 1.3 writes crops.json)' % args.crops)
    if args.golden and not os.path.isfile(args.golden):     # the golden asset's own first sheet: none approved yet
        print('SHEET NOTE: no golden asset at %s yet, the sheet goes without it' % args.golden)
        args.golden = None

    objs = named_meshes(args.objects) if args.objects else exported_meshes()
    if not objs:
        raise SystemExit('no mesh objects to render')
    # the reference row's object crops: --class, else every class among the objects' roots (a mixed lineup)
    args.classes = {args.cls} if args.cls else {root_of(o).get('style_class') for o in objs}
    # only the sheet's own sun lights it: a light left in the .blend (a preview sun) would move the toon band
    lights = [o.name for o in bpy.data.objects if o.type == 'LIGHT' and not o.hide_render
              and not o.name.startswith('SHEET_')]
    if lights:
        print('SHEET NOTE: lights %s in the .blend left out of the render' % ', '.join(lights))
    # every other renderable leaves the render: a curve, text or metaball part the FBX export (meshes only) drops too
    for o in bpy.data.objects:
        if o.type not in ('CAMERA', 'EMPTY', 'ARMATURE'):
            o.hide_render = o not in objs
    bpy.context.view_layer.update()     # matrix_world of a transform set in this run (a build script's own call)
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
    sc.render.dither_intensity = 0.0        # its noise would enter the numbers measured on the tile
    cam = bpy.data.objects.new('SHEET_Cam', bpy.data.cameras.new('SHEET_Cam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    sun = bpy.data.objects.new('SHEET_Sun', bpy.data.lights.new('SHEET_Sun', 'SUN'))
    sun.data.energy = SUN_E
    sc.collection.objects.link(sun)
    aim(sun, direction(light.get('yaw', -30.0), light.get('pitch', 50.0)))
    sc.world = bpy.data.worlds.new('SHEET_World')     # fresh: the .blend's own world may hold an HDRI
    # the backdrop is composited later (film transparent); toon takes its ambient from the material, and its shadow
    # mask needs the sun alone
    world = 0.0 if shading == 'toon' else 0.25
    sc.world.color = (world, world, world)
    if sc.world.node_tree:
        bg = next((n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if bg:
            bg.inputs['Color'].default_value = (world, world, world, 1)
            bg.inputs['Strength'].default_value = 1.0
    # Unity's _BaseMap samples UV0 whatever layer the .blend renders with (the sheet never saves the file)
    for o in objs:
        if o.data.uv_layers:
            o.data.uv_layers[0].active_render = True

    originals = {o.name: [s.material for s in o.material_slots] for o in objs}
    # an asset the game draws without the line (toon_prop's "outline": False, kit and level pieces) says so on its root
    inked = [o for o in objs if ink and root_of(o).get('outline', True)]
    hulls = add_outlines(inked, ink, ink['px'] / px_per_m) if inked else []
    looks = {}
    tmp = tempfile.mkdtemp(prefix='contact_sheet_')
    views = VIEWS + [('game', cam_cfg.get('yaw', 45.0), cam_cfg.get('pitch', 30.0))]
    rows, game_look, fills = [], None, {}
    for vname, yaw, pitch in views:
        d = direction(yaw, pitch)
        persp = vname == 'game' and projection == 'persp'
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
                            looks.setdefault(m.name, look_material(m, shading, toon, style.get('palette')))
                            s.material = looks[m.name]
            path = os.path.join(tmp, '%s_%s.png' % (vname, pass_name))
            sc.render.filepath = path
            bpy.ops.render.render(write_still=True)
            rgb, alpha = read_rgba(path, long_side=None)     # straight alpha: composite once, here
            alpha = alpha[:, :, None]
            shown = rgb * alpha + GREY_BG * (1 - alpha)
            if pass_name == 'look':
                inside = alpha[:, :, 0] > 0.5
                ys, xs = np.nonzero(inside)
                # the asset's share of its own bounding box: about 1 for a box, a can or a crate from the side
                fills[vname] = round(float(len(ys) / ((np.ptp(ys) + 1) * (np.ptp(xs) + 1))), 3) if len(ys) else None
                tiles.insert(0,upscale(np.repeat(1.0 - inside[:, :, None].astype(np.float32), 3, axis=2), tile, 1.0))
                if vname == 'game':
                    # one pixel in from the edge: anti-aliased rim pixels mix in the background and skew the numbers;
                    # palette coverage also skips the silhouette's ink ring, whose blend with the grey is no colour
                    cores = [inside]
                    for _ in range(1 + (math.ceil(ink['px']) if inked else 0)):
                        c = cores[-1].copy()
                        c[1:] &= cores[-1][:-1]
                        c[:-1] &= cores[-1][1:]
                        c[:, 1:] &= cores[-1][:, :-1]
                        c[:, :-1] &= cores[-1][:, 1:]
                        cores.append(c)
                    game_look = (rgb, *(c if c.any() else inside for c in (cores[1], cores[-1])))
                    write_png(upscale(shown, tile, GREY_BG), stem + '_game.png')
            tiles.append(upscale(shown, tile, GREY_BG))
        rows.append(to8(np.concatenate(tiles, axis=1)))
    shutil.rmtree(tmp, ignore_errors=True)

    refs_in = ref_images(args, tile, tile // n)
    extra = [t for _, t in refs_in]
    if args.golden:
        # by whole pixels as the asset tiles: every step-th pixel when it is larger than the tile, else upscaled
        golden = read_rgb(args.golden, long_side=None)
        step = -(-max(golden.shape[:2]) // tile)
        extra.append(upscale(golden[::step, ::step], tile, GREY_BG))
    width = max(3, len(extra)) * tile
    sheet = [np.pad(r, ((0, 0), (0, width - r.shape[1]), (0, 0)), constant_values=255) for r in rows]
    if extra:
        ref_row = to8(np.concatenate(extra, axis=1))
        sheet.append(np.pad(ref_row, ((0, 0), (0, width - ref_row.shape[1]), (0, 0)), constant_values=255))
    sheet = np.concatenate(sheet, axis=0)
    write_png(sheet, args.out)

    game_rgb, core, deep = game_look
    lab, g = pixels(game_rgb, core)
    measured = metrics(lab, g, k=8)
    lo, hi = style.get('value_range', [0.0, 100.0])
    refs = drawn_colours(style, shading, toon, ink)
    coverage = None
    if refs:
        deep_lab = pixels(game_rgb, deep)[0]
        dist = np.full(len(deep_lab), np.inf)
        for r in refs:
            dist = np.minimum(dist, np.linalg.norm(deep_lab - r, axis=1))
        coverage = round(float((dist <= float(style.get('palette_de', 6.0))).mean()), 3)
    inside = (lab[:, 0] >= lo) & (lab[:, 0] <= hi)
    if shading == 'toon' and refs:
        # value_range comes from evenly lit surfaces: judge the pixels nearer a lit band than a shade band
        cols = [linear(v['srgb']) for v in (style.get('palette') or {}).values()] + [linear(a) for a in
                                                                                    style.get('accents', [])]
        lit, shade = (np.array([srgb_to_lab(linear_to_srgb(np.clip(toon_bands(c, toon)[b], 0.0, 1.0))) for c in cols])
                      for b in (0, 1))
        lit_px = (np.linalg.norm(lab[:, None] - lit[None], axis=2).min(axis=1)
                  < np.linalg.norm(lab[:, None] - shade[None], axis=2).min(axis=1))
        inside = inside[lit_px] if lit_px.any() else inside
    target = style.get('look') or {}
    # STYLE.md beside style.json names the game's own signature detail on a line starting "Motif:"
    notes = os.path.join(os.path.dirname(os.path.abspath(args.style)), 'STYLE.md')
    motif = False
    if os.path.isfile(notes):
        with open(notes, encoding='utf-8') as f:
            motif = any(line.lstrip().startswith('Motif:') for line in f)
    report = {
        'sheet': os.path.abspath(args.out), 'objects': [o.name for o in objs], 'shading': shading,
        'outline': ink, 'outlined': [o.name for o in inked],
        'layout': {'rows': [v[0] for v in views] + (['references'] if extra else []),
                   'columns': ['silhouette', 'clay', 'look'], 'tile_px': tile, 'render_px': n, 'render_scale': round(render_scale, 3), 'asset_px': px,
                   'references': [n for n, _ in refs_in] + (['golden'] if args.golden else [])},
        'game_tile': os.path.abspath(stem + '_game.png'),
        'silhouette_fill': fills, 'motif': motif,
        'game_view': measured,
        'against_style': {'value_range': [lo, hi],
                          'inside_value_range': round(float(inside.mean()), 3),
                          'inside_value_range_of': 'the lit band' if shading == 'toon' else 'the asset',
                          'inside_value_range_expected': '>= 0.9',
                          'palette_coverage': coverage,
                          'palette_coverage_expected': '>= 0.85' if shading in ('toon', 'flat') and px >= 64
                          else "the golden asset's number",
                          # a guide for the reviewers, not a gate: the references are whole frames, this is one asset
                          'look': {k: {'asset': measured[k], 'style': target[k]} for k in LOOK_KEYS if k in target}},
    }
    with open(stem + '.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, indent=1)
    print('SHEET %s: %dx%d, game view L* %.0f-%.0f, inside value_range %.2f, palette coverage %s'
          % (args.out, sheet.shape[1], sheet.shape[0], measured['L_p2'], measured['L_p98'],
             report['against_style']['inside_value_range'], coverage))
    if 'chroma_mean' in target and abs(measured['chroma_mean'] - target['chroma_mean']) > CHROMA_GAP:
        # louder or duller than the references: the over-saturated toon of a generic asset, or a washed-out one
        print('SHEET WARNING: game view chroma_mean %.1f, the references %.1f (more than %d apart): the colour lens '
              'makes it a fix unless STYLE.md says why' % (measured['chroma_mean'], target['chroma_mean'], CHROMA_GAP))
    if min(fills['front'] or 0, fills['right'] or 0) >= BOX_FILL:
        print("SHEET NOTE: front and side silhouettes fill %.2f and %.2f of their boxes, a primitive's outline: say "
              "what in the silhouette is not a box or can, or why the brief wants one"
              % (fills['front'], fills['right']))
    if not motif:
        print("SHEET WARNING: %s %s: the game's signature detail every asset carries (style-bible step 1.5) goes "
              "unchecked" % (notes, 'has no line starting "Motif:"' if os.path.isfile(notes) else 'is missing'))


if __name__ == '__main__':
    main()
