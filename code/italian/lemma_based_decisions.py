def switch_nominal_case(token):
	return f"TBD-'{token['lemma']}'"

def switch_verbal_case(token):
	return f"TBD-'{token['lemma']}'"

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

	# if token["lemma"] in ["né"]:
	# 	return "Nnor"

	return f"TBD-CONJ-{token['lemma']}"


def switch_verb_modality(token):

	if token["lemma"] == "potere":
		return "Pot"

	if token["lemma"] == "volere":
		return "Des"

	if token["lemma"] == "dovere":
		return "Nec"

	return f"TBD-MOD-{token['lemma']}"


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
