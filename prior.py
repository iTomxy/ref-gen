# paper type
# https://www.openoffice.org/bibliographic/bibtex-defs.html
# TYPE = {
#   "article": "journal",
#   "conference": "conference",
#   "inproceedings": "conference",
#    "proceedings": "conference",
#   "misc": "preprint",
#   "book": "book",
# }

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
# VOCAB = r"\w\s\<\>\[\]\(\)\{\}\"\'\`\^\+\*\~\–\-\/\\\,\.\:\;\!\?\&"

# abbreviations
ABBR_PRE = {  # preprint
    "arXiv": ["arXiv preprint", "arXiv:"],
}

ABBR_CONF = {  # conference
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
}

ABBR_JOUR = {  # journal
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

ABBR = dict(**ABBR_PRE, **ABBR_JOUR, **ABBR_CONF)
