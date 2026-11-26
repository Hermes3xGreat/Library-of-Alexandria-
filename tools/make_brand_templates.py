#!/usr/bin/env python3
"""One-time: turn Plato Scroll's own pictures into blank scroll templates, so
every Scroll's icon, logo, favicon and banner has exactly the Plato mark's
size and style, only with its own colour, symbol and initials.

usage: make_brand_templates.py   (reads scrolls/plato, writes engine/brand/)

For each picture the white overlay's opacity is recovered from the flat
colour (alpha = (pixel - tile) / (255 - tile)), the Φ, the ΠΣ and the
banner title are cleared, and their boxes are saved in templates.json.
"""
import os, io, re, json, base64, zipfile
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'engine', 'brand')


def plato_images():
    d = os.path.join(ROOT, 'scrolls', 'plato')
    imgs = {}
    with zipfile.ZipFile(os.path.join(d, 'android', 'base.apk')) as z:
        imgs['fg432'] = Image.open(io.BytesIO(z.read('res/mipmap-xxxhdpi-v4/ic_launcher_foreground.png')))
        imgs['legacy192'] = Image.open(io.BytesIO(z.read('res/mipmap-xxxhdpi-v4/ic_launcher.png')))
    css = open(os.path.join(d, 'slots', 'hv-intro-css.html'), encoding='utf-8').read()
    m = re.search(r'hv-st-logo\{[^}]*?url\(data:image/\w+;base64,([A-Za-z0-9+/=]+)\)', css)
    imgs['logo180'] = Image.open(io.BytesIO(base64.b64decode(m.group(1))))
    t = open(os.path.join(d, 'text', 'banner_image.txt')).read()
    imgs['banner'] = Image.open(io.BytesIO(base64.b64decode(t.split(',', 1)[1])))
    return imgs


def boxes_of(mask):
    """vertical clusters of True rows -> [(x0,y0,x1,y1)] top to bottom."""
    rows = np.where(mask.any(axis=1))[0]
    out, start, prev = [], None, None
    for r in rows:
        if start is None:
            start = prev = r
        elif r - prev > 2:
            out.append((start, prev)); start = r
        prev = r
    if start is not None:
        out.append((start, prev))
    res = []
    for y0, y1 in out:
        cols = np.where(mask[y0:y1 + 1].any(axis=0))[0]
        res.append([int(cols[0]), int(y0), int(cols[-1]), int(y1)])
    return res


def extract(name, im):
    rgba = np.array(im.convert('RGBA')).astype(float)
    opaque = rgba[..., 3] > 250
    cols, counts = np.unique(rgba[opaque][:, :3].astype(int), axis=0, return_counts=True)
    tile = cols[counts.argmax()]
    a = ((rgba[..., :3] - tile) / np.maximum(1, 255 - tile)).mean(axis=2).clip(0, 1)
    a[~opaque & (rgba[..., 3] < 5)] = 0
    shape = (rgba[..., 3] / 255.0)          # where the tile itself is (fg icon is inset)
    H, W = a.shape
    info = {'size': [W, H], 'tile': [int(c) for c in tile]}
    # bottom bar: the lowest row with a long fully-white run
    bar = None
    for y in range(H - 1, -1, -1):
        run = np.where(a[y] > .93)[0]
        if len(run) > W * .12 and (run[-1] - run[0]) < W * .9 and (run[-1] - run[0] + 1) == len(run):
            bar = (y, int(run[0]), int(run[-1])); break
    if bar is None:
        raise SystemExit(f'{name}: no bottom bar found')
    by, x0, x1 = bar
    while by > 0 and (a[by - 1, x0 + 2:x1 - 2] > .93).all():
        by -= 1
    # sheet rows: above the bar, left edge shows the translucent sheet
    sx = x0 + max(1, (x1 - x0) // 40)
    ec = x0 + max(2, round((x1 - x0) * .08))    # a column inside the sheet's left margin, clear of the glyph
    med = lambda y: float(a[y, ec])
    bottom = by - 1
    inr = lambda y: .25 < med(y) < .9
    while bottom > 2 and not (inr(bottom) and inr(bottom - 1) and inr(bottom - 2)):
        bottom -= 1                          # skip the thin gap line above the bar
    top = bottom                             # walk up the sheet to the roller
    while top > 0 and .25 < med(top - 1) < .9:
        top -= 1
    # the roller is translucent too; it starts where the left cap (white) appears
    cap = [y for y in range(top, bottom) if (a[y, max(0, x0 - 6):x0 + 4] > .93).any()]
    if cap:
        top = max(cap) + 1                   # start below the roller and its white end cap
    while top < bottom and abs(med(top) - med(top + 2)) > .05:
        top += 1                             # and below the roller's soft lower edge
    interior = np.zeros_like(a, bool)
    interior[top:bottom + 1, sx + 1:x1 - (sx - x0)] = True
    glyph = interior & (a > .9)
    sub = interior & (a > .55) & (a < .9) & ~glyph
    gb = boxes_of(glyph)
    # main symbol = tallest white cluster; initials = the lighter cluster below it
    main = max(gb, key=lambda b: b[3] - b[1]) if gb else None
    subs = [b for b in boxes_of(sub) if main and b[1] > main[3] and (b[3] - b[1]) > 2]
    info.update(sheet=[sx, top, x1, bottom], bar=[x0, by, x1], glyph=main, initials=subs[0] if subs else None)
    # clear the sheet rows to their plain opacity (sampled at the left edge)
    for y in range(top, bottom + 1):
        a[y, sx:x1 - (sx - x0) + 1] = med(y)
    if name == 'banner':                     # title text sits right of the scroll
        right = x1 + 30
        tb = boxes_of(a[:, right:] > .5)
        if tb:
            t = tb[0]; info['title'] = [t[0] + right, t[1], max(b[2] for b in tb) + right, tb[-1][3]]
        a[:, right:] = 0
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray((a * 255).round().astype('uint8'), 'L').save(os.path.join(OUT, f'{name}-overlay.png'))
    Image.fromarray((shape * 255).round().astype('uint8'), 'L').save(os.path.join(OUT, f'{name}-tile.png'))
    return info


def main():
    meta = {n: extract(n, im) for n, im in plato_images().items()}
    json.dump(meta, open(os.path.join(OUT, 'templates.json'), 'w'), indent=1)
    for n, m in meta.items():
        print(n, m)


if __name__ == '__main__':
    main()
