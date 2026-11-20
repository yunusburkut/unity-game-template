# Fails a built asset that leaves the game's style bible (style.json). Headless, on the saved .blend of the build:
#
#   blender --background --factory-startup --python-exit-code 1 <asset>.blend --python style_gate.py -- \
#       --style Tools/Blender/Style/style.json [--class prop] [--objects SM_A,SM_B] [--report gate.json]
#
# Exit 1 is a failed gate; every failure names the object or asset, the rule and the number. Checked: the meshes an
# export takes (exported_meshes: in the view layer, rendered or a part under a classed root, which an export by
# selection ships hidden too, not a Boolean cutter; minus COL_ proxies and _LOD1+ children), or the ones --objects
# names, on the evaluated mesh (modifiers applied, as exported) with the evaluated object's material slots (a slot
# linked to the object wins, as in the FBX; a Boolean or Set Material node may add slots); the faces round one edge
# are joined, and so are the two faces of a split edge (Edge Split, a hard-edge export: exactly two faces at the
# edge's two end positions), so split edges do not read as loose parts, while a part touching at one point, or a closed
# part sharing a whole edge with another (a flush lid: four faces there), stays its own. Every run prints one
# STYLE FACTS line per asset (triangles, band, the curve, flat-waste and hidden shares, the 3 largest loose parts,
# its submeshes):
#   instances the object instances nothing (unrealized geometry nodes, particles): the counts below would miss it
#   material  every used slot has a material; none is Blender's untouched default (Blender's name, Material or
#             Material.001, at Blender's 0.8 grey; a renamed one there is judged as that light grey) or carries
#             Blender's name with a colour set (name it M_<Role>); with texel_density "atlas", none is a flat colour
#             (map it to the palette atlas); the base colour is a flat colour or an image texture linked straight to
#             Base Color (node-made colour, or an image behind a Reroute or a muted node, does not reach Unity through
#             FBX), with nothing on its Vector input but a UV Map node reading UV0 or a Texture Coordinate node's UV
#             output (Unity's material takes no Mapping: bake it into the UVs). The colour judged is the one FBX
#             carries: the Base Color of the Principled BSDF linked straight to the Material Output (one behind a Mix
#             Shader or another node fails: FBX then exports the viewport colour and no texture), then the viewport
#             colour, which the toon pipeline's manifest carries and which FBX takes when no Principled is linked
#             there. Under shading "toon" no material is a cutout (Toon.shader has no alpha clip, so it would draw as
#             a solid card)
#   palette   a flat colour sits within palette_de (CIELAB distance) of a palette role or an accent; an M_<Role>
#             material of the toon pipeline matches its own role
#   value     every colour's L* is inside value_range (a palette or accent colour may sit outside it: confirmed by
#             eye, a bright accent is too few pixels to move the p98 it comes from), and nothing else is pure black
#             (L* < 3) or pure white (L* > 97)
#   texture   sampled through the first UV layer (UV0, the one Unity's _BaseMap reads: the texels the asset shows,
#             not the whole atlas; an image material on a mesh with no UV map fails, and so does an image made in
#             memory whose pixels the .blend did not keep: pack or save it), weighted by surface area:
#             L* p2/p98 inside value_range (5 L* slack), at most texture_off_palette_max of the samples farther than
#             palette_de from every palette and accent colour. Alpha hides a texel only when the material's
#             Alpha takes the texture's alpha (a cutout); an atlas keeping smoothness in alpha is measured whole
#   detail    no loose part is smaller than detail_floor_m on its longest side, or thinner across (a rod), by its
#             widths along its face normals and principal axes (narrowest, narrowest at right angles, the rest): it
#             vanishes or breaks up at game size; the message gives the first parts' centres and sizes
#   texel     with a numeric texel_density (px/m), an image-textured material is within 10% of it
#   edges     with hard_edges_max_share set, the share of edges sharper than 80 degrees stays under it (a proxy for
#             bevel_m: the bevel width itself is not measurable from the mesh; the review sheet judges it)
#   mesh      no closed loose part is wound inside out (negative volume; a mirrored matrix's winding turned back), and
#             no edge joins two faces wound opposite ways (some faces flipped): ForwardLit culls back faces, so the
#             game would draw the part's inside; no face is an inner wall (every edge of it joins 3 or more faces:
#             what a weld, Mirror or Array merge leaves between two closed parts), which the player never sees and
#             which leaves the part with no inside for the hidden rule; no checked part is hidden in the viewport
#             (the export by selection skips it)
# and per asset: the topmost object up the parent chain with "style_class" (on the object, not its mesh) and every
# mesh under it; without one, the topmost mesh. Parent a multi-part asset's parts under one root; an Empty that only
# groups props is not an asset. With --objects naming only some parts, the report lists the rest as unchecked_parts:
#   triangles the summed triangle count is inside triangles[<class>] (class from --class or the root's "style_class");
#             the message says under or over and the remedy (under, on a root with no "style_class": parent the
#             parts first; over with no curve, waste, detail or hidden failure: a curve, flat-waste or hidden share
#             over 0.1 that failed no limit is named to cut first, else the design has more parts than the band
#             affords, drop parts or take the band to the decision page); an asset smaller than camera.asset_m
#             is held to a lower floor, ceil(floor x min(1, size_m / asset_m)), size_m its largest bounding-box
#             side in world metres, as toon_prop's check() does; the fact band_top_share is the count
#             over the band's top, a ceiling, not a target
#   mesh      no part under the root is a render-visible curve, text, metaball or other non-mesh: the export drops it
#   accent    the share of the seen surface within palette_de of an accent colour (by colour, so an M_<Role> material
#             in an accent colour counts) stays under accent_max_share; a triangle's area inside another closed loose
#             part of the asset (every edge joins two of its faces; a mirrored part's winding turned back) is not
#             seen, sampled at its corners, edge midpoints and centre, each a hair in front of the face: a face lying
#             flat on the other part (a body's top under a flush lid) is inside it, one beside it is not
#   hidden    with hidden_max_share set, the share of triangles whose corners and centre all lie inside stays under
#             it: the player never sees them, so they only cost
#   materials with materials_max[<class>] (or one number) set, the asset uses at most that many materials: each is a
#             submesh in Unity, drawn twice when outlined; the fact submeshes sums each part's materials (separate
#             parts multiply the draws: join them)
#   waste     with flat_waste_max_share set, the share of triangles that only split flat faces stays under it: those
#             flat_waste's restricted dissolve removes with nothing on screen changing (shape, shading, outline,
#             material and UV map kept); a bare Limited Dissolve is not the same
#   curve     with curve_waste_max_share[<class>] (or one number) set, curves (smooth, or facets under 1 px across)
#             cut so fine that two neighbouring segments merged into one stay within CHORD_PX (0.25 px) of the curve
#             at asset_px (each segment's own chord error under about 0.06 px), and cuts along a smooth surface's
#             straight way, stay under that share of the triangles (see curve_waste: height loops that stay count
#             with their column, so they cannot thin the share); a class the game draws larger
#             than asset_px (a close-up hero) has no entry

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
from extract_style import linear_to_srgb, read_rgba, srgb_to_lab, srgb_to_linear  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

DEFAULT_RGB = (0.8, 0.8, 0.8)
DEFAULT_NAME = re.compile(r'^Material(\.\d+)?$')     # the names Blender gives a new material
LOD_CHILD = re.compile(r'_LOD[1-9]\d*$')
TEXTURE_SIDE = 1024        # textures are sampled at most this size: an atlas cell stays pixels wide, a 4K map 16 MB
TRI_SAMPLES = (4, 4096)     # samples per triangle: about one per texel it covers, within these bounds
MAX_SAMPLES = 2_000_000     # per material; past it every triangle's count shrinks in proportion
FLAT_DEG = 0.1              # faces and normals this close count as the same plane: float noise, not modelled shape
# px at asset_px: a curve cut so fine that two neighbouring segments merged into one stay this near it shows nothing
# more than the merged one (each segment's own chord error is then under about 0.06 px; a build aims at 0.5 px)
CHORD_PX = 0.25
# renders in Blender, never exported (the FBX export takes meshes only)
NON_MESH = {'CURVE', 'SURFACE', 'META', 'FONT', 'CURVES', 'POINTCLOUD', 'VOLUME', 'GREASEPENCIL'}


def is_default(rgb):
    return all(abs(a - b) < 1e-4 for a, b in zip(rgb, DEFAULT_RGB))


def surface(mat):
    """The node linked to the active Material Output's Surface, or None."""
    out = next((n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output),
               None) if mat.node_tree else None
    return out.inputs['Surface'].links[0].from_node if out is not None and out.inputs['Surface'].links else None


def principled(mat):
    """The Principled BSDF linked straight to the active Material Output's Surface, the only one the FBX export reads
    (Blender's PrincipledBSDFWrapper); a leftover unconnected one is not judged. Behind a Mix Shader, or with no
    Principled there, it is None: FBX then carries the viewport colour and no texture."""
    n = surface(mat)
    return n if n is not None and n.type == 'BSDF_PRINCIPLED' else None


def base_colour(mat, viewport=True):
    """('image', image node) | ('rgb', sRGB tuple) | ('viewport', sRGB tuple) | ('nodes', node name) |
    ('default', None). viewport: the colour may live in the viewport colour (the toon pipeline); else that colour is
    reported as 'viewport', which FBX does not carry beside a Principled linked to the output (with none linked there
    the viewport colour is the one FBX carries: 'rgb'). 'nodes' includes an image behind a Reroute or a muted node: the
    FBX export takes only an Image Texture linked straight to Base Color. 'default' is a material Blender named
    (Material.001) with both colours at Blender's 0.8 grey; a named one there is a deliberate light grey."""
    bsdf = principled(mat)
    if bsdf is not None and bsdf.inputs['Base Color'].is_linked:
        src = bsdf.inputs['Base Color'].links[0].from_node
        if src.type == 'TEX_IMAGE' and src.image is not None:
            return 'image', src
        return 'nodes', '%s (%s)' % (src.name, src.bl_label)
    # FBX carries the Principled Base Color; a toon build may keep the palette colour only in the viewport colour, which
    # only its manifest carries (toon_prop.py writes both)
    for kind, rgb in (('rgb', tuple(bsdf.inputs['Base Color'].default_value)[:3] if bsdf else None),
                      ('rgb' if viewport or bsdf is None else 'viewport', tuple(mat.diffuse_color)[:3])):
        if rgb is not None and not is_default(rgb):
            return kind, tuple(float(c) for c in linear_to_srgb(rgb))
    if DEFAULT_NAME.match(mat.name):
        return 'default', None
    return 'rgb', tuple(float(c) for c in linear_to_srgb(DEFAULT_RGB))


def typed_srgb(val, role_lab, de):
    """A hint when the colour holds the role's sRGB numbers as if they were linear (Blender colours are linear)."""
    if np.linalg.norm(srgb_to_lab(srgb_to_linear(np.array(val))) - role_lab) <= de:
        return ': it holds the sRGB numbers; set srgb_to_linear(srgb), as toon_prop does'
    return ''


def is_cutout(mat, tex):
    """True when the material's Alpha takes this texture's alpha: only then is a low-alpha texel unseen."""
    bsdf = principled(mat)
    if bsdf is None or not bsdf.inputs['Alpha'].is_linked:
        return False
    link = bsdf.inputs['Alpha'].links[0]
    return link.from_node == tex and link.from_socket.name == 'Alpha'


# Blender keeps a generated image's pixels in a .blend only packed or in a file: reopened, it is blank. One painted in
# this run is dirty; a packed or saved one is a FILE. Ceiling: a generated image never painted (one flat colour, which
# the .blend does keep) reads as unsaved too; packing it passes
UNSAVED = ('%s was made in memory and its pixels were not saved with the .blend: image.pack() before saving, or save '
           'it to a file (image.filepath_raw, image.save())')


def unsaved(img):
    return img.source == 'GENERATED' and not img.is_dirty


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
    """Per loop triangle: material index, world area, UVs (n, 3, 2) or None, and world corners (n, 3, 3)."""
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
    if len(mesh.uv_layers):         # the first layer: FBX writes it as UV0, the one Unity's _BaseMap reads
        u = np.empty(len(mesh.loops) * 2, np.float32)
        mesh.uv_layers[0].data.foreach_get('uv', u)
        uv = u.reshape(-1, 2)[tl.reshape(-1, 3)]
    return mi, area, uv, p


def wpercentile(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return np.interp(np.asarray(q) / 100.0, c / c[-1], x[o])


def check_object(obj, style, fail, info, others=()):
    """Every per-object rule on the mesh as exported; returns its triangles, world area and accent-coloured area."""
    eval_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = eval_obj.to_mesh()
    try:
        # through the evaluated object's slots: a slot linked to the object overrides the mesh's material, and FBX
        # ships that one; a Boolean's transferred material or a Set Material node adds slots the original lacks.
        # The ink line is the game's (style "outline") and the root's ("outline": False on kit and level pieces)
        return check_mesh(obj.name, mesh, [s.material for s in eval_obj.material_slots], obj.matrix_world, style,
                          fail, info, others, bool(style.get('outline', True) and root_of(obj).get('outline', True)))
    finally:
        eval_obj.to_mesh_clear()


def check_mesh(name, mesh, mats, matrix, style, fail, info, others=(), outlined=True):
    pal = style.get('palette') or {}
    pal_lab = {r: srgb_to_lab(np.array(v['srgb'], float)) for r, v in pal.items()}
    accent_lab = [srgb_to_lab(np.array(a, float)) for a in style.get('accents') or []]
    allowed = list(pal_lab.items()) + [('accents[%d]' % i, a) for i, a in enumerate(accent_lab)]
    de = float(style.get('palette_de', 6.0))
    lo, hi = style.get('value_range', [0.0, 100.0])
    mi, area, uv, corners = mesh_arrays(mesh, matrix)
    accent_area = 0.0
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.transform(matrix)
    bm.normal_update()
    bm.faces.index_update()
    shared, find = loose_parts(bm)
    # a triangle inside another closed part of the asset (a hoop's cap inside the barrel, in this mesh or another
    # part) is never on screen: the accent share counts the surface the player sees, and the hidden rule the
    # triangles the player never sees. A long triangle can cross the other part's surface, so each is sampled at its
    # corners, edge midpoints and centre: the seen area is the outside share of those 7, and a triangle is hidden only
    # when its corners and centre are all inside (a sliver poking out between samples still errs as hidden)
    mirrored = matrix.determinant() < 0
    own = closed_parts(bm, shared, find, mirrored)
    poly = np.empty(len(mi), np.int32)
    mesh.loop_triangles.foreach_get('polygon_index', poly)
    here = np.array([find(int(i)) for i in poly], np.int64)
    # a closed part's volume by its winding (a mirrored matrix turns the winding back) is negative when its faces
    # look inward: Toon.shader's ForwardLit culls back faces, so the game would draw the part's far inside
    for p in own:
        t = corners[here == p[0]].astype(float)
        t -= t.mean((0, 1))
        if np.einsum('ij,ij->', t[:, 0], np.cross(t[:, 1], t[:, 2])) * (-1 if mirrored else 1) < -1e-12:
            fail(name, 'mesh', 'faces wound inside out, recalc normals (bmesh.ops.recalc_face_normals(bm, '
                 'faces=bm.faces[:]) in the build script; by hand Mesh > Normals > Recalculate Outside)')
            break
    # the volume test passes a part with a few faces flipped (a crate with one side turned still has a positive
    # volume), and an open part has no volume: an edge whose two faces run it the same way joins faces wound opposite
    # ways. Ceiling: faces cut apart by Edge Split share no edge, so they are not compared
    flipped = sum(1 for e in bm.edges if len(e.link_faces) == 2 and not e.is_contiguous)
    if flipped:
        fail(name, 'mesh', '%d edge(s) join faces wound opposite ways, so the game culls the flipped faces and shows '
             'the part\'s inside: recalc normals (bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]) in the build '
             'script)' % flipped)
    walls = sum(1 for f in bm.faces if all(len(e.link_faces) > 2 for e in f.edges))
    if walls:
        fail(name, 'mesh', '%d inner wall face(s) a weld, Mirror or Array merge left between parts: delete them (the '
             'player never sees them, and the part has no inside for the hidden rule)' % walls)
    pts = np.concatenate([corners, (corners + np.roll(corners, -1, axis=1)) / 2, corners.mean(1, keepdims=True)], 1)
    # a face is seen from its front, so each sample is tested 0.2 mm in front of its triangle (twice inside()'s
    # doubt) and 2% in toward its centre: a face lying on another part's surface (a body's top under a flush lid) is
    # buried, one that only meets it along an edge (their flush sides, a wall under an overhang) is not. Ceiling: on
    # a triangle under about 1.5 cm high the 2% is inside()'s doubt, so a flush sliver still errs as seen
    front = np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0])
    front *= (-2e-4 if mirrored else 2e-4) / np.maximum(np.linalg.norm(front, axis=1, keepdims=True), 1e-12)
    pts += (pts[:, 6:] - pts) * 0.02 + front[:, None]
    ids, counts = np.unique(here, return_counts=True)      # the largest loose parts, for the asset's facts line
    largest = [(int(counts[k]), name if len(ids) == 1 else '%s at (%.2f, %.2f, %.2f) m'
                % (name, *np.round(corners[here == ids[k]].mean((0, 1)), 2) + 0.0)) for k in np.argsort(-counts)[:3]]
    buried = np.zeros(pts.shape[:2], bool)
    for k, p in enumerate(own + list(others)):     # a part buries nothing of its own
        rows = np.flatnonzero(here != p[0]) if k < len(own) else np.arange(len(pts))
        buried[rows] |= inside(pts[rows].reshape(-1, 3), p).reshape(-1, 7)
    hidden = buried[:, [0, 1, 2, 6]].all(1)
    seen = np.where(hidden, 0.0, 1.0 - buried.mean(1))
    shown = area * seen

    for i in sorted(set(mi.tolist())):
        sel = mi == i
        mat = mats[i] if i < len(mats) else None
        if mat is None:
            fail(name, 'material', 'slot %d has no material' % i)
            continue
        kind, val = base_colour(mat, style.get('shading') == 'toon')
        if kind == 'default':
            fail(name, 'material', '%s is the untouched default material' % mat.name)
            continue
        if DEFAULT_NAME.match(mat.name):        # a colour was set, so its other rules still run
            fail(name, 'material', '%s carries Blender\'s default name: name it M_<Role>' % mat.name)
        via = surface(mat)
        if via is not None and via.type != 'BSDF_PRINCIPLED' and any(
                n.type == 'BSDF_PRINCIPLED' and n.outputs[0].is_linked for n in mat.node_tree.nodes):
            fail(name, 'material', '%s: the Principled BSDF reaches the output through %s, so FBX exports the '
                 'viewport colour and no texture: link it straight to the Material Output' % (mat.name, via.name))
        if kind == 'image' and style.get('shading') == 'toon' and is_cutout(mat, val):
            fail(name, 'material', '%s: a cutout under Toon.shader draws as a solid card (Toon.shader has no alpha '
                 'clip): model the shape, or give this piece a non-toon shading' % mat.name)
        if kind == 'viewport':
            fail(name, 'material', '%s has its colour only in the viewport colour, which FBX does not carry (Unity '
                 'draws it grey): set the Principled Base Color' % mat.name)
        elif kind == 'nodes':
            fail(name, 'material', '%s takes its base colour from node %s, which FBX does not carry: set a flat '
                 'colour on the Principled Base Color itself, or for a texture link an Image Texture straight to Base '
                 'Color (the export follows no Reroute or muted node), or bake the colour to an image'
                 % (mat.name, val))
        elif kind == 'rgb':
            lab = srgb_to_lab(np.array(val))
            if style.get('texel_density') == 'atlas':
                fail(name, 'material', '%s is a flat colour, but texel_density is atlas: map it to the palette atlas'
                     % mat.name)
            # a palette or accent colour was confirmed by eye (a near-black ink role too): a bright accent the
            # screenshots show in few pixels sits past the pooled p98 that value_range comes from
            confirmed = any(np.linalg.norm(lab - l) <= de for _, l in allowed)
            if not confirmed and (lab[0] < 3 or lab[0] > 97):
                fail(name, 'value', '%s is pure %s (L* %.0f)' % (mat.name, 'black' if lab[0] < 3 else 'white', lab[0]))
            elif not confirmed and not lo <= lab[0] <= hi:
                fail(name, 'value', '%s L* %.0f outside value_range %s-%s' % (mat.name, lab[0], lo, hi))
            if allowed:
                # M_Wood.001 (Blender's duplicate name) is still the Wood role
                role = re.sub(r'\.\d+$', '', mat.name[2:]) if mat.name.startswith('M_') else None
                if role in pal_lab:
                    d = float(np.linalg.norm(lab - pal_lab[role]))
                    if d > de:
                        fail(name, 'palette', '%s is %.1f from its role %s (palette_de %.0f)%s'
                             % (mat.name, d, role, de, typed_srgb(val, pal_lab[role], de)))
                else:
                    d, near, near_lab = min(((float(np.linalg.norm(lab - l)), r, l) for r, l in allowed),
                                            key=lambda t: t[0])
                    if d > de:
                        fail(name, 'palette', '%s is off-palette: nearest %s at %.1f (palette_de %.0f)%s'
                             % (mat.name, near, d, de, typed_srgb(val, near_lab, de)))
            # by colour, whatever the name: a palette role painted in an accent colour is accent surface too
            if any(np.linalg.norm(lab - a) <= de for a in accent_lab):
                accent_area += float(shown[sel].sum())
        elif uv_changed(val, mesh):
            fail(name, 'texture', '%s reads %s through node %s on its Vector input, which Unity\'s material does not '
                 'take (it samples UV0 as is): bake the mapping into the UVs' % (
                     mat.name, val.image.name, val.inputs['Vector'].links[0].from_node.name))
        else:
            accent_area += check_image(name, mat, val, area[sel], None if uv is None else uv[sel],
                                       [a for _, a in allowed], len(pal_lab), de, lo, hi, style, fail, info,
                                       seen[sel])

    floor = style.get('detail_floor_m')
    if floor:
        co = {}
        for f in bm.faces:
            c, normals = co.setdefault(find(f.index), ([], []))
            c.extend(v.co for v in f.verts)
            normals.append(f.normal)
        small, thin = [], []
        for c, normals in co.values():
            c = np.array(c)
            mid = c.mean(0)
            c -= mid
            s, axes = np.linalg.svd(c, full_matrices=False)[1:]
            # a part that fails has two widths at right angles under the floor, so every corner lies within
            # floor x sqrt(2) of one line and the two smaller singular values stay under this: the others stop here
            # (a ring of wire reads wide both ways, so it errs low)
            if s[1] ** 2 + s[2] ** 2 >= 2 * len(c) * floor ** 2:
                continue
            # widths along the part's face normals and principal axes: the principal axes of a square or round
            # section point anywhere, and a 12 mm cube read up to 17 mm along them. Narrowest first, then the narrowest
            # at right angles to it, then the way left: a rod is long one way only. Ceiling: a dense thin part (a
            # rope) takes every k-th direction, so it errs wide
            dirs = np.concatenate([np.unique(np.round(np.array(normals), 3), axis=0), axes])
            dirs = dirs[::1 + len(dirs) * len(c) // 4_000_000]
            ext, used = [], []
            for _ in range(2):
                for d in used:
                    dirs = dirs - np.outer(dirs @ d, d)
                length = np.linalg.norm(dirs, axis=1)
                dirs = dirs[length > 0.1] / length[length > 0.1, None]
                wide = np.ptp(c @ dirs.T, axis=0)
                ext.append(wide.min())
                used.append(dirs[wide.argmin()])
            ext = np.sort(ext + [np.ptp(c @ np.cross(*used))])[::-1]
            if ext[0] < floor:
                small.append((mid, ext[0]))
            elif ext[1] < floor:
                thin.append((mid, ext[1]))

        def where(parts):           # the first few, so the build script's line can be found
            return '; '.join('at (%.2f, %.2f, %.2f) m, %.3f m' % (*m, s) for m, s in parts[:3]) + (
                '; ...' if len(parts) > 3 else '')

        if small:
            fail(name, 'detail', '%d loose part(s) smaller than detail_floor_m %.3f m: %s'
                 % (len(small), floor, where(small)))
        if thin:
            fail(name, 'detail', '%d loose part(s) thinner than detail_floor_m %.3f m across, a line that breaks up '
                 'at game size: %s' % (len(thin), floor, where(thin)))
    inner = [faces for faces in shared.values() if len(faces) == 2]
    hard = sum(1 for a, b in inner if a.normal.angle(b.normal, 0.0) > math.radians(80))
    share = hard / max(1, len(inner))
    info(name, 'hard_edge_share', round(share, 3))
    limit = style.get('hard_edges_max_share')
    if limit is not None and share > limit:
        fail(name, 'edges', '%.0f%% of edges are unbevelled hard corners (max %.0f%%; bevel_m %s)'
             % (share * 100, limit * 100, style.get('bevel_m')))
    cam = style.get('camera') or {}
    around, straight = curve_waste(mesh, bm, cam['asset_px'] / (cam.get('asset_m') or 1.0), outlined) if cam.get(
        'asset_px') else (0, 0)
    info(name, 'curve_waste', around + straight)
    removable = flat_waste(mesh, bm)
    info(name, 'flat_waste', removable)
    bm.free()
    return {'triangles': int(len(mi)), 'area': float(shown.sum()), 'accent_area': accent_area, 'removable': removable,
            'curve': around + straight, 'straight': straight, 'hidden': int(hidden.sum()), 'parts': largest,
            'materials': {mats[i].name for i in set(mi.tolist()) if i < len(mats) and mats[i] is not None},
            'box': np.array([corners.min((0, 1)), corners.max((0, 1))]) if len(mi) else np.empty((0, 3))}


def loose_parts(bm):
    """bm's faces joined into loose parts: (shared, find). shared maps an edge's two end positions (0.01 mm grid) to
    the faces there; find gives a face index's part id. The faces round one edge are one part. An Edge Split modifier
    or a hard-edge export cuts faces apart along edges: those join again where exactly two faces carry the edge's
    two end positions, which a part touching the body at one vertex does not. Two closed shells sharing a whole edge
    (a lid with the body's footprint, two stacked crates) put four faces there and stay two parts. Ceiling: a split
    seam lying on another part's edge is not told from that part, so its faces stay apart and read as open parts."""
    pos = {v: tuple(int(round(c * 1e5)) for c in v.co) for v in bm.verts}
    shared = {}
    for e in bm.edges:
        shared.setdefault(frozenset((pos[e.verts[0]], pos[e.verts[1]])), []).extend(e.link_faces)
    part = list(range(len(bm.faces)))

    def find(i):
        while part[i] != i:
            part[i] = part[part[i]]
            i = part[i]
        return i

    for faces in [list(e.link_faces) for e in bm.edges] + [fs for fs in shared.values() if len(fs) == 2]:
        for f in faces[1:]:
            part[find(f.index)] = find(faces[0].index)
    return shared, find


def closed_parts(bm, shared, find, mirrored):
    """[(part id, BVH tree, box low, box high)] of bm's closed loose parts (world space), the only ones with an
    inside: every edge of the part joins exactly two of its faces (a flush neighbour's faces on the same edge are not
    its own). A label plane or an open tube buries nothing. mirrored: the matrix flipped the winding, so the faces
    are turned back to face outward."""
    open_parts = set()
    for faces in shared.values():
        ids = [find(f.index) for f in faces]
        open_parts.update(i for i in ids if ids.count(i) != 2)
    faces = {}
    for f in bm.faces:
        if find(f.index) not in open_parts:
            faces.setdefault(find(f.index), []).append(f)
    out = []
    for pid, fs in faces.items():
        verts = list({v for f in fs for v in f.verts})
        at = {v: i for i, v in enumerate(verts)}
        polys = [[at[v] for v in (list(f.verts)[::-1] if mirrored else f.verts)] for f in fs]
        co = np.array([v.co for v in verts])
        out.append((pid, BVHTree.FromPolygons([v.co.copy() for v in verts], polys), co.min(0), co.max(0)))
    return out


def inside(pts, part):
    """Which of the points pts (n, 3) lie inside the closed part: within its box, and behind its nearest face."""
    _, tree, lo, hi = part
    got = np.zeros(len(pts), bool)
    for k in np.flatnonzero(((pts >= lo) & (pts <= hi)).all(1)):
        c = Vector(pts[k])
        loc, normal, _, dist = tree.find_nearest(c)
        got[k] = loc is not None and dist > 1e-4 and (c - loc).dot(normal) < 0
    return got


def corner_normals(mesh):
    """Per loop normals (n, 3) and each polygon's first loop, in Mesh order (bmesh from_mesh keeps it)."""
    cn = np.empty(len(mesh.loops) * 3, np.float32)
    mesh.corner_normals.foreach_get('vector', cn)
    start = np.empty(len(mesh.polygons), np.int32)
    mesh.polygons.foreach_get('loop_start', start)
    return cn.reshape(-1, 3), start


def curve_waste(mesh, bm, px_per_m, outlined=True):
    """About how many triangles curves spend past what the game camera shows. Across an edge the surface turns
    by the faces' angle t between two segments, each as wide as its face (measured from the edge). A face is
    over-fine at the edge when the two segments merged into one chord stay within CHORD_PX of the curve at asset_px:
    the edge then lies that near the chord, r_px (1 - cos t) < CHORD_PX on a round part of radius r (each segment's
    own chord error, r_px (1 - cos t/2), is then under about CHORD_PX / 4, 0.06 px). The wider face of the two is
    held to a neighbour as wide as itself (width / t x (1 - cos t)), so the flat a bevel ends in is no segment of its
    curve, while the bevel's outer strip is. A face counts only when every curved edge it has is
    over-fine (a quad's diagonal turns little, its ring edge decides), and half its triangles go: merging every other
    segment one way. That errs low (both ways saves 3 in 4, a cylinder's caps shrink too), as do the other choices
    (coplanar pieces of one segment merged first, the wider face's own width). Its triangles are those of every piece
    its plane is cut into where the cuts stay (smooth pieces the straight count below leaves: a 64-sided cylinder
    fails with height loops as without), else the merged face's. Smooth edges (both faces share each end's normal),
    and hard ones whose narrower face is under 1 px across at asset_px: facets a pixel or wider are a look, and such
    an edge keeps both its faces out of the count where its turn shows (the merge would move it CHORD_PX or more);
    narrower they blur into a curve. The fix is fewer segments in the build.
    Returned apart from that (the fix differs: drop the loops): the cuts along a smooth surface's straight way
    (height loops on a cylinder's side), which flat_waste leaves since its corner normals are not the face normal. A
    plane's faces count when they share one material, one affine UV map, and corner normals and outline normals
    (OutlineNormalsPostprocessor's per-position average) affine in position (then shading, outline hull and texture
    interpolate the same across the merge), and every vertex the merge drops touches only such planes: all the
    triangles merging saves. A hard-capped cylinder's side fails the outline test (its rims tilt), so its height loops
    are not counted; that errs low. outlined False (the style's or the root's "outline"): the game draws no hull for
    this asset, so the outline test is left out and those loops count."""
    if not len(mesh.polygons):
        return 0, 0
    cn, start = corner_normals(mesh)
    flat = flat_faces(mesh, cn, start)

    def normal(f, v):
        return cn[start[f.index] + next(k for k, lp in enumerate(f.loops) if lp.vert == v)]

    same = math.cos(math.radians(FLAT_DEG))
    smooth = bm.edges.layers.int.new('style_gate_smooth')
    plane = list(range(len(bm.faces)))         # the coplanar pieces the dissolve below merges, by union-find

    def find(i):
        while plane[i] != i:
            plane[i] = plane[plane[i]]
            i = plane[i]
        return i

    for e in bm.edges:
        e[smooth] = len(e.link_faces) == 2 and all(normal(e.link_faces[0], v) @ normal(e.link_faces[1], v) >= same
                                                   for v in e.verts)
        if len(e.link_faces) == 2 and e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0) <= math.radians(
                FLAT_DEG):
            plane[find(e.link_faces[0].index)] = find(e.link_faces[1].index)
    group = bm.faces.layers.int.new('style_gate_plane')
    vid = bm.verts.layers.int.new('style_gate_vert')
    members = {}
    for f in bm.faces:
        f[group] = find(f.index)
        members.setdefault(f[group], []).append(f)
    bm.verts.index_update()
    for v in bm.verts:
        v[vid] = v.index
    chords = bm.copy()
    layers = smooth, group, vid
    smooth, group, vid = (chords.edges.layers.int['style_gate_smooth'], chords.faces.layers.int['style_gate_plane'],
                          chords.verts.layers.int['style_gate_vert'])
    bmesh.ops.dissolve_limit(chords, angle_limit=math.radians(FLAT_DEG), use_dissolve_boundaries=False,
                             verts=chords.verts[:], edges=chords.edges[:])
    kept = {v[vid] for v in chords.verts}
    left = {}
    for f in chords.faces:
        left[f[group]] = left.get(f[group], 0) + len(f.verts) - 2
    # the outline hull's normal, as OutlineNormalsPostprocessor bakes it: per position (0.1 mm grid) the sum of the
    # distinct corner normals there, so a hard cap's rim tilts 45 degrees and a height loop below it does not
    grid = {v: tuple(int(round(c * 1e4)) for c in v.co) for v in bm.verts}
    at = {}
    for f in bm.faces:
        for k, lp in enumerate(f.loops):
            ns = at.setdefault(grid[lp.vert], [])
            n = cn[start[f.index] + k]
            if not any(n @ m > 0.999 for m in ns):
                ns.append(n)
    hull = {p: sum(ns) / max(np.linalg.norm(sum(ns)), 1e-6) for p, ns in at.items()}
    uvs = bm.loops.layers.uv.values()
    tol = math.sin(math.radians(FLAT_DEG))
    clean = {g for g, fs in members.items() if len(fs) > 1 and not any(f.index in flat for f in fs)
             and len({f.material_index for f in fs}) == 1 and same_uv_map(fs, uvs)
             and affine(fs, np.concatenate([cn[start[f.index]:start[f.index] + len(f.loops)] for f in fs]), tol)
             and (not outlined or affine(fs, np.array([hull[grid[lp.vert]] for f in fs for lp in f.loops]), tol))}
    straight, merged = 0, set()         # merged: the planes whose cuts the straight count takes
    for g in clean:
        if all(find(lf.index) in clean for f in members[g] for v in f.verts if v.index not in kept
               for lf in v.link_faces):
            straight += sum(len(f.verts) - 2 for f in members[g]) - left.get(g, 0)
            merged.add(g)

    def width(f, e):
        p, d = e.verts[0].co, (e.verts[1].co - e.verts[0].co).normalized()
        return max(((v.co - p) - (v.co - p).dot(d) * d).length for v in f.verts)

    fine = {}           # (curved edge, face) -> the face is over-fine there
    for e in chords.edges:
        if len(e.link_faces) != 2:
            continue
        a, b = e.link_faces
        t = a.normal.angle(b.normal, 0.0)
        if not math.radians(FLAT_DEG) < t < math.radians(80):
            continue
        w = width(a, e), width(b, e)
        # the edge's distance from the chord that replaces the two segments; a facet under a pixel across shows no
        # facet (a flat-shaded Bevel's segments at 2 px): it is a curve. A hard facet a pixel or wider is a look: where
        # it turns enough to show (the gap is CHORD_PX or more) it holds both faces out of the count, as a smooth edge
        # that is not over-fine does; a slighter one (a flat-shaded Subsurf's long facets end to end) decides nothing
        gap = w[0] * w[1] * math.sin(t) / max(1e-12, math.sqrt(w[0] ** 2 + w[1] ** 2 + 2 * w[0] * w[1] * math.cos(t)))
        curve = e[smooth] or min(w) * px_per_m < 1
        if curve or gap * px_per_m >= CHORD_PX:
            for f, own in zip((a, b), w):
                fine[e, f] = curve and max(gap, own / t * (1 - math.cos(t))) * px_per_m < CHORD_PX
    over = 0
    for f in chords.faces:
        curved = [fine[e, f] for e in f.edges if (e, f) in fine]
        if curved and all(curved):
            # the face stands for the pieces its plane is cut into. Where the cuts stay (a smooth side's height loops
            # under hard caps hold the outline), each piece merges with its neighbour, so all of them count, and
            # pointless loops cannot thin the share; where the straight count above or flat_waste takes the cuts,
            # only the merged face does
            pieces = members[f[group]]
            whole = f[group] not in merged and not any(p.index in flat for p in pieces)
            over += (len(f.verts) - 2) * sum(len(p.verts) - 2 for p in pieces) // left[f[group]] if whole else len(
                f.verts) - 2
    chords.free()
    for seq, layer in zip((bm.edges, bm.faces, bm.verts), layers):     # last: removing one drops bm's face handles
        seq.layers.int.remove(layer)
    return over // 2, straight


def affine(faces, values, tol):
    """True when one affine map from position carries values (a row per corner of faces, in loop order)."""
    p = np.array([lp.vert.co for f in faces for lp in f.loops])
    p -= p[0]
    values = values - values[0]
    return np.abs(p @ np.linalg.lstsq(p, values, rcond=None)[0] - values).max() <= tol


def same_uv_map(faces, layers, tol=0.5 / TEXTURE_SIDE):
    """True when one affine position-to-UV map carries every corner of faces in every UV layer, so dissolving them
    interpolates the UVs as before (a 9-slice panel's stretched middle and its trim are two maps)."""
    return all(affine(faces, np.array([lp[layer].uv for f in faces for lp in f.loops]), tol) for layer in layers)


def flat_faces(mesh, cn, start):
    """Indices of the polygons whose every corner normal is the face normal (bm keeps the Mesh's face order)."""
    pn = np.empty(len(mesh.polygons) * 3, np.float32)
    mesh.polygon_normals.foreach_get('vector', pn)
    total = np.empty(len(mesh.polygons), np.int32)
    mesh.polygons.foreach_get('loop_total', total)
    same = (cn * np.repeat(pn.reshape(-1, 3), total, axis=0)).sum(1) > math.cos(math.radians(FLAT_DEG))
    return set(np.flatnonzero(np.minimum.reduceat(same.astype(np.int8), start)).tolist())


def flat_waste(mesh, bm):
    """Triangles Limited Dissolve removes with the look unchanged, counted after triangulating (Unity gets triangles,
    not the n-gons). Only faces whose every corner normal is the face normal take part, so shading interpolates as
    before; faces join only on one material and one affine UV map; a vertex goes only from inside one plane, so the
    corners and edge midpoints that steer Toon.shader's outline hull stay. Consumes bm: written back, it is that
    optimised mesh. Ceiling: a split hard edge (Edge Split) is a border whose vertices stay, so the count errs low."""
    if not len(mesh.polygons):
        return 0
    bm.normal_update()      # faces a build script just made hold no normal yet, and the verts test below reads them
    flat = flat_faces(mesh, *corner_normals(mesh))
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


def uv_changed(tex, mesh):
    """True when the image node's Vector input is linked to anything but a UV Map node reading UV0 (the first layer,
    or the render-active one when the node names none) or a Texture Coordinate node's UV output (the render-active
    layer)."""
    links = tex.inputs['Vector'].links
    if not links:
        return False
    n = links[0].from_node
    first = mesh.uv_layers[0] if len(mesh.uv_layers) else None
    return not (first is not None and (
        (n.type == 'UVMAP' and (n.uv_map == first.name or (n.uv_map == '' and first.active_render)))
        or (n.type == 'TEX_COORD' and links[0].from_socket.name == 'UV' and first.active_render)))


def check_image(name, mat, tex, area, uv, refs, n_pal, de, lo, hi, style, fail, info, seen=None):
    """The texture rules on the texels the mesh shows; returns the accent-coloured world area."""
    img = tex.image
    if unsaved(img):
        fail(name, 'texture', UNSAVED % img.name)
        return 0.0
    got = image_rgba(img)
    if got is None:
        fail(name, 'texture', '%s has no pixels (file missing and not packed)' % img.name)
        return 0.0
    rgb, alpha = got
    if uv is None:
        fail(name, 'texture', '%s is image-textured but the mesh has no UV map: Unity samples one texel for all of it'
             % mat.name)
        return 0.0
    uv_area = None
    if len(uv):
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
        rgb, alpha, weight = rgb[y, x], alpha[y, x], (area * (1.0 if seen is None else seen) / k)[tri]
    else:
        return 0.0
    if is_cutout(mat, tex):
        keep = alpha >= 0.5
        if not keep.any():
            fail(name, 'texture', '%s is transparent everywhere the mesh samples it' % img.name)
            return 0.0
        rgb, weight = rgb[keep], weight[keep]
    if weight.sum() <= 0:
        return 0.0
    lab = srgb_to_lab(rgb)
    accent_area = 0.0
    d, da = np.full(len(lab), np.inf), np.full(len(lab), np.inf)
    for k, r in enumerate(refs):            # a running minimum: N x refs x 3 at once is hundreds of MB
        dk = np.linalg.norm(lab - r, axis=1)
        d = np.minimum(d, dk)
        if k >= n_pal:                      # an accent: counted by colour, even where a palette role ties with it
            da = np.minimum(da, dk)
    # as for a flat colour, a texel within palette_de of a role was confirmed by eye: only the others meet value_range
    off_role = d > de
    if weight[off_role].sum() > 0:
        p2, p98 = wpercentile(lab[off_role, 0], weight[off_role], [2, 98])
        if p2 < lo - 5 or p98 > hi + 5:
            fail(name, 'texture', '%s L* p2-p98 %.0f-%.0f of its off-role texels outside value_range %s-%s'
                 % (img.name, p2, p98, lo, hi))
    if refs:
        off = float(weight[d > de].sum() / weight.sum())
        info(name, 'texture_off_palette', round(off, 3))
        limit = style.get('texture_off_palette_max')
        if limit is not None and off > limit:
            fail(name, 'texture', '%s: %.0f%% of the shown texels off-palette (max %.0f%%)'
                 % (img.name, off * 100, limit * 100))
        accent_area = float(weight[da <= de].sum())
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


def boolean_cutters():
    cutters = set()
    for o in bpy.data.objects:
        for m in o.modifiers:
            if m.type == 'BOOLEAN':
                cutters |= {m.object} if m.operand_type == 'OBJECT' else set(m.collection.all_objects if m.collection
                                                                            else [])
    return cutters


def exported(o, cutters):
    """An export takes o: a mesh, not a Boolean cutter, a COL_ proxy or a _LOD1+ child, and rendered, or a part under
    a classed asset root (unity-export exports by selection, which ships a part hidden from render too)."""
    return (o.type == 'MESH' and o not in cutters and not o.name.startswith('COL_') and not LOD_CHILD.search(o.name)
            and (not o.hide_render or (o.parent is not None and root_of(o).get('style_class') is not None)))


def parts_of(root):
    """The mesh objects the gate sums into root's asset."""
    cutters = boolean_cutters()
    return [o for o in [root, *root.children_recursive] if exported(o, cutters) and root_of(o) == root]


def exported_meshes():
    """The mesh objects an export of the scene takes (exported), in the view layer (its collection not excluded).
    Ceiling: a parent collection's own render switch is not followed; name the parts with --objects then."""
    bpy.context.view_layer.update()     # objects linked by a script since the last update are not listed before it
    cutters = boolean_cutters()
    return [o for o in bpy.context.view_layer.objects if exported(o, cutters)]


def named_meshes(arg):
    """The mesh objects a comma-separated --objects names; exits on a name that is missing or not a mesh."""
    names = arg.split(',')
    missing = [n for n in names if n not in bpy.data.objects]
    if missing:
        raise SystemExit('no such object(s): %s' % ', '.join(missing))
    objs = [bpy.data.objects[n] for n in names]
    not_mesh = [o.name for o in objs if o.type != 'MESH']
    if not_mesh:
        raise SystemExit('not mesh object(s): %s (name the mesh parts, not their root)' % ', '.join(not_mesh))
    return objs


def gate(objs, style, cls=None):
    """Runs every rule; returns (failures [{object, rule, message}], facts {name: {key: value}})."""
    failures, facts, assets = [], {}, {}
    _IMAGES.clear()

    def fail(o, rule, msg):
        failures.append({'object': o, 'rule': rule, 'message': msg})

    def info(o, k, v):
        facts.setdefault(o, {})[k] = v

    # instances (geometry nodes without Realize Instances, particles, vertex instancing) are exported but are not in
    # the object's own mesh, so every count below would miss them
    instanced = {}
    for i in bpy.context.evaluated_depsgraph_get().object_instances:
        if i.is_instance and i.parent is not None:
            instanced[i.parent.original.name] = instanced.get(i.parent.original.name, 0) + 1
    # each part's other parts: their closed loose parts can bury its faces (world space, as exported)
    parts, trees = {}, {}
    for obj in objs:
        parts.setdefault(root_of(obj).name, []).append(obj)
    for group in parts.values():
        for o in group if len(group) > 1 else ():
            ev = o.evaluated_get(bpy.context.evaluated_depsgraph_get())
            bm = bmesh.new()
            bm.from_mesh(ev.to_mesh())
            ev.to_mesh_clear()
            bm.transform(o.matrix_world)
            bm.faces.index_update()
            trees[o.name] = closed_parts(bm, *loose_parts(bm), o.matrix_world.determinant() < 0)
            bm.free()
    for obj in objs:
        if obj.name in instanced:
            fail(obj.name, 'instances', '%d instance(s) the gate cannot count: realize them (a Realize Instances node, '
                 'or bpy.ops.object.duplicates_make_real() for particles and vertex instancing) before the check'
                 % instanced[obj.name])
        got = check_object(obj, style, fail, info,
                           [p for o in parts[root_of(obj).name] if o is not obj for p in trees.get(o.name, ())])
        info(obj.name, 'triangles', got['triangles'])
        root = root_of(obj)
        a = assets.setdefault(root.name, {'cls': None, 'triangles': 0, 'area': 0.0, 'accent_area': 0.0, 'removable': 0,
                                          'curve': 0, 'straight': 0, 'hidden': 0, 'parts': [], 'materials': set(),
                                          'submeshes': 0, 'box': np.empty((0, 3))})
        a['cls'] = a['cls'] or cls or root.get('style_class') or obj.get('style_class')
        for k in ('triangles', 'area', 'accent_area', 'removable', 'curve', 'straight', 'hidden', 'parts'):
            a[k] += got[k]
        a['materials'] |= got['materials']
        a['submeshes'] += len(got['materials'])     # Unity draws each part's materials apart: a submesh each
        a['box'] = np.concatenate([a['box'], got['box']])
        if got['curve']:
            a.setdefault('curve_parts', []).append((got['curve'], obj.name))

    # a curve, text or metaball part renders in Blender, but the FBX export takes meshes only: Unity never gets it
    covered = set()
    for name in assets:
        root = bpy.data.objects[name]
        for o in [root, *root.children_recursive]:
            covered.add(o.name)
            if o.type in NON_MESH and not o.hide_render:
                fail(name, 'mesh', '%s is a %s, which the FBX export drops: convert it to a mesh in the build script, '
                     'or, when it is only a helper a modifier reads, hide it from render (hide_render)'
                     % (o.name, o.type.lower()))
            # unity-export exports by selection, and a part the view layer hides cannot be selected
            if o in objs and not o.visible_get():
                fail(name, 'mesh', '%s is hidden in the viewport: the export by selection skips it; show it or delete '
                     'it' % o.name)
            # an Empty instancing a collection exports its meshes, which no count above sees
            if o.name in instanced and o not in objs:
                fail(name, 'instances', '%s instances %d object(s) the gate cannot count: make them real '
                     '(bpy.ops.object.duplicates_make_real() with it selected) before the check'
                     % (o.name, instanced[o.name]))
    # an instancer under no checked asset (an Empty instancing a collection beside the props) is in no count either
    for o in bpy.context.view_layer.objects:
        if o.name in instanced and o.name not in covered and not o.hide_render:
            info(o.name, 'uncounted_instances', instanced[o.name])
    bands = style.get('triangles') or {}
    limit = style.get('accent_max_share')
    checked = {o.name for o in objs}
    for name, a in assets.items():
        info(name, 'asset_triangles', a['triangles'])
        unchecked = [o.name for o in parts_of(bpy.data.objects[name]) if o.name not in checked]
        if unchecked:       # --objects named only some parts: the sums below leave these out
            info(name, 'unchecked_parts', unchecked)
        largest = ', '.join('%s %d' % (p, n) for n, p in sorted(a['parts'], reverse=True)[:3])
        info(name, 'largest_parts', largest)
        off = [facts[o.name]['texture_off_palette'] for o in parts[name] if 'texture_off_palette' in facts[o.name]]
        if off:             # the worst part's, on the asset's facts line
            info(name, 'texture_off_palette', max(off))
        over = None         # the over-band message waits for the rules below: its remedy is what they name
        if bands:
            if a['cls'] not in bands:
                fail(name, 'triangles', 'no class: pass --class or set "style_class" on the asset root to one of %s'
                     % ', '.join(sorted(bands)))
            else:
                info(name, 'band', '%s %d-%d' % (a['cls'], *bands[a['cls']]))
                # the top is a ceiling, not a target: this shows a build parked at it
                info(name, 'band_top_share', round(a['triangles'] / max(1, bands[a['cls']][1]), 3))
                # an asset smaller than the class's typical one (camera.asset_m) is held to a proportionally lower
                # floor, the rule toon_prop's check() shares: ceil(floor x min(1, size_m / asset_m)), size_m its largest
                # bounding-box side in world metres (to 0.1 mm: float noise must not lift the ceil); an empty asset
                # has no size and keeps the band's floor; the top, a ceiling, stays
                lo, hi = bands[a['cls']]
                asset_m = (style.get('camera') or {}).get('asset_m') or 1.0
                size = round(float(np.ptp(a['box'], axis=0).max()), 4) if len(a['box']) else 0.0
                own = math.ceil(lo * min(1.0, size / asset_m)) if size > 0 else lo
                if a['triangles'] > hi:
                    over = '%d triangles over the %s band %d-%d: ' % (a['triangles'], a['cls'], lo, hi)
                elif a['triangles'] < own:
                    # parts with no classed root count as an asset each: under the band is then often the grouping
                    unrooted = bpy.data.objects[name].get('style_class') is None
                    fail(name, 'triangles', '%d triangles under the %s band %d-%d%s: %s'
                         % (a['triangles'], a['cls'], own, hi,
                            ' (the band\'s %d scaled by the asset\'s %.2f m against asset_m %s)' % (lo, size, asset_m)
                            if own < lo else '',
                            ('if this is a part, parent the asset\'s parts under one root with "style_class" (an '
                             'unparented part is an asset of its own); else ' if unrooted else '')
                            + 'add the detail the references show at asset_px (bevels, rims, planks, a trim), not cuts '
                            'on flat faces or extra segments; for a piece the references show flat (a tile, a wall '
                            'panel) set this class\'s floor to 0 on the decision page'))
        share = a['accent_area'] / a['area'] if a['area'] > 0 else 0.0
        info(name, 'accent_share', round(share, 3))
        if limit is not None and share > limit:
            fail(name, 'accent', '%.0f%% of the surface is accent colour (accent_max_share %.0f%%)'
                 % (share * 100, limit * 100))
        waste = a['removable'] / max(1, a['triangles'])
        info(name, 'flat_waste_share', round(waste, 3))
        if style.get('flat_waste_max_share') is not None and waste > style['flat_waste_max_share']:
            fail(name, 'waste', '%d of %d triangles only split flat faces (%.0f%%, flat_waste_max_share %.0f%%): '
                 'drop the cuts on flat faces in the build script (no subdivide or loop cut where nothing bends), or '
                 'call the game\'s copy of flat_waste (Tools/Blender/style_common.py) on the bmesh; a bare Limited '
                 'Dissolve is not the same (it also drops the edge midpoints the outline needs, warps a 9-slice UV and '
                 'leaves n-gons)'
                 % (a['removable'], a['triangles'], waste * 100, style['flat_waste_max_share'] * 100))
        hidden = a['hidden'] / max(1, a['triangles'])
        info(name, 'hidden_share', round(hidden, 3))
        if style.get('hidden_max_share') is not None and hidden > style['hidden_max_share']:
            fail(name, 'hidden', '%d of %d triangles (%.0f%%, hidden_max_share %.0f%%) sit inside another closed part '
                 'of the asset, where the player never sees them (a cap buried in the body, overlapping parts): leave '
                 'the buried faces out (an open band, cap_ends=False) or trim the part' % (
                     a['hidden'], a['triangles'], hidden * 100, style['hidden_max_share'] * 100))
        info(name, 'materials', len(a['materials']))
        info(name, 'submeshes', a['submeshes'])
        most = style.get('materials_max')
        most = most.get(a['cls']) if isinstance(most, dict) else most
        if most is not None and len(a['materials']) > most:
            # the ink line is the game's (style "outline") and the root's ("outline": False on kit and level pieces)
            outlined = style.get('outline', True) and bpy.data.objects[name].get('outline', True)
            fail(name, 'materials', '%d materials (%s), materials_max %d for %s: each is a submesh, drawn twice under '
                 'Toon.shader when outlined, %s%s; merge roles that read the same at game size%s' % (
                     len(a['materials']), ', '.join(sorted(a['materials'])), most, a['cls'],
                     'as this asset is (ForwardLit + Outline pass)' if outlined
                     else 'which this asset is not (one ForwardLit draw each)',
                     ', and separate parts multiply the draws (%d submeshes in %d parts: join them into one mesh)'
                     % (a['submeshes'], len(parts[name])) if len(parts[name]) > 1 else '',
                     ', or use the palette atlas' if style.get('texel_density') == 'atlas' else ''))
        curve = a['curve'] / max(1, a['triangles'])
        info(name, 'curve_waste_share', round(curve, 3))
        curve_max = style.get('curve_waste_max_share')
        curve_max = curve_max.get(a['cls']) if isinstance(curve_max, dict) else curve_max   # a number: every class
        if curve_max is not None and curve > curve_max:
            fail(name, 'curve', 'about %d of %d triangles (%.0f%%, curve_waste_max_share %.0f%%) look the same at game '
                 'size without: %d refine curves (smooth, or facets under 1 px across) cut so fine that two '
                 'neighbouring segments merged into one stay within %.2f px of the curve at asset_px (each segment\'s '
                 'own chord error under about %.2f px: fewer segments), %d cut a smooth side along its straight way '
                 '(drop those loops); a round part takes ceil(pi / acos(1 - 0.5 / r_px)) segments around, rounded up '
                 'to even, worst parts: %s'
                 % (a['curve'], a['triangles'], curve * 100, curve_max * 100, a['curve'] - a['straight'], CHORD_PX,
                    CHORD_PX / 4, a['straight'],
                    ', '.join('%s (%d)' % (p, n) for n, p in sorted(a['curve_parts'], reverse=True)[:3])))
        if over:
            names = {name} | {o.name for o in parts[name]}      # detail fails on the part, the others on the asset
            cut = sorted({f['rule'] for f in failures if f['object'] in names}
                         & {'curve', 'waste', 'detail', 'hidden'})
            # a share with no limit for this class (a hero's curves, a null flat_waste_max_share) or under its limit
            # failed nothing, but it is still triangles nothing on screen needs
            unseen = [(k, why) for k, why in (('curve_waste_share', 'fewer segments round curves'),
                                              ('flat_waste_share', 'no cuts on flat faces'),
                                              ('hidden_share', 'no faces buried in another part'))
                      if facts[name][k] > 0.1]
            fail(name, 'triangles', over + (
                'remove detail the game size cannot show, starting with what its %s failure%s' % (
                    ' and '.join(cut), ' names' if len(cut) == 1 else 's name') if cut else
                '%s failed no limit for %s, but cut there first (%s) where the game size shows no difference' % (
                    ' and '.join('%s %s' % (k, facts[name][k]) for k, _ in unseen), a['cls'],
                    '; '.join(why for _, why in unseen)) if unseen else
                'no curve, waste, detail or hidden failure names anything to cut, so the design has more parts than '
                'the band affords (largest: %s triangles): drop parts in the build script, or take the band to the '
                'decision page' % largest))
    return failures, facts


def check_colours(style, path):
    """Stops on a palette role that is not an object, or a palette, accent, light or outline colour that is not 3
    numbers 0-1 (the gate's CLI and the sheet's)."""
    colours = []
    for r, v in (style.get('palette') or {}).items():
        if not isinstance(v, dict):
            raise SystemExit('%s: palette.%s is %r: write {"srgb": [r, g, b], "smoothness": 0-1}' % (path, r, v))
        colours.append(('palette.%s.srgb' % r, v.get('srgb')))
    colours += [('accents[%d]' % i, a) for i, a in enumerate(style.get('accents') or [])]
    light, outline = style.get('light') or {}, style.get('outline')
    colours += [('light.' + k, light[k]) for k in ('color', 'shadow_srgb') if light.get(k) is not None]
    if isinstance(outline, dict) and outline.get('srgb') is not None:
        colours.append(('outline.srgb', outline['srgb']))
    for key, c in colours:
        if not (isinstance(c, list) and len(c) == 3 and all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in c)):
            raise SystemExit('%s: %s is %r: write 3 numbers 0-1 (style_metrics.json\'s toon_albedo_srgb or srgb), '
                             'not a hex or 0-255' % (path, key, c))


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
    check_colours(style, args.style)
    objs = named_meshes(args.objects) if args.objects else exported_meshes()
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
        if 'asset_triangles' in f:      # an asset root: the numbers a rebuild steers by, whatever passed
            print('STYLE FACTS %s: %d triangles, %s, curve_waste_share %s, flat_waste_share %s, hidden_share %s, '
                  'largest parts: %s; submeshes %d%s' % (
                      name, f['asset_triangles'],
                      'band %s (band_top_share %s)' % (f['band'], f['band_top_share']) if 'band' in f else 'no band',
                      f['curve_waste_share'], f['flat_waste_share'], f['hidden_share'], f['largest_parts'] or 'none',
                      f['submeshes'],
                      '; texture_off_palette %s' % f['texture_off_palette'] if 'texture_off_palette' in f else ''))
        if 'uncounted_instances' in f:
            print('STYLE NOTE %s instances %d object(s) the gate does not count: make them real '
                  '(bpy.ops.object.duplicates_make_real()), or leave it out of the export'
                  % (name, f['uncounted_instances']))
        if 'unchecked_parts' in f:
            print('STYLE NOTE %s: parts %s not named in --objects, so its triangle and accent sums leave them out'
                  % (name, ', '.join(f['unchecked_parts'])))
    print('STYLE GATE %s: %d object(s), %d failure(s)' % ('PASS' if not failures else 'FAIL', len(objs), len(failures)))
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
