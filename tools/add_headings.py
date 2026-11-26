#!/usr/bin/env python3
"""Section headings and citation numbers for long books that had neither
between chapters. Safe to run twice. usage: add_headings.py [--write]"""
import os, re, sys, json
sys.argv_keep = sys.argv[:]; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import polish as P
H = P.H
ROM = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
def roman(s):
    n = 0
    for i, c in enumerate(s): n += -ROM[c] if i + 1 < len(s) and ROM[c] < ROM[s[i + 1]] else ROM[c]
    return n
def mark_hdr(pat, label, strip=True):
    def f(a):
        out = []
        for x in a:
            m = None if H(x) else re.match(pat, x['t'])
            if m:
                out.append({'sp': 'HDR', 't': label(m)}); x = dict(x)
                if strip: x['t'] = x['t'][m.end():].lstrip()
                if x['t']: out.append(x)
            else: out.append(x)
        return out
    return f
def title_lines(maxlen=70, need_next=200):
    def f(a):
        out = []
        for i, x in enumerate(a):
            t = re.sub(r'<[^>]+>', '', x['t']); nxt = a[i + 1] if i + 1 < len(a) else None
            words = re.findall(r"[A-Za-zÀ-ÿ’']+", t)
            if (not H(x) and not x.get('st') and 3 < len(t) < maxlen and not re.search(r'[.,;:!?”’"—]$', t) and '<br>' not in x['t'] and words
                    and sum(1 for w in words if w[0].isupper() or len(w) < 4) >= len(words) * 0.75 and nxt is not None and not H(nxt) and len(nxt['t']) >= need_next):
                out.append({'sp': 'HDR', 't': t})
            else: out.append(x)
        return out
    return f
def bacon(a):
    book = 0; out = []
    for x in a:
        if H(x): book += 1; out.append(x); continue
        m = re.match(r'^([IVXLC]{1,8})\. (?=[A-Z“])', x['t'])
        if m and not x.get('st'): x = dict(x, st=f'{max(book, 1)}.{roman(m.group(1))}', t=x['t'][m.end():])
        out.append(x)
    return out
def pascal(a):
    out = []; pend = None
    for x in a:
        if not H(x) and re.fullmatch(r'\d{1,3}', x['t']): pend = x['t']; continue
        if pend and not H(x): x = dict(x, st=pend); pend = None
        out.append(x)
    return out
def bede(a):
    out = []
    for x in a:
        m = None if H(x) else re.match(r'^Chap\. ([IVXL]+)\. ', x['t'])
        if m and len(x['t']) < 420: out.append({'sp': 'HDR', 't': 'Chapter ' + m.group(1)}); out.append({'sp': 'N', 't': '<i>' + re.sub(r'</?i>', '', x['t'][m.end():]) + '</i>'})
        else: out.append(x)
    return out
RULES = {
    'schopenhauer-world-as-will-1': mark_hdr(r'^§ ?(\d+)\.\s*', lambda m: '§ ' + m.group(1)),
    'bacon-novum-organum': bacon, 'pascal-pensees': pascal, 'bede-ecclesiastical-history': bede,
    'book-of-enoch': mark_hdr(r'^\[([IVXLC]+)\]\s*', lambda m: 'Chapter ' + m.group(1)),
    'rumi-mesnevi': lambda a: [({'sp': 'HDR', 't': ((x.get('st') + '. ') if x.get('st') else '') + x['t'].rstrip('.').replace('PROEM. ', 'Proem — ')} if (not H(x) and '<br>' not in x['t'] and len(x['t']) < 70) else x) for x in a],
    'spence-myths-mexico-peru': title_lines(70, 150), 'arabian-nights': title_lines(60, 200),
    'hebraic-literature': title_lines(50, 300), 'james-varieties': lambda a: a,
}
def main():
    write = '--write' in sys.argv_keep
    for sc in P.SCROLLS:
        d = os.path.join(P.R, sc, 'books')
        for f in sorted(os.listdir(d)):
            k = f[:-3]
            if k not in RULES: continue
            pre, a, post = P.load(os.path.join(d, f)); b = RULES[k]([dict(x) for x in a])
            h0 = sum(H(x) for x in a); h1 = sum(H(x) for x in b); s0 = sum(1 for x in a if x.get('st')); s1 = sum(1 for x in b if x.get('st'))
            print(f'{sc}/{k}: headings {h0}->{h1}, citations {s0}->{s1}', [x['t'][:28] for x in b if H(x) and x not in a][:5])
            if write: open(os.path.join(d, f), 'w', encoding='utf-8').write(pre + json.dumps(b, ensure_ascii=False) + post)
if __name__ == '__main__':
    sys.argv = ['x']; main()
