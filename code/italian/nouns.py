import logging

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_noun(head_tok, children_toks):

	logging.debug("Setting %s/%s to content and copying its features", head_tok, head_tok["upos"])
	head_tok["content"] = True
	ita_utils.copy_features(head_tok)

	for child_tok in children_toks:
		logger.info("Examining child: %s", child_tok.values())

		# * evaluate copulas
		if child_tok["deprel"] in ["cop", "aux"]:
			# TODO: add polarity and verb-like features

			if child_tok.get("feats") and "Mood" in child_tok["feats"]:
				logging.debug("Adding TAM features with values Mood: %s - Tense: %s",
							child_tok["feats"]["Mood"], child_tok["feats"]["Tense"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
			else:
				logging.debug("No Mood feature in %s - %s", child_tok, child_tok["feats"])

			if child_tok.get("feats") and "Tense" in child_tok["feats"]:
				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
			else:
				logging.debug("No Tense feature in %s - %s", child_tok, child_tok["feats"])

			if child_tok.get("feats") and "VerbForm" in child_tok["feats"]:
				logging.debug("Adding VerbForm feature with value: %s",
							child_tok["feats"]["VerbForm"])
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])
			else:
				logging.debug("No VerbForm feature in %s - %s", child_tok, child_tok["feats"])

		# * evaluate determiners
		elif child_tok["deprel"] in ["det", "det:poss", "det:predet"]:

			if child_tok.get("feats") and "Gender" in child_tok["feats"]:
				logging.debug("Adding Gender feature with value %s", child_tok["feats"]["Gender"])
				head_tok["ms feats"]["Gender"].add(child_tok["feats"]["Gender"])
			if child_tok.get("feats") and "Number" in child_tok["feats"]:
				logging.debug("Adding Number feature with value %s", child_tok["feats"]["Number"])
				head_tok["ms feats"]["Number"].add(child_tok["feats"]["Number"])

			# * add definiteness
			if child_tok.get("feats") and "Definite" in child_tok["feats"]:

				logging.debug("Adding Definite feature with value %s", child_tok["feats"]["Definite"])
				head_tok["ms feats"]["Definite"].add(child_tok["feats"]["Definite"])

			elif lbd.switch_det_definitess(child_tok):

				definitess, polarity = lbd.switch_det_definitess(child_tok)
				logging.debug("Adding Definite feature with value %s", definitess)
				head_tok["ms feats"]["Definite"].add(definitess)

				if polarity:
					head_tok["ms feats"]["Polarity"].add(polarity)
			else:
				logging.debug("No Definite features in %s - %s", child_tok, child_tok["feats"])

			# * add polarity
			# ? should polarity be set to "Pos" by default?
			# polarity = lbd.switch_det_polarity(child_tok)
			# if polarity:
			# 	logging.debug("Adding Polarity feature with value %s", polarity)
			# 	head_tok["ms feats"]["Polarity"].add(polarity)

			if child_tok.get("feats") and "PronType" in child_tok["feats"]:
				if child_tok["feats"]["PronType"] == "Dem":
					dem = lbd.switch_det_dem(child_tok)
					if dem:
						logging.debug("Adding Dem feature with value %s", dem)
						head_tok["ms feats"]["Dem"].add(dem)
					else:
						logging.debug("No Dem features in %s - %s", child_tok, child_tok["feats"])

			# if not processed:
			# 	child_tok["content"] = True
			# # if Degree was set to Cmp earlier, now change it to Sup
			# if "Degree" in head_tok["ms feats"] and "Cmp" in head_tok["ms feats"]["Degree"]:
			# 	logging.debug("Changing Degree feature to Sup")
			# 	head_tok["ms feats"]["Degree"].remove("Cmp")
			# 	head_tok["ms feats"]["Degree"].add("Sup")

		# * evaluate case relations
		elif child_tok["deprel"] in ["case", "mark"]:
			logging.debug("Adding Case feature with value %s", lbd.switch_case(child_tok, head_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_case(child_tok, head_tok))

		elif child_tok["deprel"] in ["advmod"]:
			if child_tok["lemma"] in ["non"]:
				head_tok["ms feats"]["Polarity"].add("Neg")
			else:
				logging.warning("Adverb needs coding %s", child_tok)

		else:
			logging.warning("Node %s/%s with deprel '%s' needs new rules",
							child_tok, child_tok["upos"], child_tok["deprel"])

	# TODO: Handle aspect


def update_features(head_tok, children_toks):

	logging.debug("Examining content children of node %s/%s", head_tok, head_tok["upos"])
	# head_tok["content"] = True
	# ita_utils.copy_features(head_tok)

	for child_tok in children_toks:
		logger.info("Examining child: %s", child_tok.values())

		if child_tok["deprel"] in ["amod"]:
			# print("HERE")
			if child_tok.get("feats"):
				# print(head_tok["ms feats"])
				# print(child_tok["feats"])
				# input()

				if "Gender" in child_tok["feats"]:
					head_tok["ms feats"]["Gender"].add(child_tok["feats"]["Gender"])
					del child_tok["ms feats"]["Gender"]

				if "Number" in child_tok["feats"]:
					head_tok["ms feats"]["Number"].add(child_tok["feats"]["Number"])
					del child_tok["ms feats"]["Number"]

		else:
			logging.warning("Node %s/%s with deprel '%s' needs new rules",
							child_tok, child_tok["upos"], child_tok["deprel"])