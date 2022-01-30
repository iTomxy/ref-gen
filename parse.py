# -*- coding: utf-8 -*-
import argparse
import glob
import os
import os.path as osp
import platform
import prior
from parsers import ComputerEngineeringParser


parser = argparse.ArgumentParser(description='ref')
parser.add_argument('-f', type=str, nargs='+', default=["bib.bib"],
                    help="input bibtex file or folder")
parser.add_argument('-o', type=str, default="ref.txt",
                    help="output file of reference strings")
parser.add_argument('-v', action='store_true',
                    help='enable verbose to show the parsing process')
parser.add_argument('-s', action='store_true',
                    help='sort the bibtex files')
parser.add_argument('--abbr_author', action='store_true',
                    help='use short given name')
parser.add_argument('--abbr_book_title', action='store_true',
                    help='use abbreviation of book title')
parser.add_argument('--n_name', type=int, default=-1,
                    help="#author threshold, <=0 means show all authors")
args = parser.parse_args()


def _key(_str):
    """custom .bib file sorting key (ascending)"""
    _str = osp.basename(_str)
    # `<ID>.<ref-str>.bib` or `<ref-str>.bib`
    _str = _str.split(".")[0]
    if _str.isdigit():
        return int(_str)
    return _str


file_list = []
for _f in args.f:
    if osp.isfile(_f):
        file_list.append(_f)
    else:
        assert osp.isdir(_f)
        _list = glob.glob("{}/*.bib".format(_f))
        file_list.extend(_list)
if args.s:        
    _file_list = sorted(file_list, key=_key)


parser = ComputerEngineeringParser(
    prior, args.n_name, args.abbr_author, args.abbr_book_title, args.v)
fail_ids = []
with open(args.o, "w") as log_file:
    for fid, bib_f in enumerate(file_list):
        bib_key = osp.basename(bib_f).split('.')[-2]
        _info_str = "--- {}, {} ---".format(fid + 1, bib_key)
        print(_info_str)
        log_file.write('\n' + _info_str + '\n')

        bib = ""
        with open(bib_f, "r", encoding='utf-8') as f:
            for line in f:
                if "" != line.strip():
                    bib += line#.strip()
        # print(bib)
        # with open("tmp.txt", "w") as f:
            # f.write(bib)
        bib = bib.strip()

        _cite = parser.parse(bib)
        _ref = parser.gen_ref(_cite)
        if _ref is None:
            fail_ids.append(fid)
        else:
            print("{}\n".format(_ref))
            log_file.write("{}\n".format(_ref))

if len(fail_ids) > 0:
    print("*** FAILED ***")
    for _id in fail_ids:
        print(_id, ',', file_list[_id])

# if "Windows" == platform.system():
#     os.system("start {}".format(args.o))
