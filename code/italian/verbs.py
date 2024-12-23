import logging

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_verb(head_tok, children_toks):

	logger.debug("Examining head: %s", head_tok)
	head_tok["content"] = True
	head_tok["ms feats"]["tmp-head"].add("VERB")

	# keep existing features for all nominals
	ita_utils.copy_features(head_tok)

	for child_tok in children_toks:
		logger.debug("Examining child: %s", child_tok)

		#Auxiliaries and copulas
		if child_tok["deprel"] in ["aux","cop"]:

			#TAM
			#Mood
			if "Mood" in child_tok["feats"]:
				logger.debug("Adding Mood feature with value %s", child_tok["feats"]["Mood"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
			else:
				logger.warning("No MOOD: Aux/cop %s with features %s", child_tok, child_tok["feats"])

			#Tense
			if "Tense" in child_tok["feats"]:
				logger.debug("Adding Tense feature with value %s", child_tok["feats"]["Tense"])
				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
			else:
				logger.warning("No TENSE: Aux/cop %s with features %s", child_tok, child_tok["feats"])


			# Aspect
			if head_tok["feats"]["VerbForm"] == "Ger":
				if child_tok["lemma"] == "stare":
					logger.debug("Adding Aspect feature with value Prog") #child_tok["Prog"])
					# head_tok["ms feats"]["Aspect"].add(child_tok["Prog"])
					head_tok["ms feats"]["Aspect"].add("Prog")
				else:
					logger.warning("Head '%s' is 'Ger' but Aux/cop '%s' has incompatible lemma",
									head_tok, child_tok)

			# !! issues here
			#Modality
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

			#Voice:
			if child_tok["lemma"] == "venire": #how do we treat essere, which is ambigous with active forms?
				logger.debug("Adding Voice feature with value %s", child_tok["Pass"])
				head_tok["ms feats"]["Voice"].add(child_tok["Pass"])
			# else:
				# !! why the warning?
				# logger.warning("Aux/cop %s with features %s", child_tok, child_tok["feats"])

			# if child_tok["lemma"] == "fare": #it is probably not defined as aux
			# 	logger.debug("Adding Voice feature with value %s", child_tok["Cau"])
			# 	head_tok["ms feats"]["Voice"].add(child_tok["Cau"])
			# else:
			# 	logger.warning("Aux/cop %s with features %s", child_tok, child_tok["feats"])

			# TODO: Indexing (person, number)

