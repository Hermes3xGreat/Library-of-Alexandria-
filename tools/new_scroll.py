#!/usr/bin/env python3
"""Start a new Scroll.

usage: new_scroll.py ID --name "Hermetic Scroll" --package com.hermeticscroll.app
                     [--subtitle "A Library of the Hermetic Tradition"]
                     [--tagline "Hermetic tradition"]  (start screen: "The library of the …")
                     [--description "the Hermetic tradition: the Corpus Hermeticum, …"]
                     [--search "Hermes, the Chaldean Oracles"]
                     --color '#4a2c7a' --glyph ☿ [--initials ΕΤ] [--from eastern]

Copies the --from Scroll (default eastern: no Greek-only features), empties its
library, rebrands the Android base (new package, label, version 0.1 / code 1)
draws the mark, banner, favicon and launcher icons in the Plato Scroll style with
the new colour, symbol and initials (tools/brand.py), and gives the Scroll its
own starter background (engine/backgrounds/starter.js: an astrolabe in its
colour with its symbol, laid out from its id) until a bespoke one replaces
slots/hv-lib3d-js.html. Then add books (tools/add_book.py) and build
(tools/build.py ID).
"""
import os, sys, json, shutil, argparse, zipfile, subprocess, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from axml import Manifest


def wjson(path, obj, el_id, typ='application/json'):
    open(path, 'w', encoding='utf-8').write(
        f'<script id="{el_id}" type="{typ}">' + json.dumps(obj, ensure_ascii=False, separators=(',', ': ')) + '</script>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('id'); ap.add_argument('--name', required=True); ap.add_argument('--package', required=True)
    ap.add_argument('--subtitle'); ap.add_argument('--tagline'); ap.add_argument('--description')
    ap.add_argument('--search'); ap.add_argument('--color', required=True); ap.add_argument('--glyph', required=True)
    ap.add_argument('--initials', default=''); ap.add_argument('--from', dest='src', default='eastern')
    a = ap.parse_args()
    src, dst = os.path.join(ROOT, 'scrolls', a.src), os.path.join(ROOT, 'scrolls', a.id)
    if os.path.exists(dst):
        sys.exit(f'{dst} already exists')
    os.makedirs(dst)
    for sub in ('slots', 'text'):
        shutil.copytree(os.path.join(src, sub), os.path.join(dst, sub))
    os.makedirs(os.path.join(dst, 'books'))
    cfg = json.load(open(os.path.join(src, 'scroll.json'), encoding='utf-8'))
    topic = a.tagline or a.name.replace(' Scroll', '')
    subtitle = a.subtitle or f'A Library of the {topic}'
    desc = a.description or f'the {topic}.'
    plato = json.load(open(os.path.join(ROOT, 'scrolls', 'plato', 'scroll.json'), encoding='utf-8'))['text']
    t = cfg['text']
    t.update({
        'build_comment': '{{name}} {{version}} · built on the shared Scroll engine',
        'subtitle': subtitle, 'description': desc, 'description_2': desc,
        'description_3': desc + '"><meta name="theme-color" content="' + a.color,
        'covers': '', 'native_names': plato['native_names'],
        'intro_tagline_end': topic,
        'welcome_sub': f'library of the {topic}',
        'welcome_rows': '&#8644;</span><span class="ob-tx"><b>Compare.</b> Where a work has a second '
                        'translation or its original text, the parallel button in the reader sets them side by side '
                        '&mdash; the two columns move as one.</span></div><div class="ob-row"><span class="ob-ic">1.1',
        'search_examples': a.search or 'a title, an author',
        'id': a.id, 'id_upper': a.id.upper(),
    })
    src_color = cfg.get('icon_color') or cfg.get('color')   # the copied Android base still has it
    cfg.update({'id': a.id, 'name': a.name, 'version': '0.1', 'color': a.color, 'glyph': a.glyph,
                'initials': a.initials, 'icon_color': src_color, 'mark_width': cfg.get('mark_width', 1.1), 'books': 'books', 'data': None,
                'android': {'package': a.package, 'label': a.name, 'versionCode': 1, 'versionName': '0.1',
                            'alias': a.id + 'scroll'}})
    json.dump(cfg, open(os.path.join(dst, 'scroll.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    # empty library
    sd = os.path.join(dst, 'slots')
    wjson(f'{sd}/hermes-manifest.html', {'type': 'hermes-manifest', 'version': 1, 'books': []}, 'hermes-manifest')
    wjson(f'{sd}/hv-authors.html', {'sections': [{'name': 'Other', 'authors': []}]}, 'hv-authors')
    wjson(f'{sd}/hv-section-decor.html', {}, 'hv-section-decor')
    wjson(f'{sd}/hermes-encyclopedia.html', [], 'hermes-encyclopedia')
    wjson(f'{sd}/hv-changelog.html', [{'version': '0.1', 'items': [{'t': f'{a.name} opens'}]}], 'hv-changelog')
    nav = open(f'{sd}/hv-site-nav.html', encoding='utf-8').read()
    nav = re.sub(r'"colophon": "[^"]*"', f'"colophon": "{a.name}. Translations drawn from the public domain; free to read, offline, on every device."', nav)
    open(f'{sd}/hv-site-nav.html', 'w', encoding='utf-8').write(nav)
    for f in ('scroll-layer.html',):   # the source Scroll's own CSS layer stays (hides the encyclopedia etc.)
        pass
    # Android base with a new package id and label
    ad = os.path.join(dst, 'android'); os.makedirs(ad)
    with zipfile.ZipFile(os.path.join(src, 'android', 'base.apk')) as zi, \
            zipfile.ZipFile(os.path.join(ad, 'base.apk'), 'w') as zo:
        for info in zi.infolist():
            data = zi.read(info)
            if info.filename == 'AndroidManifest.xml':
                m = Manifest(data); m.rebrand(a.package, a.name); m.set(1, '0.1'); data = bytes(m.d)
            ni = zipfile.ZipInfo(info.filename, info.date_time)
            ni.compress_type = info.compress_type; ni.external_attr = info.external_attr
            zo.writestr(ni, data)
    # its own background, never another Scroll's
    bg = open(os.path.join(ROOT, 'engine', 'backgrounds', 'starter.js'), encoding='utf-8').read()
    bg = bg.replace('__BG_CONFIG__', json.dumps({'id': a.id, 'color': a.color, 'glyph': a.glyph}, ensure_ascii=False))
    open(os.path.join(sd, 'hv-lib3d-js.html'), 'w', encoding='utf-8').write('<script id="hv-lib3d-js">' + bg + '</script>')
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'brand.py'), a.id], check=True)
    print(f'scrolls/{a.id} ready. Signing key for it (once, keep it safe):\n'
          f'  keytool -genkeypair -keystore {a.id}-scroll.keystore -alias {a.id}scroll '
          f'-keyalg RSA -keysize 4096 -validity 36500')


if __name__ == '__main__':
    main()
