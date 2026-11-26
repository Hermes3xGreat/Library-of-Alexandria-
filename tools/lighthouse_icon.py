#!/usr/bin/env python3
"""The Library of Alexandria launcher icon: the Pharos lighthouse.
usage: lighthouse_icon.py  (rewrites the icons in scrolls/alexandria/android/base.apk and icon.png)"""
import os, re, io, zipfile, shutil
from PIL import Image, ImageDraw, ImageFilter
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NAVY = (20, 38, 74); NIGHT = (10, 20, 44); GOLD = (244, 205, 120); STONE = (238, 228, 208); SHADE = (196, 182, 156); SEA = (30, 62, 104)


def lighthouse(S, bg=True, pad=0.0):
    """S px square. bg: full tile with sky; else transparent foreground (adaptive icon safe zone)."""
    k = 4; n = S * k
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if bg:
        for y in range(n):
            t = y / n; d.line([(0, y), (n, y)], fill=tuple(int(NIGHT[i] + (NAVY[i] - NIGHT[i]) * t * 1.4) if NIGHT[i] + (NAVY[i] - NIGHT[i]) * t * 1.4 < 255 else 255 for i in range(3)) + (255,))
    u = n * (1 - 2 * pad); ox = n * pad; oy = n * pad
    X = lambda v: ox + v * u; Y = lambda v: oy + v * u
    cx = 0.5
    # beams
    beam = Image.new('RGBA', (n, n), (0, 0, 0, 0)); bd = ImageDraw.Draw(beam)
    fy = 0.2
    bd.polygon([(X(cx), Y(fy)), (X(-0.1), Y(fy - 0.16)), (X(-0.1), Y(fy + 0.06))], fill=GOLD + (110,))
    bd.polygon([(X(cx), Y(fy)), (X(1.1), Y(fy - 0.16)), (X(1.1), Y(fy + 0.06))], fill=GOLD + (110,))
    beam = beam.filter(ImageFilter.GaussianBlur(n * 0.012)); im.alpha_composite(beam)
    glow = Image.new('RGBA', (n, n), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([X(cx - 0.11), Y(fy - 0.11), X(cx + 0.11), Y(fy + 0.11)], fill=GOLD + (150,)); glow = glow.filter(ImageFilter.GaussianBlur(n * 0.03)); im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    # sea and rock
    if bg: d.rectangle([0, Y(0.84), n, n], fill=SEA + (255,))
    for i, yy in enumerate((0.875, 0.915, 0.955)):
        for j in range(-1, 6):
            x0 = (j + (i % 2) * 0.5) * 0.2
            d.arc([X(x0), Y(yy - 0.02), X(x0 + 0.2), Y(yy + 0.02)], 200, 340, fill=(120, 160, 200, 255), width=max(2, int(u * 0.008)))
    d.polygon([(X(0.2), Y(0.86)), (X(0.3), Y(0.8)), (X(0.7), Y(0.8)), (X(0.8), Y(0.86))], fill=(92, 84, 78, 255))
    # tier 1: tall square tower, slightly tapered
    d.polygon([(X(0.335), Y(0.8)), (X(0.365), Y(0.46)), (X(0.635), Y(0.46)), (X(0.665), Y(0.8))], fill=STONE + (255,))
    d.polygon([(X(0.5), Y(0.8)), (X(0.5), Y(0.46)), (X(0.635), Y(0.46)), (X(0.665), Y(0.8))], fill=SHADE + (255,))
    d.rectangle([X(0.335), Y(0.445), X(0.665), Y(0.47)], fill=STONE + (255,))
    for yy in (0.54, 0.64):
        d.rectangle([X(0.42), Y(yy), X(0.45), Y(yy + 0.045)], fill=NAVY + (255,)); d.rectangle([X(0.55), Y(yy), X(0.58), Y(yy + 0.045)], fill=(60, 70, 100, 255))
    d.pieslice([X(0.465), Y(0.715), X(0.535), Y(0.785)], 180, 360, fill=NAVY + (255,)); d.rectangle([X(0.465), Y(0.75), X(0.535), Y(0.8)], fill=NAVY + (255,))
    # tier 2: octagonal
    d.polygon([(X(0.4), Y(0.445)), (X(0.42), Y(0.3)), (X(0.58), Y(0.3)), (X(0.6), Y(0.445))], fill=STONE + (255,))
    d.polygon([(X(0.5), Y(0.445)), (X(0.5), Y(0.3)), (X(0.58), Y(0.3)), (X(0.6), Y(0.445))], fill=SHADE + (255,))
    d.rectangle([X(0.4), Y(0.288), X(0.6), Y(0.308)], fill=STONE + (255,))
    # tier 3: round lantern with the fire
    d.rectangle([X(0.455), Y(0.235), X(0.545), Y(0.29)], fill=STONE + (255,)); d.rectangle([X(0.5), Y(0.235), X(0.545), Y(0.29)], fill=SHADE + (255,))
    d.rectangle([X(0.44), Y(0.222), X(0.56), Y(0.24)], fill=STONE + (255,))
    for xx in (0.45, 0.5, 0.55): d.line([(X(xx), Y(0.165)), (X(xx), Y(0.225))], fill=STONE + (255,), width=max(2, int(u * 0.012)))
    d.ellipse([X(0.468), Y(0.165), X(0.532), Y(0.228)], fill=(255, 236, 170, 255))
    d.polygon([(X(0.43), Y(0.168)), (X(0.5), Y(0.105)), (X(0.57), Y(0.168))], fill=STONE + (255,))
    d.ellipse([X(0.49), Y(0.085), X(0.51), Y(0.105)], fill=GOLD + (255,))
    # stars
    if bg:
        for sx, sy in ((0.14, 0.12), (0.84, 0.3), (0.2, 0.42), (0.78, 0.08), (0.9, 0.56), (0.1, 0.62)):
            d.ellipse([X(sx) - u * 0.006, Y(sy) - u * 0.006, X(sx) + u * 0.006, Y(sy) + u * 0.006], fill=(255, 255, 255, 220))
    return im.resize((S, S), Image.LANCZOS)


def tile(S, radius=0.22):
    im = lighthouse(S, bg=True, pad=0.06)
    m = Image.new('L', (S * 4, S * 4), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, S * 4 - 1, S * 4 - 1], radius=int(S * 4 * radius), fill=255)
    im.putalpha(m.resize((S, S), Image.LANCZOS)); return im


def main():
    d = os.path.join(ROOT, 'scrolls', 'alexandria'); base = os.path.join(d, 'android', 'base.apk'); tmp = base + '.tmp'
    tile(1024).save(os.path.join(d, 'icon.png'))
    with zipfile.ZipFile(base) as zb, zipfile.ZipFile(tmp, 'w') as zo:
        for info in zb.infolist():
            data = zb.read(info); m = re.match(r'res/mipmap-(\w+?)-v4/ic_launcher(_foreground)?\.png$', info.filename)
            if m:
                S = Image.open(io.BytesIO(data)).size[0]
                im = lighthouse(S, bg=False, pad=0.2) if m.group(2) else tile(S)
                b = io.BytesIO(); im.save(b, 'PNG'); data = b.getvalue()
            ni = zipfile.ZipInfo(info.filename, info.date_time); ni.compress_type = info.compress_type; ni.external_attr = info.external_attr
            zo.writestr(ni, data)
    shutil.move(tmp, base); print('lighthouse icons written')


if __name__ == '__main__':
    main()
