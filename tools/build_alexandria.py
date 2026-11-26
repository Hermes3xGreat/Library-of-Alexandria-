#!/usr/bin/env python3
"""The Library of Alexandria: one app that houses every Scroll as a module.
Each module is the Scroll's own page (its background, chime, colours and
shelves) under modules/<id>/, with its saved data kept apart from the others;
index.html is the entrance hall.
usage: build_alexandria.py --out DIR [--apk --keystore K --storepass P]"""
import os, re, sys, json, zipfile, shutil, subprocess, argparse, base64, io
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
import build as B
from axml import Manifest
VERSION = '2.0'; CODE = 11
MODULES = [  # scroll folder, module id, wing
    ('plato-philosophy', 'plato', 'Philosophy'), ('descartes', 'descartes', 'Philosophy'),
    ('pantheon', 'pantheon', 'Greece & Rome'), ('egyptian', 'egyptian', 'The Ancient World'), ('crescent', 'crescent', 'The Ancient World'),
    ('eastern', 'eastern', 'East & North'), ('northern', 'northern', 'East & North'),
    ('africa', 'africa', 'Africa & the Americas'), ('americas', 'americas', 'Africa & the Americas'), ('liberty', 'liberty', 'Africa & the Americas')]
BLURB = {'plato': 'Ancient philosophy: Plato, Aristotle, the Stoics, the Platonists and the Hermetica.', 'descartes': 'Modern philosophy from Machiavelli and Descartes to Nietzsche and William James.',
         'pantheon': 'Homer and Virgil, the dramatists, historians, orators and sciences of Greece and Rome.', 'egyptian': 'The Book of the Dead, hymns, tales and the Greek writers on Egypt.',
         'crescent': 'Babylon, Persia, Arabia and the Bible: Gilgamesh, the Shahnameh, the Qur’an, the King James Bible.', 'eastern': 'The Vedas, Upanishads and Mahabharata, the Buddhist canon, the Tao Te Ching.',
         'northern': 'The Eddas and sagas, Beowulf, Arthur, Dante and the medieval mystics.', 'africa': 'Folk tales of the continent, Augustine, Equiano, Plaatje and the travellers.',
         'americas': 'The Popol Vuh, the Conquest, and the sacred stories of the first nations.', 'liberty': 'American history: the founding documents, presidents, explorers and reformers.'}

SHIM = r'''<style>#hv-onboard{display:none!important}</style><script>/* Library of Alexandria: keep this Scroll's saved data apart from the others, and add the way back */
(function(){var P='alx:%ID%:';try{var ls=window.localStorage,keys=function(){var o=[];for(var i=0;i<ls.length;i++){var k=ls.key(i);if(k&&k.indexOf(P)===0)o.push(k.slice(P.length));}return o;};
var w={getItem:function(k){return ls.getItem(P+k);},setItem:function(k,v){ls.setItem(P+k,String(v));},removeItem:function(k){ls.removeItem(P+k);},clear:function(){keys().forEach(function(k){ls.removeItem(P+k);});},key:function(i){var a=keys();return i<a.length?a[i]:null;}};
Object.defineProperty(w,'length',{get:function(){return keys().length;}});
var px=new Proxy(w,{get:function(t,k){if(k in t)return t[k];if(typeof k==='string'){var v=ls.getItem(P+k);return v===null?undefined:v;}},set:function(t,k,v){ls.setItem(P+k,String(v));return true;},deleteProperty:function(t,k){ls.removeItem(P+k);return true;},has:function(t,k){return (k in t)||ls.getItem(P+k)!==null;},ownKeys:function(){return keys();},getOwnPropertyDescriptor:function(t,k){var v=typeof k==='string'?ls.getItem(P+k):null;if(v!==null)return{value:v,writable:true,enumerable:true,configurable:true};}});
Object.defineProperty(window,'localStorage',{configurable:true,get:function(){return px;}});}catch(e){}
function home(e){var t=e.target&&e.target.closest?e.target.closest('#alx-home'):null;if(!t)return;e.preventDefault();e.stopImmediatePropagation();window.location.assign(new URL('../../index.html',window.location.href.split('#')[0]).href);}
window.addEventListener('click',home,true);
function btn(){if(document.getElementById('alx-home'))return;var a=document.createElement('a');a.id='alx-home';a.href='../../index.html';a.setAttribute('aria-label','Back to the Library of Alexandria');a.innerHTML='<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 2l2 3v2h-4V5zM9.5 8h5l.8 6h-6.600zM8 15h8l1.200 7H6.800z" fill="currentColor"/></svg><span>Alexandria</span>';
a.style.cssText='position:fixed;left:12px;bottom:14px;z-index:2147483000;display:flex;align-items:center;gap:6px;padding:8px 13px 8px 10px;border-radius:999px;background:rgba(20,38,74,.92);color:#f4cd78;font:600 12.5px/1 system-ui,sans-serif;letter-spacing:.04em;text-decoration:none;border:1px solid rgba(244,205,120,.55);box-shadow:0 4px 14px rgba(0,0,0,.35)';
document.body.appendChild(a);}
function reading(){return document.documentElement.classList.contains('hv-reading');}
function vis(){if(!document.body)return;var a=document.getElementById('alx-home');if(!a){btn();a=document.getElementById('alx-home');if(!a)return;}var d=reading()?'none':'flex';if(a.style.display!==d)a.style.display=d;}
function start(){btn();vis();['hashchange','popstate','pageshow','click','keyup','touchend'].forEach(function(n){window.addEventListener(n,function(){setTimeout(vis,60);setTimeout(vis,450);},true);});try{new MutationObserver(vis).observe(document.documentElement,{attributes:true,attributeFilter:['class']});}catch(e){}setInterval(vis,1000);}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();})();</script>'''


def module_html(sdir, mid):
    cfg = B.load_scroll(sdir); html = B.render(cfg)
    shim = SHIM.replace('%ID%', mid)
    i = html.lower().find('<head'); j = html.find('>', i) + 1
    return cfg, html[:j] + shim + html[j:]


def icon_b64(sdir, cfg):
    p = os.path.join(cfg['_dir'], 'icon.png')
    from PIL import Image
    if os.path.exists(p): im = Image.open(p)
    else:
        import brand
        im = brand.render('legacy192', brand.hexrgb(cfg['color']), cfg['glyph'], cfg.get('initials', ''), width=cfg.get('mark_width', 1.0))
    im = im.convert('RGBA').resize((144, 144), Image.LANCZOS); b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return base64.b64encode(b.getvalue()).decode()


def count_works(cfg):
    s = open(os.path.join(cfg['_dir'], 'slots', 'hermes-manifest.html')).read(); m = json.loads(s[s.index('>') + 1:s.rindex('</')])
    return len({re.sub(r'-(b|e|c|gr|[a-h])$', '', b['meta']['key']) for b in m['books'] if not b['meta'].get('hidden')})


def works(cfg):
    s = open(os.path.join(cfg['_dir'], 'slots', 'hermes-manifest.html')).read(); m = json.loads(s[s.index('>') + 1:s.rindex('</')]); seen = set(); out = []
    for b in m['books']:
        k = b['meta']['key']; st = re.sub(r'-(b|e|c|gr|[a-h])$', '', k)
        if st in seen or b['meta'].get('hidden'): continue
        seen.add(st); out.append((b['meta'].get('en') or b.get('text', {}).get('title') or k, b['meta'].get('author') or '', k))
    return out


def hub(cards, total, catalog):
    wings = []
    for w in dict.fromkeys(c['wing'] for c in cards):
        items = ''.join(f'''<a class="door" href="modules/{c['id']}/index.html" style="--c:{c['color']}"><img src="data:image/png;base64,{c['icon']}" alt="" width="64" height="64"><span class="tx"><b>{c['name']}</b><i>{c['blurb']}</i><em>{c['n']} works</em></span></a>''' for c in cards if c['wing'] == w)
        wings.append(f'<section><h2><span>{w}</span></h2><div class="doors">{items}</div></section>')
    tpl = open(os.path.join(HERE, '..', 'engine', 'alexandria', 'hub.html'), encoding='utf-8').read()
    from PIL import Image
    im = Image.open(os.path.join(ROOT, 'scrolls', 'alexandria', 'icon.png')).resize((192, 192), Image.LANCZOS); b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return tpl.replace('{{wings}}', '\n'.join(wings)).replace('{{total}}', f'{total:,}').replace('{{count}}', str(len(cards))).replace('{{version}}', VERSION).replace('{{catalog}}', json.dumps(catalog, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')).replace('{{icon}}', base64.b64encode(b.getvalue()).decode())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--apk', action='store_true'); ap.add_argument('--keystore'); ap.add_argument('--storepass')
    ap.add_argument('--no-zip', action='store_true'); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = []; cards = []; total = 0; catalog = {'mods': [], 'works': []}
    for sdir, mid, wing in MODULES:
        cfg, html = module_html(sdir, mid); n = count_works(cfg); total += n
        files.append((f'modules/{mid}/index.html', html.encode('utf-8')))
        for arc, src in B.asset_files(cfg): files.append((f'modules/{mid}/{arc}', src))
        catalog['mods'].append([mid, cfg['name'], cfg['color']]); catalog['works'] += [[t, au, k, len(catalog['mods']) - 1] for t, au, k in works(cfg)]
        cards.append({'id': mid, 'name': cfg['name'], 'color': cfg['color'], 'wing': wing, 'blurb': BLURB[mid], 'n': n, 'icon': icon_b64(sdir, cfg)})
        print(f'  {mid}: {n} works')
    seen = {}; dups = []
    for sdir, mid, _ in MODULES:
        t = open(os.path.join(ROOT, 'scrolls', sdir, 'slots', 'hermes-manifest.html')).read()
        for b in json.loads(t[t.index('>') + 1:t.rindex('</')])['books']:
            k = re.sub(r'-(b|c|e|gr)$', '', b['meta']['key'])
            if seen.setdefault(k, mid) != mid: dups.append((k, seen[k], mid))
    if dups: sys.exit(f'the same work is in more than one Scroll: {sorted(set(dups))[:12]}')
    index = hub(cards, total, catalog).encode('utf-8')
    files.insert(0, ('index.html', index))
    def put(zf, prefix=''):
        for arc, src in files:
            if isinstance(src, bytes): zf.writestr(zipfile.ZipInfo(prefix + arc, (2026, 1, 1, 0, 0, 0)), src, compress_type=zipfile.ZIP_DEFLATED)
            else: zf.write(src, prefix + arc, compress_type=zipfile.ZIP_DEFLATED)
    if not a.no_zip:
        z = os.path.join(a.out, f'library-of-alexandria-{VERSION}-web.zip')
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf: put(zf)
        print('web zip', z, os.path.getsize(z) // 1048576, 'MB')
    if a.apk:
        base = os.path.join(ROOT, 'scrolls', 'alexandria', 'android', 'base.apk'); unsigned = os.path.join(a.out, 'unsigned.apk')
        with zipfile.ZipFile(base) as zb, zipfile.ZipFile(unsigned, 'w') as zo:
            for info in zb.infolist():
                data = zb.read(info)
                if info.filename == 'AndroidManifest.xml':
                    m = Manifest(data); g = m.get()
                    if g.get('versionCode') != CODE or g.get('versionName') != VERSION: m.set(CODE, VERSION); data = bytes(m.d)
                if info.filename.startswith('assets/'): continue
                ni = zipfile.ZipInfo(info.filename, info.date_time); ni.compress_type = info.compress_type; ni.external_attr = info.external_attr; zo.writestr(ni, data)
            put(zo, 'assets/')
        final = os.path.join(a.out, f'LibraryOfAlexandria-{VERSION}.apk')
        if a.keystore:
            r = subprocess.run([sys.executable, os.path.join(HERE, 'apksign.py'), unsigned, final, '--ks', a.keystore, '--alias', 'alexandria', '--pass=' + a.storepass], capture_output=True, text=True)
            if r.returncode: sys.exit('signing failed: ' + r.stdout[-1500:] + r.stderr[-1500:])
            os.remove(unsigned)
        else: final = final[:-4] + '-unsigned.apk'; shutil.move(unsigned, final)
        print('apk', final, os.path.getsize(final) // 1048576, 'MB')
    json.dump({'total': total, 'modules': [{k: c[k] for k in ('id', 'name', 'n', 'wing')} for c in cards]}, open(os.path.join(a.out, 'alexandria.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
