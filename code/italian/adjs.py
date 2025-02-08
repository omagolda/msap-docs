import logging
import conllu.serializer as conllu

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_adj(head_tok, children_toks):

	logging.debug("Setting %s/%s to content and copying its features", head_tok, head_tok["upos"])
	head_tok["content"] = True
	ita_utils.copy_features(head_tok)

	# if "Degree" in head_tok["ms feats"] and "Abs" in head_tok["ms feats"]["Degree"]:
	# 	head_tok["ms feats"]["Degree"].remove("Abs")
	# 	head_tok["ms feats"]["Degree"].add("Sup")

	for child_tok in children_toks:
		logger.info("Examining child: %s", child_tok.values())

		# * evaluate copulas
		if child_tok["deprel"] in ["aux", "cop"]:

			# TODO: set defaults

			if child_tok.get("feats") and "Person" in child_tok["feats"]:
				head_tok["ms feats"]["Person"].add(child_tok["feats"]["Person"])

			if child_tok.get("feats") and "Gender" in child_tok["feats"]:
				head_tok["ms feats"]["Gender"].add(child_tok["feats"]["Gender"])

			if child_tok.get("feats") and "Number" in child_tok["feats"]:
				head_tok["ms feats"]["Number"].add(child_tok["feats"]["Number"])

			if child_tok.get("feats") and "Mood" in child_tok["feats"]:
				logging.debug("Adding Mood: %s", child_tok["feats"]["Mood"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

			if child_tok.get("feats") and "Tense" in child_tok["feats"]:
				logging.debug("Adding Tense: %s", child_tok["feats"]["Tense"])
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

		elif child_tok["deprel"] in ["det", "det:predet", "det:poss"]:


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

		elif child_tok["deprel"] in ["case", "mark"]:
			logging.debug("Add Case feature with value %s", lbd.switch_case(child_tok, head_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_case(child_tok, head_tok))

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

	if "Definite" in head_tok["ms feats"] and "Degree" in head_tok["ms feats"]:
		if "Def" in head_tok["ms feats"]["Definite"] and "Cmp" in head_tok["ms feats"]["Degree"]:
			logging.debug("Changing Cmp to Sup Degree for node %s/%s", head_tok, head_tok["upos"])
			head_tok["ms feats"]["Degree"].remove("Cmp")
			head_tok["ms feats"]["Degree"].add("Sup")

	# TODO: Handle aspect
