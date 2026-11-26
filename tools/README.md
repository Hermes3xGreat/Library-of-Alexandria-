# Scroll engine tools

One engine (`engine/shell.html`), one folder per Scroll (`scrolls/<id>/`), one combined app (Library of Alexandria).

## Build
| Tool | What it does |
|---|---|
| `build.py ID --out DIR [--apk --keystore K --storepass P]` | Builds one Scroll: web folder, zip and Android app. Adds every `engine/addons/*.js` except for the reference Scroll (`scrolls/plato`). |
| `build_alexandria.py --out DIR --apk --keystore K --storepass P` | Builds the Library of Alexandria: the hall, every Scroll as a module, the title/author catalog for search. Stops if a work is in two Scrolls. |
| `apksign.py`, `axml.py`, `make_base.py` | Android packaging and signing. |
| `brand.py`, `make_brand_templates.py`, `lighthouse_icon.py` | Icons. |
| `new_scroll.py`, `split.py`, `ingest.py`, `add_book.py`, `remove_books.py` | Create a Scroll, add or remove works. |
| `split_plato.py` | Regenerates `plato-philosophy` and Pantheon's lists from the Plato source. **Afterwards run** `polish_safe.py --soft --write plato-philosophy pantheon`. |
| `reindex_greek_tools.py` | Trims Plato's concordance and citation data to its own books (called by `split_plato.py`). |

## Texts
| Tool | What it does |
|---|---|
| `import_*.py` (with `nm_conv_lib.py`) | Convert source texts into book files, one script per batch. |
| `polish.py` (+ `polish_rules.py`, `polish_books.json`) | Full reading clean-up for converted books. Dry run unless `--write`. |
| `polish_safe.py [--soft]` | Gentle clean-up for curated books; `--soft` only adds breaks inside very long paragraphs (Plato, Pantheon). |
| `add_headings.py` | Section headings and citations for long books that lacked them. |
| `apocrypha_greek.py`, `enoch_versions.py` | Greek companions for the Apocrypha and Enoch. |
| `audit_library.py [--fix]` | Structure and text-error check for every Scroll. Run before each release. |

## Pictures
| Tool | What it does |
|---|---|
| `add_illustrations.py --all` | Puts illustrations back into every book listed in `illustrations.json`. Run it **after** any polish of those books. |
| `goetia_seals.py` | Cuts the 72 seals of the Goetia out of the plates and sets each under its spirit. |
| `find_covers.py`, `covers.py` | Museum (CC0) cover images for authors and works. |

## Add-ons (`engine/addons`)
- `single-work.js` — an author with one work opens that work at once.
- `open-links-directly.js` — a link straight to a work skips the tap-to-start screen.

## Release order
1. Import or change texts. 2. `polish.py --write KEYS`. 3. `add_illustrations.py --all` (and `goetia_seals.py`). 4. `audit_library.py --fix`. 5. Bump versions in `scroll.json` and `build_alexandria.py`. 6. Build each Scroll, then Alexandria. 7. Browser checks.
