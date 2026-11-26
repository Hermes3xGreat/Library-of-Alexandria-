# Scroll engine

One reader, many libraries. Every Scroll app (Plato Scroll, Eastern Scroll, and
any new one) is built from the same engine. Each Scroll is just a folder: its
library, its pictures, its background, its colours and its wording.

```
engine/shell.html          the shared reader (code, styles, layout), with
                           {{tokens}} and <!--@slot …--> markers
engine/default-slots/      empty versions of optional blocks
scrolls/<id>/scroll.json   name, version, colour, Android package/label/version/key alias,
                           and every piece of per-scroll wording ("text")
scrolls/<id>/slots/        whole blocks owned by the Scroll:
    hermes-manifest.html     the library (books, translations, blurbs)
    hv-authors.html          shelves and their authors
    hv-section-decor.html    shelf headings (glyph, era, motto)
    hv-lib3d-js.html         animated background
    hv-intro-css.html        start-screen look and logo
    hermes-encyclopedia.html, hv-changelog.html, hv-site-nav.html, …
    scroll-layer.html        the Scroll's own extra CSS/JS (optional)
scrolls/<id>/text/         long text values (favicon, banner, covers)
scrolls/<id>/books/        book files (books/<key>.js)
scrolls/<id>/data/         extra data (Plato Scroll: Greek word-tap, concordance)
scrolls/<id>/android/base.apk   the Android app without its assets
tools/                     build, ingest, new_scroll, add_book, brand, make_base, axml, split
```

## Build a Scroll

```
python3 tools/build.py eastern                     # dist/eastern/index.html + web zip
python3 tools/build.py eastern --apk --code 3 \
        --keystore eastern-scroll-signing.keystore --storepass '…'
```

The APK is signed when `tools/bin/uber-apk-signer.jar` is present (or
`apksigner` + `zipalign` from the Android build-tools are on PATH); otherwise
an `-unsigned.apk` is written with the two commands to sign it. Raise
`android.versionCode` (or pass `--code`) for every update, and use the
Scroll's own key so it installs over the old version:

| Scroll | package | key alias | last versionCode |
|---|---|---|---|
| Plato Scroll | com.platoscroll.app | hermes (clean-code line) | 300 |
| Eastern Scroll | com.easternscroll.app | easternscroll | 3 (1.2) |
| Egyptian Scroll | com.egyptianscroll.app | egyptianscroll (new key) | 1 (0.1) |
| Northern Scroll | com.northernscroll.app | northernscroll (new key) | 1 (0.1) |

Plato Scroll's 1,500 book files are not in this zip. Take them from any
Plato Scroll APK once:
`python3 tools/make_base.py plato-scroll.apk scrolls/plato/android/base.apk --take-books`
(or point `build.py --books` at your source tree's books folder).

## Start a new Scroll

```
python3 tools/new_scroll.py hermetic --name "Hermetic Scroll" \
        --package com.hermeticscroll.app --tagline "Hermetic tradition" \
        --subtitle "A Library of the Hermetic Tradition" \
        --description "the Hermetic tradition: the Corpus Hermeticum, the Asclepius and more." \
        --search "Hermes, Orpheus" --color '#4a2c7a' --glyph '☿' --initials 'ΕΤ'
python3 tools/add_book.py hermetic --copy-from plato --author "Hermes Trismegistus" --section Hermetica
python3 tools/add_book.py hermetic --text kybalion.txt --key kybalion --title "The Kybalion" \
        --author "Three Initiates" --translator 1908 --section "Modern Hermetica"
python3 tools/build.py hermetic --apk
keytool -genkeypair -keystore hermetic-scroll.keystore -alias hermeticscroll -keyalg RSA -keysize 4096 -validity 36500
```

`new_scroll.py` copies Eastern Scroll's setup (no Greek-only features), empties
the library and gives the Android app its own package and label, so it installs
beside the others.

**Every Scroll has its own background.** A new Scroll starts with
`engine/backgrounds/starter.js`: a slowly turning astrolabe in the Scroll's own
colour, with its symbol at the centre and rising through the scene. The layout
is seeded from the Scroll's id, so no two Scrolls look alike. Replace
`slots/hv-lib3d-js.html` with a bespoke scene when the Scroll gets one. It must keep the
`window.__hvLib3D` / `hvSetLib3D` interface. Finished scenes: Plato's WebGL temple, Eastern's ink-wash
mountains, Egyptian's Nile at Giza (`engine/backgrounds/nile.js`) and Northern's
fjord with castle, longship and aurora (`engine/backgrounds/fjord.js`).

**Every mark is the Plato Scroll mark.** `tools/brand.py` draws the app icons
(adaptive + legacy, every density), the adaptive icon's background colour, the
start-screen logo, the favicon and the top-bar banner from blank templates cut
out of Plato Scroll's own pictures (`engine/brand/`, made by
`make_brand_templates.py`). Same tile, scroll, roller, bar, sizes and
positions; only `color`, `glyph` and `initials` in scroll.json change:

```
python3 tools/brand.py eastern --color '#9e2f23' --glyph 東 --initials ES
```

Symbols are drawn in Inter Display / DejaVu Sans (bundled), with Chinese and
Japanese characters taken from Noto Serif CJK or the system's CJK font. A symbol no font here
has (runes, hieroglyphs) needs a font dropped in `engine/brand/fonts` and
added to `ORDER` in brand.py.

## Update the engine from a new Plato Scroll build

```
python3 tools/ingest.py path/to/new/plato/index.html
```

Every reader improvement made in Plato Scroll then reaches every Scroll on
their next build. Unchanged parts keep their tokens, Plato's own library
blocks go to `scrolls/plato/slots`, changed code is taken from the new build
with each token put back where it is found again, and new code gets
"Plato Scroll" turned into `{{name}}`. The new engine must rebuild the new
Plato Scroll byte for byte, or nothing is written. Spots it can't place are
listed. Check them, because the other Scrolls would show Plato's wording there.

## How it was made

`tools/split.py` compared the Plato Scroll 5.25f shell with Eastern Scroll
1.1 (which was made from it): identical code became the engine, whole
differing data blocks became slots, and the small wording differences
became 30 tokens. Both apps rebuild byte-identical from the engine, and their
APK contents match the shipped APKs entry for entry.
