# ref-gen

A Python script for generating reference string by parsing bibtex.

The core of this script is parsing the bibtex entries with regular expressions[1] for structural information, with which one can generate the reference string in whatever format needed.

# Environment Requirement

[Python 3](https://www.python.org/) only (tested under Python 3.7.4 on Windows 7)

# Usage

## basic usage

Put a bibtex in the *bib.txt* in the same directory as *parse.py*, and run:

```shell
python parse.py
```

it will output the generated reference string in both the terminal and *ref.txt*.

## specify input & output

By default, the input & output files are *bib.txt* and *ref.txt* respectively, one can specify them with `-f` and `-o`:

```shell
# specify input
python parse.py -f bib2.txt
# specify output
python parse.py -o out.txt
# specify both
python parse.py -f bib3.txt -o abc.txt
```

## specify truncation length of author list

By default, this script will truncate the author list by `3`, which means if there are more than `3` authors, only the first `3` will be shown, and the rest are represented by an `et al.`.

You can specify this truncation length with `--n_name` parameter:

```shell
# show first 1 author only
python parse.py --n_name 1
# show ALL authors WITHOUT truncation if `n_name` <= 0
python parse.py --n_name -1
# or you can also simply feed a large number like `100`
python parse.py --n_name 100
```

See the `less_author` function in this script for details.

# Customization

## abbreviations of conferences / journals

The abbreviations of conferences & journals are specified with `JC_ABBR` in the script, each item of which are of format:

```python
"<ABBR>": ["<RECSTR_1>", ...]
```

where `<ABBR>` denotes the abbreviation, and `<RECSTR_*>` denotes a *recognizing string* for a conference / journal name.  For example, for a paper from the [CVPR](Conference on Computer Vision and Pattern Recognition) conference, the `booktitle` filed may look like:

```
2017 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)
```

To recognize this conference, in this script, a representative sub-string `Computer Vision and Pattern Recognition` is used for its *recognizing string*, as every time this substring shows up in the `booktitle` field, we’re almost sure that it’s a paper from the *CVPR* conference.

Recognizing string can be multiple for a conference / journal, as the `booktitle` / `journal` filed may differ.

One can modify or add entries to the `JC_ABBR` on his own need. If an `UNRECOGNISED CONFERENCE/JOURNAL: ...` exception arise, one should add an entry to `JC_ABBR` to support that conference / journal.

Notes that both `<ABBR>` and `<RECSTR_*>` are case insensitive, see the `parse_booktitle` function for details.

## format of reference string

The parsed structural information is stored in a `Cite` object (see the `Cite` class for details), and the ref string is generated based on it in the `gen_ref` function. For custom ref string format, re-write it.

## title style

The title is processed by the `parse_title` and `parse_hyphen_word` function. Generally, they try to capitalize each word, **except**:

- Pascal-case words, like `WordNet`, as they’re usually proper nouns
- all-caps words, like `R-CNN`, also proper nouns
- some *stop words* listed in `STOP_WORD`, such as the prepositions and articles
- the word after a *prefix* listed in `PREFIX`, like the *supervised* in *semi-supervised*, as it’s treated as one word
- *suffixes* listed in `SUFFIX`

Notes that the first word is **always** capitalized. 

See these two functions for details and re-write them for customization if needed.

# Author Patterns

Here are some patterns (and some corresponding examples) of author name I’ve met. One may add more in the `parse_author` function if that’s not supported currently.

`<F>` stands for *family name*, `<M>` for *middle name*, `<G>` for *given name*, `[·]` for *optional*.

1. `<F>, <G> [<short M>.]`
   - `author = {Miller, George A.}`
   - `author = {Zhan, Yu-Wei and Luo, Xin and Wang, Yongxin and Xu, Xin-Shun}`
   - `author="Deng, Jia and Ding, Nan and Jia, Yangqing and Frome, Andrea and Murphy,  evin and Bengio, Samy and Li, Yuan and Neven, Hartmut and Adam, Hartwig"`
2. `<short G>. [<short M>.] {<F>}`
   - `author={Y. {Chen} and L. {Wang} and W. {Wang} and Z. {Zhang}}`
   - `author={A. {Sharma} and A. {Kumar} and H. {Daume} and D. W. {Jacobs}}`
3. `{<G> <F>}`

# To-dos

- add support to Chinese character

# References

1. [Python3 正则表达式](https://www.runoob.com/python3/python3-reg-expressions.html#flags)
2. [由bibtex生成引用文献字符串](https://blog.csdn.net/HackerTom/article/details/113802147)