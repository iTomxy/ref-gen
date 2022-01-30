import re
from .base import *


class ComputerEngineeringParser(Parser):

    def compose_author(self, first_name, given_name):
        if self.abbr_author:
            if isinstance(given_name, str):
                given_name = short_name(given_name)
            else:
                assert isinstance(given_name, (list, tuple))
                given_name = list(map(short_name, given_name))

        if isinstance(given_name, (list, tuple)):
            given_name = ' '.join(given_name)

        return "{} {}".format(first_name.upper(), given_name)

    def gen_ref(self, cite_obj):
        _author = less_author(cite_obj.author, self.n_name)
        res = "{}. {}".format(_author, cite_obj.title)
        # re-judge the paper type
        cite_obj.paper_type = self.judge_type(cite_obj)

        if "preprint" == cite_obj.paper_type:
            _t = time.localtime(time.time())
            _today = time.strftime("%Y-%m-%d", _t)

            # NOTE: add modification time later
            # _mod_time = cite_obj.eprint.split(".")[0]
            # _mod_year = int(_mod_time[:-2])
            # _mod_month = int(_mod_time[-2:])
            # if _mod_year > _t.tm_year % 100:
                # _mod_year += 1900
            # else:
                # _mod_year += 2000

            
            if not hasattr(cite_obj, "eprint"):
                # the one exported from arXiv should contain the `eprint` field,
                # but the one exported from Google Scholar may have NO `eprint` field`,
                # and should have the `booktitle` field
                assert hasattr(cite_obj, "booktitle")
                _pat = r"arxiv\s+preprint\s+arxiv\:([0-9\.]+)"
                m_obj = re.match(_pat, cite_obj.booktitle.lower())
                cite_obj.eprint = m_obj.group(1)
    
            _link = "https://arxiv.org/abs/{}".format(cite_obj.eprint)
            res += "[EB/OL]. [{}]. {}".format(_today, _link)
        elif "conference" == cite_obj.paper_type:
            _book_title = short_booktitle(cite_obj.booktitle) \
                if self.abbr_book_title else cite_obj.booktitle
            res += "[C]//{}".format(_book_title)

            if hasattr(cite_obj, "address") or hasattr(cite_obj, "publisher"):
                if hasattr(cite_obj, "address") and hasattr(cite_obj, "publisher"):
                    res += ". {}: {},".format(cite_obj.address, cite_obj.publisher)
                elif hasattr(cite_obj, "address"):
                    res += ". {},".format(cite_obj.address)
                elif hasattr(cite_obj, "publisher"):
                    res += ". {},".format(cite_obj.publisher)
            else:
                res += '.'

            res += " {}".format(cite_obj.year)

            if hasattr(cite_obj, "pages"):
                res += ": {}-{}".format(*cite_obj.pages)
            elif hasattr(cite_obj, "articleno") and hasattr(cite_obj, "numpages"):
                res += ": {0}:1-{0}:{1}".format(
                    cite_obj.articleno, cite_obj.numpages)
        elif "journal" == cite_obj.paper_type:
            _book_title = short_booktitle(cite_obj.booktitle) \
                if self.abbr_book_title else cite_obj.booktitle
            res += "[J]. {}, {}".format(_book_title, cite_obj.year)

            if hasattr(cite_obj, "volume"):
                res += ", {}".format(cite_obj.volume)
                if hasattr(cite_obj, "number"):
                    res += "({})".format(cite_obj.number)

            if hasattr(cite_obj, "pages"):
                res += ": {}-{}".format(*cite_obj.pages)
            elif hasattr(cite_obj, "articleno") and hasattr(cite_obj, "numpages"):
                res += ": {0}:1-{0}:{1}".format(
                    cite_obj.articleno, cite_obj.numpages)
        elif "book" == cite_obj.paper_type:
            res += "[M]"
            if hasattr(cite_obj, "edition"):
                res += ". {} ed".format(cite_obj.edition)

            if hasattr(cite_obj, "address") or hasattr(cite_obj, "publisher"):
                if hasattr(cite_obj, "address") and hasattr(cite_obj, "publisher"):
                    res += ". {}: {},".format(cite_obj.address, cite_obj.publisher)
                elif hasattr(cite_obj, "address"):
                    res += ". {},".format(cite_obj.address)
                elif hasattr(cite_obj, "publisher"):
                    res += ". {},".format(cite_obj.publisher)
            else:
                res += '.'

            res += " {}".format(cite_obj.year)

            if hasattr(cite_obj, "pages"):
                res += ": {}-{}".format(*cite_obj.pages)
            elif hasattr(cite_obj, "numpages"):
                res += ": {1}".format(cite_obj.numpages)
        else:
            print("* UNSUPPORTED ARTICLE TYPE")
            return None

        res += "."
        # res = res.replace("..", ".")
        return res
