SHELL=/bin/bash

UDDIR = /net/work/people/zeman/unidep
INPUT = $(UDDIR)/UD_Czech-PUD/cs_pud-ud-test.conllu
OUTPUT = $(UDDIR)/UD_Czech-PUD/cs_pud-ud-test.msf

.PHONY: all
all: view

SCEN = mwe.Slavic_cond mwe.Slavic_future mwe.Slavic_imperative mwe.Slavic_inf mwe.Slavic_past mwe.Slavic_pres mwe.Slavic_transgressive util.Filter delete_tree_if_node='node.udeprel == "orphan"' mwe.MsfInit mwe.MsfNumPhrase mwe.MsfCase mwe.MsfRemoveFunc

# Process a CoNLL-U file and view the resulting trees.
.PHONY: view
view:
	cat $(INPUT) | udapy -TA $(SCEN) | less -R

.PHONY: viewmsf
viewmsf:
	cat $(INPUT) | udapy -s $(SCEN) | ./conllu2msfeats.pl | less

# Process a CoNLL-U file and save it in the MSF CoNLL-U Plus format.
.PHONY: convert
convert:
	cat $(INPUT) | udapy -s $(SCEN) | ./conllu2msfeats.pl > $(OUTPUT)

