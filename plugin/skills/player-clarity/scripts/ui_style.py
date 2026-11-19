# The UI style bible's measurements (player-clarity references/ui-style-bible.md): reference screens to numbers, a
# screen gated against ui-style.json, and its review sheet. Headless, Blender's bundled numpy and OpenImageIO only:
#
#   blender --background --factory-startup --python-exit-code 1 --python ui_style.py -- extract \
#       --layouts Tools/UI/Style/ui_refs.json --out Tools/UI/Style/ui_metrics.json [--swatches palette.png]
#   ... -- gate --style Tools/UI/Style/ui-style.json --layout Tools/UI/<Screen>.layout.json [--report r.json]
#   ... -- sheet --style ... --layout ... --refs Tools/UI/Style/ui_refs.json --out <Screen>_sheet_r<N>.png \
#       [--golden Tools/UI/Style/golden.png]
#
# A layout is one screen: {"image": "menu.png", "safe_area": [x, y, w, h], "elements": [{"id": "play", "kind":
# "button", "rect": [x, y, w, h], "hit": [x, y, w, h]}, {"id": "title", "kind": "text", "rect": [...], "px": 64,
# "bold": true}, ...]}; ui_refs.json is a list of them. Rects are image pixels from the top left, "image" is relative
# to the json's folder. Kinds: text (one line's box), button, icon, panel (a plate, a card, the background), art (the
# game view or an illustration: never measured). "px" is the font size at the reference (TMP fontSize); without it the
# script estimates it from the cap height (the top of the ink to the baseline, about 0.72 em; descenders are left
# out). "hit" is a raycast area larger than the drawn button. "safe_area" is Screen.safeArea in image pixels; without
# it ui-style.json "safe_inset" applies, except to an element marked "safe": true (under a SafeAreaFitter, which moves
# it in on a phone; an Editor capture cannot show that). Button and panel rects snap to the outermost colour step within 8 reference
# px (never more than half the way to a neighbouring button or panel), so one drawn by eye that close measures exact;
# a text box is read 2 px larger than drawn and its rim is the background; an icon rect is its Image rect.
#
# Every number is read at the 1080 CanvasScaler reference: an image is scaled by 1080 / its short side, so a capture
# must have the reference aspect (16:9 or 9:16) for sizes to match the Canvas. Contrast is WCAG 2 (relative luminance)
# between the text's ink core and the worst tenth of what is behind it, so text over a busy game view reads its worst.
# The gate prints one "UI FAIL <rule> <id> at (x, y)" line per failure with the number and the fix, exits 1, and on a
# pass prints UI GATE PASS. Rules: contrast, text_px, touch, grid, radius, stroke, icon, safe_area, density, palette,
# accent. extract_style.py (genre-defaults) supplies the colour maths and the palette k-means.

import argparse
import json
import math
import os
import sys

import numpy as np
import OpenImageIO as oiio

sys.dont_write_bytecode = True     # no __pycache__ beside the plugin's scripts
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'genre-defaults', 'scripts'))
from extract_style import hexcode, kmeans, metrics, read_rgb, srgb_to_lab, write_swatches  # noqa: E402

REF_SHORT = 1080        # the CanvasScaler reference's short side (platform-targets: 1920x1080 or 1080x1920)
SAME_DE = 10.0          # CIELAB distance under which two pixels are one colour
EDGE_DE = 10.0          # a colour step above this between neighbours is an anti-aliased edge, out of the palette count
SNAP_REF = 8            # how far (reference px) a drawn rect's edge may move to the shape's real edge; a neighbour
                        # closer than twice that caps it at half the gap (Screen.snap)
CAP_EM = 0.72           # cap height per font px (top of the ink to the baseline), for an estimated "px"
PHONE_SHORT = 256       # the sheet's phone tile: a 6.1-inch phone at its real size on a 100-dpi monitor
CROP = 320              # the sheet's 1:1 crops, reference pixels
DEFAULT_CONTRAST = {'text': 4.5, 'large_text': 3.0, 'ui': 3.0}      # WCAG SC 1.4.3, 1.4.11 (player-clarity CL32)


# ---- colour


def luminance(rgb):
    """WCAG relative luminance of sRGB 0..1 values, any leading shape."""
    rgb = np.asarray(rgb, float)
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return lin @ np.array([0.2126, 0.7152, 0.0722])


def ratio(a, b):
    return (np.maximum(a, b) + 0.05) / (np.minimum(a, b) + 0.05)


def roles(style):
    """[(name, sRGB, CIELAB)] of the palette roles, then the accents as Accent1..N."""
    out = [(k, v) for k, v in style.get('palette', {}).items()]
    out += [('Accent%d' % (i + 1), v) for i, v in enumerate(style.get('accents', []))]
    return [(n, np.array(v, float), srgb_to_lab(np.array(v, float))) for n, v in out]


# ---- one screen


class Screen:
    def __init__(self, layout):
        self.layout = layout
        self.rgb = read_rgb(layout['path'], long_side=None)
        self.lab = srgb_to_lab(self.rgb)
        self.h, self.w = self.rgb.shape[:2]
        self.s = REF_SHORT / float(min(self.w, self.h))         # image px -> reference px
        gy, gx = np.gradient(self.lab, axis=(0, 1))
        self.edge = np.sqrt((gx ** 2).sum(-1) + (gy ** 2).sum(-1)) > EDGE_DE
        self.drawn = [self.box(e['rect']) for e in layout.get('elements', []) if e['kind'] in ('button', 'panel')]
        self.drawn_buttons = [self.box(e['rect']) for e in layout.get('elements', []) if e['kind'] == 'button']
        self.elements = [self.measure(i, e) for i, e in enumerate(layout.get('elements', []))]

    def box(self, rect):
        x, y, w, h = (int(round(v)) for v in rect)
        return max(0, x), max(0, y), min(self.w, x + w), min(self.h, y + h)

    def full(self, b):
        return (b[2] - b[0]) * (b[3] - b[1]) >= 0.9 * self.w * self.h

    def measure(self, i, e):
        m = {'id': e.get('id', '%s%d' % (e['kind'], i)), 'kind': e['kind'], 'under_fitter': bool(e.get('safe'))}
        b = self.box(e['rect'])
        if b[2] - b[0] < 6 or b[3] - b[1] < 6:
            raise SystemExit('element %s: rect %s is under 6 px or outside the %dx%d image'
                             % (m['id'], e['rect'], self.w, self.h))
        if e['kind'] in ('button', 'panel') and e.get('snap', True) and not self.full(b):
            b = self.snap(b)
        m['box'] = b
        m['size'] = [round((b[2] - b[0]) * self.s, 1), round((b[3] - b[1]) * self.s, 1)]
        if e['kind'] == 'icon':
            m.update(self.ink(b, e))
        if e['kind'] == 'text':      # 2 px more, so ink that touches a tight box is not read as its background
            # a label rect equal to or larger than its button (a padded one inside it reads the fill: harmless)
            if any(o[0] >= b[0] and o[1] >= b[1] and o[2] <= b[2] and o[3] <= b[3] for o in self.drawn_buttons):
                raise SystemExit('element %s: the text rect covers a whole button; take the ink box '
                                 '(TMP_Text.textBounds), not the label\'s RectTransform, or one line of a paragraph'
                                 % m['id'])
            m['ink_box'] = (max(0, b[0] - 2), max(0, b[1] - 2), min(self.w, b[2] + 2), min(self.h, b[3] + 2))
            m.update(self.ink(m['ink_box'], e))
        if e['kind'] in ('button', 'panel') and not self.full(b):
            m['radius'] = round(self.radius(b) * self.s, 1)
            m['stroke'] = round(self.stroke(b) * self.s, 1)
        if e['kind'] == 'button':
            hb = self.box(e['hit']) if e.get('hit') else b
            m['hit'] = round(min(hb[2] - hb[0], hb[3] - hb[1]) * self.s, 1)
            m['hit_box'] = hb
        return m

    def snap(self, b):
        """Each edge to the outermost colour step within SNAP_REF, read over the middle 60 % of the edge. Outward it
        moves at most half the gap to the nearest drawn button or panel on that side, so it never takes a neighbour's
        edge."""
        x0, y0, x1, y1 = b
        cols = self.lab.transpose(1, 0, 2)
        ya, yb = y0 + (y1 - y0) // 5, y1 - (y1 - y0) // 5
        xa, xb = x0 + (x1 - x0) // 5, x1 - (x1 - x0) // 5
        r = max(2, int(SNAP_REF / self.s))
        reach = [r, r, r, r]                      # left, top, right, bottom
        for o in self.drawn:
            if o == b:
                continue
            if o[0] <= x0 and o[1] <= y0 and o[2] >= x1 and o[3] >= y1:      # a panel round it: half its padding
                reach = [min(reach[0], (x0 - o[0]) // 2), min(reach[1], (y0 - o[1]) // 2),
                         min(reach[2], (o[2] - x1) // 2), min(reach[3], (o[3] - y1) // 2)]
                continue
            if min(o[3], y1) > max(o[1], y0):     # overlaps in y: a neighbour left or right
                if o[2] <= x0:
                    reach[0] = min(reach[0], (x0 - o[2]) // 2)
                if o[0] >= x1:
                    reach[2] = min(reach[2], (o[0] - x1) // 2)
            if min(o[2], x1) > max(o[0], x0):     # overlaps in x: a neighbour above or below
                if o[3] <= y0:
                    reach[1] = min(reach[1], (y0 - o[3]) // 2)
                if o[1] >= y1:
                    reach[3] = min(reach[3], (o[1] - y1) // 2)
        return (step(cols, x0, ya, yb, -1, r, reach[0]), step(self.lab, y0, xa, xb, -1, r, reach[1]),
                step(cols, x1, ya, yb, 1, r, reach[2]), step(self.lab, y1, xa, xb, 1, r, reach[3]))

    def radius(self, b):
        """Corner radius from the area each corner cuts away, r^2 (1 - pi/4), averaged over the corners that have
        an outside pixel to compare with."""
        x0, y0, x1, y1 = b
        m = min(x1 - x0, y1 - y0) // 2
        areas = []
        for cy, cx, sy, sx in ((y0, x0, 1, 1), (y0, x1 - 1, 1, -1), (y1 - 1, x0, -1, 1), (y1 - 1, x1 - 1, -1, -1)):
            oy, ox = cy - sy, cx - sx
            if not (0 <= oy < self.h and 0 <= ox < self.w):
                continue
            block = self.lab[np.ix_(cy + sy * np.arange(m), cx + sx * np.arange(m))]
            same = np.linalg.norm(block - self.lab[oy, ox], axis=-1) < SAME_DE
            areas.append(np.where(same.all(1), m, np.argmin(same, axis=1)).sum())
        return math.sqrt(np.mean(areas) / (1 - math.pi / 4)) if areas else 0.0

    def stroke(self, b):
        """Width of the border: the run of non-fill pixels from each edge's middle inward. The fill is the largest colour
        of a band 10-16 reference px inside the edge, past any border and before a label in the middle."""
        x0, y0, x1, y1 = b
        w, h = x1 - x0, y1 - y0
        d1 = int(min(10 / self.s, w / 4, h / 4))
        d2 = max(d1 + 1, int(min(16 / self.s, w / 3, h / 3)))
        band = np.zeros((h, w), bool)
        band[d1:h - d1, d1:w - d1] = True
        band[d2:h - d2, d2:w - d2] = False
        fill = kmeans(self.lab[y0:y1, x0:x1][band], 3)[0][0]
        my, mx = (y0 + y1) // 2, (x0 + x1) // 2
        runs = []
        for line in (self.lab[my, x0:x1], self.lab[my, x0:x1][::-1], self.lab[y0:y1, mx], self.lab[y0:y1, mx][::-1]):
            off = np.linalg.norm(line - fill, axis=-1) >= SAME_DE
            runs.append(0 if off.all() else int(np.argmin(off)))
        return float(np.median(runs))

    def ink(self, b, e):
        """Text or icon: its ink against what is behind it. The rect's 2 px rim is the background (its median colour);
        the ink core is the inner pixels at least 3/4 of the way to the farthest colour from it. Contrast is the core's
        median colour against the worst tenth of the rim: the whole rim for text (a line box has padding, so a busy
        picture behind it counts), the rim less the icon's own ink for an icon (its shape may touch its rect)."""
        x0, y0, x1, y1 = b
        lab, rgb = self.lab[y0:y1, x0:x1], self.rgb[y0:y1, x0:x1]
        rim = np.ones(lab.shape[:2], bool)
        rim[2:-2, 2:-2] = False
        d = np.linalg.norm(lab - np.median(lab[rim], axis=0), axis=-1)
        far = np.percentile(d[~rim], 99.5)
        out = {'px': float(e.get('px') or 0), 'px_estimated': not e.get('px'), 'bold': bool(e.get('bold'))} \
            if e['kind'] == 'text' else {}
        if far < SAME_DE:
            out.update(contrast=1.0, ink=None, fill_share=0.0, line_px=0.0, back=luminance(rgb[rim]))
            return out
        core = (d >= 0.75 * far) & ~rim
        ink_rgb = np.median(rgb[core], axis=0)
        behind = rim if e['kind'] == 'text' else rim & (d < 0.25 * far)
        back = luminance(rgb[behind] if behind.any() else rgb[rim])
        out['contrast'] = round(float(np.percentile(ratio(luminance(ink_rgb), back), 10)), 2)
        out['ink'] = hexcode(ink_rgb)
        out['back'] = back
        out['core'] = core
        shape = (d >= 0.5 * far) & ~rim
        out['fill_share'] = round(float(shape.sum()) / max(1, (~rim).sum()), 3)
        if e['kind'] == 'text':
            if not e.get('px'):      # cap height: the first ink row to the last dense one (the baseline)
                counts = core.sum(1)
                rows = np.flatnonzero(counts)
                dense = np.flatnonzero(counts >= 0.5 * np.median(counts[rows]))
                out['px'] = round((dense[-1] - rows[0] + 1) * self.s / CAP_EM, 1)
        else:
            runs = np.concatenate([run_lengths(r) for r in shape])
            out['line_px'] = round(float(np.median(runs)) * self.s, 1) if len(runs) else 0.0
        return out

    def ui_mask(self):
        """The pixels the palette counts: button, icon and panel rects plus text ink, less art and edges."""
        mask = np.zeros((self.h, self.w), bool)
        for m in self.elements:
            x0, y0, x1, y1 = m['box']
            if m['kind'] in ('button', 'icon', 'panel'):
                mask[y0:y1, x0:x1] = True
            elif m['kind'] == 'text' and m.get('ink') is not None:
                x0, y0, x1, y1 = m['ink_box']
                mask[y0:y1, x0:x1] |= m['core']
        for m in self.elements:
            if m['kind'] == 'art':
                x0, y0, x1, y1 = m['box']
                mask[y0:y1, x0:x1] = False
        return mask & ~self.edge

    def safe_box(self, style):
        if self.layout.get('safe_area'):
            return self.box(self.layout['safe_area'])
        top, right, bottom, left = (v / self.s for v in style.get('safe_inset', [0, 0, 0, 0]))
        return int(left), int(top), int(round(self.w - right)), int(round(self.h - bottom))

    def content(self):
        return [m for m in self.elements if m['kind'] in ('text', 'button', 'icon')]

    def empty_share(self, safe):
        x0, y0, x1, y1 = safe
        cover = np.zeros((self.h, self.w), bool)
        for m in self.content():
            bx0, by0, bx1, by1 = m['box']
            cover[by0:by1, bx0:bx1] = True
        return round(1.0 - float(cover[y0:y1, x0:x1].mean()), 3)

    def centre(self, m):
        x0, y0, x1, y1 = m['box']
        return (x0 + x1) // 2, (y0 + y1) // 2


def step(lab, pos, a, b, outward, r, reach):
    """lab with the edge's axis first: the index from r inward to reach outward of pos where the colour steps between
    index-1 and index, the outermost of the steps; pos when nothing steps."""
    n = lab.shape[0]
    lo, hi = (pos - reach, pos + r) if outward < 0 else (pos - r, pos + reach)
    cs = np.arange(max(1, lo), min(n - 1, hi) + 1)
    if b - a < 2 or len(cs) == 0:
        return pos
    d = np.array([np.linalg.norm(lab[c, a:b] - lab[c - 1, a:b], axis=-1).mean() for c in cs])
    if d.max() < SAME_DE:
        return pos
    strong = cs[d >= SAME_DE]          # a border's outer step can be far weaker than its inner one: any step counts
    return int(strong.min() if outward < 0 else strong.max())


def run_lengths(row):
    p = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
    return np.flatnonzero(p == -1) - np.flatnonzero(p == 1)


def neighbours(boxes):
    """(i, j, gap, axis) for each box and its nearest box to the right and below that overlaps it on the other
    axis; nested boxes are not neighbours."""
    out = []
    for i, a in enumerate(boxes):
        for axis in (0, 1):
            best = None
            for j, b in enumerate(boxes):
                lo, hi = (1, 3) if axis == 0 else (0, 2)
                if i == j or min(a[hi], b[hi]) - max(a[lo], b[lo]) <= 0:
                    continue
                gap = b[axis] - a[axis + 2]
                if gap >= 0 and (best is None or gap < best[2]):
                    best = (i, j, gap, axis)
            if best:
                out.append(best)
    return out


def box_gap(a, b):
    dx = max(b[0] - a[2], a[0] - b[2], 0)
    dy = max(b[1] - a[3], a[1] - b[3], 0)
    return math.hypot(dx, dy)


def per_kind(value, kind):
    return value.get(kind) if isinstance(value, dict) else value


# ---- gate


def gate(sc, style):
    """[{rule, id, at, msg, fix}] for one screen."""
    fails = []
    s = sc.s

    def fail(rule, m, msg, fix, at=None):
        fails.append({'rule': rule, 'id': m['id'] if m else '-', 'at': list(at or sc.centre(m)), 'msg': msg,
                      'fix': fix})

    con = dict(DEFAULT_CONTRAST, **style.get('contrast', {}))
    pal = roles(style)
    tiers = sorted(style.get('text_px', {}).values())
    text_min = style.get('text_min_px', 18)
    for m in sc.elements:
        if m['kind'] in ('text', 'icon'):
            if m['kind'] == 'text':
                large = m['px'] >= 24 or (m['bold'] and m['px'] >= 19)
                need = con['large_text'] if large else con['text']
            else:
                need = con['ui']
            if m['contrast'] < need:
                worst = {r[0]: np.percentile(ratio(luminance(r[1]), m['back']), 10) for r in pal}
                best = max(worst, key=worst.get) if worst else None
                tip = 'ink %s (%.1f:1)' % (best, worst[best]) if best else 'a darker or lighter ink'
                fail('contrast', m, '%.1f:1 < %.1f:1 (ink %s)' % (m['contrast'], need, m['ink']),
                     tip + ', or a plate or outline behind it')
        if m['kind'] == 'text':
            near = min(tiers, key=lambda t: abs(t - m['px'])) if tiers else None
            if m['px'] < text_min - 0.5:
                fail('text_px', m, '%g px < %g px (CL33)' % (m['px'], text_min),
                     'font size %g' % max(text_min, min([t for t in tiers if t >= text_min] or [text_min])))
            elif near is not None and abs(near - m['px']) > max(1.0, 0.1 * near if m['px_estimated'] else 1.0):
                fail('text_px', m, '%g px is no step of the type scale %s' % (m['px'], tiers), 'font size %g' % near)
        if m['kind'] == 'button' and m['hit'] < style.get('touch_min_px', 130) - 1:
            fail('touch', m, 'target %g px < %g px' % (m['hit'], style.get('touch_min_px', 130)),
                 'grow its short side to %g px, or add a larger "hit" raycast area' % style.get('touch_min_px', 130))
        if m['kind'] in ('button', 'panel') and 'radius' in m:
            want = per_kind(style.get('radius_px'), m['kind'])
            if want is not None and abs(m['radius'] - want) > max(2.0, 0.15 * want):
                fail('radius', m, 'corner radius %g px, the style has %g' % (m['radius'], want), 'radius %g' % want)
            want = per_kind(style.get('stroke_px'), m['kind'])
            if want is not None and abs(m['stroke'] - want) > 1.0:
                fail('stroke', m, 'border %g px, the style has %g' % (m['stroke'], want), 'border %g px' % want)
        if m['kind'] == 'icon' and style.get('icon') and m.get('ink') is not None:
            kind = 'solid' if m['fill_share'] >= 0.4 else 'line'
            want = style['icon'].get('fill')
            if want and kind != want:
                fail('icon', m, '%s icon (ink covers %.0f%%), the style draws %s icons'
                     % (kind, 100 * m['fill_share'], want), 'redraw it %s' % want)
            lw = style['icon'].get('stroke_px')
            if want == 'line' == kind and lw and abs(m['line_px'] - lw) > 1.5:
                fail('icon', m, 'line %g px, the style has %g' % (m['line_px'], lw), 'line width %g px' % lw)

    grid = style.get('grid_px')
    sized = [m for m in sc.elements if m['kind'] in ('button', 'icon', 'panel') and not sc.full(m['box'])]
    if grid:
        for m in sized:
            for v, name in zip(m['size'], ('width', 'height')):
                if abs(v - round(v / grid) * grid) > 1.0:
                    fail('grid', m, '%s %g px is off the %g px grid' % (name, v, grid),
                         '%s %g' % (name, round(v / grid) * grid))
        for i, j, gap, axis in neighbours([m['box'] for m in sized]):
            v = gap * s
            if abs(v - round(v / grid) * grid) > 1.0:
                a = sized[i]['box']
                at = (a[2], (a[1] + a[3]) // 2) if axis == 0 else ((a[0] + a[2]) // 2, a[3])
                fail('grid', sized[i], 'gap %g px to %s is off the %g px grid' % (round(v, 1), sized[j]['id'], grid),
                     'gap %g' % max(grid, round(v / grid) * grid), at)
    buttons = [m for m in sc.elements if m['kind'] == 'button']
    need_gap = style.get('touch_gap_px', 24)
    for i, a in enumerate(buttons):
        for b in buttons[i + 1:]:
            g = box_gap(a['box'], b['box']) * s
            if g < need_gap - 1:
                fail('touch', a, 'only %g px to %s' % (round(g, 1), b['id']), 'space them %g px apart' % need_gap)
            ha, hb = a['hit_box'], b['hit_box']
            if min(ha[2], hb[2]) > max(ha[0], hb[0]) and min(ha[3], hb[3]) > max(ha[1], hb[1]):
                fail('touch', a, "its hit area overlaps %s's" % b['id'],
                     'shrink both "hit" areas to meet halfway, so a tap reaches one button only')

    safe = sc.safe_box(style)
    for m in sc.content():
        if m['under_fitter'] and not sc.layout.get('safe_area'):
            continue            # an Editor capture: its SafeAreaFitter moves it in on the phone, so safe_inset can't apply
        x0, y0, x1, y1 = m['box']
        over = {'left': safe[0] - x0, 'top': safe[1] - y0, 'right': x1 - safe[2], 'bottom': y1 - safe[3]}
        over = {k: round(v * s) for k, v in over.items() if v > 0}
        if over:
            fail('safe_area', m, 'outside the safe area by ' + ', '.join('%d px %s' % (v, k) for k, v in over.items()),
                 'put it under the SafeAreaFitter child (platform-targets)' if not m['under_fitter'] else
                 'fix its offset or anchors inside the fitter; never add a notch margin by hand')
    dens = style.get('density', {})
    n = len(sc.content())
    if dens.get('max_elements') and n > dens['max_elements']:
        fail('density', None, '%d elements, the style shows at most %d' % (n, dens['max_elements']),
             'cut or group %d of them (player-clarity CL24)' % (n - dens['max_elements']), (sc.w // 2, sc.h // 2))
    empty = sc.empty_share(safe)
    if dens.get('min_empty_share') and empty < dens['min_empty_share']:
        fail('density', None, 'empty share %.2f < %.2f' % (empty, dens['min_empty_share']),
             'more space between groups, fewer elements', (sc.w // 2, sc.h // 2))

    mask = sc.ui_mask()
    if pal and mask.any():
        lab = sc.lab[mask]
        dist = np.stack([np.linalg.norm(lab - r[2], axis=1) for r in pal], axis=1)
        de = style.get('palette_de', 6)
        off = dist.min(1) > de
        share = float(off.mean())
        if share > style.get('off_palette_max_share', 0.03):
            cell = 32               # padded up to whole cells, so the last partial row and column count too
            gh, gw = -(-sc.h // cell), -(-sc.w // cell)
            img = np.zeros((gh * cell, gw * cell), bool)
            img[:sc.h, :sc.w][mask] = off
            cy, cx = (int(v) for v in np.unravel_index(np.argmax(img.reshape(gh, cell, gw, cell).sum((1, 3))), (gh, gw)))
            patch = img[:sc.h, :sc.w][cy * cell:(cy + 1) * cell, cx * cell:(cx + 1) * cell]
            col = np.median(sc.rgb[cy * cell:(cy + 1) * cell, cx * cell:(cx + 1) * cell][patch], axis=0)
            lab_c = srgb_to_lab(col)
            name, rgb_r, lab_r = min(pal, key=lambda r: np.linalg.norm(r[2] - lab_c))
            fail('palette', None, '%.1f%% of the UI is off palette (max %.1f%%), most at %s'
                 % (100 * share, 100 * style.get('off_palette_max_share', 0.03), hexcode(col)),
                 'use %s %s (dE %.0f) or add the colour to the palette with the user' % (name, hexcode(rgb_r),
                                                                                       np.linalg.norm(lab_r - lab_c)),
                 (min(sc.w - 1, cx * cell + cell // 2), min(sc.h - 1, cy * cell + cell // 2)))
        acc = [i for i, r in enumerate(pal) if r[0].startswith('Accent')]
        if acc and style.get('accent_max_share') is not None:
            a_share = float(((dist.argmin(1)[:, None] == np.array(acc)[None]).any(1) & ~off).mean())
            if a_share > style['accent_max_share']:
                fail('accent', None, 'accent covers %.1f%% of the UI (max %.1f%%)'
                     % (100 * a_share, 100 * style['accent_max_share']),
                     'keep accents for the one thing to look at; use a palette role for the rest', (sc.w // 2, sc.h // 2))
    return fails


def summary(sc):
    """The screen's numbers in reference px, for ui_metrics.json and the sheet's .json."""
    def med(v):
        return round(float(np.median(v)), 1) if len(v) else None

    els = sc.elements
    texts = [m for m in els if m['kind'] == 'text' and m.get('ink') is not None]
    icons = [m for m in els if m['kind'] == 'icon' and m.get('ink') is not None]
    buttons = [m for m in els if m['kind'] == 'button']
    sized = [m for m in els if m['kind'] in ('button', 'icon', 'panel') and not sc.full(m['box'])]
    gaps = [g * sc.s for _, _, g, _ in neighbours([m['box'] for m in sized])]
    lengths = [v for m in sized for v in m['size']] + gaps
    content = sc.content()
    margin = [min(m['box'][0], m['box'][1], sc.w - m['box'][2], sc.h - m['box'][3]) * sc.s for m in content]
    return {
        'image': os.path.basename(sc.layout['path']), 'size': [sc.w, sc.h], 'scale': round(sc.s, 3),
        'text_px': sorted(m['px'] for m in texts),
        'text_contrast_min': min((m['contrast'] for m in texts), default=None),
        'text_contrast_median': med([m['contrast'] for m in texts]),
        'icon_contrast_min': min((m['contrast'] for m in icons), default=None),
        'button_short_px': sorted(min(m['size']) for m in buttons),
        'radius_px': {k: med([m['radius'] for m in sized if m['kind'] == k and 'radius' in m]) for k in ('button', 'panel')},
        'stroke_px': {k: med([m['stroke'] for m in sized if m['kind'] == k and 'stroke' in m]) for k in ('button', 'panel')},
        'gaps_px': [round(g, 1) for g in gaps],
        'on_grid': {str(g): round(float(np.mean([abs(v - round(v / g) * g) <= 1.0 for v in lengths])), 2) if lengths else None
                    for g in (4, 8)},
        'icon_fill_share': med([m['fill_share'] for m in icons]),
        'icon_line_px': med([m['line_px'] for m in icons if m['fill_share'] < 0.4]),
        'elements': len(content),
        'empty_share': sc.empty_share((0, 0, sc.w, sc.h)),
        'edge_margin_min_px': round(min(margin), 1) if margin else None,
    }


def tiers(values):
    """Groups font sizes within 10 % of each other: [[size, count], ...]."""
    out = []
    for v in sorted(values):
        if out and v <= out[-1][0] * 1.1:
            out[-1].append(v)
        else:
            out.append([v])
    return [[round(float(np.median(g)), 1), len(g)] for g in out]


# ---- images for the sheet


def resized(rgb, w, h):
    buf = oiio.ImageBuf(oiio.ImageSpec(rgb.shape[1], rgb.shape[0], 3, oiio.FLOAT))
    buf.set_pixels(oiio.ROI(), np.ascontiguousarray(rgb, np.float32))
    out = oiio.ImageBufAlgo.resize(buf, filtername='box', roi=oiio.ROI(0, w, 0, h, 0, 1, 0, 3))
    return out.get_pixels(oiio.FLOAT)[:, :, :3]


def at_short(rgb, short):
    h, w = rgb.shape[:2]
    k = short / float(min(w, h))
    return resized(rgb, max(1, round(w * k)), max(1, round(h * k))), k


def frame(img, b, colour, t=2):
    x0, y0, x1, y1 = (int(round(v)) for v in b)
    h, w = img.shape[:2]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    img[y0:min(h, y0 + t), x0:x1] = colour
    img[max(0, y1 - t):y1, x0:x1] = colour
    img[y0:y1, x0:min(w, x0 + t)] = colour
    img[y0:y1, max(0, x1 - t):x1] = colour


def crop(rgb, cx, cy, size):
    out = np.full((size, size, 3), 0.5, np.float32)
    h, w = rgb.shape[:2]
    x0, y0 = int(cx - size // 2), int(cy - size // 2)
    sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(w, x0 + size), min(h, y0 + size)
    if sx1 > sx0 and sy1 > sy0:
        out[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = rgb[sy0:sy1, sx0:sx1]
    return out


def write_png(rgb, path):
    buf = oiio.ImageBuf(oiio.ImageSpec(rgb.shape[1], rgb.shape[0], 3, oiio.UINT8))
    buf.set_pixels(oiio.ROI(), np.clip(rgb, 0, 1).astype(np.float32))
    if not buf.write(path):
        raise SystemExit('cannot write %s: %s' % (path, buf.geterror()))


def compose(rows, gap=16, bg=0.5):
    width = max(sum(t.shape[1] for t in r) + gap * (len(r) + 1) for r in rows)
    height = sum(max(t.shape[0] for t in r) for r in rows) + gap * (len(rows) + 1)
    sheet = np.full((height, width, 3), bg, np.float32)
    places, y = [], gap
    for r in rows:
        x = gap
        for t in r:
            sheet[y:y + t.shape[0], x:x + t.shape[1]] = t
            places.append([x, y, t.shape[1], t.shape[0]])
            x += t.shape[1] + gap
        y += max(t.shape[0] for t in r) + gap
    return sheet, places


def sheet(sc, fails, style, refs, golden, out):
    """Row 1 at phone size: the screen, the screen with the gate drawn on it (red: a failing element, green: the
    others, blue: the safe area), the references, the golden screen. Row 2 at the reference's real pixels: the smallest
    text, the smallest button and the lowest contrast element of the screen, then each reference's smallest text."""
    phone, k = at_short(sc.rgb, PHONE_SHORT)
    over = phone.copy()
    bad = {f['id'] for f in fails}
    frame(over, [v * k for v in sc.safe_box(style)], (0.2, 0.45, 1.0))
    for m in sc.elements:
        if m['kind'] != 'art' and not sc.full(m['box']):
            frame(over, [v * k for v in m['box']], (1.0, 0.1, 0.1) if m['id'] in bad else (0.2, 0.85, 0.3))
    for f in fails:
        if f['id'] == '-':
            x, y = (v * k for v in f['at'])
            frame(over, (x - 6, y - 6, x + 6, y + 6), (1.0, 0.1, 0.1), 3)
    row1, legend1 = [phone, over], ['screen', 'gate']
    for r in refs:
        row1.append(at_short(r.rgb, PHONE_SHORT)[0])
        legend1.append('reference ' + os.path.basename(r.layout['path']))
    if golden:
        row1.append(at_short(read_rgb(golden, long_side=None), PHONE_SHORT)[0])
        legend1.append('golden')

    def crops(scr, which):
        real, kk = at_short(scr.rgb, REF_SHORT)
        tiles, names = [], []
        for label, m in which:
            if m is not None and m['id'] not in names:
                cx, cy = scr.centre(m)
                tiles.append(crop(real, cx * kk, cy * kk, CROP))
                names.append(m['id'])
        return tiles, ['%s %s' % (os.path.basename(scr.layout['path']), n) for n in names]

    def smallest(scr, kind, key):
        ms = [m for m in scr.elements if m['kind'] == kind and m.get(key) is not None]
        return min(ms, key=lambda m: m[key] if not isinstance(m[key], list) else min(m[key])) if ms else None

    low = min([m for m in sc.elements if m.get('contrast') is not None], key=lambda m: m['contrast'], default=None)
    row2, legend2 = crops(sc, [('text', smallest(sc, 'text', 'px')), ('button', smallest(sc, 'button', 'size')),
                               ('contrast', low)])
    for r in refs:
        t, n = crops(r, [('text', smallest(r, 'text', 'px'))])
        row2 += t
        legend2 += n
    img, places = compose([row1, row2] if row2 else [row1])
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    write_png(img, out)
    report = {
        'tiles': [{'label': l, 'rect': p} for l, p in zip(legend1 + legend2, places)],
        'phone_short_px': PHONE_SHORT, 'crop_px': CROP,
        'screen': summary(sc), 'references': [summary(r) for r in refs],
        'fails': fails,
        'style': {k: style.get(k) for k in ('text_px', 'touch_min_px', 'grid_px', 'radius_px', 'stroke_px', 'icon',
                                            'density', 'contrast', 'signature', 'avoid')},
    }
    with open(os.path.splitext(out)[0] + '.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, indent=1)
    return report


# ---- CLI


def load_layouts(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    base = os.path.dirname(os.path.abspath(path))
    out = []
    for lay in data if isinstance(data, list) else [data]:
        lay = dict(lay)
        lay['path'] = os.path.join(base, lay['image'])
        out.append(lay)
    return out


def load_style(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def extract(args):
    screens = [Screen(l) for l in load_layouts(args.layouts)]
    labs, gs = [], []
    rng = np.random.default_rng(7)
    for sc in screens:
        mask = sc.ui_mask()
        lab = sc.lab[mask]
        g = np.hypot(*np.gradient(sc.lab[..., 0]))[mask]
        keep = rng.choice(len(lab), 200000, replace=False) if len(lab) > 200000 else slice(None)
        labs.append(lab[keep])
        gs.append(g[keep])
    per = [summary(sc) for sc in screens]
    colour = metrics(np.concatenate(labs), np.concatenate(gs))

    def pooled(key):
        return [v for p in per for v in (p[key] if isinstance(p[key], list) else [p[key]]) if v is not None]

    def med(v):
        return round(float(np.median(v)), 1) if v else None

    result = {'pooled': {
        'palette': colour['palette'], 'accents': colour['accents'], 'L_p2': colour['L_p2'], 'L_p98': colour['L_p98'],
        'text_tiers': tiers(pooled('text_px')),
        'text_contrast_min': min(pooled('text_contrast_min'), default=None),
        'text_contrast_median': med(pooled('text_contrast_median')),
        'icon_contrast_min': min(pooled('icon_contrast_min'), default=None),
        'button_short_px': {'min': min(pooled('button_short_px'), default=None), 'median': med(pooled('button_short_px'))},
        'radius_px': {k: med([p['radius_px'][k] for p in per if p['radius_px'][k] is not None]) for k in ('button', 'panel')},
        'stroke_px': {k: med([p['stroke_px'][k] for p in per if p['stroke_px'][k] is not None]) for k in ('button', 'panel')},
        'on_grid': {g: med([p['on_grid'][g] for p in per if p['on_grid'][g] is not None]) for g in ('4', '8')},
        'icon_fill_share': med(pooled('icon_fill_share')),
        'icon_line_px': med(pooled('icon_line_px')),
        'elements': {'median': med(pooled('elements')), 'max': max(pooled('elements'), default=None)},
        'empty_share': med(pooled('empty_share')),
        'edge_margin_min_px': min(pooled('edge_margin_min_px'), default=None),
    }, 'screens': per,
        'note': 'reference px (1080 short side); colours are the screens as drawn: check the swatches by eye'}
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=1)
    if args.swatches:
        write_swatches(result['pooled']['palette'], result['pooled']['accents'], args.swatches)
    p = result['pooled']
    print('UI STYLE %d screens: text %s, buttons %s px, radius %s, stroke %s, %d swatches -> %s'
          % (len(per), p['text_tiers'], p['button_short_px']['median'], p['radius_px'], p['stroke_px'],
             len(p['palette']), args.out))
    return result


def run_gate(args):
    style = load_style(args.style)
    sc = Screen(load_layouts(args.layout)[0])
    fails = gate(sc, style)
    if args.report:
        with open(args.report, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'screen': summary(sc), 'fails': fails}, f, indent=1)
    for f in fails:
        print('UI FAIL %s %s at (%d, %d): %s; fix: %s' % (f['rule'], f['id'], f['at'][0], f['at'][1], f['msg'], f['fix']))
    if fails:
        raise SystemExit(1)
    print('UI GATE PASS %s: %d elements' % (os.path.basename(sc.layout['path']), len(sc.elements)))


def run_sheet(args):
    style = load_style(args.style)
    sc = Screen(load_layouts(args.layout)[0])
    refs = [Screen(l) for l in load_layouts(args.refs)] if args.refs else []
    fails = gate(sc, style)
    sheet(sc, fails, style, refs, args.golden if args.golden and os.path.exists(args.golden) else None, args.out)
    if args.golden and not os.path.exists(args.golden):
        print('UI SHEET NOTE no golden screen at %s yet (the golden screen\'s own sheets have none)' % args.golden)
    print('UI SHEET %s: %d gate failures -> %s' % (os.path.basename(sc.layout['path']), len(fails), args.out))


def main(argv=None):
    if argv is None:
        argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser(prog='ui_style.py')
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('extract')
    e.add_argument('--layouts', required=True)
    e.add_argument('--out', required=True)
    e.add_argument('--swatches')
    g = sub.add_parser('gate')
    g.add_argument('--style', required=True)
    g.add_argument('--layout', required=True)
    g.add_argument('--report')
    s = sub.add_parser('sheet')
    s.add_argument('--style', required=True)
    s.add_argument('--layout', required=True)
    s.add_argument('--refs')
    s.add_argument('--golden')
    s.add_argument('--out', required=True)
    args = ap.parse_args(argv)
    return {'extract': extract, 'gate': run_gate, 'sheet': run_sheet}[args.cmd](args)


if __name__ == '__main__':
    main()
