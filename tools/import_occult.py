#!/usr/bin/env python3
"""Book files for alchemy and occult works for the Northern and Liberty Scrolls from Project Gutenberg texts (text only)."""
import re, sys, os, importlib.util
OUTDIR = sys.argv[1]
spec = importlib.util.spec_from_file_location('nm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nm_conv_lib.py'))
nm = importlib.util.module_from_spec(spec); spec.loader.exec_module(nm)
nm.SRC = '/tmp/oc'; nm.OUT = OUTDIR; os.makedirs(OUTDIR, exist_ok=True)
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
CH = r'((Section|Chapter|Part|Stanza|Book) [IVXLC0-9]+\.( .*)?|STANZA [IVXL]+\.?( .*)?|CHAPTER [IVXLC]+\.?( .*)?|CHAP\. [IVXLC]+\.?( .*)?|BOOK [IVXL]+\.?|PART [IVXL]+\.?( .*)?|SECTION [IVXLC0-9]+\.?( .*)?|LETTER [IVXL]+\.?|INTRODUCTION\.?|INTRODUCTORY\.?|PREFACE\.?|CONCLUSION\.?|FOREWORD|APPENDIX\.?)'
def g2(key, fn, spans, heading=None, **kw):
    f = L(fn); lines = []
    for a, b in spans: lines += f[a:b] + ['']
    kw.setdefault('drop', NOTE)
    try: e = convert(lines, heading=heading or '(' + CH + '|' + C + ')', **kw)
    except Exception as ex: print('FAIL', key, ex); return
    write(key, e); print(f'{key}: {len(e)} entries, {sum(1 for x in e if x["sp"] == "HDR")} headings | ', [x['t'][:30] for x in e if x['sp'] == 'HDR'][:4], '|', e[-1]['t'][-50:])
FNS = [(r'^FOOTNOTES:?$', r'^(CHAPTER [IVXL]+\.?|SECTION [IVXL]+\.?|[IVXL]+\.|CONCLUSION\.|[A-Z][A-Z .,\'’-]{4,}\.?)$')]
# alchemy
g2('sendivogius-new-light-of-alchymie', '61112.txt', [(50, 3871)])
g2('paracelsus-nature-of-things', '61112.txt', [(3872, 8517)], heading=r'([A-Z][A-Z ,.\'’\-:;&]{5,})')
g2('waite-lives-of-alchemystical-philosophers', '68687.txt', [(270, 8839)], skip=FNS)
g2('redgrove-alchemy-ancient-and-modern', '43240.txt', [(547, 3830), (4108, 4846)])
g2('muir-story-of-alchemy', '14218.txt', [(273, 5261)])
g2('silberer-hidden-symbolism', '27755.txt', [(94, 10104)])
# magic and kabbalah
g2('levi-history-of-magic', '70033.txt', [(1258, 15309)])
g2('goetia-lesser-key-of-solomon', '72679.txt', [(110, 2374)])
g2('ginsburg-kabbalah', '69243.txt', [(30, 4383)], heading=r'([IVXL]+\.|' + C + ')')
g2('waite-key-to-the-tarot', '43548.txt', [(245, 4316)])
g2('godwin-lives-of-the-necromancers', '7082.txt', [(584, 10794)])
g2('thorndike-place-of-magic', '69622.txt', [(285, 2580)])
# astrology
g2('dee-private-diary', '19553.txt', [(124, 3603)])
g2('lilly-life-and-times', '15835.txt', [(189, 3870)])
g2('sepharial-astrology', '46963.txt', [(342, 4016)])
g2('culpeper-complete-herbal', '49513.txt', [(387, 30722)])
# witchcraft
g2('scot-discoverie-of-witchcraft', '60766.txt', [(4484, 33236)], heading=r'(The [a-z.]+ Booke\.?|The [a-z.]+ Chapter\.?|' + C + ')')
g2('scott-demonology-and-witchcraft', '14461.txt', [(190, 10248)])
g2('summers-history-of-witchcraft', '77145.txt', [(203, 13508)], skip=[(r'^NOTES TO (CHAPTER|INTRODUCTION)', r'^(CHAPTER [IVXL]+|BIBLIOGRAPHY)$')])
g2('upham-salem-witchcraft', '17845.txt', [(3197, 14731), (14823, 30358)])
# theosophy
g2('blavatsky-isis-unveiled-1', '68705.txt', [(2314, 29176)])
g2('blavatsky-isis-unveiled-2', '75871.txt', [(303, 27783)])
g2('blavatsky-secret-doctrine-1', '54824.txt', [(158, 29920)])
g2('blavatsky-secret-doctrine-2', '54488.txt', [(628, 34265)])
g2('blavatsky-secret-doctrine-3', '56880.txt', [(161, 24045)])
g2('blavatsky-key-to-theosophy', '55618.txt', [(202, 9976)], skip=FNS)
g2('steiner-outline-of-occult-science', '30718.txt', [(494, 10079)])
g2('steiner-mystics-of-the-renaissance', '75994.txt', [(106, 3816)])
