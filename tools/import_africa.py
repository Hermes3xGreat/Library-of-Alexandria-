#!/usr/bin/env python3
"""Book files for Africa Scroll from Project Gutenberg texts (text only)."""
import re, sys, os, importlib.util
OUTDIR = sys.argv[1]
spec = importlib.util.spec_from_file_location('nm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nm_conv_lib.py'))
nm = importlib.util.module_from_spec(spec); spec.loader.exec_module(nm)
nm.SRC = '/tmp/af'; nm.OUT = OUTDIR; os.makedirs(OUTDIR, exist_ok=True)
L0, idx, convert, write, UP = nm.L, nm.idx, nm.convert, nm.write, nm.UP
L = lambda f: [x.rstrip('\r') for x in L0(f)]
_clean = nm.clean
nm.clean = lambda t: _clean(re.sub(r'\[Footnote[^\]]*\]\s?|\[(\d{1,3}|[A-Z\*][a-z]?)\]|\[Illustration[^\]]*\]', '', t))
NOTE = r'^(\[\d+\]\s|\[Footnote|Footnote \d|FOOTNOTES?:?$|\[Illustration)'
END = r'\*\*\* END OF THE PROJECT'


def go(key, fn, start, end, nth=1, lines=None, **kw):
    f = lines or L(fn)
    try: a = idx(f, start, nth=nth); b = idx(f, end, a + 1)
    except SystemExit as e: print('FAIL', key, e); return
    kw.setdefault('heading', UP); kw.setdefault('drop', NOTE)
    e = convert(f[a:b], **kw); write(key, e)
    print(f'{key}: {len(e)} entries, {sum(1 for x in e if x["sp"] == "HDR")} headings | ', [x['t'][:40] for x in e if x['sp'] == 'HDR'][:5])


go('lobo-abyssinia', '1436.txt', r'^PART I--THE VOYAGE', END)
go('schreiner-african-farm', '1441.txt', r'^Part I\.$', END, nth=2, heading=r'(Part I+\.|Chapter \d\.[IVXL]+\..*)', roman_st=False)
go('plaatje-native-life', '1452.txt', r'^Chapter I +A Retrospect', r'^Notes to the text:', nth=2, heading=r'(Chapter [IVXL]+ .*|Epilogue.*)', roman_st=False)
f = L('15359.txt'); out = []; skip = False
for ln in f:                                   # drop per-chapter footnote runs
    if ln.strip() == 'FOOTNOTES:': skip = True; continue
    if skip and re.match(r'^([IVX]+ [A-Z]|SUGGESTIONS)', ln): skip = False
    if not skip: out.append(ln)
go('du-bois-the-negro', None, r'^I AFRICA$', r'^SUGGESTIONS FOR FURTHER READING', lines=out, heading=r'[IVX]+ [A-Z][A-Z ,\'’\-]+')
go('augustine-confessions', '3296.txt', r'^BOOK I$', r'GRATIAS TIBI', heading=r'BOOK [IVXL]+')
go('dayrell-southern-nigeria', '34655.txt', r'^I$', r'^THE END$', nth=1, roman_st=True, heading=r'(_[^_]{3,120}_|[A-Z][A-Z ,\'’\-]{5,})')
go('zanzibar-tales', '37472.txt', r'^ZANZIBAR TALES\.$', END)
go('south-african-folk-tales', '38339.txt', r'^ORIGIN OF THE DIFFERENCE IN MODES', r'^LITERATURE$', nth=1)
go('basutoland-legends', '44456.txt', r'^CHAPTER I\.$', r'^ROBERT STOCKWELL,$', nth=2)
go('park-travels-1', '5266.txt', r'^CHAPTER I\.$', r'^FOOTNOTES$')
go('park-travels-2', '5305.txt', r'^CHAPTER XVI\.$', r'^NOTE\.$')
go('nassau-where-animals-talk', '58900.txt', r'^PART FIRST$', r'^INDEX$', nth=2, heading=r'(PART (FIRST|SECOND|THIRD)|TALE \d+|[A-Z][A-Z ,\'’\-\?!]{3,})')
go('sancho-letters', '66908.txt', r'^LETTER I\.$', r'^FINIS\.$', heading=r'(LETTER [IVXLC]+\.|TO [A-Z][A-Z .,\'’\-]+\.?)')
go('west-african-folk-tales', '66923.txt', r'^I\. ANANSI, OR SPIDER, TALES', r'^NOTES$', roman_st=False, heading=r'([IVXL]+\. [A-Z][A-Z ,\'’‘\-\?!]{3,})')
go('theal-kaffir-folk-lore', '71335.txt', r'^KAFFIR FOLK\.$', r'^NOTES\.$')
go('bleek-reynard-south-africa', '73413.txt', r'^I\.$', r'^NOTES$', nth=1, heading=r'([IVXL]+\.|\d+\. [A-Z][A-Z ,\'’\-\?!]{3,}\.?|[A-Z][A-Z ,\'’\-]{5,}\.?)')
