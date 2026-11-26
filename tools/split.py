#!/usr/bin/env python3
"""One-time split: derive engine/shell.html (template) plus per-scroll slot
files and text tokens from two built shells (Plato Scroll and Eastern Scroll).

usage: split.py PLATO_INDEX.html EASTERN_INDEX.html OUT_DIR

Template syntax (rendered by build.py):
  <!--@slot NAME-->   whole element supplied by scrolls/<id>/slots/NAME.html
  {{key}}            text from scrolls/<id>/scroll.json  ("brand" or "text")
"""
import re, sys, os, json, difflib

SLOTS = [  # whole <script>/<style> elements that are per-scroll content
    'hermes-manifest', 'hv-authors', 'hv-section-decor', 'hv-changelog',
    'hv-site-nav', 'hv-enc-dates', 'hv-bd-keys', 'hv-update-js',
    'hermes-encyclopedia', 'hv-scenes-data', 'hv-conc-launcher',
    'hv-lib3d-js', 'hv-intro-css',
]
LAYER_AFTER = 'hv-no-audio'   # where a scroll's own layer (scroll-layer slot) goes
EXTRA_LAYER_IDS = {'es-layer'}
BRAND = {'plato': {'name': 'Plato Scroll'}, 'eastern': {'name': 'Eastern Scroll'}}

# readable token names (by auto key, then by the Plato value's start)
RENAME = {
    'gap1.1': 'build_comment', 'hv-intro-head-js.1': 'webgl_probe',
    'gap7.6': 'favicon', 'gap15.1': 'banner_image',
    'gap15.2': 'footer_links', 'gap15.3': 'footer_links_end',
    'anon5.2': 'covers', 'anon5.3': 'slot_label_langs', 'anon5.4': 'slot_label_rewrite',
    'lib-nav-v2-js.1': 'native_names', 'hv-intro-js.1': 'intro_tagline_end',
    'hv-omni-js.1': 'omni_word_test', 'hv-omni-js.2': 'omni_hint',
    'hv-onboard-js.1': 'welcome_sub', 'hv-onboard-js.2': 'welcome_rows',
    'hv-onboard-js.3': 'welcome_locus_word', 'hv-onboard-js.4': 'welcome_tip',
    'hv-517-js.1': 'parallel_hint', 'hv-517-js.3': 'share_stub_url',
    'hv-tb2-js.1': 'search_examples', 'anon12.2': 'export_site',
}
RENAME_VALUE = [
    ('An Ancient Library', 'subtitle'), ('https://plato-scroll.com/', 'site_url'),
    ('5.25f', 'version'), ('PLATO', 'id_upper'), ('plato', 'id'),
    ('Hellenic philosophy', 'description'),
]
EL = re.compile(r'<(script|style|template)\b([^>]*)>.*?</\1>', re.S)


def segments(s):
    """[(key_or_None, text)] alternating gaps (None) and elements; elements
    without an id get the key anonN (Nth id-less element)."""
    out, pos, anon = [], 0, 0
    for m in EL.finditer(s):
        i = re.search(r'\bid="([^"]+)"', m.group(2))
        if i:
            key = i.group(1)
        else:
            anon += 1
            key = f'anon{anon}'
        out.append((None, s[pos:m.start()]))
        out.append((key, m.group(0)))
        pos = m.end()
    out.append((None, s[pos:]))
    return out


# long string literals / base64 runs are single tokens, so image data diffs fast
MERGE_GAP = 40
TOK = re.compile(r'"[^"\\\n]{200,}"|[A-Za-z0-9+/=]{200,}|[A-Za-z0-9_]+|\s+|[^A-Za-z0-9_\s]')


def tokdiff(a, b, key_prefix, tokens):
    """Return template text for a/b, registering differing hunks in tokens."""
    ta, tb = TOK.findall(a), TOK.findall(b)
    assert ''.join(ta) == a and ''.join(tb) == b
    sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    # merge hunks separated by short equal runs, so one sentence = one token
    hunks = []  # [i1,i2,j1,j2]
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        if hunks and len(''.join(ta[hunks[-1][1]:i1])) < MERGE_GAP:
            hunks[-1][1] = i2; hunks[-1][3] = j2
        else:
            hunks.append([i1, i2, j1, j2])
    out, n, pa = [], 0, 0
    for i1, i2, j1, j2 in hunks:
        out.append(''.join(ta[pa:i1]))
        n += 1
        k = f'{key_prefix}.{n}'
        va, vb = ''.join(ta[i1:i2]), ''.join(tb[j1:j2])
        # keep text the two share at either end in the template
        pre = os.path.commonprefix([va, vb])
        suf = os.path.commonprefix([va[len(pre):][::-1], vb[len(pre):][::-1]])[::-1]
        w = lambda c: c.isalnum() or c == '_'
        while pre and w(pre[-1]) and len(va) > len(pre) and w(va[len(pre)]) or \
                pre and w(pre[-1]) and len(vb) > len(pre) and w(vb[len(pre)]):
            pre = pre[:-1]          # never cut inside a word
        suf = os.path.commonprefix([va[len(pre):][::-1], vb[len(pre):][::-1]])[::-1]
        while suf and w(suf[0]) and len(va) - len(suf) > len(pre) and w(va[-len(suf) - 1]) or \
                suf and w(suf[0]) and len(vb) - len(suf) > len(pre) and w(vb[-len(suf) - 1]):
            suf = suf[1:]
        va, vb = va[len(pre):len(va) - len(suf)], vb[len(pre):len(vb) - len(suf)]
        tokens[k] = {'plato': va, 'eastern': vb}
        out.append(pre + '{{' + k + '}}' + suf)
        pa = i2
    out.append(''.join(ta[pa:]))
    return ''.join(out)


def main(pp, ep, outd):
    P = open(pp, encoding='utf-8').read()
    E = open(ep, encoding='utf-8').read()
    assert '{{' not in P and '{{' not in E
    sp, se = segments(P), segments(E)
    # pull the Eastern-only layer out, remembering it as a slot
    layers = {'plato': '', 'eastern': ''}
    se2 = []
    for idx, (i, t) in enumerate(se):
        if i in EXTRA_LAYER_IDS:
            layers['eastern'] = se2.pop()[1] + t   # preceding gap belongs to it
            continue
        se2.append((i, t))
    # merge gap that followed the layer with the gap before it
    merged = []
    for i, t in se2:
        if merged and i is None and merged[-1][0] is None:
            merged[-1] = (None, merged[-1][1] + t)
        else:
            merged.append((i, t))
    se = merged
    ida = [i for i, _ in sp]; idb = [i for i, _ in se]
    assert ida == idb, 'segment structure differs'

    slots = {'plato': {}, 'eastern': {}}
    tokens = {}
    tpl = []
    gapn = 0
    for (i, a), (_, b) in zip(sp, se):
        if i in SLOTS:
            slots['plato'][i] = a; slots['eastern'][i] = b
            tpl.append(f'<!--@slot {i}-->')
        else:
            na = a.replace(BRAND['plato']['name'], '{{name}}')
            nb = b.replace(BRAND['eastern']['name'], '{{name}}')
            if i is None:
                gapn += 1
            key = i if i else f'gap{gapn}'
            tpl.append(na if na == nb else tokdiff(na, nb, key, tokens))
        if i == LAYER_AFTER:
            tpl.append('<!--@slot scroll-layer-->')
    slots['plato']['scroll-layer'] = layers['plato']
    slots['eastern']['scroll-layer'] = layers['eastern']

    # --- give tokens readable names; identical value pairs share one name ---
    tpl = ''.join(tpl)
    names, pairkey = {}, {}
    used = set(['name'])
    for k, v in tokens.items():
        pair = (v['plato'], v['eastern'])
        if pair in pairkey:
            names[k] = pairkey[pair]; continue
        base = RENAME.get(k) or next((n for pre, n in RENAME_VALUE if v['plato'].startswith(pre)), None) or k
        nm, c = base, 1
        while nm in used:
            c += 1; nm = f'{base}_{c}'
        used.add(nm); names[k] = pairkey[pair] = nm
    tpl = re.sub(r'\{\{([^{}]+)\}\}', lambda m: '{{' + names.get(m.group(1), m.group(1)) + '}}', tpl)
    tokens = {names[k]: v for k, v in tokens.items()}
    tokens['name'] = {sc: BRAND[sc]['name'] for sc in BRAND}

    os.makedirs(f'{outd}/engine', exist_ok=True)
    open(f'{outd}/engine/shell.html', 'w', encoding='utf-8').write(tpl)
    for sc in ('plato', 'eastern'):
        d = f'{outd}/scrolls/{sc}/slots'
        os.makedirs(d, exist_ok=True)
        for k, v in slots[sc].items():
            open(f'{d}/{k}.html', 'w', encoding='utf-8').write(v)
        text = {}
        for k, v in tokens.items():
            val = v[sc]
            if len(val) > 400:   # long values live in files
                fn = f'text/{k}.txt'
                os.makedirs(f'{outd}/scrolls/{sc}/text', exist_ok=True)
                open(f'{outd}/scrolls/{sc}/{fn}', 'w', encoding='utf-8').write(val)
                text[k] = {'file': fn}
            else:
                text[k] = val
        cp = f'{outd}/scrolls/{sc}/scroll.json'
        cfg = json.load(open(cp, encoding='utf-8')) if os.path.exists(cp) else {'id': sc}
        cfg['name'] = text.pop('name'); cfg['version'] = text.pop('version')
        cfg['text'] = text   # other keys (android, books…) are kept
        json.dump(cfg, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('template', len(tpl), 'tokens', len(tokens))
    for k, v in tokens.items():
        print(k, repr(v['plato'][:70]), '->', repr(v['eastern'][:70]))


if __name__ == '__main__':
    main(*sys.argv[1:4])
