#!/usr/bin/env python3
"""Gentle reading polish for curated texts (the Eastern library and works that
came from Plato Scroll): typography only, plus splitting very long paragraphs
where no parallel text depends on the paragraphing. Nothing is removed and
citations are kept. usage: polish_safe.py [--write] [--soft] SCROLL [SCROLL ...]
--soft is for the Plato and Pantheon libraries, where notes, breakdowns and links
point at paragraphs by number: wording and paragraph count are left exactly as
they are, and a very long paragraph only gets blank-line breaks inside it."""
import os, re, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); _argv = sys.argv[:]; sys.argv = ['x']; sys.path.insert(0, HERE)
import polish as P
stem = lambda k: re.sub(r'-(b|c|d|e|gr|calthrop|chalmers)$', '', k)
def inline(t):
    t = re.sub(r'(?<![A-Za-z0-9])_([^_<>]{1,300}?)_(?![A-Za-z0-9])', r'<i>\1</i>', t)
    t = re.sub(r'(?<=[A-Za-z,;:.!?’”])\s*--\s*(?=[A-Za-z“‘"\'])', '—', t); t = re.sub(r'(?<=[A-Za-z,;:.!?’”])--(?=\s|$)', '—', t)
    t = P.quotes(t); t = re.sub(r'(?<=\S) {2,}(?=\S)', ' ', t)
    return t
def run(sc, write, soft=False):
    d = os.path.join(P.R, sc, 'books'); files = sorted(f for f in os.listdir(d) if f.endswith('.js') and not re.match(r'(bd|cx)-', f))
    stems = collections.Counter(stem(f[:-3]) for f in files); tot = collections.Counter()
    for f in files:
        k = f[:-3]
        if k in P.MINE: continue
        p = os.path.join(d, f)
        try: pre, a, post = P.load(p)
        except Exception as e: print('  skip', k, e); continue
        original = bool(re.search(r'-(b|gr)$', k)); paired = stems[stem(k)] > 1
        out = []; ch = sp = 0
        for x in a:
            if not isinstance(x.get('t'), str) or P.H(x) or x.get('sp') == 'SEC': out.append(x); continue
            if not original and not soft:
                t = inline(x['t'])
                if t != x['t']: x = dict(x, t=t); ch += 1
            plain = x.get('sp') in (None, 'N')
            if (soft or not paired) and not original and plain and len(x['t']) > 1700 and '<br>' not in x['t'] and '<span' not in x['t'] and '<em' not in x['t'] and '<a ' not in x['t']:
                parts = P.split_wall(x, limit=1700, target=1000)
                if len(parts) > 1: sp += 1
                if soft: out.append(dict(x, t='<br><br>'.join(q['t'] for q in parts)) if len(parts) > 1 else x)
                else: out += parts
            else: out.append(x)
        tot['books'] += 1; tot['changed'] += ch; tot['split'] += sp
        if (ch or sp) and write:
            if os.path.islink(p): os.unlink(p)          # a link to the Plato source: write a private copy, never the source
            open(p, 'w', encoding='utf-8').write(pre + json.dumps(out, ensure_ascii=False) + post)
        if sp > 40 or ch > 800: print(f'  {sc}/{k}: typography {ch}, long paragraphs split {sp}, entries {len(a)}->{len(out)}')
    print(sc, dict(tot))
if __name__ == '__main__':
    for sc in [x for x in _argv[1:] if not x.startswith('--')]: run(sc, '--write' in _argv, '--soft' in _argv)
