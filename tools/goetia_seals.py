#!/usr/bin/env python3
"""The Goetia's seals and figures. The printed edition gives the 72 seals on three
grid plates; this cuts each seal out and sets it under its own spirit, and puts
the plates of the circle, the Hebrew names and the magical requisites at the
sections that describe them. usage: goetia_seals.py [IMAGE_DIR]"""
import os, re, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import add_illustrations as A
D = sys.argv[1] if len(sys.argv) > 1 else '/tmp/oi/img/72679'
P = os.path.join(A.ROOT, 'scrolls', 'northern', 'books', 'goetia-lesser-key-of-solomon.js')


def bbox(im):
    g = np.asarray(im.convert('L')).astype(int); dark = g < 120
    rows = np.where(dark.sum(axis=1) > 0.12 * g.shape[1])[0]; cols = np.where(dark.sum(axis=0) > 0.12 * g.shape[0])[0]
    return int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())


NUM = {3: lambda r, c: 4 * r + c + 1, 4: lambda r, c: 25 + 8 * r + c, 5: lambda r, c: 29 + 8 * r + c}
seals = {}
for n in (3, 4, 5):
    im = Image.open(os.path.join(D, f'front-{n}.jpg')).convert('RGB'); x0, y0, x1, y1 = bbox(im); cw = (x1 - x0) / 4; ch = (y1 - y0) / 6
    for r in range(6):
        for c in range(4):
            cell = im.crop((int(x0 + c * cw + 3), int(y0 + r * ch + 3), int(x0 + (c + 1) * cw - 2), int(y0 + (r + 1) * ch - 2)))
            seals[NUM[n](r, c)] = cell.resize((cell.width * 2, cell.height * 2), Image.LANCZOS)
pre, a, post = A.load(P); a = A.strip(a); out = []; done = 0
PL = {'Shemhamphorash': (2, 'The names of the seventy-two spirits in Hebrew, after Dr. Rudd'),
      'The Magical Circle': (1, 'The Magical Circle and the Magical Triangle of Solomon (Figures 153 and 154)'),
      'The Hexagram of Solomon': (6, 'The Hexagram, the Pentagram, the Ring, the Vessel of Brass and the other requisites (Figures 155–174), with seals 73–80'),
      'The Secret Seal of Solomon': (7, 'The Secret Seal of Solomon and the further figures (Figures 160–176)')}
inlist = False
for i, x in enumerate(a):
    out.append(x); t = x.get('t', '')
    if x.get('sp') == 'HDR': inlist = (t == 'Shemhamphorash')
    m = re.match(r'^\((\d+)\.?\) ?([^.—]+?)\s*[.—]', t)
    if m and int(m.group(1)) in seals and inlist:
        k = int(m.group(1)); b64, size = A.webp(seals[k], 400, q=70); out.append(A.figure(b64, size, f'The Seal of {re.split(r',| or ', m.group(2))[0].strip().title()}')); done += 1
    if x.get('sp') == 'HDR' and t in PL:
        n, cap = PL[t]; b64, size = A.webp(Image.open(os.path.join(D, f'front-{n}.jpg')), 1000, q=62); out.append(A.figure(b64, size, cap))
open(P, 'w', encoding='utf-8').write(pre + json.dumps(out, ensure_ascii=False) + post)
print('seals placed', done, 'plates', sum(1 for x in out if A.MARK in x['t']) - done, 'size', os.path.getsize(P) // 1024, 'KB')
