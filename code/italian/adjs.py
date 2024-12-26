import logging

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_adj(head_tok, children_toks):

	logging.info("Examining head: %s", head_tok)

	logging.debug("Setting %s to content node", head_tok)
	head_tok["content"] = True
	ita_utils.copy_features(head_tok)

	if "Degree" in head_tok["ms feats"] and "Abs" in head_tok["ms feats"]["Degree"]:
		head_tok["ms feats"]["Degree"].remove("Abs")
		head_tok["ms feats"]["Degree"].add("Sup")

	for child_tok in children_toks:
		logger.info("Examining child: %s/%s", child_tok, child_tok["upos"])

		# * evaluate copulas
		if child_tok["deprel"] in ["aux", "cop"]:

			if "Mood" in child_tok["feats"]:
				logging.debug("Adding TAM features with values Mood: %s - Tense: %s",
							child_tok["feats"]["Mood"], child_tok["feats"]["Tense"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

			if "Tense" in child_tok["feats"]:
				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])

			if "VerbForm" in child_tok["feats"]:
				logging.debug("Adding VerbForm feature with value: %s",
							child_tok["feats"]["VerbForm"])
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])

			# Modality
			modality = lbd.switch_verb_modality(child_tok)
			if modality:
				logger.debug("Adding Modality feature with value %s", modality)
				head_tok["ms feats"]["Modality"].add(modality)

		elif child_tok["deprel"] in ["det"]:

			# * add definiteness
			if "Definite" in child_tok["feats"]:
				logging.debug("Adding Definite feature with value %s", child_tok["feats"]["Definite"])
				head_tok["ms feats"]["Definite"].add(child_tok["feats"]["Definite"])
			elif lbd.switch_det_definitess(child_tok):
				definitess = lbd.switch_det_definitess(child_tok)
				logging.debug("Adding Definite feature with value %s", definitess)
				head_tok["ms feats"]["Definite"].add(definitess)

			# * add polarity
			# ? should polarity be set to "Pos" by default?
			polarity = lbd.switch_det_polarity(child_tok)
			if polarity:
				logging.debug("Adding Polarity feature with value %s", polarity)
				head_tok["ms feats"]["Polarity"].add(polarity)

			if "PronType" in child_tok["feats"] and child_tok["feats"]["PronType"] == "Dem":
				dem = lbd.switch_det_dem(child_tok)
				if dem:
					logging.debug("Adding Dem feature with value %s", dem)
					head_tok["ms feats"]["Dem"].add(dem)

		elif child_tok["deprel"] in ["case", "mark"]:
			logging.debug("Add Case feature with value %s", lbd.switch_nominal_case(child_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_nominal_case(child_tok))

		elif child_tok["deprel"] in ["advmod"]:

			# * add Degree feature
			if child_tok["lemma"] in ["più", "meno"]:
				logging.debug("Adding Degree feature with value Cmp")
				head_tok["ms feats"]["Degree"].add("Cmp")

			elif child_tok["lemma"] in ["non"]:
				if "Degree" in head_tok["ms feats"] and head_tok["ms feats"]["Degree"] == "Cmp":
					logging.error("What should we do here??")
					# ? what should we do here
				else:
					logging.debug("Adding Polarity feature with value Neg")
					head_tok["ms feats"]["Polarity"].add("Neg")

			else:
				logging.warning("Node %s/%s needs new rule", child_tok, child_tok["upos"])

		else:
			logging.warning("Node %s/%s with deprel '%s' needs new rules",
							child_tok, child_tok["upos"], child_tok["deprel"])
			child_tok["ms feats"]["tmp-child"].add("ADJ")

	if "Definite" in head_tok["ms feats"] and "Degree" in head_tok["ms feats"]:
		if "Def" in head_tok["ms feats"]["Definite"] and "Cmp" in head_tok["ms feats"]["Degree"]:
			logging.debug("Changing Cmp to Sup Degree for node %s/%s", head_tok, head_tok["upos"])
			head_tok["ms feats"]["Degree"].remove("Cmp")
			head_tok["ms feats"]["Degree"].add("Sup")
