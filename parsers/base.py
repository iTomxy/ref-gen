import re
import time
from .cite import Cite


def short_name(name):
    """`Tom`, `tom` -> `T.`"""
    return name.lower().capitalize()[:1] + '.'


def clean_name(name):
    """convert some character
    e.g. `\L ` -> `L`
    """
    name = re.sub(r"\\([a-zA-Z])\s?", r"\1", name)
    return name


def fix_name_order(fn, gn):
    """`Li Fei-Fei` -> `Fei-Fei Li`"""
    if ("li".lower() == gn.lower()) and (
        fn.lower() in ["fei-fei", "feifei"]
    ):
        fn, gn = gn, fn

    return fn, gn


def less_author(author_list, n_name=-1):
    """shows the first `n_name` authors only"""
    _m = len(author_list)
    if n_name > 0:
        _m = min(n_name, _m)

    _author = ""
    for i in range(_m):
        _author += author_list[i]
        if i < _m - 1:
            _author += ", "
    if len(author_list) > _m:
        _author += ", et al"
    return _author


def clean_booktitle(bt):
    """clean up the wield things in the book title"""

    # `&amp;` -> `&`
    bt = re.sub(r"\&amp\;", "&", bt)

    # remove the redundant abbreviation in the book title
    # e.g. the `, {IJCAI-20}`
    #     in `Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence, {IJCAI-20}`
    # e.g. the `, {ICLR} 2017, Toulon, France, April 24-26, 2017, Conference Track Proceedings`
    #     in `5th International Conference on Learning Representations, {ICLR} 2017, Toulon, France, April 24-26, 2017, Conference Track Proceedings`
    bt = re.sub(r"\,?\s*[\(\{][\w\d\-]+[\}\)][\w\d\s\-\,\.]*", "", bt)

    return bt


class Parser:
    def __init__(self, prior, n_name=-1, abbr_author=False, abbr_book_title=False, verbose=False):
        self.prior = prior
        self.n_name = n_name
        self.abbr_author = abbr_author
        self.abbr_book_title = abbr_book_title
        self.verbose = verbose

    def parse_type(self, bib):
        """parse the original type indication in bib text
        pattern: @<PAPER_TYPE>{<REF_STR>, ...}
        """
        match_pat = r"\s?\@([a-zA-Z]+)\{([\d\w\:\.\/\+\-\_]+)\,.*\}"
        m_obj = re.match(match_pat, bib, re.S)
        assert m_obj is not None
        paper_type = m_obj.group(1).lower()
        self.verbose and print("paper type:", paper_type)
        # ref_str = m_obj.group(2)
        # print("ref string:", ref_str)

        return paper_type

    def parse_hyphen_word(self, word):
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
                elif (_w not in self.prior.STOP_WORD) and \
                        (w_list[i-1] not in self.prior.SUFFIX) and \
                        (_w not in self.prior.SUFFIX):
                    _w = _w.lower().capitalize()
            res += _w + '-'

        return res[:-1]

    def parse_title(self, title):
        w_list = [w for w in title.split(' ')]
        # pascle case
        pat_pascle = re.compile(r"[A-Z\d]+[a-z\d]+[A-Z]\w*\:?")
        # all caps
        pat_all_cap = re.compile(r"[A-Z\d]+\:?")

        res = ""
        for i, _w in enumerate(w_list):
            # print(_w)
            if '-' in _w:
                _w = self.parse_hyphen_word(_w)
            elif (pat_pascle.match(_w) is None) and (pat_all_cap.match(_w) is None):
                if (0 == i) or (_w not in self.prior.STOP_WORD):
                    _w = _w.lower().capitalize()
            res += _w + ' '

        res = res.strip()
        self.verbose and print("title:", res)
        return res

    def compose_author(self, first_name, given_name):
        return "{} {}".format(given_name, first_name)

    def parse_author(self, s):
        # print(s)
        raw_list = s.split(" and ")
        self.verbose and print("#author:", len(raw_list))

        pat_list = []
        # pattern 0: <F>, <G> [<short M>.]
        pat_list.append(r"\s*([a-zA-Z\-\\]+)\,\s+([a-zA-Z\-\s\.\\]+)\s*")
        # pattern 1: <short G>. [<short M>.] {<F>}
        pat_list.append(r"\s*([a-zA-Z\.\s\-\\]+)\s+\{([a-zA-Z\-\\]+)\}\s*")
        # pattern 2: [{]<G> <F>[}]
        pat_list.append(r"\s*\{?([a-zA-Z\-\\]+)\s+([a-zA-Z\-\\]+)\}?\s*")
        pat_list = [re.compile(p) for p in pat_list]

        author_list = []
        for aid, a in enumerate(raw_list):
            self.verbose and print(a)
            for pid, p in enumerate(pat_list):
                m = p.match(a)
                if m is not None:
                    if 0 == pid:
                        # <F>, <G> [<short M>.]
                        fn = m.group(1)
                        gn = m.group(2).split(' ')
                        if len(gn) == 1:
                            gn = gn[0]
                            fn, gn = fix_name_order(fn, gn)
                    elif 1 == pid:
                        # <short G>. [<short M>.] {<F>}
                        fn = m.group(2)
                        gn = m.group(1).split(' ')
                        if len(gn) == 1:
                            gn = gn[0]
                            fn, gn = fix_name_order(fn, gn)
                    elif 2 == pid:
                        fn = m.group(2)
                        gn = m.group(1)
                        fn, gn = fix_name_order(fn, gn)

                    name = self.compose_author(fn, gn)
                    name = clean_name(name)
                    author_list.append(name)
                    self.verbose and print(aid + 1, '|', name)
                    break

        assert len(author_list) > 0, "* NO AUTHOR"
        return author_list

    def judge_type(self, cite_obj):
        """re-judge paper type, e.g. conference, journal, preprint, book
        because the original paper type in bibtxt may NOT always correct
        1. re-judge the paper with recognising strings from `prior`
        2. judge with original paper type from `parse_type`
        """

        if hasattr(cite_obj, "archiveprefix"):
            return "preprint"

        if hasattr(cite_obj, "booktitle"):
            bt_low = cite_obj.booktitle.lower()
            if "arxiv" in bt_low:
                return "preprint"

            for paper_t, abbr_set in zip(
                ["preprint", "conference", "journal"],
                [self.prior.ABBR_PRE, self.prior.ABBR_CONF, self.prior.ABBR_JOUR],
            ):
                for _abbr in abbr_set:
                    if _abbr in cite_obj.booktitle:
                        return paper_t
                    for _rec_str in abbr_set[_abbr]:
                        if _rec_str.lower() in bt_low:
                            return paper_t

        # if the type is NOT determined with the above process
        # then judge with preliminarily parsed paper type
        assert hasattr(cite_obj, "paper_type")
        if cite_obj.paper_type in ["conference", "inproceedings", "proceedings"]:
            return "conference"
        elif "article" == cite_obj.paper_type:
            return "journal"
        elif "book" == cite_obj.paper_type:
            return "book"
        elif "misc" == cite_obj.paper_type:
            return "preprint"

        # NOT applicable
        raise Exception("* can NOT judge the paper type")

    def parse_page(self, s):
        m = re.match(r"(\d+)\D*(\d+)", s)
        assert m is not None
        begin = int(m.group(1))
        end = int(m.group(2))
        self.verbose and print("pages:", begin, ',', end)
        return (begin, end)

    def short_booktitle(self, s):
        """convert book title to it's abbreviation"""
        s_low = s.lower()

        # special deal for arXiv
        if "arxiv" in s_low:
            return s

        bt = None
        for _abbr in self.prior.ABBR:
            if _abbr in s:
                bt = _abbr
                break
            for _name in self.prior.ABBR[_abbr]:
                if _name.lower() in s_low:
                    bt = _abbr
                    break
            if bt is not None:
                break

        assert bt is not None, \
            "* UNRECOGNISED CONFERENCE/JOURNAL: {}".format(s)
        self.verbose and print("booktitle:", bt)
        return bt

    def parse(self, bibtex):
        cite = Cite()
        # priliminary parsing, re-judge in `gen_ref` using `judge_type`
        cite.paper_type = self.parse_type(bibtex)

        # pattern: <key> = {<value>}[,}\s]
        # match the last redundant `[,}\s]` (i.e. `,` or `}` or white space) for convenience
        item_pat = re.compile(r"\w+\s*\=\s*[\{\"][^\=]*[\}\"][\,\}\s]")
        # item_pat = re.compile(r"\w+\s*\=\s*[\{\"][" + VOCAB + r"]*[\}\"][\,\}\s]")
        # print(item_pat)
        item_list = item_pat.findall(bibtex)
        self.verbose and print("#item:", len(item_list))
        # for i, _it in enumerate(item_list):
            # print(i + 1, '|', _it, '\n')

        item_split_pat = re.compile(r"(\w+)\s*\=\s*[\{\"]([^\=]*)[\}\"][\,\}\s]")
        # item_split_pat = re.compile(r"(\w+)\s*\=\s*[\{\"]([" + VOCAB + r"]*)[\}\"]")
        for i, _item in enumerate(item_list):
            # print(i + 1, '|', _item.replace('\r', '<CR>').replace('\n', '<LF>'), flush=True)
            m_obj = item_split_pat.match(_item)#[:-1])
            assert m_obj is not None
            k = m_obj.group(1).lower()
            v = m_obj.group(2)
            # print(i + 1, '|', k, '|', v, '\n')

            # v = v.replace(os.linesep, ' ')
            v = v.replace('\r', ' ').replace('\n', ' ')
            v = ' '.join(v.split())
            v = v.strip()  # remove redandunt white space
            if "" == v:
                continue

            if k in ["booktitle", "journal"]:
                v = clean_booktitle(v)
                cite.booktitle = v
                self.verbose and print("book title:", v)
            elif "author" == k:
                cite.author = self.parse_author(v)
            elif "title" == k:
                cite.title = self.parse_title(v)
            elif "pages" == k:
                cite.pages = self.parse_page(v)
            elif k in ["year", "volume", "number", "articleno", "numpages"]:
                if not v.isdigit():
                    print("NON-DIGIT:", v)
                    continue
                setattr(cite, k, int(v))
                self.verbose and print(k, ":", v)
            elif k in ["eprint", "publisher", "organization", "address", "archiveprefix", "edition"]:
                setattr(cite, k, v)
                self.verbose and print(k, ":", v)

        return cite

    def gen_ref(self, cite_obj):
        """generate reference string based on parsed Cite object"""
        raise NotImplemented
