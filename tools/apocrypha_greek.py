#!/usr/bin/env python3
"""Rebuild the King James Apocrypha with a heading per book and book-prefixed
citations (Tob 1:1), and build its Greek companion (apocrypha-kjv-b) from
Swete's Septuagint (Open Greek and Latin / nathans/lxx-swete, CC BY-SA 4.0).
usage: apocrypha_greek.py SRC_KJV_JS LXX_DATA_DIR OUT_DIR"""
import sys, json, re, os, collections
src, lxx, out = sys.argv[1:4]
s = open(src).read(); i = s.index('['); j = s.rindex(',['); A = json.loads(s[i:j])

def greek(fn):
    d = collections.OrderedDict()
    for ln in open(os.path.join(lxx, fn), encoding='utf-8'):
        p = ln.rstrip('\n').split(' ', 1)
        if len(p) < 2: continue
        _, c, v = p[0].split('.', 2); d.setdefault((c, v), []).append(p[1])
    return collections.OrderedDict((k, ' '.join(w)) for k, w in d.items())

# (start index marker text, abbreviation, English title, Greek title, Greek file, map (c,v)->st or None)
std = lambda c, v: f'{c}:{v}'
BOOKS = [
 ('The First Book of Esdras', '1 Esd', 'The First Book of Esdras', 'ΕΣΔΡΑΣ Αʹ', '17.Esdras_A.txt', std),
 ('The Second Book of Esdras', '2 Esd', 'The Second Book of Esdras', None, None, None),
 ('The Book of Tobit', 'Tob', 'The Book of Tobit', 'ΤΩΒΕΙΤ', '21.Tobias.txt', std),
 ('The Book of Judith', 'Jdt', 'The Book of Judith', 'ΙΟΥΔΕΙΘ', '20.Judith.txt', std),
 ('The Greek Additions to Esther', 'Add Esth', 'The Rest of the Chapters of the Book of Esther', None, None, None),
 ('The Book of Wisdom', 'Wis', 'The Wisdom of Solomon', 'ΣΟΦΙΑ ΣΑΛΩΜΩΝΟΣ', '33.Sapientia_Salomonis.txt', std),
 ('The Book of Sirach', 'Sir', 'The Wisdom of Jesus the Son of Sirach, or Ecclesiasticus', 'ΣΟΦΙΑ ΣΕΙΡΑΧ', '34.Ecclesiasticus.txt', std),
 ('The Book of Baruch', 'Bar', 'The Book of Baruch', 'ΒΑΡΟΥΧ', '50.Baruch.txt', std),
 ('The Epistle [or Letter] of Jeremiah', 'Ep Jer', 'The Epistle of Jeremy', 'ΕΠΙΣΤΟΛΗ ΙΕΡΕΜΙΟΥ', '52.Epistula_Jeremiae.txt', lambda c, v: f'6:{int(v) + 1}' if v.isdigit() else None),
 ('The Song of the Three Holy Children', 'S3Y', 'The Song of the Three Holy Children', 'ΠΡΟΣΕΥΧΗ ΑΖΑΡΙΟΥ ΚΑΙ ΥΜΝΟΣ ΤΩΝ ΤΡΙΩΝ', '57.Daniel_Theodotionis_versio.txt', lambda c, v: str(int(v) - 23) if c == '3' and v.isdigit() and 24 <= int(v) <= 91 else None),
 ('The Book of Susanna', 'Sus', 'The History of Susanna', 'ΣΟΥΣΑΝΝΑ', '55.Susanna_Theodotionis_versio.txt', std),
 ('The History of the Destruction of', 'Bel', 'Bel and the Dragon', 'ΒΗΛ ΚΑΙ ΔΡΑΚΩΝ', '59.Bel_et_Draco_Theodotionis_versio.txt', std),
 ('The Prayer of Manasses', 'Pr Man', 'The Prayer of Manasses', 'ΠΡΟΣΕΥΧΗ ΜΑΝΑΣΣΗ', '28.Odae.txt', lambda c, v: 'all' if c == '8' else None),
 ('The First Book of the Maccabees', '1 Macc', 'The First Book of the Maccabees', 'ΜΑΚΚΑΒΑΙΩΝ Αʹ', '23.Machabaeorum_i.txt', std),
 ('The Second Book of the Maccabees', '2 Macc', 'The Second Book of the Maccabees', 'ΜΑΚΚΑΒΑΙΩΝ Βʹ', '24.Machabaeorum_ii.txt', std),
]
starts = []
for mark, *_ in BOOKS:
    k = next(n for n, x in enumerate(A) if x['t'].startswith(mark) and (not starts or n > starts[-1]))
    starts.append(k)
E, G = [], []; rep = []
for bi, (mark, ab, title, gt, gf, mp) in enumerate(BOOKS):
    seg = A[starts[bi] + 1:starts[bi + 1] if bi + 1 < len(BOOKS) else len(A)]
    E.append({'sp': 'HDR', 't': title}); est = []
    for x in seg:
        x = dict(x); t = x['t']
        if ab == 'S3Y':
            m = re.match(r'^(\d{1,2}) (.*)$', t, re.S)
            if m: x['t'] = m.group(2); x['st'] = m.group(1)
        if ab == 'Pr Man' and not x.get('st'): x['st'] = 'all'
        if x.get('sp') == 'HDR': x['sp'] = 'N'
        if x.get('st'):
            x['st'] = f"{ab} {x['st']}" if x['st'] != 'all' else ab; est.append(x['st'])
        E.append(x)
    if not gf:
        G.append({'sp': 'HDR', 't': title}); G.append({'sp': 'N', 't': '<i>No Greek text of this book is included.' + (' The Second Book of Esdras survives in Latin, not in Greek.' if ab == '2 Esd' else ' In the Greek Bible these chapters are woven through the Book of Esther.') + '</i>'})
        rep.append((ab, len(est), 0, 0)); continue
    g = greek(gf); G.append({'sp': 'HDR', 't': gt}); n = hit = 0; pm = []
    for (c, v), t in g.items():
        st = mp(c, v)
        if ab == 'Sir' and c == '0': G.append({'sp': 'N', 't': t}); continue
        if st is None:
            if ab in ('S3Y', 'Pr Man'): continue
            st = f'{c}:{v}'
        if st == 'all': pm.append(t); continue
        full = f'{ab} {st}'; n += 1; hit += full in est
        G.append({'sp': 'N', 'st': full, 't': t})
    if pm: G.append({'sp': 'N', 'st': ab, 't': ' '.join(pm)}); n = hit = 1
    rep.append((ab, len(est), n, hit))
post = s[j:]
open(os.path.join(out, 'apocrypha-kjv.js'), 'w').write(s[:i] + json.dumps(E, ensure_ascii=False) + post)
open(os.path.join(out, 'apocrypha-kjv-b.js'), 'w').write(s[:i].replace('"apocrypha-kjv"', '"apocrypha-kjv-b"') + json.dumps(G, ensure_ascii=False) + post)
for r in rep: print('%-9s english %4d  greek %4d  matched %4d' % r)
print(len(E), len(G))
