# Measures the look of a reference game from its screenshots, as numbers a style.json can hold. Headless, Blender's
# bundled numpy and OpenImageIO only (this machine has no system Python):
#
#   blender --background --factory-startup --python-exit-code 1 --python extract_style.py -- \
#       --images <dir or files...> [--crops crops.json] [--k 12] --out style_metrics.json [--swatches palette.png]
#
# crops.json: [{"file": "a.png", "rect": [x, y, w, h], "note": "flat-lit wall, mid distance"}, ...]; rect in pixels
# from the top left. A file listed without rect is used whole; with --crops only the listed regions are measured.
# Crop flat-lit surfaces: the numbers describe the final graded frame (light, fog, bloom, grading), not the albedo, so
# a crop full of fog or UI moves the palette. The metrics() function is shared with contact_sheet.py.
#
# Output per crop and pooled: palette (k-means in CIELAB, swatches by share), L* percentiles 2/50/98, mean chroma,
# accent_share (pixels with C* > 60), detail_energy (mean |grad L*| at 256 px on the long side) and dark_edge_share
# (pixels with L* < 15 on a strong edge: a proxy for drawn outlines).

import argparse
import json
import os
import sys

import numpy as np
import OpenImageIO as oiio

LONG_SIDE = 256          # every crop is measured at this size, so detail_energy compares across screenshot sizes
ACCENT_CHROMA = 60.0
EXTS = ('.png', '.jpg', '.jpeg', '.webp', '.tga', '.bmp', '.exr', '.tif', '.tiff')


def linear_to_srgb(c):
    c = np.clip(np.asarray(c, float), 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def read_rgba(path, rect=None, long_side=LONG_SIDE):
    """(sRGB (h, w, 3), alpha (h, w)) in 0..1 with straight, not premultiplied, colour; cropped to rect [x, y, w, h]
    and box-resampled to long_side on the long side (None keeps the size). Float files (EXR, float TIFF) hold linear
    values and are converted to sRGB."""
    cfg = oiio.ImageSpec()
    cfg.attribute('oiio:UnassociatedAlpha', 1)     # OIIO premultiplies on read otherwise: a cutout edge reads dark
    buf = oiio.ImageBuf(path, 0, 0, cfg)
    if buf.has_error:
        raise SystemExit('cannot read %s: %s' % (path, buf.geterror()))
    spec = buf.spec()
    if rect:
        x, y, w, h = (int(round(v)) for v in rect)
        x0, y0, x1, y1 = max(0, x), max(0, y), min(spec.width, x + w), min(spec.height, y + h)
        if x1 - x0 < 8 or y1 - y0 < 8:
            raise SystemExit('rect %s lies outside %s (%dx%d)' % (rect, path, spec.width, spec.height))
        buf = oiio.ImageBufAlgo.cut(buf, oiio.ROI(x0, x1, y0, y1))
        spec = buf.spec()
    scale = long_side / float(max(spec.width, spec.height)) if long_side else 1.0
    if scale < 1.0:
        w, h = max(1, round(spec.width * scale)), max(1, round(spec.height * scale))
        buf = oiio.ImageBufAlgo.resize(buf, roi=oiio.ROI(0, w, 0, h, 0, 1, 0, spec.nchannels))
    px = buf.get_pixels(oiio.FLOAT)
    if px.ndim == 2:
        px = px[:, :, None]
    n = px.shape[2]
    alpha = px[:, :, 3] if n >= 4 else px[:, :, 1] if n == 2 else np.ones(px.shape[:2], np.float32)
    rgb = px[:, :, :3] if n >= 3 else np.repeat(px[:, :, :1], 3, axis=2)
    if spec.format.basetype in (oiio.FLOAT, oiio.HALF):
        rgb = linear_to_srgb(rgb)
    return np.clip(rgb, 0.0, 1.0), np.clip(alpha, 0.0, 1.0)


def read_rgb(path, rect=None):
    return read_rgba(path, rect)[0]


def srgb_to_lab(rgb):
    """CIELAB (D65) of sRGB 0..1 values, any leading shape."""
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
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


def metrics(flat, g, k=12):
    """The numbers for a set of pixels from pixels(), one image or several pooled."""
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
        'palette': swatches(centres, shares, 0.005),
        'accents': swatches(*accents, 0.0),     # share = of the accent pixels, not of the image
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


def swatches(centres, shares, floor):
    return [{'srgb': [round(float(c), 3) for c in s], 'hex': hexcode(s), 'lab': [round(float(c), 1) for c in l],
             'share': round(float(sh), 3)}
            for l, s, sh in zip(centres, lab_to_srgb(centres), shares) if sh >= floor]


def write_swatches(palette, path, cell=64):
    """A strip of the pooled swatches, widest share first, for the decision page."""
    strip = np.zeros((cell, cell * len(palette), 3), np.float32)
    for i, sw in enumerate(palette):
        strip[:, i * cell:(i + 1) * cell] = sw['srgb']
    buf = oiio.ImageBuf(oiio.ImageSpec(strip.shape[1], cell, 3, oiio.UINT8))
    buf.set_pixels(oiio.ROI(), strip)
    if not buf.write(path):
        raise SystemExit('cannot write %s: %s' % (path, buf.geterror()))


def jobs(args):
    if args.crops:
        base = os.path.dirname(os.path.abspath(args.crops))
        with open(args.crops, encoding='utf-8') as f:
            for c in json.load(f):
                yield os.path.join(base, c['file']), c.get('rect'), c.get('note', '')
        return
    for p in args.images:
        if os.path.isdir(p):
            for name in sorted(os.listdir(p)):
                if name.lower().endswith(EXTS):
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
    args = ap.parse_args(argv)
    per, pooled = [], []
    for path, rect, note in jobs(args):
        lab, g = pixels(read_rgb(path, rect))
        per.append({'file': os.path.basename(path), 'rect': rect, 'note': note, **metrics(lab, g, args.k)})
        pooled.append((lab, g))
    if not per:
        raise SystemExit('no images: pass --images <dir or files> or --crops crops.json')
    result = {'pooled': metrics(np.concatenate([p[0] for p in pooled]), np.concatenate([p[1] for p in pooled]), args.k),
              'crops': per,
              'note': 'L* 0-100 (CIELAB D65); colours are the graded frame, not albedo: check the swatches by eye'}
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=1)
    if args.swatches:
        write_swatches(result['pooled']['palette'] + result['pooled']['accents'], args.swatches)
    p = result['pooled']
    print('STYLE %d crops: L* %.0f-%.0f, accent %.3f, detail %.1f, %d swatches -> %s'
          % (len(per), p['L_p2'], p['L_p98'], p['accent_share'], p['detail_energy'], len(p['palette']), args.out))


if __name__ == '__main__':
    main()
