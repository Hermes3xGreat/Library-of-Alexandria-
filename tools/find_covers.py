#!/usr/bin/env python3
"""Find public-domain (CC0) museum images for Scroll covers and make a
labelled contact sheet. Sources: The Met Open Access, Cleveland Museum of Art.
usage: find.py LABEL "query" [met|cma] [n]"""
import sys, json, os, io, urllib.request, urllib.parse
from PIL import Image, ImageDraw
UA = {'User-Agent': 'ScrollLibrary/1.0'}
D = '/home/claude/covers/cand'
os.makedirs(D, exist_ok=True)


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
    return b if binary else json.loads(b)


def met(q, n):
    ids = get('https://collectionapi.metmuseum.org/public/collection/v1.1/search?' + urllib.parse.urlencode(
        {'q': q, 'hasImages': 'true', 'isPublicDomain': 'true', 'limit': n * 3}))['objectIDs'] or []
    out = []
    for i in ids:
        try:
            o = get(f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{i}')
        except Exception:
            continue
        if o.get('isPublicDomain') and o.get('primaryImageSmall'):
            out.append({'src': 'met', 'id': i, 'title': o['title'], 'date': o.get('objectDate', ''),
                        'img': o['primaryImageSmall'], 'credit': f"The Metropolitan Museum of Art, {o.get('accessionNumber')} (CC0)"})
        if len(out) >= n:
            break
    return out


def cma(q, n):
    d = get('https://openaccess-api.clevelandart.org/api/artworks/?' + urllib.parse.urlencode(
        {'q': q, 'has_image': 1, 'cc0': 1, 'limit': n}))['data']
    return [{'src': 'cma', 'id': x['id'], 'title': x['title'], 'date': x.get('creation_date', ''),
             'img': x['images']['web']['url'], 'credit': f"Cleveland Museum of Art, {x['accession_number']} (CC0)"} for x in d if x.get('images', {}).get('web')]


def main():
    label, q = sys.argv[1], sys.argv[2]
    src = sys.argv[3] if len(sys.argv) > 3 else 'met'
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    c = (met if src == 'met' else cma)(q, n)
    json.dump(c, open(f'{D}/{label}.json', 'w'), indent=1)
    th = []
    for k, x in enumerate(c):
        try:
            im = Image.open(io.BytesIO(get(x['img'], True))).convert('RGB')
            im.save(f'{D}/{label}-{k}.jpg', quality=92)
            im.thumbnail((220, 220)); th.append((k, x, im))
        except Exception:
            pass
    W = 230 * max(1, len(th)); sheet = Image.new('RGB', (W, 270), 'white'); d = ImageDraw.Draw(sheet)
    for j, (k, x, im) in enumerate(th):
        sheet.paste(im, (j * 230 + 5, 5)); d.text((j * 230 + 5, 230), f"{k}: {x['title'][:34]}", fill='black'); d.text((j * 230 + 5, 245), x['date'][:30], fill='gray')
    sheet.save(f'{D}/{label}-sheet.png')
    print(label, len(th), 'candidates')


main()
