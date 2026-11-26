#!/usr/bin/env python3
"""Book files for Masonic works for the Liberty and Northern Scrolls from Project Gutenberg texts (text only)."""
import re, sys, os, importlib.util
OUTDIR = sys.argv[1]
spec = importlib.util.spec_from_file_location('nm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nm_conv_lib.py'))
nm = importlib.util.module_from_spec(spec); spec.loader.exec_module(nm)
nm.SRC = '/tmp/fm'; nm.OUT = OUTDIR; os.makedirs(OUTDIR, exist_ok=True)
L0, idx, convert, write, UP = nm.L, nm.idx, nm.convert, nm.write, nm.UP
L = lambda f: [x.strip() for x in L0(f)]
_clean = nm.clean
nm.clean = lambda t: _clean(re.sub(r'\[Footnote[^\]]*\]\s?|\[(\d{1,3}|[A-Z\*][a-z]?)\]|\[Illustration[^\]]*\]|\(\d{1,3}\)(?=[\s,.;:]|$)' if False else r'\[Footnote[^\]]*\]\s?|\[(\d{1,3}|[A-Z\*][a-z]?)\]|\[Illustration[^\]]*\]', '', t))
NOTE = r'^(\[\d+\]\s|\[Footnote|Footnote \d|FOOTNOTES?:?$|\[Illustration)'
END = r'\*\*\* END OF THE PROJECT'


def go(key, fn, start, end, nth=1, lines=None, **kw):
    f = lines or L(fn)
    try: a = idx(f, start, nth=nth); b = idx(f, end, a + 1)
    except SystemExit as e: print('FAIL', key, e); return
    kw.setdefault('heading', UP); kw.setdefault('drop', NOTE)
    e = convert(f[a:b], **kw); write(key, e)
    print(f'{key}: {len(e)} entries, {sum(1 for x in e if x["sp"] == "HDR")} headings | ', [x['t'][:40] for x in e if x['sp'] == 'HDR'][:5])



C = r'[A-Z][A-Z ,\'’\-:;&]{5,}\.?'
FN = [(r'^FOOTNOTES:$', r'^(CHAPTER [IVXL]+\.?|BOOK [IVX]+|PART [IVX]+.*|Part [IVX]+--.*|BIBLIOGRAPHY|INDEX)$')]
# Liberty
go('pike-morals-and-dogma', '19447.txt', r'^I\.$', r'^DIGEST--INDEX$', heading=r'([IVXL]+\.|' + C + ')')
go('mackey-symbolism-of-freemasonry', '11937.txt', r'^I\.$', r'^Synoptical Index\.$', nth=1, heading=r'([IVXL]+\.|[A-Z][A-Za-z ,\'’\-:;]{3,60}\.)', roman_st=False)
go('mackey-principles-of-masonic-law', '12186.txt', r'^Introduction\.$', r'^Index\.$', nth=1, heading=r'(Introduction\.|Book (First|Second|Third|Fourth)\.?|Chapter [IVXL]+\.|Section [IVXL]+\.)')
go('newton-the-builders', '19049.txt', r'^THE ANTEROOM$', r'^BIBLIOGRAPHY$', nth=1, skip=[(r'^TABLE OF CONTENTS$', r'^Part I--Prophecy$')] + FN, heading=r'(Part [IVX]+--.*|CHAPTER [IVXL]+|' + C + ')')
go('thornburgh-masonic-monitor', '30118.txt', r'^ENTERED APPRENTICE\.$', END, heading=C)
go('washington-masonic-correspondence', '29949.txt', r'^FOREWORD$', r'^INDEX\.$', heading=r'(FOREWORD|[IVXL]+\.|' + C + ')')
# Northern
SC = L('42072.txt'); a_ = SC.index('CONTENTS'); b_ = [i for i, x in enumerate(SC) if x == 'BOOK I'][-1]; SC = SC[:a_] + SC[b_:]
go('scott-cathedral-builders', '42072.txt', r'^PROEM$', r'^INDEX$', nth=1, lines=SC, skip=[(r'^FOOTNOTES?:$', r'^(CHAPTER [IVXL]+\.?|BOOK [IVX]+|INDEX)$')], heading=r'(PROEM|BOOK [IVX]+|CHAPTER [IVXL]+|' + C + ')')
go('addison-knights-templars', '38593.txt', r'^CHAPTER I\.$', r'^FOOTNOTES:$', nth=2, heading=r'(CHAPTER [IVXL]+\.|' + C + ')')
go('mysteries-of-the-rosie-cross', '35350.txt', r'^CHAPTER I\.$', r'^THE END\.$', heading=r'(CHAPTER [IVXL]+\.|' + C + ')')
