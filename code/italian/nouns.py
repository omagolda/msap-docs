import logging

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_noun(head_tok, children_toks):

	logging.info("Examining head: %s", head_tok)

	logging.debug("Setting node %s/%s to content and copying its features", head_tok, head_tok["upos"])
	head_tok["content"] = True
	ita_utils.copy_features(head_tok)

	for child_tok in children_toks:
		logger.info("Examining child: %s/%s", child_tok, child_tok["upos"])

		# * evaluate copulas
		if child_tok["deprel"] in ["cop", "aux"]:
			if "Mood" in child_tok["feats"]:
				logging.debug("Adding TAM features with values Mood: %s - Tense: %s",
							child_tok["feats"]["Mood"], child_tok["feats"]["Tense"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
			else:
				logging.debug("No Mood feature in %s - %s", child_tok, child_tok["feats"])

			if "Tense" in child_tok["feats"]:
				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
			else:
				logging.debug("No Tense feature in %s - %s", child_tok, child_tok["feats"])

			if "VerbForm" in child_tok["feats"]:
				logging.debug("Adding VerbForm feature with value: %s",
							child_tok["feats"]["VerbForm"])
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])
			else:
				logging.debug("No VerbForm feature in %s - %s", child_tok, child_tok["feats"])

		# * evaluate determiners
		elif child_tok["deprel"] in ["det", "det:poss", "det:predet"]:
			processed = False

			# * add definiteness
			if "Definite" in child_tok["feats"]:
				processed = True
				logging.debug("Adding Definite feature with value %s", child_tok["feats"]["Definite"])
				head_tok["ms feats"]["Definite"].add(child_tok["feats"]["Definite"])
			elif lbd.switch_det_definitess(child_tok):
				processed = True
				definitess = lbd.switch_det_definitess(child_tok)
				logging.debug("Adding Definite feature with value %s", definitess)
				head_tok["ms feats"]["Definite"].add(definitess)
			else:
				logging.debug("No Definite features in %s - %s", child_tok, child_tok["feats"])

			# * add polarity
			# ? should polarity be set to "Pos" by default?
			polarity = lbd.switch_det_polarity(child_tok)
			if polarity:
				processed = True
				logging.debug("Adding Polarity feature with value %s", polarity)
				head_tok["ms feats"]["Polarity"].add(polarity)

			if "PronType" in child_tok["feats"]:
				if child_tok["feats"]["PronType"] == "Dem":
					dem = lbd.switch_det_dem(child_tok)
					if dem:
						processed = True
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
		elif child_tok["deprel"] in ["mark", "case"]:
			logging.debug("Adding Case feature with value %s", lbd.switch_nominal_case(child_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_nominal_case(child_tok))

		elif child_tok["deprel"] in ["advmod"]:
			if child_tok["lemma"] in ["non"]:
				head_tok["ms feats"]["Polarity"].add("Neg")
			else:
				logging.warning("Adverb needs coding %s", child_tok)

		else:
			logging.warning("Node %s/%s with deprel '%s' needs new rules",
							child_tok, child_tok["upos"], child_tok["deprel"])
			child_tok["ms feats"]["tmp-child"].add("NOUN")
