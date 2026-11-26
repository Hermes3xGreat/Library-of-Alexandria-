#!/usr/bin/env python3
"""Bring a new Plato Scroll build into the shared engine, so every Scroll
gets the reader's new code.

usage: ingest.py NEW_PLATO_index.html [--dry-run]

How it works: the current engine rendered as Plato Scroll is the "old" build.
Each part of the page (every <script>/<style> element and the markup between
them) is compared with the new build:
  * unchanged parts keep their engine text (with all the per-scroll {{tokens}});
  * Plato's own content blocks (manifest, encyclopedia, …) go to scrolls/plato/slots;
  * changed engine parts are taken from the new build and every {{token}} is put
    back where its text (plus surrounding context) is found again;
  * new parts are added with "Plato Scroll" turned into {{name}}.
Anything that can't be placed is listed at the end — those spots will show
Plato's wording in the other Scrolls until a token is added by hand.
Afterwards the engine must render the new build byte for byte, or nothing is written.
"""
import os, re, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from split import segments, SLOTS
import build

PH = re.compile(r'\{\{([\w.-]+)\}\}|<!--@slot ([\w-]+)-->')


def keyed(segs):
    """[(key, gap_before, element)], final_gap"""
    out, gap = [], ''
    for k, t in segs:
        if k is None:
            gap = t
        else:
            out.append((k, gap, t)); gap = ''
    return out, gap


def tpl_segments(tpl):
    t = re.sub(r'<!--@slot ((?!scroll-layer)[\w-]+)-->', r'<template id="@slot:\1"></template>', tpl)
    return segments(t)


def untpl(x):
    return re.sub(r'<template id="@slot:([\w-]+)"></template>', r'<!--@slot \1-->', x)


def render_piece(t, vals):
    """rendered text and [(start, end, placeholder_text)] for a template piece."""
    out, spans, pos = [], [], 0
    n = 0
    for m in PH.finditer(t):
        out.append(t[pos:m.start()]); n += len(t[pos:m.start()])
        v = vals[m.group(1)] if m.group(1) else ''
        spans.append((n, n + len(v), m.group(0)))
        out.append(v); n += len(v); pos = m.end()
    out.append(t[pos:])
    return ''.join(out), spans


OVERRIDE = {}   # token -> its value in the new build (version, build comment)


def retemplate(t, new, vals, where, report):
    old, spans = render_piece(t, vals)
    found = []
    for s, e, ph in spans:
        v = old[s:e]; hit = None
        k = ph[2:-2] if ph.startswith('{{') else None
        if k in OVERRIDE:
            v = OVERRIDE[k]
        for L in (80, 40, 20, 10):
            left, right = old[max(0, s - L):s], old[e:e + L]
            needle = left + v + right
            i = new.find(needle)
            if i >= 0 and new.find(needle, i + 1) < 0:
                hit = (i + len(left), i + len(left) + len(v), ph); break
        if hit:
            found.append(hit)
        elif ph != '{{name}}':
            report.append(f'{where}: could not place {ph} (Plato text: {v[:60]!r})')
    found.sort()
    out, pos = [], 0
    for s, e, ph in found:
        if s < pos:
            continue
        out.append(new[pos:s].replace('Plato Scroll', '{{name}}')); out.append(ph); pos = e
    out.append(new[pos:].replace('Plato Scroll', '{{name}}'))
    return ''.join(out)


def main():
    newp = sys.argv[1]; dry = '--dry-run' in sys.argv
    NEW = open(newp, encoding='utf-8').read()
    cfg = build.load_scroll('plato')
    tpl = open(os.path.join(ROOT, 'engine', 'shell.html'), encoding='utf-8').read()
    OLD = build.render(cfg)
    vals = build.token_values(cfg)
    # a new build carries its own version in the comment on line 2
    m = re.match(r'<!DOCTYPE html>\n<!-- (build (\S+?)-\d{4}-\d\d-\d\d[^>]*?) -->', NEW)
    newmeta = {}
    if m:
        newmeta = {'build_comment': m.group(1), 'version': m.group(2)}
        OVERRIDE.update(newmeta)
    old_vals = dict(vals)
    T, tg = keyed(tpl_segments(tpl)); O, og = keyed(segments(OLD)); N, ng = keyed(segments(NEW))
    tmap = {k: (g, e) for k, g, e in T}
    omap = {k: (g, e) for k, g, e in O}
    # template keys use @slot:NAME for slot elements
    def tkey(k): return f'@slot:{k}' if k in SLOTS else k
    report, parts, slots_out, changed = [], [], {}, 0
    for k, g, e in N:
        tk = tkey(k)
        # gap before the element
        if k in omap and tk in tmap:
            og_, tg_ = omap[k][0], tmap[tk][0]
            parts.append(tg_ if og_ == g else retemplate(tg_, g, vals, f'markup before {k}', report))
        else:
            parts.append(g.replace('Plato Scroll', '{{name}}'))
        if k in SLOTS:
            slots_out[k] = e; parts.append(f'<!--@slot {k}-->')
        elif k in omap and tk in tmap:
            if omap[k][1] == e:
                parts.append(tmap[tk][1])
            else:
                changed += 1
                parts.append(retemplate(tmap[tk][1], e, vals, k, report))
        else:
            report.append(f'new block {k}: added as shared code')
            parts.append(e.replace('Plato Scroll', '{{name}}'))
    parts.append(tg if og == ng else retemplate(tg, ng, vals, 'markup at the end', report))
    for k in omap:
        if k not in {x[0] for x in N}:
            report.append(f'block {k} is gone from the new build (removed from the engine)')
    newtpl = untpl(''.join(parts))
    cfgp = os.path.join(cfg['_dir'], 'scroll.json')
    cfg_raw = open(cfgp, encoding='utf-8').read()
    if newmeta:
        cj = json.loads(cfg_raw); cj['version'] = newmeta['version']; cj['text']['build_comment'] = newmeta['build_comment']
        open(cfgp, 'w', encoding='utf-8').write(json.dumps(cj, ensure_ascii=False, indent=2))

    # verify: new engine + Plato's slots must give the new build exactly
    tplpath = os.path.join(ROOT, 'engine', 'shell.html')
    backup = {}
    sd = os.path.join(cfg['_dir'], 'slots')
    try:
        backup['tpl'] = tpl
        open(tplpath, 'w', encoding='utf-8').write(newtpl)
        for k, v in slots_out.items():
            p = os.path.join(sd, k + '.html')
            backup[p] = open(p, encoding='utf-8').read() if os.path.exists(p) else None
            open(p, 'w', encoding='utf-8').write(v)
        ok = build.render(build.load_scroll('plato')) == NEW
    finally:
        if dry or not locals().get('ok'):
            open(tplpath, 'w', encoding='utf-8').write(backup['tpl'])
            open(cfgp, 'w', encoding='utf-8').write(cfg_raw)
            for p, v in backup.items():
                if p != 'tpl':
                    if v is None: os.remove(p)
                    else: open(p, 'w', encoding='utf-8').write(v)
    print(f'{changed} shared blocks changed; render check:', 'OK' if ok else 'FAILED (nothing written)')
    for r in report:
        print(' -', r)
    if ok and not dry:
        print('engine/shell.html and scrolls/plato/slots updated')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
