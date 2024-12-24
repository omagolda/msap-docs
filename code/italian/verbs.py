import logging

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_verb(head_tok, children_toks):

	logger.debug("Examining head: %s", head_tok)
	head_tok["content"] = True
	head_tok["ms feats"]["tmp-head"].add("VERB")

	# TODO: copy relevant verbal features
	# ita_utils.copy_features(head_tok)

	# * default polarity to Pos, than change to Neg if "not" is present
	head_tok["ms feats"]["Polarity"].add("Pos")

	# TODO: default Mood to "Ind"

	# TODO: default VerbForm to "Fin"

	# TODO: default Voice to "Act"


	for child_tok in children_toks:
		logger.debug("Examining child: %s", child_tok)

		# TODO: agreement on pronouns
		# TODO: Handle adding "Case" on fell for es. "So I cried until I fell asleep"

		# Auxiliaries and copulas
		if child_tok["deprel"] in ["aux","cop"]:

			#TAM
			# Mood
			if "Mood" in child_tok["feats"]:
				logger.debug("Adding Mood feature with value %s", child_tok["feats"]["Mood"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
			else:
				logger.warning("No MOOD: Aux/cop %s with features %s", child_tok, child_tok["feats"])

			# Tense
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

			# Modality
			modality = lbd.switch_verb_modality(child_tok)
			if modality:
				logger.debug("Adding Modality feature with value %s", modality)
				head_tok["ms feats"]["Modality"].add(modality)

			# Voice:
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

		if child_tok["lemma"] == "non":
			# # Polarity
			# if ""
			# TODO: check what the negation refers to, either modality or polarity
			# TODO: difference "non possiamo andare" vs. "possiamo non andare"
			logger.warning("Found negation")

		if child_tok["deprel"] == "mark":
			# TODO: handle "Case"

			logger.debug("Adding Case feature with value %s", lbd.switch_sconj_case(child_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_sconj_case(child_tok))
			

		# TODO: Indexing (person, number)

	# TODO: if no subj found -> create abstract node