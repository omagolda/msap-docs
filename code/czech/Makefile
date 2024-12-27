SHELL=/bin/bash

UDDIR = /net/work/people/zeman/unidep
INPUT = $(UDDIR)/UD_Czech-PUD/cs_pud-ud-test.conllu
OUTPUT = $(UDDIR)/UD_Czech-PUD/cs_pud-ud-test.msf
LKDIR = /net/work/people/zeman/casovani-sloves/Slavic_languages
TMPFILE = /net/work/people/zeman/msap-docs/code/czech/lk.conllu

.PHONY: all
all: view

# MsfCreateAbstract must not be invoked before Msf features are removed from function words.
SCEN = util.Filter delete_tree_if_node='node.udeprel == "orphan"' mwe.MsfInit mwe.MsfNumPhrase mwe.MsfCase mwe.MsfRemoveFunc mwe.MsfCreateAbstract
LKSCEN = mwe.Slavic_cond mwe.Slavic_future mwe.Slavic_imperative mwe.Slavic_inf mwe.Slavic_past mwe.Slavic_pres mwe.Slavic_transgressive

# Process a CoNLL-U file and view the resulting trees.
.PHONY: view
view:
	cd $(LKDIR) ; ./main.sh -i $(INPUT) -o $(TMPFILE)
	cat $(TMPFILE) | udapy -TA $(SCEN) | less -R

.PHONY: viewmsf
viewmsf:
	cd $(LKDIR) ; ./main.sh -i $(INPUT) -o $(TMPFILE)
	cat $(TMPFILE) | udapy -s $(SCEN) | ./conllu2msfeats.pl | less

# Process a CoNLL-U file and save it in the MSF CoNLL-U Plus format.
.PHONY: convert
convert:
	cd $(LKDIR) ; ./main.sh -i $(INPUT) -o $(TMPFILE)
	cat $(TMPFILE) | udapy -s $(SCEN) | ./conllu2msfeats.pl > $(OUTPUT)

