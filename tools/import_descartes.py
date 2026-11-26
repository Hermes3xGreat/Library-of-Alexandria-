#!/usr/bin/env python3
"""Book files for Descartes Scroll (modern philosophy) from Project Gutenberg texts (text only)."""
import re, sys, os, importlib.util
OUTDIR = sys.argv[1]
spec = importlib.util.spec_from_file_location('nm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nm_conv_lib.py'))
nm = importlib.util.module_from_spec(spec); spec.loader.exec_module(nm)
nm.SRC = '/tmp/mp'; nm.OUT = OUTDIR; os.makedirs(OUTDIR, exist_ok=True)
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
go('descartes-discourse', '59.txt', r'^PART I$', END, nth=2, heading=r'PART [IVX]+')
go('descartes-meditations', '70091.txt', r'^MEDITAT\. I\.', r'^_FINIS\._', heading=r'MEDITAT\. [IVX]+\.')
go('bacon-novum-organum', '45988.txt', r'^APHORISMS--BOOK I', r'^END OF .NOVUM ORGANUM', heading=r'APHORISMS--BOOK I+|' + C, roman_st=False)
go('hobbes-leviathan', '3207.txt', r'^THE INTRODUCTION', END, heading=r'(THE INTRODUCTION|PART [IVX]+\..*|CHAPTER [IVXL]+\..*|' + C + ')')
go('spinoza-ethics', '3800.txt', r'^PART I\. CONCERNING GOD', END, heading=r'(PART [IVX]+\..*|Part [IVX]+\.|' + C + ')', roman_st=False)
go('pascal-pensees', '18269.txt', r'^SECTION I$', r'^NOTES$', heading=r'(SECTION [IVX]+|' + C + ')', roman_st=False)
go('locke-essay-1', '10615.txt', r'^THE EPISTLE TO THE READER', r'^END OF VOLUME I', nth=2, heading=r'(BOOK [IVX]+.*|CHAPTER [IVXL]+\..*|' + C + ')')
go('locke-essay-2', '10616.txt', r'^BOOK III$', END, heading=r'(BOOK [IVX]+.*|CHAPTER [IVXL]+\..*|' + C + ')')
go('locke-second-treatise', '7370.txt', r'^CHAPTER\. I\.', END, heading=r'(CHAPTER\. [IVXL]+\.|' + C + ')')
go('berkeley-principles', '4723.txt', r'^INTRODUCTION$', END, nth=2)
go('berkeley-three-dialogues', '4724.txt', r'^THE FIRST DIALOGUE', END, heading=r'THE (FIRST|SECOND|THIRD) DIALOGUE')
go('hume-enquiry-understanding', '9662.txt', r'^SECTION I\.$', r'^INDEX$', heading=r'(SECTION [IVX]+\.|PART [IVX]+\.|' + C + ')')
go('hume-enquiry-morals', '4320.txt', r'^SECTION I\.', END, heading=r'(SECTION [IVX]+\..*|PART [IVX]+\.|APPENDIX [IVX]+\..*|' + C + ')')
go('hume-treatise', '4705.txt', r'^INTRODUCTION\.$', END, heading=r'(INTRODUCTION\.|BOOK [IVX]+.*|PART [IVX]+.*|SECT\. [IVXL]+.*|APPENDIX)')
go('hume-dialogues-religion', '4583.txt', r'^PAMPHILUS TO HERMIPPUS', END, heading=r'(PART \d+|PAMPHILUS TO HERMIPPUS)')
go('rousseau-social-contract', '46333.txt', r'^BOOK I$', END, nth=2, heading=r'(BOOK [IVX]+|CHAPTER [IVXL]+|' + C + ')')
go('kant-pure-reason', '4280.txt', r'^PREFACE TO THE FIRST EDITION', END, heading=r'(PREFACE TO .*|INTRODUCTION.*|[IVX]+\. [A-Z].{3,90}|S(ECTION|ection) [IVX]+\..*|C(HAPTER|hapter) [IVX]+\..*|B(OOK|ook) [IVX]+\..*|§ ?\d+.{0,90}|' + C + ')', roman_st=False)
go('kant-practical-reason', '5683.txt', r'^PREFACE\.$', r'^THE END', drop=NOTE + r'|^[A-Z_0-9]+\|[A-Z_0-9|]+$', heading=r'(PREFACE\.|INTRODUCTION\.|BOOK [IVX]+\..*|CHAPTER [IVX]+\..*|[IVX]+\. .{3,80}|' + C + ')', roman_st=False)
go('kant-groundwork', '5682.txt', r'^PREFACE$', r'^THE END')
go('kant-prolegomena', '52821.txt', r'^INTRODUCTION\.$', END, nth=2, heading=r'(§ ?\d+.{0,80}|' + C + ')')
go('kant-perpetual-peace', '50922.txt', r'^_FIRST SECTION_', r'^INDEX$', heading=r'(_[^_]{3,120}_\.?|' + C + ')')
go('schopenhauer-world-as-will-1', '38427.txt', r'^FIRST BOOK\. THE WORLD AS I', r'^FOOTNOTES', heading=r'((FIRST|SECOND|THIRD|FOURTH) BOOK\..*|§ ?\d+\..{0,60})')
go('schopenhauer-wisdom-of-life', '10741.txt', r'^INTRODUCTION\.$', END, heading=r'(INTRODUCTION\.|CHAPTER [IVX]+\.|' + C + ')')
go('schopenhauer-pessimism', '10732.txt', r'^ON THE SUFFERINGS OF THE WORLD', END, nth=2)
go('kierkegaard-selections', '60333.txt', r'^DIAPSALMATA', END, nth=2)
go('mill-on-liberty', '34901.txt', r'^CHAPTER I\.$', END, nth=2, heading=r'(CHAPTER [IVX]+\.|' + C + ')')
go('mill-utilitarianism', '11224.txt', r'^CHAPTER I\.$', r'^THE END\.', heading=r'(CHAPTER [IVX]+\.|' + C + ')')
go('mill-subjection-of-women', '27083.txt', r'^CHAPTER I\.$', r'^THE END\.', heading=r'CHAPTER [IVX]+\.')
go('marx-communist-manifesto', '61.txt', r'^I\.$', END, roman_st=False, heading=r'([IVX]+\.|\d\. [A-Z].*|[A-Z]\. [A-Z].*|' + C + ')')
go('nietzsche-zarathustra', '1998.txt', r'^FIRST PART\. ZARATHUSTRA', r'^APPENDIX\.$', roman_st=False, heading=r'((FIRST|SECOND|THIRD) PART\..*|FOURTH AND LAST PART\.|ZARATHUSTRA’S PROLOGUE\.|[IVXL]+\. [A-Z].{2,60})')
go('nietzsche-beyond-good-and-evil', '4363.txt', r'^PREFACE$', END, nth=2, heading=r'(PREFACE|CHAPTER [IVX]+[.:].*|FROM THE HEIGHTS.*)')
go('nietzsche-genealogy-of-morals', '52319.txt', r'^PREFACE\.$', r'^PEOPLES AND COUNTRIES', heading=r'(PREFACE\.|(FIRST|SECOND|THIRD) ESSAY\..*|' + C + ')')
go('nietzsche-birth-of-tragedy', '51356.txt', r'^AN ATTEMPT AT SELF-CRITICISM', r'^APPENDIX\.$', nth=2)
go('emerson-essays-1', '2944.txt', r'^I\.$', END, heading=r'([IVX]+\.|[A-Z][A-Z \-]{2,})')
go('emerson-essays-2', '2945.txt', r'^THE POET\.$', END, heading=r'([IVX]+\. [A-Z .]+|[A-Z][A-Z \-]{2,}\.)')
go('james-pragmatism', '5116.txt', r'^Lecture I$', END, nth=2, heading=r'(Lecture [IVX]+|' + C + ')')
go('james-varieties', '621.txt', r'^LECTURE I\. RELIGION AND NEUROLOGY', r'^INDEX\.$', heading=r'(LECTURES? [IVXL, AND]+\..*|POSTSCRIPT\.)')
go('russell-problems-of-philosophy', '5827.txt', r'^CHAPTER I\.', r'^BIBLIOGRAPHICAL NOTE', heading=r'CHAPTER [IVX]+\..*')
go('bergson-creative-evolution', '26163.txt', r'^INTRODUCTION$', r'^INDEX$', heading=r'(INTRODUCTION|CHAPTER [IVX]+|' + C + ')')
go('machiavelli-prince', '1232.txt', r'^CHAPTER I\.', r'^DESCRIPTION OF THE METHODS', nth=2, heading=r'(CHAPTER [IVXL]+\.|' + C + ')')
go('wollstonecraft-vindication', '3420.txt', r'^INTRODUCTION\.$', END, nth=2, heading=r'(INTRODUCTION\.|CHAPTER \d+\..*|SECTION \d+\.\d+\.)')
