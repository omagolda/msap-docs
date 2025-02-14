# Simple Makefile to process three UD Turkish IMST files.

PYTHON = python

# Default rule to build all three .msf outputs
all: tr_imst-ud-train.msf tr_imst-ud-dev.msf tr_imst-ud-test.msf

# Each target depends on the corresponding .conllu file
%.msf: %.conllu
	$(PYTHON) parser.py $<

clean:
	rm -f tr_imst-ud-train.msf tr_imst-ud-dev.msf tr_imst-ud-test.msf
