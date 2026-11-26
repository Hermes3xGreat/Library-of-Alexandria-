#!/usr/bin/env python3
"""Draw a Scroll's mark in exactly the Plato Scroll style: the same flat tile,
translucent scroll, roller and bar, sizes and positions taken from Plato
Scroll's own pictures (engine/brand, made by make_brand_templates.py).
Only the colour, the symbol and the initials change.

usage: brand.py SCROLL_ID [--color '#9e2f23'] [--glyph 東] [--initials ES]

Writes: launcher icons in android/base.apk (adaptive foreground + legacy, and
the adaptive background colour), the start-screen logo (slots/hv-intro-css),
the favicon and the top-bar banner (text/), and icon.png (1024 px) for stores.
Settings are kept in scroll.json (color, glyph, initials).
"""
import os, re, io, json, base64, zipfile, argparse, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, 'engine', 'brand')
FONTS = os.path.join(BRAND, 'fonts')
# order matters: the first face that has every character is used
ORDER = ['InterDisplay-SemiBold.otf',   # closest match to Plato's Φ and ΠΣ
         'DejaVuSans.ttf',              # Greek, Hebrew, astrological and other symbols
         'FreeMono.ttf',                # runes (thin strokes, drawn thicker below)
         'FreeSerifBold.ttf',           # Coptic
         ]
SYSTEM_FONTS = ['/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc',   # Chinese / Japanese
                'C:/Windows/Fonts/msyhbd.ttc', 'C:/Windows/Fonts/YuGothB.ttc', '/System/Library/Fonts/PingFang.ttc',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                'C:/Windows/Fonts/seguisym.ttf', 'C:/Windows/Fonts/seguihis.ttf',
                '/System/Library/Fonts/Apple Symbols.ttf']
_cmaps = {}


def covers(path, text):
    if path not in _cmaps:
        try:
            f = TTFont(path, fontNumber=0, lazy=True); _cmaps[path] = set(f.getBestCmap() or {})
        except Exception:
            _cmaps[path] = set()
    return all(ord(c) in _cmaps[path] for c in text if not c.isspace())


def glyph_font(text):
    """the first bundled face (engine/brand/fonts, in ORDER) that has the characters,
    then any system face that does."""
    cands = [os.path.join(FONTS, f) for f in ORDER] + SYSTEM_FONTS
    for p in cands:
        if os.path.exists(p) and covers(p, text):
            return p
    print(f'  warning: no font here has {text!r}; put one in engine/brand/fonts and add it to ORDER')
    return os.path.join(FONTS, ORDER[1])


def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


THIN = ('FreeMono.ttf',)   # faces whose strokes are thickened to match Plato's Φ


def stroke_for(path, size):
    return max(1, round(size * .045)) if os.path.basename(path) in THIN else 0


def fit_text(draw, text, path, box_w, box_h):
    """font sized so the text's ink fits box_w x box_h (height first)."""
    size = max(4, int(box_h * 1.6))
    while size > 4:
        f = ImageFont.truetype(path, size)
        x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=f, stroke_width=stroke_for(path, size))
        if (y1 - y0) <= box_h and (x1 - x0) <= box_w:
            return f
        size -= max(1, size // 40)
    return ImageFont.truetype(path, 4)


def draw_centered(layer, text, path, box, alpha, max_w=None, scale=4):
    """white text, ink centred in box, drawn 4x and reduced for clean edges."""
    if not text:
        return
    x0, y0, x1, y1 = box
    bw, bh = (max_w or (x1 - x0 + 1)), (y1 - y0 + 1)
    W, H = layer.size
    big = Image.new('L', (W * scale, H * scale), 0)
    d = ImageDraw.Draw(big)
    f = fit_text(d, text, path, bw * scale, bh * scale)
    sw = stroke_for(path, f.size)
    ix0, iy0, ix1, iy1 = d.textbbox((0, 0), text, font=f, stroke_width=sw)
    cx, cy = (x0 + x1 + 1) / 2 * scale, (y0 + y1 + 1) / 2 * scale
    d.text((cx - (ix0 + ix1) / 2, cy - (iy0 + iy1) / 2), text, font=f, fill=int(255 * alpha),
           stroke_width=sw, stroke_fill=int(255 * alpha))
    small = big.resize((W, H), Image.LANCZOS)
    a = np.maximum(np.array(layer), np.array(small))
    layer.paste(Image.fromarray(a))


def widen(over, meta, f):
    """stretch the scroll (sheet, roller, cap, bar) sideways about its centre."""
    a = np.array(over)
    cols = np.where(a.max(axis=0) > 0)[0]
    x0, x1 = int(cols[0]), int(cols[-1]) + 1
    crop = over.crop((x0, 0, x1, over.height))
    nw = round((x1 - x0) * f)
    crop = crop.resize((nw, over.height), Image.LANCZOS)
    out = Image.new('L', over.size, 0)
    out.paste(crop, (round((x0 + x1) / 2 - nw / 2), 0))
    m = dict(meta)
    c = (x0 + x1) / 2
    sx = lambda x: round(c + (x - c) * f)
    m['sheet'] = [sx(meta['sheet'][0]), meta['sheet'][1], sx(meta['sheet'][2]), meta['sheet'][3]]
    return out, m


def render(name, color, glyph, initials, title=None, width=1.0):
    meta = json.load(open(os.path.join(BRAND, 'templates.json')))[name]
    over = Image.open(os.path.join(BRAND, f'{name}-overlay.png')).copy()
    tile = Image.open(os.path.join(BRAND, f'{name}-tile.png'))
    if width and abs(width - 1) > 0.01:
        over, meta = widen(over, meta, width)
    W, H = meta['size']
    sheet = meta['sheet']
    inner_w = sheet[2] - sheet[0] - 2 * max(2, (sheet[2] - sheet[0]) // 12)
    gb = meta['glyph']
    # a wider symbol (東, ☿…) may use the sheet's width; keep Plato's Φ height
    draw_centered(over, glyph, glyph_font(glyph), gb, 1.0, max_w=max(gb[2] - gb[0] + 1, inner_w))
    if initials and meta.get('initials'):
        ib = meta['initials']
        draw_centered(over, initials, glyph_font(initials), ib, .70, max_w=inner_w)
    if title and meta.get('title'):
        tb = meta['title']
        cinzel = os.path.join(FONTS, 'Cinzel-Bold.ttf')
        big = Image.new('L', (W, H), 0); d = ImageDraw.Draw(big)
        f = fit_text(d, title, cinzel, W - tb[0] - 50, tb[3] - tb[1] + 1)
        ix0, iy0, ix1, iy1 = d.textbbox((0, 0), title, font=f)
        d.text((tb[0] - ix0, (tb[1] + tb[3] + 1) / 2 - (iy0 + iy1) / 2), title, font=f, fill=255)
        over = Image.fromarray(np.maximum(np.array(over), np.array(big)))
    c = np.array(color, float)
    a = np.array(over, float)[..., None] / 255
    rgb = c * (1 - a) + 255 * a
    out = np.dstack([rgb, np.array(tile, float)]).round().clip(0, 255).astype('uint8')
    return Image.fromarray(out, 'RGBA')


def b64(im, fmt='PNG', **kw):
    buf = io.BytesIO(); im.save(buf, fmt, **kw); return base64.b64encode(buf.getvalue()).decode()


def png(im):
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True); return buf.getvalue()


def recolor_arsc(data, old, new):
    """swap typed colour values (#AARRGGBB) old -> new in resources.arsc."""
    o = struct.pack('<I', 0xff000000 | (old[0] << 16) | (old[1] << 8) | old[2])
    n = struct.pack('<I', 0xff000000 | (new[0] << 16) | (new[1] << 8) | new[2])
    b = bytearray(data); i = 0; hits = 0
    while True:
        i = b.find(o, i)
        if i < 0:
            break
        if i >= 4 and b[i - 4:i - 2] == b'\x08\x00' and b[i - 1] in (0x1c, 0x1d, 0x1e, 0x1f):
            b[i:i + 4] = n; hits += 1
        i += 4
    return bytes(b), hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scroll'); ap.add_argument('--color'); ap.add_argument('--glyph'); ap.add_argument('--initials'); ap.add_argument('--width', type=float)
    a = ap.parse_args()
    d = os.path.join(ROOT, 'scrolls', a.scroll)
    cp = os.path.join(d, 'scroll.json'); cfg = json.load(open(cp, encoding='utf-8'))
    old_color = cfg.get('icon_color') or cfg.get('color')
    if a.width: cfg['mark_width'] = a.width
    for k in ('color', 'glyph', 'initials'):
        if getattr(a, k) is not None:
            cfg[k] = getattr(a, k)
    color = hexrgb(cfg['color']); glyph = cfg.get('glyph') or cfg['name'][0]; ini = cfg.get('initials', '')
    wd = float(cfg.get('mark_width', 1.0))   # >1 makes the scroll wider than Plato's
    # pictures
    logo = render('logo180', color, glyph, ini, width=wd)
    banner = render('banner', color, glyph, '', title=cfg['name'].upper(), width=wd)
    os.makedirs(os.path.join(d, 'text'), exist_ok=True)
    open(os.path.join(d, 'text', 'favicon.txt'), 'w').write(b64(logo.resize((32, 32), Image.LANCZOS)))
    open(os.path.join(d, 'text', 'banner_image.txt'), 'w').write('png;base64,' + b64(banner.convert('RGB')))
    big = render('legacy192', color, glyph, ini, width=wd).resize((1024, 1024), Image.LANCZOS)
    big.save(os.path.join(d, 'icon.png'))
    cfg['text']['favicon'] = {'file': 'text/favicon.txt'}
    cfg['text']['banner_image'] = {'file': 'text/banner_image.txt'}
    cfg['text']['description_3'] = re.sub(r'#[0-9a-fA-F]{6}$', cfg['color'], cfg['text'].get('description_3', ''))
    sp = os.path.join(d, 'slots', 'hv-intro-css.html')
    css = open(sp, encoding='utf-8').read()
    css, n = re.subn(r'(\.hv-st-logo\{[^}]*?background:)#[0-9a-fA-F]{3,6} url\(data:image/\w+;base64,[A-Za-z0-9+/=]+\)',
                     lambda m: m.group(1) + cfg['color'] + ' url(data:image/png;base64,' + b64(logo) + ')', css, count=1)
    open(sp, 'w', encoding='utf-8').write(css)
    # Android launcher icons + adaptive background colour
    bp = os.path.join(d, 'android', 'base.apk')
    if os.path.exists(bp):
        scale = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
        fg = render('fg432', color, glyph, ini, width=wd); lg = render('legacy192', color, glyph, ini, width=wd)
        tmp = bp + '.tmp'; hits = 0
        with zipfile.ZipFile(bp) as zi, zipfile.ZipFile(tmp, 'w') as zo:
            for info in zi.infolist():
                data = zi.read(info)
                m = re.match(r'res/mipmap-(\w+?)-v4/ic_launcher(_foreground)?\.png$', info.filename)
                if m and m.group(1) in scale:
                    s = scale[m.group(1)]
                    data = png(fg.resize((round(108 * s),) * 2, Image.LANCZOS) if m.group(2)
                               else lg.resize((round(48 * s),) * 2, Image.LANCZOS))
                if info.filename == 'resources.arsc' and old_color and old_color.lower() != cfg['color'].lower():
                    data, hits = recolor_arsc(data, hexrgb(old_color), color)
                ni = zipfile.ZipInfo(info.filename, info.date_time)
                ni.compress_type = info.compress_type; ni.external_attr = info.external_attr
                zo.writestr(ni, data)
        os.replace(tmp, bp)
        cfg['icon_color'] = cfg['color']
    json.dump(cfg, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('branded', a.scroll, cfg['color'], glyph, ini)


if __name__ == '__main__':
    main()
