#!/usr/bin/env python3
"""Cover pictures for a Scroll's authors and works.

Put pictures in scrolls/<id>/covers/authors/<Author Name>.jpg and
scrolls/<id>/covers/works/<book-key>.jpg (any size; credits in
covers/credits.json), then run:  covers.py SCROLL_ID
Each picture becomes a 300×438 JPEG (the size of the Plato Scroll busts) and
is written into the Scroll's "covers" text, which adds them to the reader's
BUSTS_BY_AUTHOR / WORK_COVERS maps. Wide or tall objects are fitted on a
background of their own edge colour rather than cropped.
"""
import os, io, sys, json, base64, re
from PIL import Image, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 300, 438


def fit(im):
    im = im.convert('RGB')
    r, R = im.width / im.height, W / H
    if abs(r - R) / R < 0.18:                     # close to portrait: fill and crop
        s = max(W / im.width, H / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (im.width - W) // 2, (im.height - H) // 2
        return im.crop((x, y, x + W, y + H))
    edge = Image.new('RGB', (im.width, 4)); edge.paste(im.crop((0, 0, im.width, 4)))
    border = [im.crop((0, 0, im.width, 3)), im.crop((0, im.height - 3, im.width, im.height)),
              im.crop((0, 0, 3, im.height)), im.crop((im.width - 3, 0, im.width, im.height))]
    col = tuple(int(sum(ImageStat.Stat(b).mean[k] for b in border) / 4) for k in range(3))
    s = min(W * .94 / im.width, H * .94 / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    bg = Image.new('RGB', (W, H), col)
    bg.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return bg


def b64(im):
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=84, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def main():
    sid = sys.argv[1]
    d = os.path.join(ROOT, 'scrolls', sid)
    cp = os.path.join(d, 'scroll.json'); cfg = json.load(open(cp, encoding='utf-8'))
    var = 'SC_COVERS_' + re.sub(r'\W', '_', sid).upper()
    imgs, authors, works = {}, {}, {}
    for kind, target in (('authors', authors), ('works', works)):
        folder = os.path.join(d, 'covers', kind)
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            name, ext = os.path.splitext(f)
            if ext.lower() not in ('.jpg', '.jpeg', '.png', '.webp'):
                continue
            k = f'{kind[0]}{len(imgs)}'
            imgs[k] = b64(fit(Image.open(os.path.join(folder, f))))
            target[name] = k
    js = 'window.' + var + '=' + json.dumps(imgs) + ';try{'
    js += 'Object.assign(BUSTS_BY_AUTHOR,{' + ','.join(f'{json.dumps(a, ensure_ascii=False)}:{var}[{json.dumps(k)}]' for a, k in authors.items()) + '});'
    js += 'Object.assign(WORK_COVERS,{' + ','.join(f'{json.dumps(w)}:{var}[{json.dumps(k)}]' for w, k in works.items()) + '})}catch(e){};'
    os.makedirs(os.path.join(d, 'text'), exist_ok=True)
    open(os.path.join(d, 'text', 'covers.txt'), 'w', encoding='utf-8').write(js if imgs else '')
    cfg['text']['covers'] = {'file': 'text/covers.txt'}
    json.dump(cfg, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(sid, len(authors), 'authors,', len(works), 'works,', round(len(js) / 1024), 'KB')


if __name__ == '__main__':
    main()
