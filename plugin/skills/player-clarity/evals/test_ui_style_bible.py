# The UI style bible script end to end on painted screens, about 20 s, no references or game needed:
#
#   blender --background --factory-startup --python-exit-code 1 --python test_ui_style_bible.py -- --out <empty dir>
#
# 1. extract reads a 1920x1080 menu and a half-size copy with button and panel rects drawn 6 reference px off (snap and the 1080 scale): the
#    palette roles, the type scale, the button size, corner radius and border, the 8 px grid and solid icons.
# 2. gate passes the menu and fails each rule once, with the place and a fix: low-contrast text (and names the palette
#    ink that passes), an off-palette patch, a small button, an off-grid width and gap, a font size off the type
#    scale, a button in the notch, a wrong radius, a missing border, a line icon, too many elements, accent overuse.
#    Text over a busy picture is read at its worst background. The CLI exits 1 on a failure and 0 on a pass.
# 3. sheet draws the phone-size tiles and the 1:1 crops, marks the failing element red, and writes its .json.
# Prints UI STYLE BIBLE PASS; any failed assert exits 1.

import copy
import json
import os
import sys

import numpy as np
import OpenImageIO as oiio

sys.dont_write_bytecode = True     # no __pycache__ beside the plugin's scripts
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import ui_style  # noqa: E402
from extract_style import srgb_to_lab  # noqa: E402

BG, CARD, TEXT, MUTED = (0.12, 0.15, 0.23), (0.22, 0.27, 0.38), (0.96, 0.93, 0.86), (0.45, 0.50, 0.60)
PRIMARY, INK, RED = (0.98, 0.72, 0.20), (0.10, 0.08, 0.06), (0.90, 0.22, 0.22)
STYLE = {
    'game': 'Fixture',
    'palette': {'Background': BG, 'Card': CARD, 'Text': TEXT, 'Muted': MUTED, 'Primary': PRIMARY, 'Ink': INK},
    'accents': [RED],
    'palette_de': 6, 'off_palette_max_share': 0.02, 'accent_max_share': 0.05,
    'contrast': {'text': 4.5, 'large_text': 3.0, 'ui': 3.0},
    'text_px': {'title': 64, 'button': 40, 'body': 32}, 'text_min_px': 18,
    'touch_min_px': 130, 'touch_gap_px': 16, 'grid_px': 8,
    'radius_px': {'button': 24, 'panel': 32}, 'stroke_px': {'button': 4, 'panel': 0},
    'icon': {'fill': 'solid', 'stroke_px': None},
    'density': {'max_elements': 12, 'min_empty_share': 0.5},
    'safe_inset': [0, 88, 0, 88],
}


def rrect(img, box, r, colour, stroke=0, stroke_colour=INK, ring=False):
    x, y, w, h = box
    yy, xx = np.mgrid[y:y + h, x:x + w] + 0.5

    def inside(inset, rad):
        cx = np.clip(xx, x + inset + rad, x + w - inset - rad)
        cy = np.clip(yy, y + inset + rad, y + h - inset - rad)
        return (xx - cx) ** 2 + (yy - cy) ** 2 <= rad ** 2 + 1e-9

    outer, inner = inside(0, r), inside(stroke, max(r - stroke, 0))
    region = img[y:y + h, x:x + w]
    region[outer] = stroke_colour if stroke else colour
    if ring:
        region[inner] = img[y + h // 2, x - 1]        # a line icon: the inside shows what is behind
    elif stroke:
        region[inner] = colour


def text(img, box, px, colour):
    """Glyph-like strokes: capitals CAP_EM x px tall and every third letter with a 0.2 em descender, the line centred
    in its box, letters 0.6 em apart."""
    x, y, w, h = box
    gh, dh = int(round(ui_style.CAP_EM * px)), int(round(0.2 * px))
    top = y + (h - gh - dh) // 2
    sw = max(2, px // 8)
    for n, gx in enumerate(range(x + px // 6, x + w - px // 2, int(0.6 * px))):
        img[top:top + gh + (dh if n % 3 == 2 else 0), gx:gx + sw] = colour
        img[top:top + sw, gx:gx + px // 3] = colour
        img[top + gh // 2:top + gh // 2 + sw, gx:gx + px // 4] = colour


def menu(variant=None):
    """A 1920x1080 menu and its layout; variant plants one fault."""
    img = np.zeros((1080, 1920, 3), np.float32)
    img[:] = BG
    els = [{'id': 'background', 'kind': 'panel', 'rect': [0, 0, 1920, 1080]}]
    rrect(img, (560, 160, 800, 760), 32, CARD)
    els.append({'id': 'card', 'kind': 'panel', 'rect': [560, 160, 800, 760]})
    text(img, (616, 216, 560, 80), 64, TEXT)
    els.append({'id': 'title', 'kind': 'text', 'rect': [616, 216, 560, 80], 'px': 64, 'bold': True})
    body_px = 20 if variant == 'text_px' else 32
    text(img, (616, 344, 600, 48), body_px, MUTED if variant == 'contrast' else TEXT)
    els.append({'id': 'body', 'kind': 'text', 'rect': [616, 344, 600, 48], 'px': body_px})
    if variant == 'icon':
        rrect(img, (1208, 216, 96, 96), 48, TEXT, stroke=8, stroke_colour=TEXT, ring=True)
    else:
        rrect(img, (1208, 216, 96, 96), 48, TEXT)
    els.append({'id': 'gear', 'kind': 'icon', 'rect': [1208, 216, 96, 96]})
    rrect(img, (1224, 360, 24, 24), 12, RED)                     # a notification dot: accent, no element
    w = 322 if variant == 'grid' else 320
    radius = 8 if variant == 'radius' else 24
    stroke = 0 if variant == 'stroke' else 4
    gap = {'grid': 30, 'tight': 8}.get(variant, 32)
    for i, name in enumerate(('play', 'options')):
        bx = 616 + i * (w + gap) if variant != 'safe_area' or i == 0 else 40
        rrect(img, (bx, 720, w, 136), radius, PRIMARY, stroke)
        text(img, (bx + 40, 768, w - 80, 48), 40, INK)
        els.append({'id': name, 'kind': 'button', 'rect': [bx, 720, w, 136]})
        if variant == 'hit' and i == 0:
            els[-1]['hit'] = [bx - 8, 700, w + 48, 176]          # reaches 8 px into options
        els.append({'id': name + '_label', 'kind': 'text', 'rect': [bx + 40, 768, w - 80, 48], 'px': 40})
    if variant == 'touch':
        rrect(img, (1208, 456, 96, 96), 24, PRIMARY, 4)
        els.append({'id': 'close', 'kind': 'button', 'rect': [1208, 456, 96, 96]})
    if variant == 'palette':
        img[480:680, 640:940] = (0.20, 0.80, 0.30)
    if variant == 'accent':
        rrect(img, (616, 440, 560, 240), 24, RED)
    if variant == 'density':
        for i in range(8):
            text(img, (616 + (i % 4) * 136, 440 + (i // 4) * 64, 120, 48), 32, TEXT)
            els.append({'id': 'stat%d' % i, 'kind': 'text', 'rect': [616 + (i % 4) * 136, 440 + (i // 4) * 64, 120, 48],
                        'px': 32})
    return img, {'elements': els}


def save(img, layout, folder, name, scale=1, jitter=0):
    os.makedirs(folder, exist_ok=True)
    if scale != 1:
        img = ui_style.resized(img, img.shape[1] // scale, img.shape[0] // scale)
    ui_style.write_png(img, os.path.join(folder, name + '.png'))
    lay = copy.deepcopy(layout)
    lay['image'] = name + '.png'
    for i, e in enumerate(lay['elements']):
        j = (jitter if i % 2 else -jitter) if e['kind'] in ('button', 'panel') else 0    # the kinds that snap
        e['rect'] = [v / scale + j * (k < 2) for k, v in enumerate(e['rect'])]
        if scale != 1:
            e.pop('px', None)                  # a reference: px estimated from the ink
    path = os.path.join(folder, name + '.layout.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(lay, f)
    return lay, path


def gate_of(variant, style=STYLE):
    img, layout = menu(variant)
    _, path = save(img, layout, OUT, 'menu_%s' % (variant or 'good'))
    return ui_style.gate(ui_style.Screen(ui_style.load_layouts(path)[0]), style), path


def near(swatches, rgb, de=4.0):
    target = srgb_to_lab(np.array(rgb, float))
    return min(np.linalg.norm(np.array(s['lab']) - target) for s in swatches) < de


def main():
    global OUT
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    OUT = os.path.abspath(argv[argv.index('--out') + 1]) if '--out' in argv else os.path.join(os.getcwd(), 'ui_bible')
    refs = os.path.join(OUT, 'reference')

    # 1. extract: a full-size reference and a half-size one with rects drawn 3 image px (6 reference px) off
    img, layout = menu()
    a, _ = save(img, layout, refs, 'menu_full')
    b, _ = save(img, layout, refs, 'menu_half', scale=2, jitter=3)
    with open(os.path.join(refs, 'ui_refs.json'), 'w', encoding='utf-8') as f:
        json.dump([a, b], f)
    res = ui_style.main(['extract', '--layouts', os.path.join(refs, 'ui_refs.json'), '--out',
                         os.path.join(OUT, 'ui_metrics.json'), '--swatches', os.path.join(OUT, 'palette.png')])
    p = res['pooled']
    for name, rgb in (('Background', BG), ('Card', CARD), ('Text', TEXT), ('Primary', PRIMARY)):
        assert near(p['palette'], rgb), 'extract missed %s: %s' % (name, [s['hex'] for s in p['palette']])
    assert near(p['accents'], RED, 6) or near(p['palette'], RED, 6), 'extract missed the red accent'
    sizes = [t[0] for t in p['text_tiers']]
    for px in (64, 40, 32):
        assert any(abs(s - px) <= 0.12 * px for s in sizes), 'type scale %s misses %d' % (p['text_tiers'], px)
    assert abs(p['button_short_px']['median'] - 136) <= 3, 'button short side %s' % p['button_short_px']
    assert abs(p['radius_px']['button'] - 24) <= 3 and abs(p['radius_px']['panel'] - 32) <= 3, p['radius_px']
    assert abs(p['stroke_px']['button'] - 4) <= 1.5 and p['stroke_px']['panel'] <= 1, p['stroke_px']
    assert p['on_grid']['8'] >= 0.9, 'grid %s' % p['on_grid']
    assert p['icon_fill_share'] >= 0.6, 'icon fill %s' % p['icon_fill_share']
    assert p['text_contrast_min'] >= 4.5, 'contrast %s' % p['text_contrast_min']
    half = res['screens'][1]
    assert half['scale'] == 2.0 and abs(min(half['button_short_px']) - 136) <= 3, 'half-size screen %s' % half

    # 2. gate: the good menu passes, each variant fails its own rule only
    fails, good = gate_of(None)
    assert not fails, 'the good menu failed: %s' % fails
    expect = {'contrast': {'body'}, 'palette': {'-'}, 'touch': {'close'}, 'grid': {'play'}, 'text_px': {'body'},
              'safe_area': {'options'}, 'radius': {'play', 'options'}, 'stroke': {'play', 'options'},
              'icon': {'gear'}, 'accent': {'-'}, 'density': {'-'}}
    for variant, ids in expect.items():
        fails, _ = gate_of(variant)
        rules = {f['rule'] for f in fails}
        if variant == 'safe_area':
            rules.discard('grid')                  # the moved button also leaves the 32 px gap: a second, true finding
        assert rules == {variant}, '%s: expected only %s, got %s' % (variant, variant, fails)
        assert {f['id'] for f in fails if f['rule'] == variant} >= ids, '%s named %s' % (variant, fails)
        assert all(f['fix'] and len(f['at']) == 2 for f in fails), fails
    fails, _ = gate_of('contrast')
    assert 'ink Text' in fails[0]['fix'], 'the contrast fix names no passing ink: %s' % fails[0]
    fails, _ = gate_of('palette')
    x, y = fails[0]['at']
    assert 640 <= x <= 940 and 480 <= y <= 680, 'off-palette place %s is not the green patch' % fails[0]
    fails, _ = gate_of('grid')
    assert any('width 320' in f['fix'] for f in fails) and any('gap' in f['msg'] for f in fails), fails
    fails, _ = gate_of('text_px')
    assert fails[0]['fix'] == 'font size 32', fails
    # a button 5 px inside a panel snaps to its own edge, not the panel's
    img, layout = menu()
    rrect(img, (600, 880, 720, 150), 8, CARD)
    rrect(img, (605, 887, 320, 136), 24, PRIMARY, 4)
    layout['elements'] += [{'id': 'tray', 'kind': 'panel', 'rect': [600, 880, 720, 150]},
                           {'id': 'buy', 'kind': 'button', 'rect': [605, 887, 320, 136]}]
    _, path = save(img, layout, OUT, 'menu_tray')
    sc = ui_style.Screen(ui_style.load_layouts(path)[0])
    assert [m['size'] for m in sc.elements if m['id'] == 'buy'] == [[320, 136]], sc.elements
    # an off-palette bar in the last 24 px (1080 is no multiple of the 32 px cells) is found, not a crash
    img, layout = menu()
    img[1058:1080, 0:1920] = (0.20, 0.80, 0.30)
    layout['elements'].append({'id': 'bar', 'kind': 'panel', 'rect': [0, 1058, 1920, 22], 'snap': False})
    _, path = save(img, layout, OUT, 'menu_bar')
    fails = ui_style.gate(ui_style.Screen(ui_style.load_layouts(path)[0]), dict(STYLE, off_palette_max_share=0.01))
    pal = [f for f in fails if f['rule'] == 'palette']       # the bar's own radius and grid fails are true too
    assert len(pal) == 1 and pal[0]['at'][1] >= 1056 and '#33cc4d' in pal[0]['msg'], fails
    # a label rect stretched over its button is refused: the ink box is needed
    img, layout = menu()
    layout['elements'].append({'id': 'stretched', 'kind': 'text', 'rect': [616, 720, 320, 136], 'px': 40})
    _, path = save(img, layout, OUT, 'menu_stretched')
    try:
        ui_style.Screen(ui_style.load_layouts(path)[0])
        raise AssertionError('a text rect over a whole button was measured')
    except SystemExit as e:
        assert 'textBounds' in str(e), e
    # an element under a SafeAreaFitter ("safe": true) skips safe_inset on an Editor capture, but not a device's safe_area
    img, layout = menu('safe_area')
    for e in layout['elements']:
        e['safe'] = e['id'] in ('options', 'options_label')
    _, path = save(img, layout, OUT, 'menu_fitter')
    lay = ui_style.load_layouts(path)[0]
    assert 'safe_area' not in {f['rule'] for f in ui_style.gate(ui_style.Screen(lay), STYLE)}, 'fitter child failed'
    lay['safe_area'] = [88, 0, 1744, 1080]
    assert 'safe_area' in {f['rule'] for f in ui_style.gate(ui_style.Screen(lay), STYLE)}, 'device safe area unchecked'
    # buttons 8 px apart: each snaps to its own edge, not its neighbour's, and the touch gap fails
    fails, path = gate_of('tight')
    sc = ui_style.Screen(ui_style.load_layouts(path)[0])
    assert [m['size'] for m in sc.elements if m['kind'] == 'button'] == [[320, 136]] * 2, sc.elements
    assert {f['rule'] for f in fails} == {'touch'} and 'only 8 px' in fails[0]['msg'], fails
    # hit areas that overlap: a tap could reach both buttons
    fails, _ = gate_of('hit')
    assert [(f['rule'], f['id']) for f in fails] == [('touch', 'play')] and 'overlaps' in fails[0]['msg'], fails

    # text over a busy picture: half its background matches the ink, so its worst tenth fails though the mean passes
    img, layout = menu()
    stripes = np.arange(1920) % 16 < 8
    img[392:448, 600:1232][:, stripes[600:1232]] = (0.88, 0.85, 0.78)     # the picture runs past the box
    text(img, (616, 400, 600, 40), 32, TEXT)
    layout['elements'].append({'id': 'over_art', 'kind': 'text', 'rect': [616, 400, 600, 40], 'px': 32})
    _, path = save(img, layout, OUT, 'menu_busy')
    busy = ui_style.Screen(ui_style.load_layouts(path)[0])
    m = [e for e in busy.elements if e['id'] == 'over_art'][0]
    assert m['contrast'] < 2.0, 'text over the bright stripes read %.2f:1' % m['contrast']

    # the CLI: exit 0 on the pass, 1 with UI FAIL lines on a failure
    style_path = os.path.join(OUT, 'ui-style.json')
    with open(style_path, 'w', encoding='utf-8') as f:
        json.dump(STYLE, f)
    ui_style.main(['gate', '--style', style_path, '--layout', good])
    for variant in ('palette', 'touch'):     # --report writes plain JSON (numpy ints were a crash)
        _, bad = gate_of(variant)
        try:
            ui_style.main(['gate', '--style', style_path, '--layout', bad, '--report', os.path.join(OUT, 'r.json')])
        except SystemExit:
            pass
        with open(os.path.join(OUT, 'r.json'), encoding='utf-8') as f:
            assert json.load(f)['fails'][0]['rule'] == variant
    try:
        ui_style.main(['gate', '--style', style_path, '--layout', bad, '--report', os.path.join(OUT, 'r.json')])
        code = 0
    except SystemExit as e:
        code = e.code
    assert code == 1, 'the gate CLI exited %s on a failing screen' % code

    # 3. sheet: phone tiles, gate overlay with the failing button red, 1:1 crops, json
    out = os.path.join(OUT, 'review', 'menu_sheet_r1.png')
    ui_style.main(['sheet', '--style', style_path, '--layout', bad, '--refs', os.path.join(refs, 'ui_refs.json'),
                   '--out', out, '--golden', os.path.join(OUT, 'golden.png')])
    with open(os.path.splitext(out)[0] + '.json', encoding='utf-8') as f:
        rep = json.load(f)
    labels = [t['label'] for t in rep['tiles']]
    assert labels[:2] == ['screen', 'gate'] and sum(l.startswith('reference') for l in labels) == 2, labels
    assert sum(' ' in l and l.split(' ')[0].endswith('.png') for l in labels) >= 3, 'no 1:1 crops: %s' % labels
    gate_tile = rep['tiles'][1]['rect']
    assert gate_tile[2] == 455 and gate_tile[3] == ui_style.PHONE_SHORT, 'phone tile %s' % gate_tile
    buf = oiio.ImageBuf(out)
    sheet_px = buf.get_pixels(oiio.FLOAT)[:, :, :3]
    x0, y0, w, h = gate_tile
    k = ui_style.PHONE_SHORT / 1080.0
    cx, cy = int(x0 + 1208 * k), int(y0 + (456 + 48) * k)
    red = sheet_px[cy - 2:cy + 2, cx - 2:cx + 3]
    assert ((red[..., 0] > 0.8) & (red[..., 1] < 0.3)).any(), 'the failing button is not framed red on the gate tile'
    crop_tile = rep['tiles'][-1]['rect']
    assert crop_tile[2] == crop_tile[3] == ui_style.CROP, 'crop tile %s' % crop_tile
    assert rep['fails'] and rep['fails'][0]['rule'] == 'touch', rep['fails']
    print('UI STYLE BIBLE PASS')


if __name__ == '__main__':
    main()
