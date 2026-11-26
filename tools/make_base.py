#!/usr/bin/env python3
"""Turn an existing app APK into an Android base for a Scroll: keeps the
compiled code, icons and manifest, drops assets/ and the old signature.

usage: make_base.py APP.apk scrolls/<id>/android/base.apk [--take-books]
  --take-books also unpacks the APK's assets/books and assets/data into
  scrolls/<id>/books and scrolls/<id>/data (handy for Plato Scroll's 1,500 books).
"""
import sys, os, zipfile

src, dst = sys.argv[1], sys.argv[2]
take = '--take-books' in sys.argv
sdir = os.path.dirname(os.path.dirname(os.path.abspath(dst)))
os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, 'w') as zo:
    for info in zi.infolist():
        n = info.filename
        if n.startswith('assets/') or n.startswith('META-INF/'):
            if take and (n.startswith('assets/books/') or n.startswith('assets/data/')) and not n.endswith('/'):
                out = os.path.join(sdir, n[len('assets/'):])
                os.makedirs(os.path.dirname(out), exist_ok=True)
                open(out, 'wb').write(zi.read(info))
            continue
        ni = zipfile.ZipInfo(n, info.date_time)
        ni.compress_type = info.compress_type
        ni.external_attr = info.external_attr
        zo.writestr(ni, zi.read(info))
print(dst, os.path.getsize(dst), 'bytes')
