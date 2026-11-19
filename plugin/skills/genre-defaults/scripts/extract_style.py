# Measures the look of a reference game from its screenshots, as numbers a style.json can hold. Headless, Blender's
# bundled numpy and OpenImageIO only (this machine has no system Python):
#
#   blender --background --factory-startup --python-exit-code 1 --python extract_style.py -- \
#       --images <dir or files...> [--crops crops.json] [--k 12] --out style_metrics.json [--swatches palette.png] \
#       [--style style.json]
#
# crops.json: [{"file": "a.png", "rect": [x, y, w, h], "note": "flat-lit wall, mid distance"}, ...]; rect in pixels
# from the top left. A file listed without rect is used whole; with --crops only the listed regions are measured.
# Crop flat-lit surfaces: the numbers describe the final graded frame (light, fog, bloom, grading), not the albedo, so
# a crop full of fog or UI moves the palette. An entry with "kind": "object" (a prop of one class, "class": "prop") is
# for contact_sheet's reference row and is skipped here. The metrics() function is shared with contact_sheet.py.
#
# Output per crop and pooled: palette (k-means in CIELAB, swatches by share), L* percentiles 2/50/98, mean chroma,
# accent_share (pixels with C* > 60), detail_energy (mean |grad L*|) and dark_edge_share (pixels with L* < 15 on a
# strong edge: a proxy for drawn outlines). Every shot is measured as if 1080 px tall (SCREEN_H), the scale
# camera.asset_px is given at, so the last two compare with contact_sheet's game tile. Each swatch's toon_albedo is
# the base colour Toon.shader's lit band draws as it, under style.json "light" when --style is given (as the sheet
# draws), else Unity's defaults (the template Main scene's sun, SUN_SRGB x 1); "toon_lit" in the output is that light.
# An albedo cannot pass 1: a pooled swatch brighter in a channel than that light's lit band reaches (under the default
# warm sun, sRGB blue over about 0.89) prints a STYLE WARNING with the colour the band really draws and is listed in
# "albedo_clipped": [{"swatch": <SWATCH number>, "hex", "channels": ["b"], "drawn_srgb", "drawn_hex"}] ([] when none).
# Pixel values are read as sRGB: a file whose colour profile says otherwise (a Display P3 phone screenshot) prints a
# STYLE WARNING to convert it first, and a --style light.color that is not 3 numbers 0-1 stops the run.
# Each measured crop prints its image size and the rect it takes (a rect running off the image is cut to it, with a
# STYLE WARNING), and crops.png beside the first measured shot (the game's git-ignored reference folder: it shows
# another game's art) holds every measured crop as a numbered thumbnail, in that order: look at it before writing
# style.json.

import argparse
import json
import os
import sys

import numpy as np
import OpenImageIO as oiio

LONG_SIDE = 256          # read_rgba's default long side (no screen_h, no long_side)
SCREEN_H = 1080          # screenshots are measured as if 1080 px tall: the scale camera.asset_px is given at, so the
                         # game tile of contact_sheet and a crop compare on detail_energy and dark_edge_share
POOL_MAX = 200000        # pixels per crop in the pooled numbers: 20 full 1080p shots would be over 1 GB of CIELAB
ACCENT_CHROMA = 60.0
SUN_SRGB = [1.0, 0.957, 0.839]     # Unity's default sun, the light in every template game's Main scene
EXTS = ('.png', '.jpg', '.jpeg', '.webp', '.tga', '.bmp', '.exr', '.tif', '.tiff')


def srgb_to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    c = np.clip(np.asarray(c, float), 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


_NOT_SRGB = set()        # files already warned about, so a shot read for several crops says it once


def read_rgba(path, rect=None, long_side=LONG_SIDE, screen_h=None):
    """(sRGB (h, w, 3), alpha (h, w)) in 0..1 with straight, not premultiplied, colour; cropped to rect [x, y, w, h]
    and box-resampled: with screen_h, by the factor that makes the whole image screen_h tall (the pixel scale
    camera.asset_px is given at); otherwise down to long_side on the long side (None keeps the size). Float files
    (EXR, float TIFF) hold linear values and are converted to sRGB."""
    cfg = oiio.ImageSpec()
    cfg.attribute('oiio:UnassociatedAlpha', 1)     # OIIO premultiplies on read otherwise: a cutout edge reads dark
    buf = oiio.ImageBuf(path, 0, 0, cfg)
    if buf.has_error:
        raise SystemExit('cannot read %s: %s' % (path, buf.geterror()))
    spec = buf.spec()
    # the pixel values are taken as sRGB whatever the file's profile says: a Display P3 shot then reads duller
    icc = spec.getattribute('ICCProfile:profile_description')
    if icc and 'sRGB' not in icc and path not in _NOT_SRGB:
        _NOT_SRGB.add(path)
        print('STYLE WARNING: %s carries the colour profile %s and is read as sRGB, so saturated colours read duller: '
              'convert the shot to sRGB first (an iPhone screenshot is Display P3)' % (path, icc))
    full_h = spec.height
    if rect:
        x0, y0, w, h = clip_rect(rect, spec.width, spec.height)
        if w < 1 or h < 1:
            raise SystemExit('rect %s lies outside %s (%dx%d)' % (rect, path, spec.width, spec.height))
        if w < 8 or h < 8:
            raise SystemExit('rect %s is %dx%d px inside %s: a crop needs 8 px a side, so widen it (on a 1x game tile '
                             'take the widest flat run of the surface)' % (rect, w, h, path))
        buf = oiio.ImageBufAlgo.cut(buf, oiio.ROI(x0, x0 + w, y0, y0 + h))
        spec = buf.spec()
    if screen_h:
        scale = screen_h / float(full_h)
    else:
        scale = min(1.0, long_side / float(max(spec.width, spec.height))) if long_side else 1.0
    if abs(scale - 1.0) > 1e-3:
        w, h = max(1, round(spec.width * scale)), max(1, round(spec.height * scale))
        # box: the default windowed sinc rings at hard edges and invents overshoot colours the k-means would keep
        buf = oiio.ImageBufAlgo.resize(buf, filtername='box', roi=oiio.ROI(0, w, 0, h, 0, 1, 0, spec.nchannels))
    px = buf.get_pixels(oiio.FLOAT)
    if px.ndim == 2:
        px = px[:, :, None]
    n = px.shape[2]
    alpha = px[:, :, 3] if n >= 4 else px[:, :, 1] if n == 2 else np.ones(px.shape[:2], np.float32)
    rgb = px[:, :, :3] if n >= 3 else np.repeat(px[:, :, :1], 3, axis=2)
    if spec.format.basetype in (oiio.FLOAT, oiio.HALF):
        rgb = linear_to_srgb(rgb)
    return np.clip(rgb, 0.0, 1.0), np.clip(alpha, 0.0, 1.0)


def clip_rect(rect, width, height):
    """rect [x, y, w, h] cut to a width x height image, in whole pixels."""
    x, y, w, h = (int(round(v)) for v in rect)
    x0, y0 = max(0, x), max(0, y)
    return [x0, y0, min(width, x + w) - x0, min(height, y + h) - y0]


def read_rgb(path, rect=None, **kw):
    return read_rgba(path, rect, **kw)[0]


def srgb_to_lab(rgb):
    """CIELAB (D65) of sRGB 0..1 values, any leading shape."""
    lin = srgb_to_linear(rgb)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = lin @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def lab_to_srgb(lab):
    fy = (lab[..., 0] + 16) / 116
    f = np.stack([fy + lab[..., 1] / 500, fy, fy - lab[..., 2] / 200], axis=-1)
    xyz = np.where(f ** 3 > 216 / 24389, f ** 3, (116 * f - 16) / (24389 / 27)) * np.array([0.95047, 1.0, 1.08883])
    m = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])
    lin = np.clip(xyz @ m.T, 0.0, 1.0)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


def kmeans(lab, k, iters=25):
    """Deterministic k-means++ in CIELAB; returns (centres, shares) sorted by share."""
    rng = np.random.default_rng(7)
    pts = lab if len(lab) <= 40000 else lab[rng.choice(len(lab), 40000, replace=False)]
    k = min(k, len(np.unique(np.round(pts, 1), axis=0)))
    centres = [pts[rng.integers(len(pts))]]
    for _ in range(1, k):
        d = np.min([((pts - c) ** 2).sum(1) for c in centres], axis=0)
        centres.append(pts[rng.choice(len(pts), p=d / d.sum())] if d.sum() > 0 else pts[rng.integers(len(pts))])
    centres = np.array(centres)
    for _ in range(iters):
        label = np.argmin(((pts[:, None, :] - centres[None]) ** 2).sum(2), axis=1)
        moved = np.array([pts[label == i].mean(0) if np.any(label == i) else centres[i] for i in range(k)])
        if np.allclose(moved, centres, atol=0.05):
            break
        centres = moved
    # shares from the sample: labelling every pooled pixel would need N x k x 3 floats (hundreds of MB for 20 shots)
    label = np.argmin(((pts[:, None, :] - centres[None]) ** 2).sum(2), axis=1)
    shares = np.bincount(label, minlength=k) / float(len(pts))
    order = np.argsort(-shares)
    return centres[order], shares[order]


def hexcode(srgb):
    return '#%02x%02x%02x' % tuple(int(round(c * 255)) for c in srgb)


def pixels(rgb, mask=None):
    """(CIELAB, |grad L*|) of one image's pixels (h, w, 3 sRGB) as flat arrays; mask (h, w) bool keeps those pixels
    (an asset render without its background)."""
    lab = srgb_to_lab(rgb)
    gy, gx = np.gradient(lab[..., 0])
    sel = np.ones(lab.shape[:2], bool) if mask is None else mask
    return lab[sel], np.hypot(gx, gy)[sel]


def toon_lit(light):
    """Toon.shader's lit band factor (linear, per channel) under style.json light, as contact_sheet's toon_params
    reads it: main light colour x intensity + the scene's SH level light.ambient x light.ambient_strength."""
    return (srgb_to_linear(light.get('color', SUN_SRGB)) * float(light.get('intensity', 1.0))
            + float(light.get('ambient', 0.5)) * float(light.get('ambient_strength', 0.18)))


TOON_LIT = toon_lit({})      # Toon.shader's lit band under Unity's defaults: sun x 1 + SH ambient 0.5 x 0.18


def metrics(flat, g, k=12, lit=TOON_LIT):
    """The numbers for a set of pixels from pixels(), one image or several pooled; lit is toon_lit()."""
    if len(flat) == 0:
        raise ValueError('no pixels to measure')
    chroma = np.hypot(flat[:, 1], flat[:, 2])
    centres, shares = merge(*kmeans(flat, k))
    # accents are few pixels by nature (a red door, a gold coin) and fall under the share floor: their own pass
    hot = flat[chroma > ACCENT_CHROMA]
    accents = merge(*kmeans(hot, 4), de=12.0) if len(hot) >= 20 else (np.zeros((0, 3)), np.zeros(0))
    return {
        'pixels': int(len(flat)),
        'L_p2': round(float(np.percentile(flat[:, 0], 2)), 1),
        'L_p50': round(float(np.percentile(flat[:, 0], 50)), 1),
        'L_p98': round(float(np.percentile(flat[:, 0], 98)), 1),
        'chroma_mean': round(float(chroma.mean()), 1),
        'accent_share': round(float((chroma > ACCENT_CHROMA).mean()), 3),
        'detail_energy': round(float(g.mean()), 2),
        'dark_edge_share': round(float(((flat[:, 0] < 15) & (g > 8)).mean()), 3),
        'palette': swatches(centres, shares, 0.005, lit),
        'accents': swatches(*accents, 0.0, lit),     # share = of the accent pixels, not of the image
    }


def merge(centres, shares, de=5.0):
    """Folds swatches closer than de (CIELAB distance) into the larger one: resampled edges make near-twins."""
    keep_c, keep_s = [], []
    for c, s in zip(centres, shares):
        near = [i for i, kc in enumerate(keep_c) if np.linalg.norm(kc - c) < de]
        if near:
            keep_s[near[0]] += s
        else:
            keep_c.append(c)
            keep_s.append(s)
    return np.array(keep_c).reshape(-1, 3), np.array(keep_s)


def swatches(centres, shares, floor, lit=TOON_LIT):
    """toon_albedo: the base colour Toon.shader's lit band draws as this swatch (the frame shows the lit colour)."""
    return [{'srgb': [round(float(c), 3) for c in s], 'hex': hexcode(s), 'lab': [round(float(c), 1) for c in l],
             'share': round(float(sh), 3), 'toon_albedo': hexcode(toon_albedo(s, lit)),
             'toon_albedo_srgb': [round(float(c), 3) for c in toon_albedo(s, lit)]}   # style.json's palette takes this
            for l, s, sh in zip(centres, lab_to_srgb(centres), shares) if sh >= floor]


def toon_albedo(s, lit=TOON_LIT):
    return linear_to_srgb(srgb_to_linear(s) / lit)


def albedo_clipped(found, lit):
    """The swatches (numbered as write_swatches prints them) whose toon_albedo was cut at 1: the lit band draws
    albedo x lit, so a channel brighter than lit itself cannot be reached. Each prints a STYLE WARNING."""
    out = []
    for i, sw in enumerate(found, 1):
        drawn = linear_to_srgb(np.minimum(srgb_to_linear(sw['srgb']) / lit, 1.0) * lit)
        over = [c for c, a, b in zip('rgb', sw['srgb'], drawn) if a - b > 0.5 / 255]
        if over:
            out.append({'swatch': i, 'hex': sw['hex'], 'channels': over,
                        'drawn_srgb': [round(float(c), 3) for c in drawn], 'drawn_hex': hexcode(drawn)})
            print('STYLE WARNING: swatch %d %s needs an albedo over 1 in %s: the lit band under this light draws %s. '
                  'Change the reading\'s light (--style: light.color, intensity, ambient) and rerun, or take %s as the '
                  'colour the game will show' % (i, sw['hex'], '/'.join(over), out[-1]['drawn_hex'],
                                                 out[-1]['drawn_hex']))
    return out


def write_swatches(palette, accents, path, cell=64):
    """A strip for the decision page: the pooled palette (widest share first), a white gap, then the accents, each in
    style_metrics.json's order; the run prints every cell's number and hex."""
    gap = cell // 4 if accents else 0
    strip = np.ones((cell, cell * (len(palette) + len(accents)) + gap, 3), np.float32)
    for i, sw in enumerate(palette + accents):
        x = i * cell + (gap if i >= len(palette) else 0)
        strip[:, x:x + cell] = sw['srgb']
        print('SWATCH %d %s %s toon_albedo %s'
              % (i + 1, 'accent' if i >= len(palette) else 'palette', sw['hex'], sw['toon_albedo']))
    save(strip, path)


def save(rgb, path):
    buf = oiio.ImageBuf(oiio.ImageSpec(rgb.shape[1], rgb.shape[0], 3, oiio.UINT8))
    buf.set_pixels(oiio.ROI(), rgb)
    if not buf.write(path):
        raise SystemExit('cannot write %s: %s' % (path, buf.geterror()))


# 3 x 5 digits, row by row: this OpenImageIO has no font rendering
DIGITS = ('111101101101111', '010110010010111', '111001111100111', '111001111001111', '101101111001001',
          '111100111001111', '111100111101111', '111001001001001', '111101111101111', '111101111001111')


def write_crops(thumbs, path, cell=128, k=3):
    """crops.png: each measured crop fitted in a cell, left to right in the order measured, its number in black on
    white at the top left (the CROP lines print the same numbers)."""
    strip = np.full((cell, len(thumbs) * (cell + 8), 3), 0.5, np.float32)     # grey: a white crop still shows
    for i, img in enumerate(thumbs):
        x = i * (cell + 8)
        strip[:img.shape[0], x:x + img.shape[1]] = img
        label = str(i + 1)
        strip[:5 * k + 2 * k, x:x + len(label) * 4 * k + k] = 1.0
        for j, d in enumerate(label):
            glyph = np.array([int(b) for b in DIGITS[int(d)]], bool).reshape(5, 3)
            big = np.repeat(np.repeat(glyph, k, axis=0), k, axis=1)
            region = strip[k:k + 5 * k, x + k + j * 4 * k:x + k + j * 4 * k + 3 * k]
            region[big] = 0.0
    save(strip, path)


def jobs(args):
    if args.crops:
        base = os.path.dirname(os.path.abspath(args.crops))
        with open(args.crops, encoding='utf-8') as f:
            for c in json.load(f):
                if c.get('kind', 'surface') == 'surface':      # object crops hold background: the sheet shows them
                    yield os.path.join(base, c['file']), c.get('rect'), c.get('note', '')
        return
    for p in args.images:
        if os.path.isdir(p):
            for name in sorted(os.listdir(p)):
                if name.lower().endswith(EXTS) and name != 'crops.png':      # main() writes it beside the shots
                    yield os.path.join(p, name), None, ''
        else:
            yield p, None, ''


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser(prog='extract_style.py')
    ap.add_argument('--images', nargs='*', default=[])
    ap.add_argument('--crops')
    ap.add_argument('--k', type=int, default=12)
    ap.add_argument('--out', required=True)
    ap.add_argument('--swatches')
    ap.add_argument('--style')
    args = ap.parse_args(argv)
    lit = TOON_LIT
    if args.style:
        with open(args.style, encoding='utf-8') as f:
            light = json.load(f).get('light') or {}
        c = light.get('color', SUN_SRGB)      # style_gate's check_colours test: this file cannot import it
        if not (isinstance(c, list) and len(c) == 3 and all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in c)):
            raise SystemExit('%s: light.color is %r: write 3 numbers 0-1 (the Inspector\'s 0-255 values over 255), not '
                             'a hex or 0-255' % (args.style, c))
        lit = toon_lit(light)
    per, pooled, thumbs = [], [], []
    rng = np.random.default_rng(7)
    for i, (path, rect, note) in enumerate(jobs(args), 1):
        lab, g = pixels(read_rgb(path, rect, screen_h=SCREEN_H))
        spec = oiio.ImageBuf(path).spec()
        used = clip_rect(rect, spec.width, spec.height) if rect else [0, 0, spec.width, spec.height]
        print('CROP %d %s: image %dx%d, rect %s' % (i, os.path.basename(path), spec.width, spec.height, used))
        if rect and used != [int(round(v)) for v in rect]:
            print('STYLE WARNING: crop %d rect %s runs off %s (%dx%d): only %s is measured; fix the rect in crops.json'
                  % (i, rect, os.path.basename(path), spec.width, spec.height, used))
        thumbs.append(read_rgb(path, rect, long_side=128))
        per.append({'file': os.path.basename(path), 'rect': rect, 'note': note, **metrics(lab, g, args.k, lit)})
        keep = rng.choice(len(lab), POOL_MAX, replace=False) if len(lab) > POOL_MAX else slice(None)
        pooled.append((lab[keep], g[keep]))
    if not per:
        raise SystemExit('%s holds only object crops: add surface crops (step 1.3), extract_style measures those'
                         % args.crops if args.crops
                         else 'no images: pass --images <dir or files> or --crops crops.json')
    result = {'pooled': metrics(np.concatenate([p[0] for p in pooled]), np.concatenate([p[1] for p in pooled]), args.k,
                                lit),
              'crops': per, 'toon_lit': [round(float(c), 4) for c in np.broadcast_to(lit, 3)],
              'note': 'L* 0-100 (CIELAB D65); colours are the graded frame, not albedo: check the swatches by eye'}
    result['albedo_clipped'] = albedo_clipped(result['pooled']['palette'] + result['pooled']['accents'], lit)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=1)
    # beside the shots, not --out: the thumbnails are another game's art, and reference/ is the git-ignored folder
    crops_png = os.path.join(os.path.dirname(os.path.abspath(next(jobs(args))[0])), 'crops.png')
    write_crops(thumbs, crops_png)
    print('CROPS %s: %d measured crop(s), numbered as the CROP lines' % (crops_png, len(thumbs)))
    if args.swatches:
        write_swatches(result['pooled']['palette'], result['pooled']['accents'], args.swatches)
    p = result['pooled']
    print('STYLE %d crops: L* %.0f-%.0f, accent %.3f, detail %.1f, %d swatches -> %s'
          % (len(per), p['L_p2'], p['L_p98'], p['accent_share'], p['detail_energy'], len(p['palette']), args.out))


if __name__ == '__main__':
    main()
