#!/usr/bin/env python3
"""Make the Egyptian Scroll's new book files from Project Gutenberg texts and
from Plutarch's Moralia (Isis and Osiris). Text only: introductions, notes,
note markers and page numbers are dropped, as with the earlier imports."""
import re, json, sys, os

SRC = '/tmp/egsrc'
OUT = sys.argv[1]
PLATO_BOOKS = '/home/claude/in/ps/assets/books'
os.makedirs(OUT, exist_ok=True)


def italics(t):
    return re.sub(r'_([^_\n]{1,120})_', r'<i>\1</i>', t)


def clean(t):
    t = re.sub(r'\{\d+\}\s?', '', t)                 # page numbers {42}
    t = re.sub(r'\[\d+\]', '', t)                    # note markers [1]
    t = re.sub(r'(?<=[\w,.;:’”"\]\)])\((\d{1,3})\)', '', t)   # note markers word(1)
    t = re.sub(r'[ \t]+', ' ', t)
    return italics(t.strip())


def blocks(lines):
    """[(blank_lines_before, [raw lines])]"""
    out, cur, blank = [], [], 0
    for ln in lines:
        if ln.strip() == '':
            if cur:
                out.append((blank, cur)); cur = []; blank = 0
            blank += 1
        else:
            cur.append(ln.rstrip('\n'))
    if cur:
        out.append((blank, cur))
    return out


def is_heading(blank, ls, min_blank):
    if len(ls) != 1:
        return False
    t = ls[0].strip()
    if len(t) > 80 or len(t) < 2:
        return False
    if t.isupper() and not re.match(r'^\d', t):
        return True
    return blank >= min_blank and not re.search(r'[.,;:!?”"’)]$', t)


def convert(lines, min_blank=3, numbered=False, verse_indent=True, skip=None):
    entries = []; pend_st = None
    for blank, ls in blocks(lines):
        raw = ' '.join(l.strip() for l in ls)
        if raw.count('--') >= 3 and len(raw) < 400:     # transcriber's list of page headers
            continue
        if skip and skip(raw):
            continue
        if raw.startswith('[Illustration') or raw.startswith('[Transcriber'):
            continue
        if is_heading(blank, ls, min_blank):
            t = ls[0].strip()
            if re.match(r'^(IT IS FINISHED|FROM ITS BEGINNING|EVEN AS FOUND|B\. G\. G\.)', t, re.I):
                if not t.startswith('B. G.'):
                    entries.append({'sp': 'N', 't': clean(t.capitalize())})
                continue
            if re.match(r'^[IVXL]+\.?$', t):          # a bare stanza / part number
                pend_st = t.rstrip('.'); continue
            if t.isupper():
                t = t.title().replace("'S ", "'s ").replace('’S ', '’s ')
                t = re.sub(r'\b([IVXL]+)\b', lambda m: m.group(1), re.sub(r'\b([IiVvXxLl]+)\b', lambda m: m.group(1).upper() if re.fullmatch(r'[ivxlIVXL]+', m.group(1)) and len(m.group(1)) > 1 or m.group(1) in ('I',) else m.group(1), t))
            if clean(t):
                entries.append({'sp': 'HDR', 't': clean(t)})
            continue
        indented = verse_indent and len(ls) > 1 and all(re.match(r'^\s{2,}', l) for l in ls)
        text = '<br>'.join(clean(l) for l in ls) if indented else clean(raw)
        e = {'sp': 'N', 't': text}
        if pend_st:
            e['st'] = pend_st; pend_st = None
        if numbered:
            m = re.match(r'^([0-9]{1,2}|[A-Z])\.\s+(.*)$', text)
            if m:
                e['st'] = m.group(1); e['t'] = m.group(2)
        entries.append(e)
    return entries


def write(key, entries, notes=None):
    js = ('(function(){if(!window.__hermes_register_book)return;window.__hermes_register_book('
          + json.dumps(key) + ',' + json.dumps(entries, ensure_ascii=False) + ',' + json.dumps(notes or []) + ');})();')
    open(os.path.join(OUT, key + '.js'), 'w', encoding='utf-8').write(js)
    words = sum(len(re.sub('<[^>]+>', '', e['t']).split()) for e in entries)
    print(f'{key}: {len(entries)} entries, {sum(1 for e in entries if e["sp"]=="HDR")} headings, {words} words')


def lines_of(f, a, b):
    return open(os.path.join(SRC, f), encoding='utf-8').read().split('\n')[a - 1:b - 1]


def find(f, pat, start=1):
    L = open(os.path.join(SRC, f), encoding='utf-8').read().split('\n')
    for i in range(start - 1, len(L)):
        if re.search(pat, L[i]):
            return i + 1
    raise SystemExit(f'{pat} not found in {f}')


# --- Egyptian Literature (ed. Wilson, 1901) ---
EL = '28282.txt'
tales_at = find(EL, r'^EGYPTIAN TALES$'); amarna_at = find(EL, r'^THE TELL AMARNA TABLETS$')
hymns_at = find(EL, r'^CUNEIFORM INSCRIPTIONS AND HIERATIC PAPYRI$')
notes_at = find(EL, r'^FOOTNOTES$|^Footnotes$', hymns_at)
end_at = find(EL, r'\*\*\* END OF THE PROJECT')
ani_at = find(EL, r'^THE BOOK OF THE DEAD$', 300)

ani = convert(lines_of(EL, ani_at + 1, tales_at))
ani = [e for e in ani if not e['t'].startswith('According to the Theban')]
write('egypt-papyrus-of-ani', ani)

tales = convert(lines_of(EL, tales_at + 1, amarna_at))
tales = [e for e in tales if not e['t'].startswith('Translated from the Papyri')]
write('egypt-tales', tales)

hymns = convert(lines_of(EL, hymns_at + 1, notes_at),
                skip=lambda r: r.startswith('Translated by Various'))
write('egypt-hymns-inscriptions', hymns)

# --- Ptah-hotep, Ke'Gemni, Amenemhe'et (Gunn, 1906) ---
P = '30508.txt'
p0 = find(P, r"^THE INSTRUCTION OF PTAH-HOTEP$", 300); p1 = find(P, r'^AN EXPLANATION OF NAMES')
ptah = convert(lines_of(P, p0, p1), min_blank=3, numbered=True,
               skip=lambda r: r.startswith('NOTE TO APPENDIX') or r == 'APPENDIX')
# drop Gunn's footnote paragraphs ("[1] ...") that sit inside the text
ptah = [e for e in ptah if not re.match(r'^(Footnotes?|FOOTNOTES?)$', e['t'])]
write('ptahhotep-instruction', ptah)

# --- Murray, Ancient Egyptian Legends (1913) ---
M = '74354.txt'
m0 = find(M, r'^THE PRINCESS AND THE DEMON$', 160)
m1 = find(M, r'^NOTES$', m0)                    # Murray's notes all sit at the end
keep = lines_of(M, m0, m1)
murray = convert(keep, min_blank=2)
for e in murray:
    if e['sp'] == 'HDR':
        e['t'] = re.sub(r'^[IVXL]+\.\s*', '', e['t'])
write('murray-egyptian-legends', murray)

# --- Plutarch, Isis and Osiris (from Moralia, Part II) ---
s = open(os.path.join(PLATO_BOOKS, 'plut-moralia-2.js'), encoding='utf-8').read()
dec = json.JSONDecoder()
i = s.index('__hermes_register_book(') + len('__hermes_register_book(')
_, e1 = dec.raw_decode(s, i); ents, _ = dec.raw_decode(s, s.index('[', e1))
hd = [n for n, e in enumerate(ents) if e.get('sp') == 'HDR']
a = next(n for n in hd if ents[n]['t'].startswith('Isis and Osiris')); b = hd[hd.index(a) + 1]
isis = [dict(e) for e in ents[a:b]]
write('plutarch-isis-osiris', isis)
