#!/usr/bin/env python3
"""Add books to a Scroll's library.

Borrow works another Scroll already has (book files, manifest entries, the
companion slots they pair with, and the author's portrait stays in the engine):
  add_book.py hermetic --copy-from plato --author "Hermes Trismegistus" --section "Hermetica"
  add_book.py hermetic --copy-from plato --key orphic-hymns --section "Hymns & Oracles"

Make a new book from plain text (blank line = new paragraph, "# " = heading,
"[1.2] " at the start of a paragraph = its reference):
  add_book.py hermetic --text kybalion.txt --key kybalion --title "The Kybalion"
              --author "Three Initiates" --translator "1908" --section "Modern Hermetica"
              [--blurb "…"] [--color '#6b4f8a']
"""
import os, re, sys, json, shutil, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_el(path):
    s = open(path, encoding='utf-8').read()
    i, j = s.index('>') + 1, s.rindex('</')
    return s[:i], json.loads(s[i:j]), s[j:]


def write_el(path, head, obj, tail):
    open(path, 'w', encoding='utf-8').write(head + json.dumps(obj, ensure_ascii=False, separators=(',', ': ')) + tail)


def scroll_dir(sid):
    return os.path.join(ROOT, 'scrolls', sid)


def books_dir(sid):
    d = scroll_dir(sid)
    cfg = json.load(open(os.path.join(d, 'scroll.json'), encoding='utf-8'))
    return os.path.join(d, cfg.get('books') or 'books')


def add_author(sid, author, section):
    p = os.path.join(scroll_dir(sid), 'slots', 'hv-authors.html')
    h, a, t = read_el(p)
    if any(author in s['authors'] for s in a['sections']):
        return
    sec = next((s for s in a['sections'] if s['name'] == section), None)
    if not sec:
        sec = {'name': section, 'authors': []}
        other = next((i for i, s in enumerate(a['sections']) if s['name'] == 'Other'), len(a['sections']))
        a['sections'].insert(other, sec)
    sec['authors'].append(author)
    write_el(p, h, a, t)


def text_to_entries(txt):
    entries = []
    for para in re.split(r'\n\s*\n', txt.strip()):
        para = ' '.join(l.strip() for l in para.splitlines()).strip()
        if not para:
            continue
        if para.startswith('# '):
            entries.append({'sp': 'HDR', 't': para[2:].strip()}); continue
        m = re.match(r'\[([^\]]+)\]\s*(.*)', para)
        e = {'st': m.group(1), 't': m.group(2)} if m else {'t': para}
        entries.append(e)
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scroll'); ap.add_argument('--copy-from'); ap.add_argument('--author'); ap.add_argument('--key')
    ap.add_argument('--section', default='Other'); ap.add_argument('--text'); ap.add_argument('--title')
    ap.add_argument('--translator', default=''); ap.add_argument('--blurb', default=''); ap.add_argument('--color', default='#6b4f8a')
    a = ap.parse_args()
    mp = os.path.join(scroll_dir(a.scroll), 'slots', 'hermes-manifest.html')
    h, man, t = read_el(mp)
    have = {b['meta']['key'] for b in man['books']}
    dst_books = books_dir(a.scroll); os.makedirs(dst_books, exist_ok=True)
    added = []
    if a.copy_from:
        _, src, _ = read_el(os.path.join(scroll_dir(a.copy_from), 'slots', 'hermes-manifest.html'))
        want = set()
        for b in src['books']:
            m = b['meta']
            if (a.key and m['key'] == a.key) or (a.author and m.get('author') == a.author and not m.get('hidden')):
                want.add(m['key'])
                want.update((m.get('transPair') or {}).values())   # companion texts come too
        for b in src['books']:
            k = b['meta']['key']
            if k in want and k not in have:
                f = os.path.join(books_dir(a.copy_from), k + '.js')
                if not os.path.exists(f):
                    print('  (no book file for', k, '— skipped)'); continue
                shutil.copy(f, dst_books); man['books'].append(b); added.append(k)
                if not b['meta'].get('hidden'):
                    add_author(a.scroll, b['meta']['author'], a.section)
    elif a.text:
        if not (a.key and a.title and a.author):
            sys.exit('--text needs --key, --title and --author')
        entries = text_to_entries(open(a.text, encoding='utf-8').read())
        js = ('(function(){if(!window.__hermes_register_book)return;window.__hermes_register_book('
              + json.dumps(a.key) + ',' + json.dumps(entries, ensure_ascii=False) + ',[]);})();')
        open(os.path.join(dst_books, a.key + '.js'), 'w', encoding='utf-8').write(js)
        meta = {'key': a.key, 'en': a.title, 'kind': 'prose', 'color': a.color, 'author': a.author, 'blurb': a.blurb}
        text = {'title': a.title, 'translator': a.translator, 'lang': 'eng', 'noSpeakerLabels': True}
        man['books'] = [b for b in man['books'] if b['meta']['key'] != a.key] + [{'meta': meta, 'text': text}]
        add_author(a.scroll, a.author, a.section); added.append(a.key)
    else:
        sys.exit('give --copy-from or --text')
    write_el(mp, h, man, t)
    print('added', len(added), 'book files:', ', '.join(added) or '-')


if __name__ == '__main__':
    main()
