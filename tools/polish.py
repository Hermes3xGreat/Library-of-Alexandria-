#!/usr/bin/env python3
"""Reading polish for converted Scroll books: typography (dashes, quotes,
italics), leftover scan/transcription marks, over-long paragraphs, headings.
usage: polish.py [--write] [--report N] [key ...]   (default: dry run, all converted books)"""
import os, re, json, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, '..', 'scrolls')
MINE = json.load(open(os.path.join(HERE, 'polish_books.json')))
SCROLLS = ['egyptian', 'northern', 'crescent', 'americas', 'liberty', 'africa', 'descartes']
STATS = collections.Counter()
ABBR = re.compile(r'(?:\b(?:Mr|Mrs|Ms|Dr|St|Messrs|Gen|Col|Capt|Lieut|Lt|Maj|Rev|Hon|Gov|Prof|Sr|Jr|No|Nos|vol|Vol|pp|p|cf|viz|etc|vs|ch|Ch|Art|Sec|fol|col|Esq|Co|Bros|Mt|Ft|i\.e|e\.g|A\.D|B\.C|[A-Z]|\d{1,3}))\.["”’)]*$')
SMALL = r'\b(Of|The|And|In|To|A|An|With|From|On|At|By|For|Or|As|Is|His|Her|Its|Their|Into|Upon|That)\b'


def load(p):
    s = open(p, encoding='utf-8').read(); i = s.index('[', s.index('__hermes_register_book('))
    a, j = json.JSONDecoder().raw_decode(s[i:]); return s[:i], a, s[i + j:]


def H(x): return x.get('sp') == 'HDR'


def titlecase(t):
    if not re.search('[a-z]', t):
        t = t.title(); t = re.sub(r"(['’])S\b", r"\1s", t)
        t = re.sub(SMALL, lambda m: m.group(1).lower(), t)
        t = re.sub(r'\b[IVXLC]+[ivxlc]+\b', lambda m: m.group(0).upper() if re.fullmatch(r'[IVXLCivxlc]+', m.group(0)) and m.group(0).lower() not in ('civil', 'ill', 'live', 'mix', 'mill', 'vivid', 'lid', 'mild', 'dim', 'did', 'vim') else m.group(0), t)
        t = t[:1].upper() + t[1:]
    return t


def quotes(t):
    if '"' not in t and "'" not in t: return t
    parts = re.split(r'(<[^>]*>)', t); out = []; prev = ' '
    for p in parts:
        if p.startswith('<'): out.append(p); continue
        r = []
        for i, c in enumerate(p):
            b = p[i - 1] if i else prev; n = p[i + 1] if i + 1 < len(p) else ' '
            if c == '"':
                c = '“' if (b in ' \t([{—–-‘' or b == '\xa0') and n != ' ' else '”'
                if b == ' ' and n == ' ': c = '”'
            elif c == "'":
                if b.isalnum() and n.isalnum(): c = '’'
                elif (b in ' ([{—–“' ) and n.isalpha():
                    c = '’' if re.match(r"(tis|twas|twere|twill|twould|em|gainst|neath|mid|midst|tween|twixt|ere|cause|bout|round|til|un)\b", p[i + 1:], re.I) else '‘'
                else: c = '’'
            r.append(c)
        s = ''.join(r); out.append(s); prev = s[-1] if s else prev
    return ''.join(out)


def inline(t, hdr=False):
    o = t
    t = re.sub(r'\[(?:Footnote|Sidenote|Illustration|Transcriber)[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', '', t)
    t = re.sub(r'\[(?:Greek|Hebrew|Arabic): ([^\]]*)\]', r'<i>\1</i>', t)
    t = re.sub(r'\[=([a-zA-Z])\]', lambda m: m.group(1) + '̄', t); t = t.replace('[oe]', 'œ').replace('[ae]', 'æ').replace('[OE]', 'Œ').replace('[AE]', 'Æ')
    t = re.sub(r'(?<![A-Za-z0-9])_([^_<>]{1,400}?)_(?![A-Za-z0-9])', r'<i>\1</i>', t)
    t = re.sub(r'^_([^_]+)$', r'<i>\1</i>', t); t = re.sub(r'^([^_]+)_$', r'<i>\1</i>', t) if t.count('_') == 1 and t.endswith('_') else t
    t = re.sub(r'_{3,}', '———', t); t = t.replace('_', '')
    t = re.sub(r'(?<![=\w])=([A-Za-z][^=<>]{0,80}?)=(?![=\w])', r'\1', t)
    t = re.sub(r'\s*-{4,}\s*', ' —— ', t); t = re.sub(r'\s*--\s*', '—', t); t = re.sub(r'—{3,}', '——', t)
    t = re.sub(r'(?:\*\s*){3,}', ' … ' if re.search(r'[A-Za-z]', t) else '* * *', t)
    t = quotes(t)
    t = re.sub(r'[ \t\xa0]{2,}', ' ', t); t = re.sub(r' +([,;:!?])(?=\s|$)', r'\1', t); t = re.sub(r'\s+(<br>)|(<br>)\s+', r'\1\2', t)
    t = re.sub(r'<i>\s*</i>', '', t).strip()
    if hdr:
        t = re.sub(r'</?(i|em|b)>', '', t); t = titlecase(t); t = re.sub(r'\s*—\s*', ' — ', t); t = re.sub(r'\.\s+—', ' —', t); t = re.sub(r'[\s—:,]+$', '', t); t = re.sub(r'(?<![A-Z])\.$', '', t) if not re.search(r'\b(etc|Esq|Jr|Sr|Co)\.$', t) else t
        t = re.sub(r'(— )([a-z])', lambda m: m.group(1) + m.group(2).upper(), t)
    if t != o: STATS['inline'] += 1
    return t


def sentences(t):
    cuts = [m.end() for m in re.finditer(r'[.!?]["”’)\]]*\s+(?=["“‘(\[]?[A-Z]|\d{1,3}\. )', t)]
    out, a = [], 0
    for c in cuts:
        seg = t[a:c]
        if ABBR.search(seg.rstrip()): continue
        out.append(seg); a = c
    out.append(t[a:]); return out


def split_wall(x, limit=1500, target=950):
    t = x['t']
    if len(t) <= limit or '<br>' in t: return [x]
    chunks, cur = [], ''
    for s in sentences(t):
        if cur and len(cur) + len(s) > target and cur.count('<i>') == cur.count('</i>') and len(cur) > 350:
            chunks.append(cur); cur = s
        else: cur += s
    if cur:
        if chunks and len(cur) < 300: chunks[-1] += cur
        else: chunks.append(cur)
    if len(chunks) < 2: return [x]
    STATS['split'] += 1
    out = []
    for i, c in enumerate(chunks):
        y = dict(x); y['t'] = c.strip()
        if i: y.pop('st', None); y.pop('ref', None)
        out.append(y)
    return out


JUNK = re.compile(r'^(End of (the )?Project Gutenberg|Project Gutenberg|\[?The End\.?\]?$|THE END\.?$|Finis\.?$|FINIS\.?$|\[Editor:|Footnotes?:?$|FOOTNOTES?:?$|Transcriber|Appendices$|\[English Translation\]$)', re.I)


def generic(key, a):
    out = []
    for x in a:
        t = x.get('t', '')
        if not t.strip() or JUNK.search(t.strip()) or (not H(x) and re.fullmatch(r'[_\-=\s]{3,}', t)): STATS['junk'] += 1; continue
        x = dict(x); x['t'] = inline(t, H(x))
        if not x['t']: continue
        if not H(x) and len(x['t']) > 80 and not re.search('[a-z]', re.sub(r'<[^>]+>', '', x['t'])) and re.search('[A-Z]{4}', x['t']):      # all-caps synopsis
            s = titlecase(x['t']); x['t'] = '<i>' + s + '</i>'; STATS['caps'] += 1
        out.append(x)
    # long synopsis headings: keep the chapter label, move the synopsis below it
    o2 = []
    for x in out:
        if H(x) and len(x['t']) > 110 and ' — ' in x['t']:
            head, rest = x['t'].split(' — ', 1)
            if len(head) < 60 and re.match(r'(Chapter|Chap\.|Book|Part|Letter|Tablet|Alcove)\b', head):
                o2.append({**x, 't': head}); o2.append({'sp': 'N', 't': '<i>' + rest.replace(' — ', ' ') + '</i>'}); STATS['hdrsplit'] += 1; continue
        o2.append(x)
    out = o2
    out = [x for i, x in enumerate(out) if not (x['t'] == '* * *' and (i == 0 or H(out[i - 1]) or i + 1 == len(out) or H(out[i + 1])))]
    while out and H(out[-1]): out.pop(); STATS['endhdr'] += 1
    return out


def subtitle_merge(a, skip=()):
    out = []
    for i, x in enumerate(a):
        p = out[-1] if out else None
        if p is not None and H(p) and not H(x) and not p.get('_m') and not x.get('st'):
            t = re.sub(r'</?i>', '', x['t'])
            words = re.findall(r"[A-Za-zÀ-ÿ’']+", t)
            capw = sum(1 for w in words if w[0].isupper() or len(w) < 4)
            nxt = a[i + 1] if i + 1 < len(a) else None
            if (5 < len(t) < 90 and '<br>' not in t and not re.search(r'[.,;:!?”’"]$', t) and words and capw >= len(words) * 0.8 and nxt is not None and not H(nxt)
                    and len(p['t']) + len(t) < 120 and not any(re.search(s, t) for s in skip)):
                p['t'] += ' — ' + titlecase(t); p['_m'] = 1; STATS['subtitle'] += 1; continue
        out.append(x)
    for x in out: x.pop('_m', None)
    return out


def caps_to_hdr(a, maxlen=70, pat=None):
    out = []
    for x in a:
        t = re.sub(r'<[^>]+>', '', x['t'])
        if not H(x) and not x.get('st') and len(t) < maxlen and ((pat and re.fullmatch(pat, t)) or (not pat and re.search('[A-Z]{3}', t) and not re.search('[a-z]', t) and not re.fullmatch(r'([A-Z]\. ?)+[A-Z][A-Z\'’\-]*[.,]?', t))):
            out.append({'sp': 'HDR', 't': inline(t, True)}); STATS['caps2hdr'] += 1
        else: out.append(x)
    return out


def cut_between(a, start, stop_at_hdr=True, inclusive=True):
    """drop from an entry matching `start` up to the next heading"""
    out, cutting = [], False
    for x in a:
        if cutting and H(x): cutting = False
        if not cutting and not H(x) and re.search(start, x['t']): cutting = True
        if cutting: STATS['cut'] += 1; continue
        out.append(x)
    return out


def cut_tail(a, pat):
    for i, x in enumerate(a):
        if re.search(pat, x['t']) and i > len(a) * 0.5: STATS['tail'] += len(a) - i; return a[:i]
    return a


def cut_head(a, pat, keep=True):
    for i, x in enumerate(a):
        if re.search(pat, x['t']) and i < len(a) * 0.5: return a[i if keep else i + 1:]
    return a


def insert_hdr(a, pat, title, before=True):
    for i, x in enumerate(a):
        if re.search(pat, x['t']): return a[:i + (0 if before else 1)] + [{'sp': 'HDR', 't': title}] + a[i + (0 if before else 1):]
    print('   ! marker not found:', pat); return a


def unnumber(a, tail=False):
    """drop verse line numbers (multiples of 5) left in the text"""
    for x in a:
        if H(x): continue
        f = lambda m: m.group(1) if int(m.group(2)) % 5 == 0 else m.group(0)
        if tail: x['t'] = re.sub(r'(,|;|\.|:|!|\?|[a-z’”])\s+(\d{1,5})(?=<br>|$)', f, x['t'])
        else: x['t'] = re.sub(r'(^|<br>)(\d{1,5}) (?=\S)', f, x['t'])
    return a


# ---------------------------------------------------------------- per book
def b_quran(a):
    a = cut_between(a, r'^———|^_{5,}')
    for x in a:
        x['t'] = re.sub(r'(?<=[A-Za-z,.;:!?’”)])\d{1,3}(?=[\s,.;:!?’”)\-—]|$)', '', x['t'])
        x['t'] = re.sub(r'(?<=[;:,.!?a-z])-(?=\s|$|[A-Z])', ' —', x['t']); x['t'] = re.sub(r'\s+—$', ' —', x['t']); x['t'] = re.sub(r'\.\s—\s*', '. — ', x['t']) if H(x) else x['t']
    return a


def b_enoch(a):
    out = []
    for x in a:
        t = x['t']
        if t in ('E',): x = {'sp': 'N', 't': '<i>(Ethiopic text)</i>'}
        elif re.fullmatch(r'G\^?[a-z0-9]*', t): x = {'sp': 'N', 't': '<i>(Greek text)</i>'}
        else: x['t'] = re.sub(r'[⌜⌝〚〛†‡]', '', re.sub(r'(\d)\^([a-z])', r'\1\2', t)).replace('^', '')
        out.append(x)
    return out


def b_franklin(a):
    a = [x for x in a if not re.fullmatch(r'[A-Z .•]{20,}', x['t'])]
    a = [{'sp': 'HDR', 't': 'Part One — Twyford, 1771'}] + a
    a = insert_hdr(a, r'^Memo\. Thus far was written', 'Letters Urging Him to Continue', before=False)
    a = insert_hdr(a, r'^Continuation of the Account of my Life', 'Part Two — Passy, 1784')
    a = insert_hdr(a, r'I am now about to write at home, August, 1788', 'Part Three — Philadelphia, 1788')
    return a


def b_federalist(a):
    out = []; i = 0
    while i < len(a):
        x = a[i]
        if H(x) and re.match(r'Federalist No', x['t'], re.I):
            num = re.sub(r'(?i)federalist', 'Federalist', x['t']); j = i + 1; sub = []; author = ''
            while j < len(a) and j < i + 6:
                y = a[j]
                if H(y) and re.fullmatch(r'(Hamilton|Madison|Jay)( (and|or|with) (Hamilton|Madison))?|Madison, with Hamilton|Hamilton and Madison|Hamilton or Madison', y['t'], re.I): author = y['t'].title().replace(' And ', ' and ').replace(' Or ', ' or ').replace(' With ', ' with '); j += 1; break
                if H(y): break
                sub.append(y['t']); j += 1
            if author:
                title = next((s for s in sub if not re.match(r'(For the|From the|To the People)', s)), '')
                when = ' '.join(s for s in sub if re.match(r'(For the|From the)', s))
                out.append({'sp': 'HDR', 't': num + (' — ' + title.rstrip('.') if title and len(title) < 90 else '')})
                if title and len(title) >= 90: out.append({'sp': 'N', 't': '<i>' + title + '</i>'})
                out.append({'sp': 'N', 't': '<i>' + author + (' · ' + when if when else '') + '</i>'})
                i = j; continue
        if not H(x): x['t'] = re.sub(r'^([A-Z]{2,})(?=[ ,])', lambda m: m.group(1).capitalize(), x['t'])
        out.append(x); i += 1
    return out


def b_lincoln(a):
    out = []
    for x in a:
        if H(x) and (len(x['t']) > 150 or re.match(r'(First|Second|Third|Fourth|Fifth|Sixth)\.', x['t']) or x['t'].endswith('?')): x = {'sp': 'N', 't': x['t']}
        if H(x) and re.match(r"Lincoln.s Speeches and Letters — ", x['t']): x['t'] = x['t'].split(' — ', 1)[1]
        out.append(x)
    return out


def b_tocq(a):
    out = []
    for x in a:
        if H(x):
            x['t'] = re.sub(r'\s*—\s*Chapter Summary', '', x['t']); x['t'] = re.sub(r'(\b[A-Z][a-z]*\b)', lambda m: m.group(1), x['t'])
            x['t'] = re.sub(SMALL, lambda m: m.group(1).lower(), x['t']); x['t'] = x['t'][:1].upper() + x['t'][1:]; x['t'] = re.sub(r'(: |— )([a-z])', lambda m: m.group(1) + m.group(2).upper(), x['t'])
            if x['t'] == 'Chapter Summary': continue
        out.append(x)
    return out


def b_lewis(a):
    for x in a:
        if H(x): x['t'] = re.sub(r'^\[(\w+), ([^\]]+)\]$', r'\2 — \1', x['t'])
    return a


def b_beowulf(a):
    for x in a:
        if H(x): continue
        t = re.sub(r'^\[[IVXL]+\]\s*', '', x['t'])
        if re.fullmatch(r'\{[^{}]*\}', t): t = '<i>' + t[1:-1].replace('<br>', ' ') + '</i>'
        x['t'] = re.sub(r'\{([^{}]*)\}', lambda m: '<i>' + m.group(1) + '</i>', t)
    return unnumber(a)


def b_gawain(a):
    out = []
    for x in a:
        t = x['t']
        if not H(x) and len(t) < 80 and not re.search(r'[.,;:!?”’]$', t) and '<' not in t: x = {'sp': 'HDR', 't': t}
        out.append(x)
    return out


BOOK = {
    'book-of-enoch': b_enoch, 'franklin-autobiography': b_franklin, 'federalist-papers': b_federalist,
    'lincoln-speeches-letters': b_lincoln, 'tocqueville-democracy-1': b_tocq, 'tocqueville-democracy-2': b_tocq, 'lewis-clark-journals': b_lewis,
    'beowulf': b_beowulf, 'sir-gawain': b_gawain,
    'parzival-1': lambda a: unnumber(a, tail=True), 'parzival-2': lambda a: unnumber(a, tail=True),
    'chretien-arthurian-romances': lambda a: [x for x in cut_between(a, r'^(——|—)?\s*Endnotes') if not re.fullmatch(r'[A-ZÈÉ ]{4,20}', x['t']) or H(x)],
    'rubaiyat-fitzgerald': lambda a: [{'sp': 'HDR', 't': 'The Rubáiyát'}] + cut_head(a, r'^THE RUBÁIYÁT$', keep=False),
    'adams-familiar-letters': lambda a: [x for x in a if x['t'] not in ('OF', 'JOHN ADAMS AND HIS WIFE.', 'Familiar Letters')],
    'pistis-sophia': lambda a: [dict(x, t=re.sub(r'\s*\[\d+\^?[a-z]?\]', '', x['t']).replace('^', '')) for x in a],
    'anglo-saxon-chronicle': lambda a: [dict(x, t=re.sub(r'\s?\((\d{1,3})\)(?=[\s,.;:]|$)', '', x['t'])) for x in a],
    'imitation-of-christ': lambda a: [dict(x, t=re.sub(r'\s?\((\d{1,2})\)(?=[\s,.;:]|$)', '', x['t'])) for x in a if not re.match(r'^\(\d{1,2}\) ', x['t'])],
    'shahnameh': lambda a: caps_to_hdr(a, 50), 'tlingit-myths': lambda a: caps_to_hdr(a, 80, r'\d+\. [A-Z][A-Z ,\'’\-]+'),
    'budge-creation-tablets': lambda a: caps_to_hdr(a, 40), 'thoreau-civil-disobedience': lambda a: [{'sp': 'HDR', 't': 'On the Duty of Civil Disobedience'}] + a,
    'old-indian-legends': lambda a: [dict(x, t=re.sub(r'^([A-Z]{2,})(?=[ ,])', lambda m: m.group(1).capitalize(), x['t'])) if not H(x) else x for x in a],
}
TAIL = {}
PRE = {}
HEADCUT = {}
NOSUB = {'federalist-papers', 'quran-rodwell', 'hafiz-divan', 'rumi-mesnevi', 'kalevala', 'divine-comedy', 'wheatley-poems'}
NOSPLIT = {'bible-kjv-ot', 'bible-kjv-nt', 'apocrypha-kjv', 'quran-rodwell', 'code-of-hammurabi'}
try:
    exec(open(os.path.join(HERE, 'polish_rules.py')).read())
except FileNotFoundError:
    pass


def polish(key, a):
    a = [x for x in a if isinstance(x.get('t'), str)]
    if key in PRE: a = PRE[key](a)
    if key in HEADCUT: a = cut_head(a, *HEADCUT[key])
    for pat in TAIL.get(key, []): a = cut_tail(a, pat)
    a = generic(key, a)
    if key in BOOK: a = BOOK[key](a)
    if key not in NOSUB: a = subtitle_merge(a)
    if key not in NOSPLIT:
        b = []
        for x in a: b += [x] if H(x) else split_wall(x)
        a = b
    a = [x for x in a if x['t'].strip()]
    while a and H(a[-1]): a.pop()
    return a


def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]; write = '--write' in sys.argv; rep = '--tails' in sys.argv
    paths = {}
    for sc in SCROLLS:
        d = os.path.join(R, sc, 'books')
        for f in sorted(os.listdir(d)):
            if f[:-3] in MINE and (not args or f[:-3] in args): paths.setdefault(f[:-3], []).append(os.path.join(d, f))
    for key, ps in paths.items():
        STATS.clear(); pre, a, post = load(ps[0]); n0 = len(a); b = polish(key, a)
        h = sum(1 for x in b if H(x))
        print(f'{key}: {n0}->{len(b)} h={h} ' + ' '.join(f'{k}={v}' for k, v in STATS.items()))
        if rep:
            for x in b[:3]: print('    ', ('H:' if H(x) else '- ') + x['t'][:80])
            for x in b[-3:]: print('   …', ('H:' if H(x) else '- ') + x['t'][-80:])
        if write:
            for p in ps: open(p, 'w', encoding='utf-8').write(pre + json.dumps(b, ensure_ascii=False) + post)


if __name__ == '__main__':
    main()
