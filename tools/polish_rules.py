# flake8: noqa  per-book end matter, front matter and one-off fixes. This file is not a module:
# polish.py runs it inside its own namespace, so re, H, PRE, BOOK, TAIL and the helpers come from there.
def _eq_hdr(a):
    return [({'sp': 'HDR', 't': x['t'].strip('=')} if re.fullmatch(r'=[^=]{2,80}=', x['t']) else x) for x in a]
def _drop(pat):
    return lambda a: [x for x in a if H(x) or not re.search(pat, x['t'])]
def _strip(pat, rep=''):
    return lambda a: [dict(x, t=re.sub(pat, rep, x['t'])) for x in a]
PRE.update({
    'quran-rodwell': lambda a: b_quran([dict(x) for x in cut_between(a, r'^_{5,}')]),
    'hopi-unwritten-literature': _eq_hdr,
    'tocqueville-democracy-1': lambda a: [x for x in a if not x['t'].startswith('Book One Introductory Chapter Chapter I') and not re.match(r'^[a-z]{1,2} \[', x['t']) and not (x['t'].startswith('[') and x['t'].endswith(']') and not H(x))],
    'amarna-letters': lambda a: [({'sp': 'HDR', 't': x['t']} if re.fullmatch(r'The Hittite Invasion Of Damascus|The Amorite Treachery|The War In Phœnicia|Northern Palestine|Southern Palestine|Royal Letters|SUYARDATA.S LETTERS.*', x['t']) else x) for x in a],
    'bede-ecclesiastical-history': _strip(r'\((\d{1,4})\)'),
    'rumi-mesnevi': _strip(r'\s\d{1,3}$'),
    'riis-other-half': lambda a: [x for x in a if not re.match(r'^p\. \d+ ', x['t'])],
    'bible-kjv-ot': lambda a: [x for x in a if x['t'] not in ('***', 'The New Testament of the King James Bible')],
    'song-of-roland': lambda a: [dict(x, t='So ends the tale which Turold hath conceived.') if x['t'].startswith('SO ENDS THE TALE') else x for x in a],
    'paine-american-crisis': lambda a: a,
    'rowlandson-captivity': lambda a: a,
})
TAIL.update({
    'ptahhotep-instruction': [r'^A ceremonial title applied to'],
    'julian-revelations': [r'^Glossary$'], 'mabinogion': [r'^Footnotes$'],
    'morte-darthur-1': [r'^GLOSSARY'], 'morte-darthur-2': [r'^GLOSSARY'],
    'parzival-2': [r'^Appendices'], 'parzival-1': [r'^Appendices'],
    'shahnameh': [r'^\[FOOTNOTES to'], 'cherokee-myths': [r'^VI--Notes and Parallels'],
    'cherokee-sacred-formulas': [r'^Index\.$'], 'eskimo-folk-tales': [r'^Note\.--The particular sources'],
    'popol-vuh': [r'^Bibliographical Appendix'], 'schoolcraft-hiawatha': [r'^Wild Notes of the Pibbigwun'],
    'sioux-myths': [r'^Note: I have made the following changes'], 'zuni-folk-tales': [r'^Transcriber.s note'],
    'addams-hull-house': [r'^This chapter has been put on-line'], 'sojourner-truth': [r'^This book is put on-line'],
    'inaugural-addresses': [r'^Notes--Presidents Who Were Not Inaugurated'], 'riis-other-half': [r"^Transcriber.s Note"],
    'tocqueville-democracy-2': [r'^Part I\.$'], 'budge-legends-of-the-gods': [r'^End of Project'],
})

# ---- Africa Scroll
def _sancho(a):
    out = []
    for x in a:
        if H(x) and ' — To ' in x['t']:
            h, to = x['t'].split(' — ', 1); out.append({'sp': 'HDR', 't': h}); out.append({'sp': 'N', 't': '<i>' + titlecase(to) + '</i>'})
        else: out.append(x)
    return out
def _lead(a):
    return [dict(x, t=re.sub(r'^([A-Z]{2,})(?=[ ,])', lambda m: m.group(1).capitalize(), x['t'])) if not H(x) else x for x in a]
def _roman_hdr(a):
    for x in a:
        if H(x): x['t'] = re.sub(r'^([IVXL]+) (\w)', lambda m: m.group(1) + ' — ' + m.group(2).upper(), x['t'])
    return [x for x in a if x['t'] != 'MILLER']
PRE.update({
    'sancho-letters': _sancho, 'park-travels-1': _lead, 'park-travels-2': _lead,
    'plaatje-native-life': lambda a: [dict(x, t=re.sub(r'^(Chapter [IVXL]+)\s+', r'\1 — ', x['t'])) if H(x) else x for x in a],
    'theal-kaffir-folk-lore': lambda a: [dict(x, t='Introduction — The People and Their Customs') if H(x) and x['t'].startswith('Kaffir Folk') else x for x in a],
})
BOOK.update({'du-bois-the-negro': _roman_hdr})
TAIL.update({'plaatje-native-life': [r'^\[?(Original )?Advertisements']})
BOOK.update({'plaatje-native-life': lambda a: caps_to_hdr(a, 20, r'Epilogue')})

# ---- Descartes Scroll (modern philosophy)
PRE.update({
    'emerson-essays-1': lambda a: [x for x in a if x['t'] != 'Next Volume'],
    'kierkegaard-selections': lambda a: [({'sp': 'HDR', 't': 'Diapsalmata'} if x['t'] == 'DIAPSALMATA' else x) for x in a],
    'descartes-meditations': lambda a: [dict(x, t=re.sub(r'^Meditat\. ([IVX]+)\.?$', r'Meditation \1', x['t'])) if H(x) else x for x in a],
    'locke-second-treatise': lambda a: [dict(x, t=x['t'].replace('Chapter. ', 'Chapter ')) if H(x) else x for x in a],
    'hume-enquiry-morals': _lead, 'nietzsche-beyond-good-and-evil': _lead, 'hume-dialogues-religion': lambda a: a,
})

# ---- second batch for Egyptian and Africa
TAIL.update({
    'budge-future-life': [r'^Printed BALLANTYNE'], 'weigall-akhnaton': [r'^SURVEY DEP\. CAIRO'],
    'dayrell-ikom-folk-stories': [r'^(<i>)?Fig\. 1\.'], 'cronise-cunnie-rabbit': [r'^Obvious printer errors'],
    'budge-literature-egyptians': [r'^Editions of Egyptian Texts|^EDITIONS OF EGYPTIAN'],
})
BOOK.update({'dayrell-ikom-folk-stories': lambda a: [dict(x, t=re.sub(r'^([IVXL]+)\. — ', r'\1. ', x['t'])) if H(x) else x for x in a]})
