#!/usr/bin/env python3
"""Give the Book of Enoch (Charles) chapter.verse citations for chapters 1-36, and
build its Greek companion (the surviving Greek, Flemming & Radermacher 1901, via
Open Greek and Latin First1KGreek, CC BY-SA 4.0).
usage: enoch_versions.py SRC_EN_JS HENOCH_XML OUT_DIR"""
import sys, json, re, os, html
src, xml, out = sys.argv[1:4]
s = open(src).read(); i = s.index('['); j = s.rindex(',['); A = json.loads(s[i:j])
ch = 0; v = 0; E = []; done = False; firsts = {}
for x in A:
    x = dict(x); t = x['t']
    if not done and x.get('sp') == 'HDR' and 'Parables' in t: done = True
    if done or x.get('sp') == 'HDR' or re.match(r'^[IVXLC]+(-[IVXLC]+)?\. (\d|<i>)', t) or t.startswith('<i>('): E.append(x); continue
    m = re.match(r'^(\d{1,2})(?:<i>[a-z]\.</i>|[a-z])?\.? ', t)
    if t.startswith('Observe and see how (in the winter)'): ch, v = 3, 1
    elif t.startswith('And again, observe ye the days of summer'): ch, v = 4, 1
    elif m and int(m.group(1)) == 1 and not (ch == 0 and v > 0 and False): ch += 1 if ch not in (2, 3) else (5 - ch); v = 1
    elif m: v = int(m.group(1))
    if ch:
        st = f'{ch}.{v}'
        if st not in firsts: firsts[st] = 1; x['st'] = st
        if v == 1 and f'c{ch}' not in firsts: firsts[f'c{ch}'] = t[:46]
    E.append(x)
print('english chapters', ch, [(k, firsts[k]) for k in ('c6', 'c12', 'c17', 'c21', 'c33', 'c36') if k in firsts])
t = open(xml, encoding='utf-8').read()
a = t.index('<div type="edition"'); b = t.find('<div type="translation"', a); b = b if b > 0 else t.find('<div type="edition"', a + 10); body = t[a:b if b > 0 else len(t)]
G = [{'sp': 'HDR', 't': 'ΒΙΒΛΟΣ ΕΝΩΧ'}, {'sp': 'N', 't': '<i>The surviving Greek of chapters 1–32 (the Akhmim manuscript), with the later fragments where the edition gives them.</i>'}]
seen = set(); n = 0
for cm in re.finditer(r'<div type="textpart" subtype="chapter" n="([^"]+)">(.*?)(?=<div type="textpart" subtype="chapter"|\Z)', body, re.S):
    c = cm.group(1)
    for sm in re.finditer(r'<div type="textpart" subtype="section" n="([^"]+)">(.*?)</div>', cm.group(2), re.S):
        tx = sm.group(2); tx = re.sub(r'<note.*?</note>', '', tx, flags=re.S); tx = re.sub(r'<[^>]+>', ' ', tx); tx = re.sub(r'\s+', ' ', html.unescape(tx)).strip()
        tx = re.sub(r'(\w)- (\w)', r'\1\2', tx)
        if not tx or not re.search(r'[Ͱ-Ͽἀ-῿]', tx): continue
        st = f'{c}.{sm.group(1)}'; e = {'sp': 'N', 't': tx}
        if st not in seen: seen.add(st); e['st'] = st
        G.append(e); n += 1
print('greek sections', n, 'chapters', sorted({k.split('.')[0] for k in seen}, key=lambda z: int(re.sub(r'\D', '', z) or 0)))
est = {x['st'] for x in E if x.get('st')}; print('matched', len(seen & est), 'of', len(seen))
post = s[j:]
open(os.path.join(out, 'book-of-enoch.js'), 'w').write(s[:i] + json.dumps(E, ensure_ascii=False) + post)
open(os.path.join(out, 'book-of-enoch-b.js'), 'w').write(s[:i].replace('"book-of-enoch"', '"book-of-enoch-b"') + json.dumps(G, ensure_ascii=False) + post)
for x in G[2:6]: print(x.get('st'), x['t'][:150])
