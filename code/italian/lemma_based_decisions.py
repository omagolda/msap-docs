def switch_nominal_case(token):
	# TODO: check "rispetto a", "riguardo a" (deprel = case, fixed) = Cns, considerative

	# TODO: check "nonostante" when deprel = case (i.e., ha continuato a lavorare nonostante la malattia) vs. when deprel = mark (i.e., ha continuato a lavorare nonostante fosse malato), always concessive (?).

	return f"TBD-'{token['lemma']}'"

def switch_verbal_case(token):
	# NOTE: modus operandi. In a totally exploratory fashion I am 
	# 1) Retrieving lemmas
	# 1.1) having a look at the lemmas proposed by Omer and Leonie in 'inventory.md' for each 'Case'
	# 1.2) having a look at LICO (http://connective-lex.info/#{%22s%22:[%22lico_d%22]}) to see if other lemmas can be added to the 'inventory.md'
	# 2) then I am looking for examples in a corpus (for now, CORIS) of that lemma in context. 
	# 3) And then I am using the UDPipe demo to understand how they are parsed (i.e., are they considered MWE?, are they parsed as case, mark or advmod). 

	# For now I am working on 'mark' (as 'case' is handled above, however we can also have a discussion about this).

	# Adding comments as I go on to keep track of the categories already covered.

    if token["lemma"] in ["giacché", "perché", "poiché", "siccome"]:
        return "Caus"  # Causative

    if token["lemma"] in ["affinché"]:
        return "Pur"  # Purposive

    if token["lemma"] in ["anche se", "benché", "malgrado", "nonostante", "quantunque", "sebbene"]:
        return "Ccs"  # Concessive 

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
