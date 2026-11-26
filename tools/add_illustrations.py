#!/usr/bin/env python3
"""Put a book's illustrations back into its text.

Reads the illustrated (HTML) Project Gutenberg edition, takes every real picture
(not covers, ornaments, drop capitals or tiny inline glyphs), shrinks it to WebP,
and inserts it into the Scroll's book after the paragraph it follows in the
source. Safe to run again: earlier pictures are removed first.

usage: add_illustrations.py --all            (every book listed in illustrations.json)
       add_illustrations.py SCROLL KEY PGID [--html DIR] [--min 110] [--max 900] [--strict] [--aspect 4.2] [--no-front]
--strict drops a picture whose place cannot be found (use when one source file holds two books).
"""
import os, re, sys, io, json, base64, html, subprocess
from html.parser import HTMLParser
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
MIRROR = 'https://gutenberg.pglaf.org/cache/epub'
MARK = 'class="hv-fig"'
norm = lambda t: re.sub(r'[^a-z0-9]+', '', re.sub(r'<[^>]+>', ' ', html.unescape(t)).lower())


def load(p):
    s = open(p, encoding='utf-8').read(); i = s.index('['); j = s.rindex(',[')
    return s[:i], json.loads(s[i:j]), s[j:]


class Stream(HTMLParser):
    BLOCK = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'td', 'li', 'blockquote', 'figcaption', 'tr', 'table', 'br', 'hr'}
    def __init__(self):
        super().__init__(convert_charrefs=True); self.items = []; self.buf = []; self.skip = 0
    def flush(self):
        t = re.sub(r'\s+', ' ', ''.join(self.buf)).strip(); self.buf = []
        if t: self.items.append(('t', t))
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'): self.skip += 1
        if tag in self.BLOCK: self.flush()
        if tag == 'img': self.flush(); self.items.append(('i', a))
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
        if tag in self.BLOCK: self.flush()
    def handle_data(self, d):
        if not self.skip: self.buf.append(d)


def fetch(pg, src, cache):
    f = os.path.join(cache, str(pg), os.path.basename(src)); os.makedirs(os.path.dirname(f), exist_ok=True)
    if not (os.path.exists(f) and os.path.getsize(f) > 200):
        subprocess.run(['curl', '-s', '--max-time', '120', '-o', f, f'{MIRROR}/{pg}/{src}'], check=False)
    return f


def webp(im, mx, q=58):
    im = im.convert('RGB')
    if max(im.size) > mx: im.thumbnail((mx, mx), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6); return base64.b64encode(b.getvalue()).decode(), im.size


def figure(b64, size, cap=''):
    cap = html.escape(cap.strip())
    return {'sp': 'N', 't': f'<img {MARK} alt="{cap}" width="{size[0]}" height="{size[1]}" style="display:block;max-width:100%;height:auto;margin:.7em auto;background:#fff;border-radius:4px" src="data:image/webp;base64,{b64}">' + (f'<br><i>{cap}</i>' if cap else '')}


def strip(a): return [x for x in a if MARK not in x.get('t', '')]


def run(scroll, key, pg, cache, mn=110, mx=900, verbose=True, fallback=True, aspect=4.2, frontis=True):
    hp = os.path.join(cache, f'{pg}.html')
    if not os.path.exists(hp): subprocess.run(['curl', '-s', '--max-time', '240', '-o', hp, f'{MIRROR}/{pg}/pg{pg}-images.html'], check=False)
    st = Stream(); st.feed(open(hp, encoding='utf-8', errors='replace').read()); st.flush()
    p = os.path.join(ROOT, 'scrolls', scroll, 'books', key + '.js'); pre, a, post = load(p); a = strip(a)
    N = [norm(x.get('t', '')) for x in a]
    ins = []; ptr = 0; last = ''; stats = dict(seen=0, small=0, placed=0, lost=0); kb = 0
    its = st.items; import collections
    uses = collections.Counter(v.get('src', '') for k, v in its if k == 'i'); front = 0
    for n, (k, v) in enumerate(its):
        if k == 't':
            if len(v) >= 25: last = v
            continue
        src = v.get('src', ''); alt = (v.get('alt') or '').strip(); stats['seen'] += 1
        if uses[src] > 1: stats['small'] += 1; continue          # a repeated picture is a printer's ornament
        if not src or 'cover' in src.lower() or re.search(r'(?i)ornament|decorat|drop.?cap|logo|publisher|colophon|tailpiece|headpiece', alt) or re.fullmatch(r'[A-Z“"‘\']{1,2}', alt): stats['small'] += 1; continue
        try: w = int(float(v.get('width') or 0)); h = int(float(v.get('height') or 0))
        except ValueError: w = h = 0
        if w and h and min(w, h) < mn * 0.6: stats['small'] += 1; continue
        try: im = Image.open(fetch(pg, src, cache)); im.load()
        except Exception: stats['lost'] += 1; continue
        if min(im.size) < mn or max(im.size) / min(im.size) > aspect: stats['small'] += 1; continue   # too small, or a rule/strip
        cap = alt if alt and not re.fullmatch(r'(?i)figures?|illustration|image|\[?illustration\]?|.*\.(jpg|png|gif)', alt) else ''
        if not cap:                                   # a short line right after the picture is its caption
            nx = next((t for kk, t in its[n + 1:n + 2] if kk == 't'), '')
            if nx and len(nx) < 140 and not nx.endswith(','): cap = nx
        key40 = norm(last)[:40]; tail40 = norm(last)[-40:]; at = None
        if key40:
            for i in list(range(ptr, len(N))) + list(range(0, ptr)):
                if key40 in N[i] or (len(tail40) == 40 and tail40 in N[i]): at = i; break
        if at is None:
            if not fallback: stats['lost'] += 1; continue
            if ptr == 0:                              # before the book's first matched place: keep one frontispiece only
                if front or not frontis or min(im.size) < 300: stats['lost'] += 1; continue
                front = 1
            at = ptr                                  # no anchor: keep it next to the picture before it
        ptr = at; b64, size = webp(im, mx); kb += len(b64) * 3 // 4 // 1024
        ins.append((at, figure(b64, size, cap))); stats['placed'] += 1
    out = []; byi = {}
    for at, f in ins: byi.setdefault(at, []).append(f)
    for i, x in enumerate(a):
        out.append(x); out += byi.get(i, [])
    open(p, 'w', encoding='utf-8').write(pre + json.dumps(out, ensure_ascii=False) + post)
    if verbose: print(f'{scroll}/{key}: {stats}, {kb} KB')
    return stats, kb


if __name__ == '__main__':
    opt = lambda n, d: (sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d)
    if '--all' in sys.argv:
        for key, c in json.load(open(os.path.join(HERE, 'illustrations.json'))).items():
            run(c['scroll'], key, c['pg'], opt('--html', '/tmp/oi'), c.get('min', 110), c.get('max', 900), fallback=not c.get('strict'), aspect=c.get('aspect', 4.2), frontis=not (c.get('strict') or c.get('no_front')))
        sys.exit()
    args = [x for x in sys.argv[1:] if not x.startswith('--') and not (sys.argv[sys.argv.index(x) - 1] in ('--html', '--min', '--max', '--aspect'))]
    run(args[0], args[1], args[2], opt('--html', '/tmp/oi'), int(opt('--min', 110)), int(opt('--max', 900)), fallback='--strict' not in sys.argv, aspect=float(opt('--aspect', 4.2)), frontis='--no-front' not in sys.argv)
