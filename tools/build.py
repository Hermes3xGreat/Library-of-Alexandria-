#!/usr/bin/env python3
"""Build one Scroll app from the shared engine.

usage:
  build.py SCROLL_ID [--out dist] [--html-only]
           [--apk --keystore FILE --storepass PASS [--keypass PASS]]
           [--code N] [--books DIR]

Writes dist/<id>/index.html, dist/<id>/<id>-<version>-web.zip and, with
--apk, dist/<id>/<Name>-<version>.apk signed with the given keystore
(the alias comes from scroll.json -> android.alias).
"""
import json, os, re, sys, zipfile, shutil, subprocess, argparse, hashlib, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from axml import Manifest

SLOT_RE = re.compile(r'<!--@slot ([\w-]+)-->')
TOKEN_RE = re.compile(r'\{\{([\w.-]+)\}\}')


def load_scroll(sid):
    d = os.path.join(ROOT, 'scrolls', sid)
    cfg = json.load(open(os.path.join(d, 'scroll.json'), encoding='utf-8'))
    cfg['_dir'] = d
    return cfg


def token_values(cfg):
    vals = {'name': cfg['name'], 'version': cfg['version']}
    for k, v in cfg.get('text', {}).items():
        if isinstance(v, dict):
            v = open(os.path.join(cfg['_dir'], v['file']), encoding='utf-8').read()
        vals[k] = v
    # values may themselves mention {{name}} etc. (one level)
    for k in vals:
        vals[k] = TOKEN_RE.sub(lambda m: vals.get(m.group(1), m.group(0)) if m.group(1) != k else m.group(0), vals[k])
    return vals


def addons(cfg, html):
    """engine add-ons shared by every Scroll; the Plato reference build stays byte-identical without them."""
    if cfg.get('reference'):
        return html
    d = os.path.join(ROOT, 'engine', 'addons'); js = ''
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith('.js'): js += '<script data-addon="' + f[:-3] + '">' + open(os.path.join(d, f), encoding='utf-8').read() + '</script>'
    i = html.lower().find('<head'); j = html.find('>', i) + 1
    return html[:j] + js + html[j:] if js else html


def render(cfg):
    tpl = open(os.path.join(ROOT, 'engine', 'shell.html'), encoding='utf-8').read()
    vals = token_values(cfg)
    missing = sorted(set(TOKEN_RE.findall(tpl)) - set(vals))
    if missing:
        sys.exit(f'scroll.json is missing text keys: {missing}')
    html = TOKEN_RE.sub(lambda m: vals[m.group(1)], tpl)

    def slot(m):
        for base in (os.path.join(cfg['_dir'], 'slots'), os.path.join(ROOT, 'engine', 'default-slots')):
            p = os.path.join(base, m.group(1) + '.html')
            if os.path.exists(p):
                return open(p, encoding='utf-8').read()
        sys.exit(f'no slot file for {m.group(1)}')
    return addons(cfg, SLOT_RE.sub(slot, html))


def asset_files(cfg, books_override=None):
    """[(path_in_app, source_file)] for books/ and data/."""
    out = []
    for key, sub in (('books', 'books'), ('data', 'data')):
        rel = cfg.get(key)
        if not rel:
            continue
        src = books_override if (key == 'books' and books_override) else os.path.join(cfg['_dir'], rel)
        if not os.path.isdir(src):
            sys.exit(f'{key} folder not found: {src}')
        for dp, _, fs in os.walk(src):
            for f in sorted(fs):
                full = os.path.join(dp, f)
                out.append((sub + '/' + os.path.relpath(full, src).replace(os.sep, '/'), full))
    return sorted(out)


def build_web(cfg, html, assets, outd):
    z = os.path.join(outd, f"{cfg['id']}-scroll-{cfg['version']}-web.zip")
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('index.html', html)
        for arc, src in assets:
            zf.write(src, arc)
        extras = os.path.join(cfg['_dir'], cfg.get('web_extras') or 'web')
        if os.path.isdir(extras):
            for dp, _, fs in os.walk(extras):
                for f in fs:
                    full = os.path.join(dp, f)
                    zf.write(full, os.path.relpath(full, extras).replace(os.sep, '/'))
    return z


def find_signer():
    """uber-apk-signer.jar in tools/bin, or apksigner (Android build-tools) on PATH."""
    jar = os.path.join(ROOT, 'tools', 'bin', 'uber-apk-signer.jar')
    if os.path.exists(jar):
        return ('uber', jar)
    if shutil.which('apksigner') and shutil.which('zipalign'):
        return ('apksigner', None)
    if shutil.which('jarsigner'):
        return ('builtin', os.path.join(ROOT, 'tools', 'apksign.py'))   # v1 + v2, PKCS12 keystore
    return (None, None)


def build_apk(cfg, html, assets, outd, a):
    an = cfg['android']
    base = os.path.join(cfg['_dir'], 'android', 'base.apk')
    if not os.path.exists(base):
        sys.exit(f'no Android base for {cfg["id"]}: run tools/make_base.py on an existing APK')
    code = a.code or an['versionCode']
    unsigned = os.path.join(outd, 'unsigned.apk')
    with zipfile.ZipFile(base) as zb, zipfile.ZipFile(unsigned, 'w') as zo:
        for info in zb.infolist():
            data = zb.read(info)
            if info.filename == 'AndroidManifest.xml':
                m = Manifest(data); g = m.get()
                if g.get('versionCode') != int(code) or g.get('versionName') != an['versionName']:
                    m.set(code, an['versionName']); data = bytes(m.d)
            ni = zipfile.ZipInfo(info.filename, info.date_time)
            ni.compress_type = info.compress_type
            ni.external_attr = info.external_attr
            zo.writestr(ni, data)
        zo.writestr(zipfile.ZipInfo('assets/index.html', (2026, 1, 1, 0, 0, 0)), html.encode('utf-8'),
                    compress_type=zipfile.ZIP_DEFLATED)
        for arc, src in assets:
            zo.write(src, 'assets/' + arc, compress_type=zipfile.ZIP_DEFLATED)
    final = os.path.join(outd, f"{an['label'].replace(' ', '')}-{an['versionName']}.apk")
    kind, jar = find_signer()
    if not (a.keystore and a.storepass) or not kind:
        out = final[:-4] + '-unsigned.apk'
        shutil.move(unsigned, out)
        why = 'no keystore given' if not (a.keystore and a.storepass) else 'no signer found'
        print(f'APK left unsigned ({why}). Sign it on your computer with:\n'
              f'  zipalign -f 4 {os.path.basename(out)} aligned.apk\n'
              f'  apksigner sign --ks <keystore> --ks-key-alias {an["alias"]} --out {os.path.basename(final)} aligned.apk\n'
              f'or put uber-apk-signer.jar in tools/bin and pass --keystore/--storepass.')
        return out, code
    if kind == 'uber':
        tmpd = os.path.join(outd, 'sign-tmp')
        shutil.rmtree(tmpd, ignore_errors=True)
        cmd = ['java', '-jar', jar, '-a', unsigned, '-o', tmpd,
               '--ks', a.keystore, '--ksAlias', an['alias'], '--ksPass', a.storepass,
               '--ksKeyPass', a.keypass or a.storepass]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode:
            sys.exit('signing failed:\n' + r.stdout[-2000:] + r.stderr[-2000:])
        shutil.move(glob.glob(os.path.join(tmpd, '*.apk'))[0], final)
        shutil.rmtree(tmpd)
    elif kind == 'builtin':
        r = subprocess.run([sys.executable, jar, unsigned, final, '--ks', a.keystore, '--alias', an['alias'],
                            '--pass=' + a.storepass], capture_output=True, text=True)
        if r.returncode:
            sys.exit('signing failed:\n' + r.stdout[-2000:] + r.stderr[-2000:])
    else:
        aligned = unsigned + '.aligned'
        subprocess.run(['zipalign', '-f', '4', unsigned, aligned], check=True)
        subprocess.run(['apksigner', 'sign', '--ks', a.keystore, '--ks-key-alias', an['alias'],
                        '--ks-pass', 'pass:' + a.storepass, '--key-pass', 'pass:' + (a.keypass or a.storepass),
                        '--out', final, aligned], check=True)
        os.remove(aligned)
    os.remove(unsigned)
    return final, code


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scroll'); ap.add_argument('--out', default=os.path.join(ROOT, 'dist'))
    ap.add_argument('--html-only', action='store_true'); ap.add_argument('--books')
    ap.add_argument('--apk', action='store_true'); ap.add_argument('--keystore')
    ap.add_argument('--storepass'); ap.add_argument('--keypass'); ap.add_argument('--code', type=int)
    a = ap.parse_args()
    cfg = load_scroll(a.scroll)
    outd = os.path.join(a.out, cfg['id']); os.makedirs(outd, exist_ok=True)
    html = render(cfg)
    p = os.path.join(outd, 'index.html')
    open(p, 'w', encoding='utf-8').write(html)
    print('index.html', len(html.encode()), hashlib.sha256(html.encode()).hexdigest()[:16])
    if a.html_only:
        return
    assets = asset_files(cfg, a.books)
    print('web zip', build_web(cfg, html, assets, outd))
    if a.apk:
        f, code = build_apk(cfg, html, assets, outd, a)
        print('apk', f, 'versionCode', code)


if __name__ == '__main__':
    main()
