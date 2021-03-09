# -*- coding: utf-8 -*-
import argparse
import chardet
import os
import platform
import re


parser = argparse.ArgumentParser(description='ref')
parser.add_argument('-f', type=str, default="bib.txt", help="input bibtex")
parser.add_argument('-o', type=str, default="ref.txt", help="output ref")
parser.add_argument('-a', action='store_true', help='append mode')
parser.add_argument('--n_name', type=int, default=3,
                    help="#author threshold, <=0 means show all authors")
args = parser.parse_args()


if not args.a:
    if "Windows" == platform.system():
        os.system("cls")
    elif "Linux" == platform.system():
        os.system("clear")


# journal/conference abbreviation
JC_ABBR = {
    # preprint
    "arXiv": ["arXiv preprint", "arXiv:"],
    # conference
    "3DV": ["International Conference on 3D Vision"],
    "AAAI": ["AAAI Conference on Artificial Intelligence"],
    "ACM MM": ["ACM International Conference on Multimedia"],
    "BMVC": ["British Machine Vision Conference"],
    "CVPR": ["Computer Vision and Pattern Recognition"],
    "ECCV": ["European Conference on Computer Vision"],
    "ICCV": ["International Conference on Computer Vision"],
    "ICIP": ["International Conference on Image Processing"],
    "ICLR": ["International Conference on Learning Representations"],
    "ICME": ["International Conference on Multimedia & Expo"],
    "ICML": ["International Conference on Machine Learning"],
    "ICMR": ["International Conference on Multimedia Retrieval"],
    "IJCAI": ["International Joint Conference on Artificial Intelligence"],
    "NIPS": ["Conference on Neural Information Processing Systems"],
    "SIGIR": ["Research and Development in Information Retrieval"],
    "SIGKDD": ["Knowledge Discovery and Data Mining"],
    "SIGMOD": ["Conference on Management of Data"],
    "WACV": ["Winter Conference on Applications of Computer Vision"],
    # journal
    "AI": ["Artificial Intelligence"],
    "Comm. ACM": ["Communications of the ACM",
                 "Commun. ACM"],
    "IJCV": ["International Journal of Computer Vision"],
    "JMLR": ["Journal of Machine Learning Research"],
    "TCSVT": ["Transactions on Circuits and Systems for Video Technology",
              "Trans. Cir. and Sys. for Video Technol."],
    "TIP": ["Transactions on Image Processing"],
    "TMM": ["IEEE Transactions on Multimedia"],
    "TNNLS": ["Transactions on Neural Networks and Learning Systems"],
    "TOG": ["Transactions on Graphics",
            "ACM Trans. Graph."],
    "TOMM": ["Transactions on Multimedia Computing, Communications and Application",
             "Trans. Multimedia Comput. Commun. Appl."],
    "TPAMI": ["Transactions on Pattern Analysis and Machine Intelligence"],
}

# paper type
# https://www.openoffice.org/bibliographic/bibtex-defs.html
TYPE = {
    "article": "journal",
    "conference": "conference",
    "inproceedings": "conference",
    "proceedings": "conference",
}

# words that will NOT be capitalised in title
STOP_WORD = [
    "a", "an", "and", "as", "by", "for", "in", "into", "of", "on", "onto",
    "through", "the", "to", "under", "using", "via", "with",
]

# in `<prefix>-<word>`, the <word> will NOT be capitalised
PREFIX = [
    "anti", "auto", "multi", "semi", "un", "uni", "weakly"
]

# in `<word>-<suffix>`, the <suffix> will NOT be capitalised
SUFFIX = [
    "based",
]

# to match the complex abstract
# DON'T include `=`, or raise an error
VOCAB = r"\w\s\<\>\[\]\(\)\{\}\"\'\`\^\+\*\~\–\-\/\\\,\.\:\;\!\?\&"


class Cite:
    __slots__ = ["articleno", "author", "booktitle", "number",
        "numpages", "pages", "paper_type", "title", "volume", "year"]


def parse_type(bib):
    # pattern: @<type>{<ref>, ... }
    match_pat = r"\@([a-zA-Z]+)\{([\w\.\/\+]+)\,.*\}"
    m_obj = re.match(match_pat, bib, re.S)
    assert m_obj is not None
    paper_type = m_obj.group(1).lower()
    print("paper type:", paper_type)
    ref_str = m_obj.group(2)
    print("ref string:", ref_str)

    paper_t = None
    for _t in TYPE:
        if _t == paper_type:
            paper_t = TYPE[_t]
            break
    assert paper_t is not None, \
        "* UNSUPPORTED ARTICLE TYPE: {}".format(paper_type)

    return paper_t


def short_name(name):
    """`Tom`, `tom` -> `T.`"""
    return name.lower().capitalize()[:1] + '.'


def parse_author(s):
    # print(s)
    raw_list = s.split(" and ")
    print("#author:", len(raw_list))

    pat_list = []
    # pattern 0: <F>, <G> [<short M>.]
    pat_list.append(r"\s*([a-zA-Z\-]+)\,\s+([a-zA-Z\-\s\.]+)\s*")
    # pattern 1: <short G>. [<short M>.] {<F>}
    pat_list.append(r"\s*([a-zA-Z\.\s]+)\s+\{([a-zA-Z]+)\}\s*")
    # pattern 2: {<G> <F>}
    pat_list.append(r"\s*\{([a-zA-Z]+)\s+([a-zA-Z]+)\}\s*")
    pat_list = [re.compile(p) for p in pat_list]

    author_list = []
    for aid, a in enumerate(raw_list):
        print(a)
        for pid, p in enumerate(pat_list):
            m = p.match(a)
            if m is not None:
                if 0 == pid:
                    fn = m.group(1)
                    gn = m.group(2).split(' ')
                    if len(gn) == 1:
                        gn = gn[0]
                        if ("Li" == gn) and ("Fei-Fei" == fn):
                            fn, gn = gn, fn
                        gn = short_name(gn)
                        name = "{} {}".format(gn, fn)
                    else:
                        name = ""
                        for _gn in gn:
                            name += short_name(_gn) + ' '
                        name += fn
                elif 1 == pid:
                    fn = m.group(2)
                    gn = m.group(1).split(' ')
                    name = ""
                    for _gn in gn:
                        name += _gn + ' '
                    name += fn
                elif 2 == pid:
                    fn = m.group(2)
                    gn = short_name(m.group(1))
                    name = "{} {}".format(gn, fn)

                author_list.append(name)
                print(aid + 1, '|', name)
                break

    assert len(author_list) > 0, "* NO AUTHOR"
    return author_list


def less_author(author_list):
    """shows the first `n_name` authors only"""
    _m = len(author_list)
    if args.n_name > 0:
        _m = min(args.n_name, _m)

    _author = ""
    for i in range(_m):
        _author += author_list[i]
        if i < _m - 1:
            _author += ", "
    if len(author_list) > _m:
        _author += ", et al"
    return _author


def parse_page(s):
    m = re.match(r"(\d+)\D*(\d+)", s)
    assert m is not None
    begin = int(m.group(1))
    end = int(m.group(2))
    print("pages:", begin, ',', end)
    return (begin, end)


def parse_hyphen_word(word):
    """deal with the hythen word in title"""
    # pattern: w1-w2[-w3...]
    w_list = word.split('-')
    m = len(w_list)
    assert m > 1
    # pascle case
    pat_pascle = re.compile(r"[A-Z\d]+[a-z\d]+[A-Z]\w*\:?")
    # all caps
    pat_all_cap = re.compile(r"[A-Z\d]+\:?")

    res = ""
    for i, _w in enumerate(w_list):
        if (pat_pascle.match(_w) is None) and (pat_all_cap.match(_w) is None):
            if 0 == i:
                _w = _w.lower().capitalize()
            elif (_w not in STOP_WORD) and (w_list[i-1] not in SUFFIX) and \
                    (_w not in SUFFIX):
                _w = _w.lower().capitalize()
        res += _w + '-'

    return res[:-1]


def parse_title(title):
    w_list = [w for w in title.split(' ')]
    # pascle case
    pat_pascle = re.compile(r"[A-Z\d]+[a-z\d]+[A-Z]\w*\:?")
    # all caps
    pat_all_cap = re.compile(r"[A-Z\d]+\:?")

    res = ""
    for i, _w in enumerate(w_list):
        # print(_w)
        if '-' in _w:
            _w = parse_hyphen_word(_w)
        elif (pat_pascle.match(_w) is None) and (pat_all_cap.match(_w) is None):
            if (0 == i) or (_w not in STOP_WORD):
                _w = _w.lower().capitalize()
        res += _w + ' '

    res = res.strip()
    print("title:", res)
    return res


def parse_booktitle(s):
    s_low = s.lower()

    # special deal for arXiv
    if "arxiv" in s_low:
        return s

    bt = None
    for _abbr in JC_ABBR:
        if _abbr in s:
            bt = _abbr
            break
        for _name in JC_ABBR[_abbr]:
            if _name.lower() in s_low:
                bt = _abbr
                break
        if bt is not None:
            break

    assert bt is not None, \
        "* UNRECOGNISED CONFERENCE/JOURNAL: {}".format(s)
    print("booktitle:", bt)
    return bt


def gen_ref(cite_obj):
    _author = less_author(cite_obj.author)
    res = "{}. {}".format(_author, cite_obj.title)

    if "arxiv" in cite_obj.booktitle.lower():
        res += ". {}({})".format(cite_obj.booktitle, cite_obj.year)
    elif "conference" == cite_obj.paper_type:
        res += "[C]//{} {}".format(cite_obj.booktitle, cite_obj.year)
    elif "journal" == cite_obj.paper_type:
        res += "[J]. {}, {}".format(cite_obj.booktitle, cite_obj.year)
    else:
        print("* UNSUPPORTED ARTICLE TYPE")
        return None

    if hasattr(cite_obj, "volume"):
        res += ", {}".format(cite_obj.volume)
        if hasattr(cite_obj, "number"):
            res += "({})".format(cite_obj.number)

    if hasattr(cite_obj, "pages"):
        res += ": {}-{}".format(*cite_obj.pages)
    elif hasattr(cite_obj, "articleno") and hasattr(cite_obj, "numpages"):
        res += ": {0}:1-{0}:{1}".format(
            cite_obj.articleno, cite_obj.numpages)

    res += "."
    return res


bib = ""
with open(args.f, "r") as f:
    for line in f:
        bib += line.strip()


cite = Cite()
cite.paper_type = parse_type(bib)


# pattern: <key> = {<value>}[,}\s]
# match the last redundant `[,}\s]` (i.e. `,` or `}` or white space) for convenience
item_pat = re.compile(r"\w+\s*\=\s*[\{\"][" + VOCAB + r"]*[\}\"][\,\}\s]")
# print(item_pat)
item_list = item_pat.findall(bib)
print("#item:", len(item_list))
# for i, _it in enumerate(item_list):
    # print(i + 1, '|', _it, '\n')

item_split_pat = re.compile(r"(\w+)\s*\=\s*[\{\"]([" + VOCAB + r"]*)[\}\"]")
for i, _item in enumerate(item_list):
    # print(i + 1, '|', _item)
    # simply remove the last redundant character
    m_obj = item_split_pat.match(_item[:-1])
    assert m_obj is not None
    k = m_obj.group(1).lower()
    v = m_obj.group(2)
    # print(i + 1, '|', k, '|', v, '\n')
    if "" == v:
        continue

    if "author" == k:
        cite.author = parse_author(v)
    elif "title" == k:
        cite.title = parse_title(v)
    elif "year" == k:
        cite.year = int(v)
        print("year:", cite.year)
    elif "volume" == k:
        cite.volume = int(v)
        print("volume:", cite.volume)
    elif "number" == k:
        cite.number = int(v)
        print("number:", cite.number)
    elif "pages" == k:
        cite.pages = parse_page(v)
    elif "articleno" == k:
        cite.articleno = int(v)
        print("article No.:", cite.articleno)
    elif "numpages" == k:
        cite.numpages = int(v)
        print("num pages:", cite.numpages)
    elif "booktitle" == k:
        cite.booktitle = parse_booktitle(v)
    elif "journal" == k:
        assert "journal" == cite.paper_type
        cite.booktitle = parse_booktitle(v)

ref = gen_ref(cite)
print("\n{}".format(ref))
w_mode = "a" if args.a else "w"
with open(args.o, w_mode) as f:
    f.write("{}\n".format(ref))
    if args.a:
        f.write("\n")

if (not args.a) and ("Windows" == platform.system()):
    os.system("start {}".format(args.o))
