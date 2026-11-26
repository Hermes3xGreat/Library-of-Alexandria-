#!/usr/bin/env python3
"""Check every Scroll for broken structure and leftover text errors.

Structure: each listed work has a readable book file; every shelf author has a
work and every work's author is on a shelf; version switches point at real
books; no work sits in two Scrolls; no empty paragraphs or headings.
Text: leftovers from the source files (Gutenberg notices, [Illustration],
[Footnote], page marks, _underscores_, =marks=, mis-encoded letters, doubled
spaces, words broken by a line-end hyphen).

usage: audit_library.py [--fix] [SCROLL ...]
--fix repairs the text leftovers that are safe to repair automatically, in
converted books only (never the Plato source links, never a picture).
"""
import os, re, sys, json, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL = ['plato-philosophy', 'descartes', 'pantheon', 'egyptian', 'crescent', 'eastern', 'northern', 'africa', 'americas', 'liberty']
VAR = r'-(b|e|c|d|gr|h)$'
DROP = re.compile(r"^\*?Transcriber[’']s Note:|presented on the Internet by Project Gutenberg")   # whole paragraphs that are not the author's


def slot(sc, name):
    s = open(os.path.join(ROOT, 'scrolls', sc, 'slots', name), encoding='utf-8').read()
    return json.loads(s[s.index('>') + 1:s.rindex('</')])


def load(p):
    s = open(p, encoding='utf-8').read(); i = s.index('['); d = json.JSONDecoder()
    a, end = d.raw_decode(s, i); return s[:i], a, s[end:]


TEXT = [  # name, pattern, replacement (None = report only)
    ('gutenberg notice', re.compile(r'Project Gutenberg|PROJECT GUTENBERG|gutenberg\.org'), None),
    ('illustration tag', re.compile(r'\s*\[Illustration:?[^\]]{0,200}\]'), ''),
    ('footnote tag', re.compile(r'\[Footnote \d+:'), None),
    ('page mark', re.compile(r'\s*\[(?:Pg|Page) ?\d+\]'), ''),
    ('transcriber note', re.compile(r"(?i)transcriber[’']?s? note"), None),
    ('underscore italics', re.compile(r'(?<![A-Za-z0-9])_([^_<>]{1,200}?)_(?![A-Za-z0-9])'), r'<i>\1</i>'),
    ('equals marks', re.compile(r'(?<![=\w])=([A-Za-z][^=<>]{0,80}?)=(?![=\w])'), r'\1'),
    ('mis-encoded letters', re.compile(r'Ã[\u0080-\u00bf]|â€[\u0090-\u00bf™œ]|Â[\u00a0-\u00bf]'), None),
    ('doubled space', re.compile(r'(?<=\S) {2,}(?=\S)'), ' '),
    ('space before comma', re.compile(r'(?<=[A-Za-z]) +([,;:])(?= )'), r'\1'),
    ('double hyphen', re.compile(r'(?<=[A-Za-z,;:.!?’”])\s*--\s*(?=[A-Za-z“‘])'), '—'),
    ('transcriber aside', re.compile(r'\s*\((?:<i>)?see Transcriber[’\']s Note(?:</i>)?\)'), ''),
    ('broken word', re.compile(r'\b([a-z]{3,})- (?!(?:and|or|nor|to|but|say|then|nay|either|that|which|for|if|as|so|not|the|in|of|with|from)\b)([a-z]{3,})\b'), r'\1-\2'),
    ('stray footnote number', re.compile(r'(?<=[a-z.,;”’])\[(\d{1,3}|[A-Z])\]'), ''),
]


def audit(scrolls, fix):
    seen = {}; problems = collections.defaultdict(list); text = collections.Counter(); fixed = collections.Counter(); books = 0
    for sc in scrolls:
        man = slot(sc, 'hermes-manifest.html')['books']; shelves = slot(sc, 'hv-authors.html')['sections']; decor = slot(sc, 'hv-section-decor.html')
        keys = {b['meta']['key'] for b in man}; d = os.path.join(ROOT, 'scrolls', sc, 'books')
        onshelf = {a for s in shelves for a in s['authors']}; authors = collections.Counter(b['meta'].get('author') for b in man if not b['meta'].get('hidden'))
        for a in onshelf - set(authors): problems[sc].append(f'shelf author with no work: {a}')
        for a in set(authors) - onshelf: problems[sc].append(f'author on no shelf: {a} ({authors[a]} works)')
        for s in shelves:
            if s['authors'] and s['name'] not in decor: problems[sc].append(f'shelf without decoration: {s["name"]}')
        for b in man:
            k = b['meta']['key']; p = os.path.join(d, k + '.js')
            for v in (b['meta'].get('transPair') or {}).values():
                if v not in keys: problems[sc].append(f'{k}: version switch points at missing {v}')
            if not b['meta'].get('hidden'):
                if not (b['meta'].get('blurb') or '').strip(): problems[sc].append(f'{k}: no description')
                st = re.sub(VAR, '', k)
                if st in seen and seen[st] != sc: problems[sc].append(f'{k}: also in {seen[st]}')
                seen.setdefault(st, sc)
            if not os.path.exists(p): problems[sc].append(f'{k}: book file missing'); continue
            try: pre, a, post = load(p)
            except Exception as e: problems[sc].append(f'{k}: unreadable ({str(e)[:50]})'); continue
            books += 1
            if not a: problems[sc].append(f'{k}: empty book'); continue
            if a[-1].get('sp') == 'HDR': problems[sc].append(f'{k}: ends on a heading')
            if not any(x.get('sp') == 'HDR' for x in a) and len(a) > 400 and not b['meta'].get('hidden'): problems[sc].append(f'{k}: {len(a)} paragraphs and no headings')
            pic = lambda x: (x.get('sp') == 'IMG' and x.get('src')) or 'hv-fig' in (x.get('t') or '')   # the engine's own picture entries, and added illustrations
            empty = sum(1 for x in a if not pic(x) and (not isinstance(x.get('t'), str) or not re.sub(r'<[^>]+>|\s', '', x['t'])))
            if empty: problems[sc].append(f'{k}: {empty} empty paragraphs')
            if os.path.islink(p) or re.search(r'-(b|gr)$', k) or sc in ('plato-philosophy', 'pantheon'): continue   # originals and the Plato library: structure only
            changed = False
            if fix:
                keep = [x for x in a if not (isinstance(x.get('t'), str) and len(x['t']) < 260 and DROP.search(x['t']))]
                if len(keep) != len(a): fixed[(sc, 'dropped note paragraphs')] += len(a) - len(keep); text[(sc, 'dropped note paragraphs')] += len(a) - len(keep); a = keep; changed = True
            for x in a:
                t = x.get('t')
                if not isinstance(t, str) or 'hv-fig' in t: continue
                for name, rx, rep in TEXT:
                    n = len(rx.findall(t))
                    if not n: continue
                    text[(sc, name)] += n
                    if fix and rep is not None:
                        t2 = rx.sub(rep, t)
                        if t2 != t: t = t2; fixed[(sc, name)] += n; changed = True
                if fix and t != x['t']:
                    if re.sub(r'<[^>]+>|\s', '', t): x['t'] = t
            if fix and changed: open(p, 'w', encoding='utf-8').write(pre + json.dumps(a, ensure_ascii=False) + post)
    return problems, text, fixed, books


if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]; fix = '--fix' in sys.argv
    problems, text, fixed, books = audit(args or ALL, fix)
    print(f'{books} book files read')
    for sc, ps in problems.items():
        print(f'\n{sc}: {len(ps)} structural problems')
        for p in ps[:40]: print('  -', p)
    print('\ntext leftovers (found' + (' / fixed' if fix else '') + '):')
    names = sorted({n for _, n in text})
    for n in names:
        row = {sc: text[(sc, n)] for sc in (args or ALL) if text[(sc, n)]}
        print(f'  {n}: {sum(row.values())}' + (f' / {sum(v for (s, m), v in fixed.items() if m == n)}' if fix else ''), row)
