#!/usr/bin/env python3
"""Book files for the Crescent Scroll (apocrypha) from Project Gutenberg texts (text only)."""
import re, sys, os, importlib.util
OUTDIR = sys.argv[1]
spec = importlib.util.spec_from_file_location('nm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nm_conv_lib.py'))
nm = importlib.util.module_from_spec(spec); spec.loader.exec_module(nm)
nm.SRC = '/tmp/ap'; nm.OUT = OUTDIR; os.makedirs(OUTDIR, exist_ok=True)
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



go('book-of-enoch-e', '77815.txt', r'^CHAP\. I\.$', END, heading=r'(CHAP\. [IVXLC]+\.?|SECT\. [IVXLC]+\.?.*)', roman_st=False)
