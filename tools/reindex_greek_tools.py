#!/usr/bin/env python3
"""Trim the word finder (concordance) and citation data to a Scroll's own
library, so results never point at works that now live in another Scroll.
usage: reindex_greek_tools.py SRC_DATA OUT_DATA MANIFEST_SLOT"""
import os, re, sys, json, gzip
def main():
    src, outd, slot = sys.argv[1:4]
    s = open(slot, encoding='utf-8').read(); man = json.loads(s[s.index('>') + 1:s.rindex('</')])
    have = {b['meta']['key'] for b in man['books']}; stems = {re.sub(r'-(b|c|d|e|gr|[a-h])$', '', k) for k in have}
    loci = json.loads(gzip.open(os.path.join(src, 'hv-loci.json.gz')).read())
    keep = [i for i, k in enumerate(loci['books']) if k in have or re.sub(r'-(b|c|d|e|gr|[a-h])$', '', k) in stems]
    bmap = {old: new for new, old in enumerate(keep)}
    emap = [-1] * len(loci['ent_book']); ent_book = []; ent_st = []
    for e, b in enumerate(loci['ent_book']):
        if b in bmap: emap[e] = len(ent_book); ent_book.append(bmap[b]); ent_st.append(loci['ent_st'][e])
    os.makedirs(os.path.join(outd, 'conc'), exist_ok=True)
    for f in os.listdir(os.path.join(outd, 'conc')): os.remove(os.path.join(outd, 'conc', f))
    shards = []; words = dropped = 0
    for f in sorted(os.listdir(os.path.join(src, 'conc'))):
        d = json.loads(gzip.open(os.path.join(src, 'conc', f)).read()); tok = {}
        for w, (cnt, fl, deltas) in d['tok'].items():
            ids = []; c = 0
            for x in deltas:
                c += x
                if emap[c] >= 0: ids.append(emap[c])
            if not ids: dropped += 1; continue
            nd = []; prev = 0
            for i in ids: nd.append(i - prev); prev = i
            n = len(ids) if not fl else max(len(ids), round(cnt * len(ids) / max(1, len(deltas))))
            tok[w] = [n, fl, nd]; words += 1
        if tok:
            with gzip.open(os.path.join(outd, 'conc', f), 'wb') as o: o.write(json.dumps({'v': d.get('v', 1), 'cap': d.get('cap', 100), 'tok': tok}, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
            shards.append(f[:-8])
    out = {'v': loci.get('v', 1), 'books': [loci['books'][i] for i in keep], 'ent_book': ent_book, 'ent_st': ent_st, 'titles': [loci['titles'][i] for i in keep], 'concShards': shards}
    with gzip.open(os.path.join(outd, 'hv-loci.json.gz'), 'wb') as o: o.write(json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    print(f'books {len(loci["books"])} -> {len(keep)}; entries {len(emap)} -> {len(ent_book)}; words kept {words}, dropped {dropped}; shards {len(shards)}')
if __name__ == '__main__':
    main()
