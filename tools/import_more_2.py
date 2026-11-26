#!/usr/bin/env python3
"""Book files for the Egyptian and Africa Scrolls (second batch) from Project Gutenberg texts (text only)."""
import re, sys, os, importlib.util
OUTDIR = sys.argv[1]
spec = importlib.util.spec_from_file_location('nm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nm_conv_lib.py'))
nm = importlib.util.module_from_spec(spec); spec.loader.exec_module(nm)
nm.SRC = '/tmp/ex'; nm.OUT = OUTDIR; os.makedirs(OUTDIR, exist_ok=True)
L0, idx, convert, write, UP = nm.L, nm.idx, nm.convert, nm.write, nm.UP
L = lambda f: [x.strip() for x in L0(f)]
_clean = nm.clean
nm.clean = lambda t: _clean(re.sub(r'\[Footnote[^\]]*\]\s?|\[(\d{1,3}|[A-Z\*][a-z]?)\]|\[Illustration[^\]]*\]|\(\d{1,3}\)(?=[\s,.;:]|$)' if False else r'\[Footnote[^\]]*\]\s?|\[(\d{1,3}|[A-Z\*][a-z]?)\]|\[Illustration[^\]]*\]', '', t))
NOTE = r'^(\[\d+\]\s|\[Footnote|Footnote \d|FOOTNOTES?:?$|\[Illustration)'
END = r'\*\*\* END OF THE PROJECT'


def go(key, fn, start, end, nth=1, lines=None, **kw):
    f = lines or L(fn)
    try: a = idx(f, start, nth=nth); b = idx(f, end, a + 1)
    except SystemExit as e: print('FAIL', key, e); return
    kw.setdefault('heading', UP); kw.setdefault('drop', NOTE)
    e = convert(f[a:b], **kw); write(key, e)
    print(f'{key}: {len(e)} entries, {sum(1 for x in e if x["sp"] == "HDR")} headings | ', [x['t'][:40] for x in e if x['sp'] == 'HDR'][:5])



C = r'[A-Z][A-Z ,\'’\-:;]{5,}\.?'
# Egyptian
go('budge-literature-egyptians', '15932.txt', r'^CHAPTER I$', r'^INDEX$', heading=r'(CHAPTER [IVXL]+|' + C + ')')
go('budge-future-life', '11277.txt', r'^CHAPTER I\.$', END, heading=r'(CHAPTER [IVXL]+\.|' + C + ')')
go('petrie-religion-egypt', '29010.txt', r'^CHAPTER I$', r'^INDEX$', heading=r'(CHAPTER [IVXL]+|' + C + ')')
go('weigall-akhnaton', '62434.txt', r'^INTRODUCTION\.$', r'^INDEX\.$', heading=r'(INTRODUCTION\.|[IVXL]+\.|' + C + ')', roman_st=False)
# Africa
go('speke-source-of-the-nile', '3284.txt', r'^Chapter 1\. London', END, heading=r'(Chapter [IVXL\d]+\..*|Conclusion.*)', roman_st=False)
go('kingsley-travels-west-africa', '5891.txt', r'^CHAPTER I\. ', r'^NOTES\.$', nth=2, heading=r'(CHAPTER [IVXL]+\..*|APPENDIX\..*)')
go('fitzpatrick-jock-of-the-bushveld', '36951.txt', r'^CHAPTER ONE\.$', r'^GLOSSARY\.$', heading=r'(CHAPTER [A-Z ]+\.|' + C + ')')
go('cronise-cunnie-rabbit', '48828.txt', r'^CHAPTER I$', END, nth=1, heading=r'(CHAPTER [IVXL]+|' + C + ')')
go('hobley-bantu-beliefs', '67426.txt', r'^PART I$', r'^GLOSSARY$', nth=2, heading=r'(PART [IVX]+|CHAPTER [IVXL]+\.?|' + C + ')')
go('weeks-congo-life-folklore', '69558.txt', r'^PART I$', r'^INDEX$', nth=2, skip=[(r'^NOTES TO PART I', r'^PART II$')], heading=r'(PART [IVX]+|CHAPTER [IVXL]+|INTRODUCTION|' + C + ')')
go('dayrell-ikom-folk-stories', '70959.txt', r'^I\.--HOW AN INKUM WOMAN', r'^FOOTNOTES:', roman_st=False, heading=r'([IVXL]+\.--[A-Z].*|[A-Z][A-Z ,\'’\-:;]{5,}\.?)')
