@echo off
setlocal enabledelayedexpansion
REM cls

for %%f in (bib/*.txt) do (
	REM echo %%f
	python parse.py -f bib/%%f -o ref.txt -a
)

start ref.txt
