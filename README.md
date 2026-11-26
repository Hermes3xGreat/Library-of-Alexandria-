# The Library of Alexandria

A free, offline reading app that gathers ten libraries of public-domain classics under one roof: 793 works, from Plato and Homer to the Vedas, the sagas, the Popol Vuh and the Federalist Papers.

| Library | Holds |
|---|---|
| Plato Scroll | Ancient philosophy: Plato, Aristotle, the Stoics, the Neoplatonists |
| Descartes Scroll | Modern philosophy, Machiavelli to Russell |
| Pantheon Scroll | Greek and Roman literature, history, drama and science |
| Egyptian Scroll | Ancient Egypt and the Hermetica |
| Crescent Scroll | The Near East: Babylon, Persia, Arabia, the Bible and the Apocrypha |
| Eastern Scroll | India, China and the Buddhist canon |
| Northern Scroll | The North and the Middle Ages, alchemy, magic and theosophy |
| Africa Scroll | Folk tales, Augustine, Equiano and the travellers |
| Americas Scroll | The first nations and the Conquest |
| Liberty Scroll | American history, and American Freemasonry |

Each library keeps its own bookmarks, notes and reading place. The front hall searches titles, authors and the full text of every book. Where a work has a second translation or its original-language text, a switch at the top of the page changes between them. 63 books carry their illustrations (1,142 pictures), including every seal of the *Lesser Key of Solomon* and every card of Waite's Tarot.

## What is in this repository
| Folder | Contents |
|---|---|
| `app/` | The built app, version 2.0, as a plain web folder. Open `app/index.html`; it needs no server and no network. |
| `engine/` | The shared reader (`shell.html`), backgrounds, chimes, add-ons and the Alexandria hall. |
| `scrolls/` | One folder per library: settings, shelves, book files, covers, Android base. |
| `tools/` | Build, import, clean-up, picture and audit tools. See `tools/README.md`. |
| `docs/` | Notes on the engine. |

The Android app (about 275 MB) is larger than GitHub allows inside a repository, so it is not here. Build it with `tools/build_alexandria.py`, or attach it to a Release.

## Building
```
python3 tools/build.py africa --out out                 # one library
python3 tools/build_alexandria.py --out out/alexandria  # the whole Library (add --apk --keystore K --storepass P for Android)
python3 tools/audit_library.py                          # structure and text check
```
Signing keys are not in this repository and must never be added to it.

## Status
Version 2.0 has been checked in a desktop browser. It has not yet been tested on a phone.

## Texts and credits
See `NOTICE.md`.
