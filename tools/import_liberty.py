#!/usr/bin/env python3
"""Book files for Liberty Scroll (American history) from Project Gutenberg texts.
Text only: editors' introductions, notes, indexes and licence text dropped."""
import re, sys, os, importlib.util
OUTDIR = sys.argv[1]
spec = importlib.util.spec_from_file_location('nm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nm_conv_lib.py'))
nm = importlib.util.module_from_spec(spec); spec.loader.exec_module(nm)
nm.SRC = '/tmp/us'; nm.OUT = OUTDIR; os.makedirs(OUTDIR, exist_ok=True)
L0, idx, convert, write, UP, clean = nm.L, nm.idx, nm.convert, nm.write, nm.UP, nm.clean
nm.L = L = lambda f: [re.sub(r'\[\d+:\d+\]', '', x.rstrip('\r')) if not re.match(r'^\[\d+:\d+\]', x) else x.rstrip('\r') for x in L0(f)]
_clean = nm.clean
nm.clean = lambda t: _clean(re.sub(r'\[Footnote[^\]]*\]\s?|\[(\d{1,3}|\d+:\d+|[A-Z\*][a-z]?)\]|\[Illustration[^\]]*\]', '', t))
NOTE = r'^(\[\d+\]\s|\[\d+:\d+\]|\[Footnote|Footnote \d|FOOTNOTES?:?$|\[Illustration)'
END = r'\*\*\* END OF THE PROJECT'
NOFN = []


_write = write
def write(key, e):
    out = []
    for x in e:
        if x['sp'] == 'HDR':
            x['t'] = re.sub(r'\b((?:[A-Z] ){2,}[A-Z])\b', lambda m: m.group(1).replace(' ', ''), x['t'])
            x['t'] = re.sub(r'(?<=\b[A-Z]) (?=[A-Z]\b)', '', x['t']) if re.fullmatch(r'[A-Z .]+', x['t']) else x['t']
            if re.fullmatch(r'[\d,\-\s.]+', x['t']): continue
            x['t'] = {'To M AE CENAS.': 'To Maecenas.', 'ONVIRTUE.': 'On Virtue.', 'ODETONEPTUNE.': 'Ode to Neptune.'}.get(x['t'], x['t'])
            if out and out[-1]['sp'] == 'HDR' and len(out[-1]['t']) + len(x['t']) < 160 and not out[-1].get('st'):
                out[-1]['t'] += ' — ' + x['t']; continue
        out.append(x)
    _write(key, out)


def go(key, fn, start, end, nth=1, endnth=1, **kw):
    f = L(fn); a = idx(f, start, nth=nth); b = idx(f, end, a + 1, nth=endnth)
    kw.setdefault('heading', UP); kw.setdefault('drop', NOTE)
    e = convert(f[a:b], **kw)
    write(key, e)
    print(f'{key}: {len(e)} entries, {sum(1 for x in e if x["sp"] == "HDR")} headings')


def paras(lines):
    out, cur = [], []
    for ln in lines + ['']:
        if ln.strip():
            cur.append(ln.strip())
        elif cur:
            out.append(clean(' '.join(cur))); cur = []
    return [p for p in out if p and not p.startswith('[Footnote')]


def doc(fn, start, end, title, st=None, keep_lines=False):
    f = L(fn); a = idx(f, start); b = idx(f, end, a + 1) if end else len(f)
    if keep_lines:
        ps = [clean(x) for x in f[a:b] if x.strip()]
    else:
        ps = paras(f[a:b])
    return [{'sp': 'HDR', 't': title, **({'st': st} if st else {})}] + [{'sp': 'N', 't': p} for p in ps]


# ---- Charters of Freedom: the founding documents in one book -------------
ch = []
ch += doc('7.txt', r'^In the name of God', r'^Mr\. John Carver|^John Carver|\*\*\* END', 'The Mayflower Compact (1620)')
ch += doc('6.txt', r'^No man thinks more highly', END, 'Patrick Henry: “Give Me Liberty or Give Me Death” (1775)')
ch += doc('1.txt', r'^IN CONGRESS, July 4', END, 'The Declaration of Independence (1776)')
# The Constitution and Amendments I–XV, from the appendix of Reeve's Tocqueville
f = L('816.txt'); a = idx(f, r'^We The People'); b = idx(f, r'^Article XV', a) + 8
part, inamend = [{'sp': 'HDR', 't': 'The Constitution of the United States (1787)'}], False
blocks = []; cur = []
for ln in f[a:b] + ['']:
    if ln.strip(): cur.append(ln.strip())
    elif cur: blocks.append(cur); cur = []
for bl in blocks:
    raw = ' '.join(bl)
    if raw.startswith('[Footnote'): continue
    if raw.startswith('In addition to, and amendment of'):
        part.append({'sp': 'HDR', 't': 'The Amendments: the Bill of Rights and After'}); inamend = True
        part.append({'sp': 'N', 't': clean(raw)}); continue
    if re.fullmatch(r'Article [IVXL]+', raw):
        part.append({'sp': 'HDR', 't': ('Amendment ' if inamend else '') + raw.replace('Article ', '' if inamend else 'Article ')}); continue
    if raw.startswith('Done in Convention'):
        part.append({'sp': 'N', 't': clean(raw)}); continue
    if len(bl) > 3 and all(len(x) < 40 for x in bl):      # signers list
        part.append({'sp': 'N', 't': ' · '.join(bl)}); continue
    part.append({'sp': 'N', 't': clean(raw)})
ch += part
ch += doc('4.txt', r'^Four score and seven', END, 'The Gettysburg Address (1863)')
ch += doc('22082.txt', r'^By the President of the United States', END, 'The Emancipation Proclamation (1863)')
ch = [e for e in ch if not re.search(r'(gutenberg|etext|E-text|\*\*\*)', e['t'], re.I)]
_write('charters-of-freedom', ch); print('charters-of-freedom:', len(ch))

# ---- Colonies ----------------------------------------------------------------
go('bradford-plymouth', '24950.txt', r'^1\. Chapter\.', r'^(INDEX|APPENDIX)\.?$|' + END,
   heading=r'(The )?\d+\. Chap(ter)?\.?|Anno (Dom: )?\d{4}\.?|(The )?2\. Booke\.?|[A-Z][A-Z ,\'’\-]{6,}')
go('john-smith-generall-historie', '56347.txt', r'THE FIRST BOOKE\.', END, nth=2, skip=NOFN)
go('rowlandson-captivity', '851.txt', r'^THE FIRST REMOVE', END)
go('crevecoeur-american-farmer', '4666.txt', r'^LETTER I$', END, roman_st=False,
   heading=r'(LETTER [IVXL]+|[A-Z][A-Z ,\'’\-;]{6,})')
go('franklin-autobiography', '148.txt', r'^Dear Son', r'^CHIEF EVENTS|' + END, heading=r'([IVX]+\.?|[A-Z][A-Z ,\'’\-]{6,}\.?)', skip=NOFN)
go('wheatley-poems', '409.txt', r'^\s*To\s+M\s*AE', r'^\s*F\s*I\s*N\s*I\s*S|' + END, verse=True, heading=r'\s*((?:[A-Z]\s+){3,}.*|(To|On|An|A|Thoughts|Goliath|Isaiah|Niobe|Ode) [^.]{2,90}\.(\s*\d{4}\.)?|[A-Z][A-Z ,\'’\-]{6,}\.?)')
# ---- Revolution and the Founding --------------------------------------------
go('paine-common-sense', '147.txt', r'^INTRODUCTION\.$', r'^F  I  N  I  S|' + END)
go('paine-american-crisis', '3741.txt', r'^THE CRISIS I\. \(THESE', END, drop=NOTE + r'|^COMMON SENSE\.$', skip=NOFN)
go('adams-familiar-letters', '34123.txt', r'^FAMILIAR LETTERS$', r'^INDEX\.?$|' + END, nth=1, skip=[(r'^\s*FOOTNOTES?:?\s*$', r'^\d+\. (JOHN|ABIGAIL)')],
   heading=r'(\d+\. (JOHN|ABIGAIL) ADAMS\.|[A-Z][A-Z ,\'’\-]{6,})')
go('federalist-papers', '1404.txt', r'^FEDERALIST No\. 1$', END, heading=r'(FEDERALIST No\. \d+|HAMILTON|MADISON|JAY|HAMILTON AND MADISON|HAMILTON OR MADISON|MADISON, with HAMILTON)')
go('jefferson-autobiography', '16781.txt', r'^MEMOIR\.$', r'^APPENDIX TO THE MEMOIR\.$', skip=NOFN)
# ---- Presidents --------------------------------------------------------------
go('inaugural-addresses', '925.txt', r'^GEORGE WASHINGTON, FIRST INAUGURAL', END)
go('lincoln-speeches-letters', '14721.txt', r"^LINCOLN'S SPEECHES AND LETTERS$", r'^APPENDIX$|^INDEX|' + END, skip=NOFN,
   heading=r'([A-Z][A-Z0-9 ,.\'’\-:;]{8,})', chapter=r'^_')
# ---- The Nation Expands ------------------------------------------------------
LC = L('8419.txt'); open('/tmp/us/8419s.txt', 'w').write('\n'.join(re.sub(r'^(\[(Clark|Lewis|Ordway|Floyd|Gass|Whitehouse)[^\]]{0,40}\])\s*$', r'\n\1\n', x) for x in LC))
go('lewis-clark-journals', '8419s.txt', r'^\[Clark, May 14, 1804\]', END, heading=r'\[(Clark|Lewis|Ordway|Floyd|Gass|Whitehouse)[^\]]{0,40}\]', join_heads=False)
go('tocqueville-democracy-1', '815.txt', r'^\s*Book One\s*$', END, heading=r'\s*(Book (One|Two)|Introductory Chapter|Conclusion|Chapter [IVXL]+:.*|Chapter Summary)', skip=NOFN, roman_st=False)
go('tocqueville-democracy-2', '816.txt', r'^Chapter I: Philosophical', r'^Appendix A\s*$', heading=r'\s*(Book [IVX]+.*|Chapter [IVXL]+:.*|Section [IVX]+.*|Chapter Summary)', skip=NOFN, roman_st=False)
go('parkman-oregon-trail', '1015.txt', r'^CHAPTER I$', END, heading=r'(CHAPTER [IVXL]+|[A-Z][A-Z ,\'’“”\-]{3,})')
go('turner-frontier', '22994.txt', r'^THE SIGNIFICANCE OF THE FRONTIER IN AMERICAN HISTORY', r'^INDEX$', skip=NOFN)
# ---- Slavery, Freedom and the Civil War ----------------------------------------
go('equiano-narrative', '15399.txt', r'^CHAPTER I\.$', END, heading=r'(CHAP(TER)?\. [IVXL]+\.|[A-Z][A-Z ,\'’\-]{6,}\.?)', skip=NOFN)
go('douglass-narrative', '23.txt', r'^ CHAPTER I$', r'^ ?APPENDIX|' + END, heading=r'\s*(CHAPTER [IVXL]+|[A-Z][A-Z ,\'’\-]{6,})')
go('jacobs-incidents', '11030.txt', r'^\s+I\. Childhood', r'^\s*APPENDIX\.?\s*$|' + END, heading=r'\s*([IVXL]+\. .{3,60}|[A-Z][A-Z ,\'’\-]{6,})', roman_st=False)
go('northup-twelve-years', '45631.txt', r'^CHAPTER I\.$', r'^APPENDIX\.$', skip=NOFN)
go('sojourner-truth', '1674.txt', r'^HER BIRTH AND PARENTAGE\.', END, nth=1, skip=NOFN)
go('grant-memoirs', '4367.txt', r'^CHAPTER I\.$', END, skip=NOFN,
   heading=r'(CHAPTER [IVXL]+\.|[A-Z][A-Z ,\'’\-\.]{6,}|CONCLUSION\.?|APPENDIX\.?)')
# ---- Reform and the Modern Nation ----------------------------------------------
go('thoreau-civil-disobedience', '71.txt', r'^I heartily accept', END)
go('history-woman-suffrage-1', '28020.txt', r'^CHAPTER I\.$', r'^APPENDIX\.$', skip=NOFN)
go('washington-up-from-slavery', '2376.txt', r'^Chapter I\.$', END, heading=r'(Chapter [IVXL]+\.?|[A-Z][A-Za-z ,\'’\-]{3,60})', roman_st=False, chapter=r'^Chapter [IVXL]+\.')
go('du-bois-souls', '408.txt', r'^The Forethought', END, heading=r'(The Forethought|The Afterthought|[IVX]+\.|[A-Z][A-Za-z ,\'’\-]{3,60})', chapter=None)
go('riis-other-half', '45502.txt', r'^\s*_INTRODUCTION\._', r'^\s*INDEX\.?\s*$|' + END, heading=r'\s*(CHAPTER [IVXL]+\.|[A-Z][A-Z ,\'’\-]{6,}\.?)', skip=NOFN)
go('addams-hull-house', '1325.txt', r'^CHAPTER I$', r'^INDEX$|' + END, skip=NOFN)
go('roosevelt-autobiography', '3335.txt', r'^CHAPTER I$', END, skip=NOFN)
