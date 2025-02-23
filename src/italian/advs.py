import logging

import src.italian.ita_utils as ita_utils
import src.italian.lemma_based_decisions as lbd

logger = logging.getLogger(__name__)

def process_adv(head_tok, children_toks):

	# * setting all adverbs to content words, except for "non", "più", "meno"
	if not head_tok["lemma"] in ["non", "più", "meno"]:
		logging.debug("Setting node %s/%s to content and copying its features",
					head_tok, head_tok["upos"])
		head_tok["content"] = True
		ita_utils.copy_features(head_tok)


	for child_tok in children_toks:
		logger.debug("Examining child: %s", child_tok.values())

		if child_tok["deprel"] in ["aux", "cop"]:
			if child_tok.get("feats") and "Mood" in child_tok["feats"]:
				logging.debug("Adding TAM features with values Mood: %s - Tense: %s",
							child_tok["feats"]["Mood"], child_tok["feats"]["Tense"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

			if child_tok.get("feats") and "Tense" in child_tok["feats"]:
				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])

			if child_tok.get("feats") and "VerbForm" in child_tok["feats"]:
				logging.debug("Adding VerbForm feature with value: %s",
							child_tok["feats"]["VerbForm"])
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])

			# Modality
			modality = lbd.switch_verb_modality(child_tok)
			if modality:
				logger.debug("Adding Modality feature with value %s", modality)
				head_tok["ms feats"]["Modality"].add(modality)

		elif child_tok["deprel"] in ["det"]:
			if child_tok.get("feats") and "Gender" in child_tok["feats"]:
				head_tok["ms feats"]["Gender"].add(child_tok["feats"]["Gender"])
			if child_tok.get("feats") and "Number" in child_tok["feats"]:
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

			# * add polarity
			# ? should polarity be set to "Pos" by default?
			# polarity = lbd.switch_det_polarity(child_tok)
			# if polarity:
			# 	logging.debug("Adding Polarity feature with value %s", polarity)
			# 	head_tok["ms feats"]["Polarity"].add(polarity)

			if child_tok.get("feats") and "PronType" in child_tok["feats"] and child_tok["feats"]["PronType"] == "Dem":
				dem = lbd.switch_det_dem(child_tok)
				if dem:
					logging.debug("Adding Dem feature with value %s", dem)
					head_tok["ms feats"]["Dem"].add(dem)

		elif child_tok["deprel"] == "advmod":
			# * add Degree feature
			if child_tok["lemma"] in ["più", "meno"]:
				logging.debug("Adding Degree feature with value Cmp")
				head_tok["ms feats"]["Degree"].add("Cmp")

				if "Definite" in child_tok["ms feats"]:
					for x in child_tok["ms feats"]["Definite"]:
						head_tok["ms feats"]["Definite"].add(x)
					del child_tok["ms feats"]["Definite"]

		elif child_tok["deprel"] in ["case", "mark"] and head_tok["lemma"] not in ["più", "meno"]:
			logging.debug("Add Case feature with value %s", lbd.switch_case(child_tok, head_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_case(child_tok, head_tok))

		elif child_tok["deprel"] in ["case", "mark"]:
			logging.debug("Ignoring node %s for head %s", child_tok, head_tok)

		else:
			logging.warning("Node %s/%s with deprel '%s' needs new rules",
							child_tok, child_tok["upos"], child_tok["deprel"])

	if "Def" in head_tok["ms feats"]["Definite"] and "Cmp" in head_tok["ms feats"]["Degree"]:
		logging.debug("Changing Cmp to Sup Degree for node %s/%s", head_tok, head_tok["upos"])
		head_tok["ms feats"]["Degree"].remove("Cmp")
		head_tok["ms feats"]["Degree"].add("Sup")
	# TODO: Handle aspect
