# ref-gen

[English version](README-en.md)

用 Python 根据 bibtex 文件生成引用字符串，用于中文论文。目前只支持英文 bibtex。

# 依赖

- [Python 3](https://www.python.org/)

# 用法

用例见 *parse.bat*。

## 参数

- `-f`：（可多个）要解析的 .bib 文件、有 .bib 的目录
- `-o`：输出文件，默认 *ref.txt*。
- `-v`：verbose，解析过程的 logging。
- `-s`：对 .bib 文件排序。可在 *parse.py* 自定义排序。
- `--abbr_author`：将名（given name）和中间名（middle name）改用缩写，如：`Tom` -> `T.`。
- `--abbr_book_title`：期刊、会议用缩写名，如：`IEEE Conference on Computer Vision and Pattern Recognition` -> `CVPR`。可在 *prior.py* 自定义缩写。
- `--n_name`：作者列表长度上限，超过则截断并加 `et al`，默认 `-1` 表示不截断。

# 自定义

## 会议、期刊缩写

在 *prior.py* 定义，其中 `ABBR_PRE`、`ABBR_CONF`、`ABBR_JOUR` 分别表示预印（如 arXiv）、会议、期刊的缩写，`ABBR` 是并集。

条目的定义格式形如：

```
"<缩写>": ["<基因1>", ...]
```

其中 `<缩写>` 就是会议等的目标缩写，如 `CVPR`；「基因」是指用来从 bibtex 的 `booktitle`/`journal` 域中辨认预印、会议和期刊的字符串，如 [CVPR](Conference on Computer Vision and Pattern Recognition) 会议的 `booktitle` 形如：

```
2017 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)
```

其中  `Conference on Computer Vision and Pattern Recognition` 就可以作为其「基因」，因为只要出现这个模式，必然是 CVPR 会议。

## 生成引用格式

生成的引用格式由所使用的解析器（parser）的 `gen_ref` 函数决定。parser 在 *parsers/* 下定义，*parsers/base.py* 是 parser 类的基类。

*parsers/ComputerEngineering.py* 是[计算机工程](http://www.ecice06.com/CN/1000-3428/home.shtml)期刊的例子，其格式要求见其[参考文献著录格式](http://www.ecice06.com/attached/file/20190617/20190617114639_479.docx)。

# 论文作者模式

目前支持的作者模式有以下几种。可以在 `parse_author` 函数里添加新的支持。

`<F>`：姓（family name），`<M>`：中间名（middle name），`<G>`：名（given name），`[·]`：可有可无。

1. `<F>, <G> [<short M>.]`
   - `author = {Miller, George A.}`
   - `author = {Zhan, Yu-Wei and Luo, Xin and Wang, Yongxin and Xu, Xin-Shun}`
   - `author="Deng, Jia and Ding, Nan and Jia, Yangqing and Frome, Andrea and Murphy,  evin and Bengio, Samy and Li, Yuan and Neven, Hartmut and Adam, Hartwig"`
2. `<short G>. [<short M>.] {<F>}`
   - `author={Y. {Chen} and L. {Wang} and W. {Wang} and Z. {Zhang}}`
   - `author={A. {Sharma} and A. {Kumar} and H. {Daume} and D. W. {Jacobs}}`
3. `[{]<G> <F>[}]`

# TODO

1. 支持中文 bibtex

# 参考

1. [由bibtex生成引用文献字符串](https://blog.csdn.net/HackerTom/article/details/113802147)

