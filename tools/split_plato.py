#!/usr/bin/env python3
"""Split Plato Scroll's library: philosophy stays (scrolls/plato-philosophy),
the rest of the Greek and Roman world goes to Pantheon Scroll. Works that
already live in other Scrolls (Norse, Vedic, Avestan, Book of the Dead) leave
Plato and are not copied. scrolls/plato itself is left as the reference build."""
import os, re, json, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC_BOOKS = '/home/claude/in/ps/assets/books'; SRC_DATA = '/home/claude/in/ps/assets/data'
def rd(sc, n):
    s = open(f'{ROOT}/scrolls/{sc}/slots/{n}').read(); i = s.index('>') + 1; j = s.rindex('</'); return s[:i], json.loads(s[i:j]), s[j:]
def wr(sc, n, h, o, t): open(f'{ROOT}/scrolls/{sc}/slots/{n}', 'w').write(h + json.dumps(o, ensure_ascii=False, separators=(',', ': ')) + t)
base = lambda k: re.sub(r'-(b|e|c|gr)$', '', k)

h, man, t = rd('plato', 'hermes-manifest.html'); _, auth, _ = rd('plato', 'hv-authors.html'); _, decor, _ = rd('plato', 'hv-section-decor.html')
sec_of = {a: s['name'] for s in auth['sections'] for a in s['authors']}
PHIL_SECTIONS = {'Plato', 'Dialogues & Socratica', 'Fragments of the Philosophers', 'The Platonists'}
PHIL_AUTHORS = {'Aristotle', 'Epicurus', 'Nicomachus', 'Epictetus', 'Marcus Aurelius', 'Dio Chrysostom', 'Maximus of Tyre', 'Alcinous', 'Sextus Empiricus', 'Lucretius',
                'Orpheus', 'Apollo', 'Hermes Trismegistus', 'Cornelius Agrippa', 'Giordano Bruno', 'Diogenes Laertius'}
PHIL_WORKS = {'memorabilia', 'oeconomicus', 'xeno-symposium', 'xeno-apology', 'hiero', 'characters', 'seneca-epistles', 'seneca-essays', 'apuleius-on-plato', 'apuleius-god-of-socrates',
              'julian-orations', 'julian-essays', 'julian-galilaeans', 'chaldaean-oracles', 'phil-apollonius', 'plut-moralia-1', 'plut-moralia-2', 'plut-moralia-3', 'plut-moralia-4'}
ELSEWHERE = {'yasna', 'vendidad', 'visperad', 'khordeh-avesta', 'book-of-the-dead'}
# one home per work: these live in other Scrolls (Egyptian, Northern, Crescent) and leave both Plato and Pantheon
ELSE_AUTHORS = {'Hermes Trismegistus', 'Cornelius Agrippa', 'Giordano Bruno', 'Pseudo-Dionysius', 'Plethon', 'Marsilio Ficino', 'Pico della Mirandola', 'Boethius', 'Josephus'}
ELSE_SECTIONS = {'The North', 'The East — China', 'The East — India', 'The East — Persia'}
SPLIT_AUTHORS = {'Xenophon', 'Theophrastus', 'Seneca', 'Apuleius', 'Julian', 'Zoroaster', 'Philostratus', 'Plutarch'}

def where(b):
    k = base(b['meta']['key']); a = b['meta'].get('author'); s = sec_of.get(a, 'Other')
    if k in ELSEWHERE or s in ELSE_SECTIONS or a in ELSE_AUTHORS: return 'else'
    if k in PHIL_WORKS: return 'phil'
    if a in SPLIT_AUTHORS: return 'pan'
    if s in PHIL_SECTIONS or a in PHIL_AUTHORS: return 'phil'
    return 'pan'

side = {b['meta']['key']: where(b) for b in man['books']}
phil = [b for b in man['books'] if side[b['meta']['key']] == 'phil']; pan = [b for b in man['books'] if side[b['meta']['key']] == 'pan']
print('philosophy', len(phil), 'pantheon', len(pan), 'elsewhere', sum(1 for v in side.values() if v == 'else'))

def link_books(sc, books):
    d = f'{ROOT}/scrolls/{sc}/books'
    if os.path.islink(d): os.unlink(d)
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    n = miss = 0
    for b in books:
        f = b['meta']['key'] + '.js'
        if os.path.exists(f'{SRC_BOOKS}/{f}'): os.symlink(f'{SRC_BOOKS}/{f}', f'{d}/{f}'); n += 1
        else: miss += 1
    extra = [f for f in os.listdir(SRC_BOOKS) if not f.endswith('.js') or f[:-3] not in side]
    return n, miss, extra

# ---- Plato Scroll, philosophy only
P = 'plato-philosophy'; pd = f'{ROOT}/scrolls/{P}'
shutil.rmtree(pd, ignore_errors=True); shutil.copytree(f'{ROOT}/scrolls/plato', pd, symlinks=True)
n, miss, extra = link_books(P, phil); print('plato books linked', n, 'no file', miss, 'unlisted files in source', len(extra), extra[:6])
philkeys = {b['meta']['key'] for b in phil}
for f in extra:
    if re.match(r'(bd|cx)-', f) and f[3:-3] not in philkeys: continue
    if not os.path.exists(f'{pd}/books/{f}') and os.path.isfile(f'{SRC_BOOKS}/{f}'): os.symlink(f'{SRC_BOOKS}/{f}', f'{pd}/books/{f}')
# data: everything linked from the source, except the word finder and citation data, which are trimmed to this library below
if os.path.islink(f'{pd}/data'): os.unlink(f'{pd}/data')
shutil.rmtree(f'{pd}/data', ignore_errors=True); os.makedirs(f'{pd}/data')
for f in os.listdir(SRC_DATA):
    if f not in ('conc', 'hv-loci.json.gz'): os.symlink(f'{SRC_DATA}/{f}', f'{pd}/data/{f}')
wr(P, 'hermes-manifest.html', h, {**man, 'books': phil}, t)
import subprocess, sys
print(subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'reindex_greek_tools.py'), SRC_DATA, f'{pd}/data', f'{pd}/slots/hermes-manifest.html'], capture_output=True, text=True).stdout.strip())
pa = {b['meta'].get('author') for b in phil}
RENAME = {'Treatises & Orations': 'Aristotle & the Schools', 'Lives & History': 'Lives & Moralia', 'Oracles, Hymns & Hermetica': 'Oracles & Hymns'}
secs = []
for s in auth['sections']:
    au = [a for a in s['authors'] if a in pa]
    if s['name'] == 'Treatises & Orations' and 'Lucretius' in pa: au.insert(au.index('Epicurus') + 1, 'Lucretius')
    if s['name'] == 'Epic & Lyric': au = []
    if au or s['name'] == 'Other': secs.append({**s, 'name': RENAME.get(s['name'], s['name']), 'authors': au})
ha, _, ta = rd('plato', 'hv-authors.html'); wr(P, 'hv-authors.html', ha, {**auth, 'sections': secs}, ta)
hd, _, td = rd('plato', 'hv-section-decor.html'); nd = {RENAME.get(k, k): v for k, v in decor.items() if RENAME.get(k, k) in {s['name'] for s in secs}}
if 'Lives & Moralia' in nd: nd['Lives & Moralia'] = {**nd['Lives & Moralia'], 'era': 'Plutarch · Diogenes Laertius · Philostratus'}
wr(P, 'hv-section-decor.html', hd, nd, td)
j = json.load(open(f'{pd}/scroll.json')); j.pop('reference', None); j['version'] = '5.26'; j['android']['versionName'] = '5.26'; j['android']['versionCode'] = j['android']['versionCode'] + 1
json.dump(j, open(f'{pd}/scroll.json', 'w'), indent=1, ensure_ascii=False)
print('plato sections:', [(s['name'], len(s['authors'])) for s in secs])

# ---- Pantheon Scroll
S = 'pantheon'; n, miss, _ = link_books(S, pan); print('pantheon books linked', n, 'no file', miss)
dd = f'{ROOT}/scrolls/{S}/data'; shutil.rmtree(dd, ignore_errors=True); os.makedirs(dd)
for f in os.listdir(SRC_DATA):
    if re.match(r'(grc-forms|grc-lemmas|hv-lemma|lsj)', f): os.symlink(f'{SRC_DATA}/{f}', f'{dd}/{f}')
hm, m2, tm = rd(S, 'hermes-manifest.html')
books = []
for b in pan:
    b = json.loads(json.dumps(b)); b['meta'].pop('pdf', None); b['meta'].pop('iamb', None); b['meta'].pop('iambDesc', None); books.append(b)
m2['books'] = books; wr(S, 'hermes-manifest.html', hm, m2, tm)
SH = [('Epic & Myth', ['Homer', 'Hesiod', 'Apollonius Rhodius', 'Virgil', 'Ovid', 'Nonnus', 'Apollodorus']),
      ('Lyric & Fable', ['Archilochus', 'Solon', 'Sappho', 'Ibycus', 'Anacreon', 'Simonides', 'Pindar', 'Aesop', 'Callimachus', 'Theocritus', 'Catullus', 'Horace']),
      ('Drama', ['Aeschylus', 'Sophocles', 'Euripides', 'Aristophanes', 'Seneca']),
      ('History', ['Herodotus', 'Thucydides', 'Xenophon', 'Polybius', 'Julius Caesar', 'Sallust', 'Diodorus Siculus', 'Livy', 'Tacitus', 'Josephus', 'Suetonius', 'Arrian', 'Appian', 'Cassius Dio', 'Ammianus Marcellinus']),
      ('Lives, Letters & Travels', ['Plutarch', 'Pliny the Younger', 'Strabo', 'Pausanias', 'Philostratus', 'Lucian', 'Apuleius', 'Julian']),
      ('Orators', ['Lysias', 'Isocrates', 'Demosthenes', 'Aeschines', 'Quintilian']),
      ('Science & the Arts', ['Hippocrates', 'Theophrastus', 'Aristoxenus', 'Euclid', 'Archimedes', 'Aratus', 'Manilius', 'Ptolemy', 'Vitruvius', 'Pliny the Elder', 'Galen', 'Dionysius Thrax', 'Donatus'])]
qa = {b['meta'].get('author') for b in pan}; listed = {a for _, au in SH for a in au}
print('pantheon authors not shelved:', qa - listed, '| shelved but empty:', listed - qa)
ha, a2, ta = rd(S, 'hv-authors.html'); a2['sections'] = [{'name': n, 'authors': [a for a in au if a in qa]} for n, au in SH] + [{'name': 'Other', 'authors': sorted(x for x in qa - listed if x)}]; wr(S, 'hv-authors.html', ha, a2, ta)
dec = {'Epic & Myth': {'id': 'epic', 'glyph': 'lyre', 'era': 'Homer to Nonnus', 'line': 'Sing, goddess, the wrath of Achilles, Peleus’ son.'},
       'Lyric & Fable': {'id': 'lyric', 'glyph': 'lyre', 'era': '7th century BC – 1st century BC', 'line': 'Some say a host of horsemen is the fairest thing on the black earth; but I say it is what one loves.'},
       'Drama': {'id': 'drama', 'glyph': 'theatre', 'era': 'Athens and Rome', 'line': 'Many are the wonders, and none more wonderful than man.'},
       'History': {'id': 'history', 'glyph': 'scroll', 'era': 'Herodotus to Ammianus', 'line': 'A possession for all time.'},
       'Lives, Letters & Travels': {'id': 'lives', 'glyph': 'column', 'era': '1st – 4th century', 'line': 'It is not histories I am writing, but lives.'},
       'Orators': {'id': 'orators', 'glyph': 'tripod', 'era': 'Athens and Rome', 'line': 'Delivery, delivery, delivery.'},
       'Science & the Arts': {'id': 'science', 'glyph': 'star', 'era': 'Hippocrates to Ptolemy', 'line': 'Give me a place to stand, and I will move the earth.'}}
hd, _, td = rd(S, 'hv-section-decor.html'); wr(S, 'hv-section-decor.html', hd, dec, td)
j = json.load(open(f'{ROOT}/scrolls/{S}/scroll.json')); j['data'] = 'data'; j['text']['intro_tagline_end'] = 'Greeks and Romans'
for k, v in list(j['text'].items()):
    if isinstance(v, str): j['text'][k] = v.replace('library of the Greece and Rome', 'library of Greece and Rome')
json.dump(j, open(f'{ROOT}/scrolls/{S}/scroll.json', 'w'), indent=1, ensure_ascii=False)
json.dump({'philosophy': sorted(b['meta']['key'] for b in phil), 'pantheon': sorted(b['meta']['key'] for b in pan), 'elsewhere': sorted(k for k, v in side.items() if v == 'else')}, open(f'{ROOT}/scrolls/plato-split.json', 'w'), indent=0)
