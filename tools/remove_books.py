#!/usr/bin/env python3
"""Take works out of a Scroll (every translation and original-text slot of each),
tidying its shelves. usage: remove_books.py SCROLL key [key ...]"""
import os, re, sys, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
base = lambda k: re.sub(r'-(b|c|e|gr)$', '', k)
def rd(sc, n):
    s = open(f'{ROOT}/scrolls/{sc}/slots/{n}').read(); i = s.index('>') + 1; j = s.rindex('</'); return s[:i], json.loads(s[i:j]), s[j:]
def wr(sc, n, h, o, t): open(f'{ROOT}/scrolls/{sc}/slots/{n}', 'w').write(h + json.dumps(o, ensure_ascii=False, separators=(',', ': ')) + t)
def remove(sc, keys):
    keys = set(keys); h, m, t = rd(sc, 'hermes-manifest.html')
    gone = [b['meta']['key'] for b in m['books'] if base(b['meta']['key']) in keys]
    m['books'] = [b for b in m['books'] if base(b['meta']['key']) not in keys]; wr(sc, 'hermes-manifest.html', h, m, t)
    for k in gone:
        for pre in ('', 'bd-', 'cx-'):
            p = f'{ROOT}/scrolls/{sc}/books/{pre}{k}.js'
            if os.path.lexists(p): os.remove(p)
    left = {b['meta'].get('author') for b in m['books']}
    h, a, t = rd(sc, 'hv-authors.html')
    for s in a['sections']: s['authors'] = [x for x in s['authors'] if x in left]
    a['sections'] = [s for s in a['sections'] if s['authors'] or s['name'] == 'Other']; wr(sc, 'hv-authors.html', h, a, t)
    names = {s['name'] for s in a['sections']}
    h, d, t = rd(sc, 'hv-section-decor.html'); wr(sc, 'hv-section-decor.html', h, {k: v for k, v in d.items() if k in names}, t)
    print(f'{sc}: removed {len(gone)} entries; {len(m["books"])} left; shelves: {[s["name"] for s in a["sections"] if s["authors"]]}')
if __name__ == '__main__':
    remove(sys.argv[1], sys.argv[2:])
