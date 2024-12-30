def switch_case(token, parent = None):
	lemma = token["lemma"]
	deprel = token["deprel"]

	#======<Static location>===========================================
	# Inessive
	if lemma in ["in", "entro", "dentro"]:
		return "Ine"
	
	# NOTE: 'entro' has also many occurrences in which it is temporal Lim (e.g., 'entro sessanta giorni dalla consegna dalla pubblicazione della legge', ISDT), however, promoted spatial sense, according to the guidelines.

	# Interessive
	# TODO: decide how to treat things that are not 'fixed' e.g., 'in mezzo a', which could be mapped to 'Ces' (Interessive)
	
	# Intrative (between X and Y)
	if lemma in ["tra", "fra"]:
		return "Int"

	# External
	if lemma in ["fuori", "fuori da"]:
		return "Ext"

	# Superadessive
	if lemma in ["su", "su di"]:
		return "Adt"
	
	# NOTE: 'su di' can also have a The - Themative meaning: 'i libri che si scriveranno su di lui' 'the books that will be written about him'.

	# Apudessive (next to something)
	if lemma in ["accanto a"]:
		return "Apu"

	# Circumessive
	if lemma in ["attorno a", "intorno a"]:
		return "Cir"
	
	# Proximative
	if lemma in ["vicino", "vicino a"]:
		return "Prx"
	
	# Distantive
	if lemma in ["lontano da"]:
		return "distantive"
	
	# Superessive
	if lemma in ["sopra"]:
		return "Sup"
	
	# Subessive
	if lemma in ["sotto"]:
		return "Sub"
	
	# TODO: handle 'sopra o sotto'
	
	# Antessive
	if lemma in ["davanti", "davanti a"]:
		return "Ant"

	# Postessive
	if lemma in ["dietro", "dietro a", "dietro di"]:
		return "Pst"

	# Oppositive
	# TODO: decide how to treat things that are not 'fixed' e.g., 'di fronte a', which could be mapped to 'Opp' (Oppositive)
	#======<\Static location>============================================

	#======<Direction focused on origin>=================================
	
	# Ablative
	if lemma in ["da"]:
		if parent["deprel"] != "obl:agent":
			return "Abl"

	# TODO: avoid falling back to default when deprel == obl:agent

	#======<\Direction focused on origin>==================================
	
	#======<Direction focused on path>=====================================

	# TODO: direction focused on path

	#======<\Direction focused on path>====================================
	
	#======<Direction focused on destination>==============================
	
	# Lative
	if lemma in ["a", "verso"]:
		return "Lat" 
	
	# NOTE: it seems impossible to distinguish when "a" introduces a Dative. It it. treebanks when the indirect object is realized as a prepositional phrase, it is labeled as obl (ex. Dare a qualcuno qualcosa, give something to someone).

	# NOTE: 'verso' can be also temporal approximative
	
	#======<\Direction focused on destination>==============================

	#======<Temporal>=======================================================
	
	# Temporal antessive
	if lemma in ["prima di", "prima che"]:
			return "Tan"
	
	# Temporal postessive (after a point or period)
	if token["lemma"] in ["dopo", "dopodiché", "dopo di che"]:
			return "Tps"

	# Temporal terminative
	if token["lemma"] in ["fino a", "finché", "fino a che"]:
			return "Ttr"
	
	# NOTE: it's normal that when deprel = mark the lemma has only temporal meaning and when deprel = case it can have both temporal and spatial, because if it is 'mark' then it's anchored to an 'event' and an 'event' cannot be before, after or until in a spatial sense, but only in a temporal sense. 

	# Temporal (at, on, in, upon a point in time)
	if token["lemma"] in ["appena", "quando"]:
		return "Tem"
	
	# NOTE: 'Quando' (when) is also conditional, but we treat the conditional meaning as an extension of the temporal. 
	
	# Durative (during a period)
	if token["lemma"] in ["mentre"]:
		return "Dur"
	
	# deprel = advmod; frattanto, intanto (Durative - Dur).
	# deprel = advmod; circa (Temporal approximative - Tpx). But also not temporal (is approximative in general: circa il 12% della popolazione; no case of approximation beside temporal approximation).

	#======<\Temporal>======================================================

	#======<Relation>=======================================================
	
	# Genitive
	if token["lemma"] in ["di"]: # be aware of polysemy
		return "Gen"
	
	# Comitative
	if token["lemma"] in ["con"]: # be aware of polisemy
		return "Com"

	# Abessive (without something)
	if token["lemma"] in ["salvo che", "senza", "senza che"]:
		return "Abe"
	
	# TODO: decide how to treat things that are not 'fixed': e.g., 'a meno che'.
	
	# NOTE: in 'inventory.md' also 'salvo' is under Absessive, but in the treebank 'salvo' has deprel = amod and is considered 'ADJ'.

	# Inclusive
	# TODO: decide what to do with form = 'compreso', 'incluso'.

	# Additive (besides, in addition to something)
	if token["lemma"] in ["oltre", "oltre a", "oltre che"]:
		return "Add"
	
	# NOTE: example: "... pagando, oltre il valore della metà del muro, il valore del suolo da occupare con la nuova fabbrica)". However, 'oltre' can also be used as a Spx (Superprolative) (?) ex. "In Italia vi sono oltre 40 modelli posti in commercio da una ventina di distributori". 

	# Exclusive
	if token["lemma"] in ["tranne", "tranne che", "tranne in", "eccetto", "eccetto che", "tranne quando", "fuorché"]:
		return "Exc"
	
	# NOTE: Exclusive - lemmas from LICO "Negative condition:Arg2" + "Exception:Arg2"

	# TODO: precise difference between Abessive and Exclusive?

	# Substitutive
	if token["lemma"] in ["anziché", "piuttosto che", "invece di"]:
		return "Sbs"

	# NOTE: Substitutive - lemmas from LICO Substitution:Arg1
	# deprel = advmod; 'piuttosto che' (Sbs - Substitutive)
	# TODO: decide what to do with 'al posto di' [lemma = 'posto', child lemma = 'a', 'il'], 'in luogo di'.

	#======<\Relation>======================================================

	#======<Similarity>=====================================================

	# TODO: Similarity

	#======<\Similarity>====================================================
	
	#======<Cause, consequence, circumstance, other>========================
	
	# TODO: work in progress
	
	# Causative
	if token["lemma"] in ["giacché", "perché", "poiché", "siccome"]:
		return "Caus"
	
	# Purposive
	if token["lemma"] in ["affinché"]:
		return "Pur"

	# Themative
	if token["lemma"] in ["riguardo a", "circa"]:
		return "The"
	
	# Concessive
	if token["lemma"] in ["anche se", "benché", "malgrado", "nonostante", "quantunque", "sebbene", "seppure"]:
		return "Ccs"  
	
	# lemma = seppur(e) in ISDT has only 2 occurrences and one time is deprel = mark and the other is deprel = advmod
	
	# Adversative
	if token["lemma"] in ["contro"]:
		return "Adv"
	
	# 'anti', suggested in 'inventory.md' is usually a prefix 'anti-'. When written with a whitespace in between is marked with deprel = amod and considered an ADJ.

	#======<\Cause, consequence, circumstance, other>=====================================================

	return f"TBD-'{token['lemma']}'"

def switch_conj_case(token):

	#======<\Coordination>=====================================================

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

	#======<\Coordination>=====================================================

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
