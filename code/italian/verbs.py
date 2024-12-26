import logging

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_verb(head_tok, children_toks):

	logger.info("Examining head: %s", head_tok)
	head_tok["content"] = True

	# TODO: copy relevant verbal features
	# ita_utils.copy_features(head_tok)

	# * default polarity to Pos, than change to Neg if "not" is present
	head_tok["ms feats"]["Polarity"].add("Pos")
	# TODO: default Mood to "Ind"
	# TODO: default VerbForm to "Fin"
	# TODO: default Voice to "Act"

	for child_tok in children_toks:
		logger.info("Examining child: %s/%s", child_tok, child_tok["upos"])

		# TODO: agreement on pronouns

		# * Auxiliaries and copulas
		if child_tok["deprel"] in ["aux","cop"]:

			# TAM
			# Mood
			if "Mood" in child_tok["feats"]:
				logger.debug("Adding Mood feature with value %s", child_tok["feats"]["Mood"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
			elif child_tok["feats"]["VerbForm"] == "Fin":
				logger.debug("No Mood: Aux/cop %s with features %s", child_tok, child_tok["feats"])

			# Tense
			if "Tense" in child_tok["feats"]:
				logger.debug("Adding Tense feature with value %s", child_tok["feats"]["Tense"])
				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
			else:
				logger.debug("No Tense: Aux/cop %s with features %s", child_tok, child_tok["feats"])


			# Aspect
			if head_tok["feats"]["VerbForm"] == "Ger":
				if child_tok["lemma"] == "stare":
					logger.debug("Adding Aspect feature with value Prog") #child_tok["Prog"])
					# head_tok["ms feats"]["Aspect"].add(child_tok["Prog"])
					head_tok["ms feats"]["Aspect"].add("Prog")
				else:
					logger.warning("Head '%s' is 'Ger' but Aux/cop '%s' has incompatible lemma",
									head_tok, child_tok)

			# Modality
			modality = lbd.switch_verb_modality(child_tok)
			if modality:
				logger.debug("Adding Modality feature with value %s", modality)
				head_tok["ms feats"]["Modality"].add(modality)

			# Voice:
			if child_tok["lemma"] == "venire": #how do we treat essere, which is ambigous with active forms?
				logger.debug("Adding Voice feature with value 'Pass'")
				head_tok["ms feats"]["Voice"].add("Pass")
			# else:
				# !! why the warning?
				# logger.warning("Aux/cop %s with features %s", child_tok, child_tok["feats"])

			# if child_tok["lemma"] == "fare": #it is probably not defined as aux
			# 	logger.debug("Adding Voice feature with value %s", child_tok["Cau"])
			# 	head_tok["ms feats"]["Voice"].add(child_tok["Cau"])
			# else:
			# 	logger.warning("Aux/cop %s with features %s", child_tok, child_tok["feats"])

		elif child_tok["deprel"] == "aux:pass":
			logger.debug("Adding Voice feature with value 'Pass'")
			head_tok["ms feats"]["Voice"].add("Pass")

		# * evaluate determiners (cases like "Il perdurare...")
		elif child_tok["deprel"] in ["det"]:

			# * add definiteness
			if "Definite" in child_tok["feats"]:
				logging.debug("Adding Definite feature with value %s", child_tok["feats"]["Definite"])
				head_tok["ms feats"]["Definite"].add(child_tok["feats"]["Definite"])
			elif lbd.switch_det_definitess(child_tok):
				definitess = lbd.switch_det_definitess(child_tok)
				logging.debug("Adding Definite feature with value %s", definitess)
				head_tok["ms feats"]["Definite"].add(definitess)
			else:
				logging.debug("No Definite features in %s - %s", child_tok, child_tok["feats"])

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
				else:
					logging.debug("No Dem features in %s - %s", child_tok, child_tok["feats"])

		elif child_tok["deprel"] in ["advmod"]:

			if child_tok["lemma"] in ["non"]:

				head_tok["ms feats"]["Polarity"].remove("Pos")
				head_tok["ms feats"]["Polarity"].add("Neg")
				# TODO: check what the negation refers to, either modality or polarity
				# TODO: difference "non possiamo andare" vs. "possiamo non andare"

		elif child_tok["deprel"] in ["case", "mark"]:
			head_tok["ms feats"]["Case"].add(lbd.switch_verb_modality(child_tok))
			# TODO: handle "Case"

		else:
			logging.warning("Node %s/%s with deprel '%s' needs new rules",
							child_tok, child_tok["upos"], child_tok["deprel"])
			child_tok["ms feats"]["tmp-child"].add("VERB")

	# TODO: if no subj found -> create abstract node