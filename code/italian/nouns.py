import logging

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_noun(head_tok, children_toks):

	logger.debug("Examining head: %s", head_tok)
	head_tok["content"] = True

	# keep existing features for all nominals
	ita_utils.copy_features(head_tok)

	for child_tok in children_toks:
		logger.debug("Examining child: %s", child_tok)

		if child_tok["deprel"] == "cop":
			logger.debug("Adding TAM features with values Mood: %s - Tense: %s",
						child_tok["feats"]["Mood"], child_tok["feats"]["Tense"])
			head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
			head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])

			# TODO: add Person and Number to subject


		# determiners
		elif child_tok["deprel"] == "det":
			# add definiteness
			if "Definite" in child_tok["feats"]:
				logger.debug("Adding Definite feature with value %s", child_tok["feats"]["Definite"])
				head_tok["ms feats"]["Definite"].add(child_tok["feats"]["Definite"])
			else:
				logger.warning("DET %s with features %s", child_tok, child_tok["feats"])

			# if Degree was set to Cmp earlier, now change it to Sup
			if "Degree" in head_tok["ms feats"] and "Cmp" in head_tok["ms feats"]["Degree"]:
				logger.debug("Changing Degree feature to Sup")
				head_tok["ms feats"]["Degree"].remove("Cmp").add("Sup")


		# case relations
		elif child_tok["deprel"] == "case":
			logger.debug("Adding Case feature with value %s", lbd.switch_nominal_case(child_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_nominal_case(child_tok))

		elif child_tok["deprel"] == "cc":

			logger.debug("Adding Case feature with value %s", lbd.switch_conj_case(child_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_conj_case(child_tok))

		# if child_tok["upos"] in ["NOUN", "PROPN"]:
		# 	logger.debug("Switching node to content and keeping its features")
		# 	ita_utils.copy_features(child_tok)
		# 	child_tok["content"] = True

		else:
			logger.warning("Node %s/%s needs new rules", child_tok, child_tok["upos"])
			child_tok["ms feats"]["tmp-child"].add("NOUN")
