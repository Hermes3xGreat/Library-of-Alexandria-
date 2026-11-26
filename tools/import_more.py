#!/usr/bin/env python3
"""More books for the Egyptian and Northern Scrolls (Project Gutenberg).
Text only, as before: introductions, notes and note markers dropped."""
import re, sys, os
sys.argv = [sys.argv[0], sys.argv[1]]
OUTDIR = sys.argv[1]
import importlib.util
spec = importlib.util.spec_from_file_location('nm', os.path.join(os.path.dirname(__file__), 'nm_conv_lib.py'))
nm = importlib.util.module_from_spec(spec); spec.loader.exec_module(nm)
nm.SRC = '/tmp/more'; nm.OUT = OUTDIR
os.makedirs(OUTDIR, exist_ok=True)
L, idx, convert, write, UP = nm.L, nm.idx, nm.convert, nm.write, nm.UP
_clean = nm.clean
nm.clean = lambda t: _clean(re.sub(r'\[FN#\d+\]', '', t))
NOTE = r'^(\[FN#\d+\]|\[\d+\]\s)'

# Egyptian: Budge, Legends of the Gods (1912) — the translations (second half)
f = L('9411.txt'); a = idx(f, r'^THE HISTORY OF CREATION--A\.$'); b = idx(f, r'\*\*\* END OF THE PROJECT')
write('budge-legends-of-the-gods', convert(f[a:b], heading=UP, drop=NOTE))

# Northern
f = L('831.txt'); a = idx(f, r'^EREC ET ENIDE'); b = idx(f, r'\*\*\* END OF THE PROJECT')
ents = convert(f[a:b], heading=UP, drop=NOTE + r'|^Endnotes|^ENDNOTES')
for e in ents:
    m = re.match(r'^\(Vv\. ([\d\-]+)\.\)\s*(.*)$', e['t'], re.S)
    if m: e['st'] = m.group(1); e['t'] = m.group(2)
out = [{'sp': 'HDR', 't': 'Erec and Enide'}]
for e in ents:
    if e.get('st') == '1-44' and e['t'].startswith('He who wrote of Erec'):
        out.append({'sp': 'HDR', 't': 'Cligès'})
    out.append(e)
write('chretien-arthurian-romances', out)

f = L('14244.txt'); a = idx(f, r'^PART THE FIRST$', 70); b = idx(f, r'^THE END$')
write('tristan-and-iseult', convert(f[a:b], heading=UP))

f = L('11417.txt'); a = idx(f, r'^PROLOGUE$', 480); b = idx(f, r'\*\*\* END OF THE PROJECT')
write('marie-de-france-lays', convert(f[a:b], heading=UP, drop=NOTE))

f = L('657.txt'); a = idx(f, r'^THE ANGLO-SAXON CHRONICLE$', 700); b = idx(f, r'^ENDNOTES:$', a)
ents = convert(f[a + 1:b], heading=None, roman_st=False, drop=NOTE)
for e in ents:
    m = re.match(r'^A\.D\. ?(\d{1,4})\.\s*(.*)$', e['t'], re.S)
    if m: e['st'] = m.group(1); e['t'] = m.group(2) or e['t']
write('anglo-saxon-chronicle', ents)

f = L('38326.txt'); a = idx(f, r'^BOOK I$', 1300); b = idx(f, r'^INDEX$', a)
write('bede-ecclesiastical-history', convert(f[a:b], heading=UP, drop=NOTE))

f = L('1653.txt'); a = idx(f, r'^THE FIRST BOOK$'); b = idx(f, r'\*\*\* END OF THE PROJECT')
write('imitation-of-christ', convert(f[a:b], heading=UP))

f = L('52958.txt'); a = idx(f, r'^\s+REVELATIONS OF DIVINE LOVE\s*$', 1500); b = idx(f, r'\*\*\* END OF THE PROJECT')
write('julian-revelations', convert([x.strip() if x.strip() in ('REVELATIONS OF DIVINE LOVE',) or re.match(r'^\s+CHAPTER [IVXLC]+\s*$', x) else x for x in f[a:b]],
                                    heading=UP, drop=NOTE, roman_st=False))

for key, fn, start in (('parzival-1', '47297.txt', r'^BOOK I$'), ('parzival-2', '47298.txt', r'^BOOK X$')):
    f = L(fn); a = idx(f, start, 300 if key.endswith('1') else 80)
    b = idx(f, r'^APPENDIX A$|^NOTES$', a)
    write(key, convert(f[a:b], heading=UP, verse=True, drop=NOTE))
