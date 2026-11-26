#!/usr/bin/env python3
"""Book files for the Northern Scroll from Project Gutenberg texts.
Text only: introductions, notes, glossaries, note markers and page numbers
are dropped, as with the earlier imports."""
import re, json, os

SRC = '/tmp/nmsrc'
OUT = None
ROMAN = r'[IVXLC]+'


def L(f):
    return open(os.path.join(SRC, f), encoding='utf-8').read().split('\n')


def idx(lines, pat, start=0, nth=1):
    n = 0
    for i in range(start, len(lines)):
        if re.search(pat, lines[i]):
            n += 1
            if n == nth:
                return i
    raise SystemExit(f'not found: {pat}')


def clean(t):
    t = re.sub(r'\{\d+\}\s?', '', t)
    t = re.sub(r'\[(\d+|[a-z])\]', '', t)
    t = re.sub(r'(?<=[\w,.;:’”"\]\)])\((\d{1,3})\)', '', t)
    t = re.sub(r'_([^_\n]{1,160})_', r'<i>\1</i>', t)
    t = re.sub(r'[ \t]+', ' ', t)
    return t.strip()


def titlecase(t):
    if not t.isupper():
        return t
    t = t.title()
    t = re.sub(r"(['’])S\b", r"\1s", t)
    t = re.sub(r'\b(Of|The|And|In|To|A|An|With|From|On|At|By|For)\b', lambda m: m.group(1).lower(), t)
    t = re.sub(r'\b([IVXLC]+)\b', lambda m: m.group(1), re.sub(r'\b([ivxlc]+|[IiVvXxLlCc]+)\b', lambda m: m.group(1).upper() if re.fullmatch(r'[IVXLCivxlc]+', m.group(1)) and m.group(1).lower() not in ('i', 'civil', 'ill', 'live', 'lix') else m.group(1), t))
    return t[0].upper() + t[1:]


def convert(lines, heading=None, verse=False, num_prefix=False, roman_st=True,
            skip=(), drop=None, join_heads=True, chapter=None):
    # 1. cut skip sections
    out, cutting = [], None
    for ln in lines:
        s = ln.strip()
        if cutting is not None:
            if re.search(cutting, s):
                cutting = None
            else:
                continue
        hit = next((e for b, e in skip if re.search(b, s)), None)
        if hit is not None:
            cutting = hit; continue
        out.append(ln)
    # 2. blocks
    blocks, cur = [], []
    for ln in out + ['']:
        if ln.strip() == '':
            if cur: blocks.append(cur); cur = []
        else:
            cur.append(ln.rstrip())
    entries, pend = [], None
    for b in blocks:
        raw = ' '.join(x.strip() for x in b)
        if raw.startswith(('[Illustration', '[Footnote', '[Transcriber', 'Footnote')) or (drop and re.search(drop, raw)):
            continue
        if roman_st and len(b) == 1 and re.fullmatch(ROMAN + r'\.?', raw):
            pend = raw.rstrip('.'); continue
        if chapter and re.match(chapter, b[0].strip()) and len(raw) < 300:
            entries.append({'sp': 'HDR', 't': clean(raw)}); continue
        if heading and all(re.fullmatch(heading, x.strip()) for x in b) and len(raw) < 140:
            t = clean(titlecase(raw if len(b) == 1 else ' — '.join(x.strip() for x in b)))
            t = re.sub(r'(—|:|\.)\s+([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), t)
            if join_heads and entries and entries[-1]['sp'] == 'HDR' and not entries[-1].get('_closed'):
                entries[-1]['t'] += ' — ' + t[0].upper() + t[1:]
            else:
                entries.append({'sp': 'HDR', 't': t})
            continue
        if entries and entries[-1]['sp'] == 'HDR':
            entries[-1]['_closed'] = True
        if verse:
            ls = [re.sub(r'\s+\|\s+', '&emsp;', x.strip()) for x in b]
            text = '<br>'.join(clean(x) for x in ls)
        else:
            text = clean(raw)
        e = {'sp': 'N', 't': text}
        if num_prefix:
            m = re.match(r'^(\d{1,4})\.\s+(.*)$', text, re.S)
            if m:
                e['st'] = m.group(1); e['t'] = m.group(2)
        if pend:
            e.setdefault('st', pend); pend = None
        if e['t']:
            entries.append(e)
    for e in entries:
        e.pop('_closed', None)
    return entries


def write(key, entries):
    js = ('(function(){if(!window.__hermes_register_book)return;window.__hermes_register_book('
          + json.dumps(key) + ',' + json.dumps(entries, ensure_ascii=False) + ',[]);})();')
    open(os.path.join(OUT, key + '.js'), 'w', encoding='utf-8').write(js)
    w = sum(len(re.sub('<[^>]+>', ' ', e['t']).split()) for e in entries)
    hd = [e['t'] for e in entries if e['sp'] == 'HDR']
    print(f'{key}: {len(entries)} entries, {len(hd)} headings, {w} words | {hd[:6]}')


UP = r"[A-Z0-9][A-Z0-9 ,.'’\-—:;&()]+"
