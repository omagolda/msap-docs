def switch_nominal_case(token):
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

# if child_tok["lemma"] == "potere":
			# 	logger.debug("Adding Mood feature with value %s", child_tok["Pot"])
			# 	head_tok["ms feats"]["Mood"].add(child_tok["Pot"])
			# else:
			# 	logger.warning("Aux/cop %s with features %s", child_tok, child_tok["feats"])

			# if child_tok["lemma"] == "volere":
			# 	logger.debug("Adding Mood feature with value %s", child_tok["Des"])
			# 	head_tok["ms feats"]["Mood"].add(child_tok["Des"])
			# else:
			# 	logger.warning("Aux/cop %s with features %s", child_tok, child_tok["feats"])

			# if child_tok["lemma"] == "dovere":
			# 	logger.debug("Adding Mood feature with value %s", child_tok["Nec"])
			# 	head_tok["ms feats"]["Mood"].add(child_tok["Nec"])
			# else:
			# 	logger.warning("Aux/cop %s with features %s", child_tok, child_tok["feats"])

# | *__Other conjunctions__*                                                                                                                         ||
# | Advs     | adversative            |                                    | X but Y                                                                          |                                                      | but, yet, though                            | ale, avšak, však, nýbrž                                                                  | ale                                                                    | ale                                                                    | але, аднак, затое, прычым | но, зато | но | tačiau | bet | ma | pero | mas | aber, sondern | maar | men | لٰكِنَّ | lākinna |
# | Reas     | reason                 |                                    | X because / for Y (if paratactic; hypotactic constructions would be Case=Cau above) |                                                      | for                                         | neboť                                                                                    | lebo                                                                   | bo                                                                     |  | ведь | защото |  | jo |  |  |  | denn | want | för, ty |  |  |
# | Cnsq     | consequence            |                                    | X therefore Y                                                                    |                                                      | so, therefore                               | tedy, tak                                                                                | takže, tak                                                             | tak, dlatego                                                           | таму | поэтому | така |  | tātad, tā | quindi | pues, entonces | então | also, so | dus, daarom | därför, så | فَ | fa
# | Cnsc     | consecutive            |                                    | Y after X (applicable only to predicates and only if different from conjuctive)  | 	Swahili                                             ||
# | Temp     |                        | temporal                           | X when Y                                                                         |                                                      | when                                        |                                             |                                                                                          |                                                                        |                                                                        |                                                                        |                                                                        |
# | Doubt    |                        | 	introduces doubt                  | X whether Y                                                                      |                                                      | whether                                     | | | | | | | | | | | | ob