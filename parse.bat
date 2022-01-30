@echo off
setlocal enabledelayedexpansion

cls

python parse.py -f 0.bib1.bib bib -o ref.txt -s --n_name 3
REM python parse.py -f bib/ -o ref.txt -s --n_name 3 -v

REM start ref.txt
