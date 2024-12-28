def switch_nominal_case(token):

	if token["lemma"] in ["entro", "dentro"]:
		return "Ine" # Inessive
	
	# NOTE: 'entro' has also many occurrences in which it is temporal Lim (e.g., 'entro sessanta giorni dalla consegna dalla pubblicazione della legge', ISDT), however, according to the guidelines, we promoted the spatial sense.
	
	if token["lemma"] in ["tra", "fra"]:
		return "Int" # Intrative (between X and Y)

	if token["lemma"] in ["su"]:
		return "Adt" # Superadessive 
	
	if token["lemma"] in ["a"]:
		return "Lat" # Lative 
	
	# NOTE: it seems impossible to distinguish when "a" introduces a Dative. It it. treebank when the indirect object is realized as a prepositional phrase, it is labeled as obl (ex. Dare a qualcuno qualcosa, give something to someone).

	if token["lemma"] in ["prima di"]:
		return "Ant" # Antessive but Temporal antessive much more frequent

	if token["lemma"] in ["dopo"]:
		return "Pst" # Postessive but Temporal postessive much more frequent

	if token["lemma"] in ["fino a"]:
		return "Ter" # Terminative but Temporal terminative much more frequent

	# NOTE: it's normal that deprel = mark has only temporal meaning and deprel = case can have both temporal and spatial, because if it is 'mark' then it's anchored to an 'event' and an 'event' cannot be before, after or until in a spatial sense, but only in a temporal sense. 

	if token["lemma"] in ["oltre", "oltre che"]:
		return "Add" # Additive (besides, in addition to something 
	
	# NOTE: example: "... pagando, oltre il valore della metà del muro, il valore del suolo da occupare con la nuova fabbrica)". However, 'oltre' can also be used as a Spx (Superprolative) ex. "In Italia vi sono oltre 40 modelli posti in commercio da una ventina di distributori". 

	if token["lemma"] in ["con"]:
		return "Com" # Comitative

	if token["lemma"] in ["di"]:
		return "Gen" # Genitive

	if token["lemma"] in ["senza"]:
		return "Abe" # Abessive (without something)
	
	# NOTE: in 'inventory.md' also 'salvo' is under Absessive (which is correct), but in the treebank 'salvo' has deprel = amod and is considered 'ADJ'.

	if token["lemma"] in ["tranne", "tranne che", "tranne in", "eccetto", "eccetto che"]:
		return "Exc" # Exclusive

	if token["lemma"] in ["piuttosto che"]:
		return "Sbs" # Substitutive

	if token["lemma"] in ["rispetto a", "riguardo a"]:
		return "Cns" # Considerative
	
	if token["lemma"] in ["nonostante", "malgrado"]:
		return "Ccs" # Concessive
	
	if token["lemma"] in ["contro"]:
		return "Adv" # Adversative
	
	# 'anti', suggested in 'inventory.md' is usually a prefix 'anti-'. When written with a whitespace in between is marked with deprel = amod and considered an ADJ.

	return f"TBD-'{token['lemma']}'"

def switch_verbal_case(token):
	# NOTE: modus operandi. In a totally exploratory fashion I am 
	# 1) Retrieving lemmas
	# 1.1) having a look at the lemmas proposed by Omer and Leonie in 'inventory.md' for each 'Case'
	# 1.2) having a look at LICO (http://connective-lex.info/#{%22s%22:[%22lico_d%22]}) to see if other lemmas can be added to the 'inventory.md'
	# 2) then I am looking for examples in ISDT of that lemma in context.  

	# For now I am working on 'mark' and 'case' separately, however it can have little sense.

	if token["lemma"] in ["prima di", "prima che"]:
		return "Tan" # Temporal antessive (before a point in time)
	
	if token["lemma"] in ["finché", "fino a che"]:
		return "Ttr" # Temporal terminative
	
	if token["lemma"] in ["dopo", "dopodiché", "dopo di che"]:
		return "Tps" # Temporal postessive (after a point or period)
	
	# deprel = advmod; poi (Temporal postessive)
	
	if token["lemma"] in ["appena", "quando"]:
		return "Tem" # Temporal (at, on, in, upon a point in time)
					 # 'Quando' (when) is also very often conditional, but we treat the conditional meaning as an extension of the temporal. 
	
	if token["lemma"] in ["mentre"]:
		return "Dur" # Durative (during a period)
	
	# deprel = advmod; frattanto, intanto (Durative - Dur).
	# deprel = advmod; circa (Temporal approximative - Tpx). But also not temporal (is approximative in general: circa il 12% della popolazione; no case of approximation beside temporal approximation).

	if token["lemma"] in ["salvo che", "senza", "senza che"]:
		return "Abe" # Abessive (without something)
	
	# TODO: decide how to treat things that are not 'fixed': e.g., 'a meno che'.

	if token["lemma"] in ["tranne quando", "fuorché"]:
		return "Exc" # Exclusive
	
	# TODO: deepen the understanding of the differences between Abessive and Exclusive.
	
	# NOTE: Exclusive - lemmas from LICO "Negative condition:Arg2" + "Exception:Arg2"

	if token["lemma"] in ["oltre a"]:
		return "Add" # Additive
	
	# deprel = advmod; inoltre (Add - Additive)
	
	if token["lemma"] in ["anziché", "piuttosto che", "invece di"]:
		return "Sbs" # Substitutive

	# deprel = advmod; 'piuttosto che' (Sbs - Substitutive)
	# TODO: decide what to do with 'al posto di' [lemma = 'posto', child lemma = 'a', 'il'], 'in luogo di'.

	# NOTE: Substitutive - lemmas from LICO Substitution:Arg1

	if token["lemma"] in ["giacché", "perché", "poiché", "siccome"]:
		return "Caus"  # Causative
	
	if token["lemma"] in ["affinché"]:
		return "Pur"  # Purposive
	
	if token["lemma"] in ["anche se", "benché", "malgrado", "nonostante", "quantunque", "sebbene", "seppure"]:
		return "Ccs"  # Concessive 
	
	# lemma = seppur(e) in ISDT has only 2 occurrences and one time is deprel = mark and the other is deprel = advmod

    # Default mapping for unlisted lemmas
	return f"TBD-{token['lemma']}"

def switch_conj_case(token):

	if token["lemma"] in ["e", "ed"]:
		return "Conj"

	if token["lemma"] in ["o", "oppure"]:
		return "Disj"

	if token["lemma"] in ["né"]:
		return "Nnor"

	if token["lemma"] in ["ma", "però"]:
		return "Advs"

	if token["lemma"] in ["se"]:
		return "Doubt"

	if token["lemma"] in ["anziché", "piuttosto che"]:
		return "Sbs"
	# Here because in ISDT many 'anziché' and 'piuttosto che' have deprel = cc

	return f"TBD-CONJ-{token['lemma']}"


def switch_verb_modality(token):

	if token["lemma"] == "potere":
		return "Pot"

	if token["lemma"] == "volere":
		return "Des"

	if token["lemma"] == "dovere":
		return "Nec"

	# TODO: what about prms?


def switch_det_definitess(token):
	if token["lemma"] == "nessuno":
		return "Def"

	if token["lemma"] == "alcuno":
		return "Def"

	if token["lemma"] == "qualche":
		return "Ind"

	if token["lemma"] == "questo":
		return "Def"

	if token["lemma"] == "quello":
		return "Ind"

	# * accounts for dei, degli, della etc...
	if token["lemma"] == "di":
		return "Ind"


def switch_det_polarity(token):
	if token["lemma"] == "nessuno":
		return "Neg"

	if token["lemma"] == "alcuno":
		return "Neg"


def switch_det_dem(token):
	if token["lemma"] == "questo":
		return "Prox"

	if token["lemma"] == "quello":
		return "Dist"


# def switch_pron_person(token):
# 	if token["lemma"] in ["io", "noi", "mi", "ci"]:
# 		return "1"
# 	if token["lemma"] in ["tu", "voi", "ti", "vi"]:
# 		return "2"
# 	if token["lemma"] in ["lui", "lei", "egli", "ella", "esso", "essa",
# 								"loro", "le", "gli", "il", "lo", "la", "le", "li",
# 								"chi", "che", "si"]:
# 		return "3"
