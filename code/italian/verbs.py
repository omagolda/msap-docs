import logging

import code.italian.lemma_based_decisions as lbd
# ? do we use utils somewhere?
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_verb(head_tok, children_toks):

	logging.debug("Setting %s/%s to content node", head_tok, head_tok["upos"])
	head_tok["content"] = True

	# * default polarity to Pos, than change to Neg if "not" is present
	logging.debug("Setting Polarity as Pos")
	head_tok["ms feats"]["Polarity"].add("Pos")

	for child_tok in children_toks:
		logger.info("Examining child: %s", child_tok.values())


		# * Auxiliaries and copulas
		if child_tok["deprel"] in ["aux","cop"]:

			# ? Not clear why we add features and then in italian.py we remove those features. We add Person from aux/cop to the head and then in italian.py (line 164) we remove Person.

			if "Person" in child_tok["feats"]:
				head_tok["ms feats"]["Person"].add(child_tok["feats"]["Person"])

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
				# TODO: c'è un caso in cui il tense del child è Pres ma il tense della head deve essere Past (è andato/ha fatto)
			else:
				logger.debug("No Tense: Aux/cop %s with features %s", child_tok, child_tok["feats"])


			# Aspect
			if head_tok["feats"]["VerbForm"] == "Ger":
				if child_tok["lemma"] == "stare": # TODO: or "andare"
					logger.debug("Adding Aspect feature with value Prog") #child_tok["Prog"])
					# head_tok["ms feats"]["Aspect"].add(child_tok["Prog"])
					head_tok["ms feats"]["Aspect"].add("Prog")
				else:
					logger.warning("Head '%s' is 'Ger' but Aux/cop '%s' has incompatible lemma",
									head_tok, child_tok)

			# Aspect and Tense with participles = Perfective aspect
			elif head_tok["feats"]["VerbForm"] == "Part":
				# TODO: remove "Part" from VerbForm
				logger.debug("Adding VerbForm feature with value %s", child_tok["feats"]["VerbForm"])
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])
				if head_tok["feats"]["Tense"] in ["Past"]:
					logger.debug("Adding Aspect feature with value Perf")
					head_tok["ms feats"]["Aspect"].add("Perf")

			# TODO: handle Prosp: Like inchoative/cessative aspect, these are lexically marked in Italian like comincio/finisco

			# Modality
			modality = lbd.switch_verb_modality(child_tok)
			if modality:
				logger.debug("Adding Modality feature with value %s", modality)
				head_tok["ms feats"]["Modality"].add(modality)

			# Voice:
			if child_tok["lemma"] == "venire":
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

		elif child_tok["deprel"] in ["case", "mark"]:
			logger.debug("Adding Case feature with value %s", lbd.switch_case(child_tok, head_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_case(child_tok, head_tok))



		# TODO: Indexing (person, number)
		# * evaluate determiners (cases like "Il perdurare...")
		# ? From the 'det' we get Gender and Number, but then we remove it in italian.py
		elif child_tok["deprel"] in ["det", "det:poss", "det:predet"]:
			if child_tok.get("feats") and "Gender" in child_tok["feats"]:
				head_tok["ms feats"]["Gender"].add(child_tok["feats"]["Gender"])
			if child_tok.get("feats") and "Number" in child_tok["feats"]:
				head_tok["ms feats"]["Number"].add(child_tok["feats"]["Number"])

			# * add definiteness
			if child_tok.get("feats") and "Definite" in child_tok["feats"]:
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

			if child_tok.get("feats") and "PronType" in child_tok["feats"] and child_tok["feats"]["PronType"] == "Dem":
				dem = lbd.switch_det_dem(child_tok)
				if dem:
					logging.debug("Adding Dem feature with value %s", dem)
					head_tok["ms feats"]["Dem"].add(dem)
				else:
					logging.debug("No Dem features in %s - %s", child_tok, child_tok["feats"])

		elif child_tok["deprel"] in ["advmod"]:

			if child_tok["lemma"] in ["non"]:
				if "Pos" in head_tok["ms feats"]["Polarity"]:
					head_tok["ms feats"]["Polarity"].remove("Pos")
					head_tok["ms feats"]["Polarity"].add("Neg")
					# TODO: check what the negation refers to, either modality or polarity
					# TODO: difference "non possiamo andare" vs. "possiamo non andare"
				else:
					logging.warning("'Pos' not found in Polarity for token: %s", head_tok)

		else:
			logging.warning("Node %s/%s with deprel '%s' needs new rules",
							child_tok, child_tok["upos"], child_tok["deprel"])

	if head_tok.get("feats"):
		for feat in head_tok.get("feats"):
			if not feat in head_tok["ms feats"]:
				head_tok["ms feats"][feat].add(head_tok["feats"][feat])

	#Default features: indicative mood, finite verb forms and active voice
	# TODO: add default tense Pres?
	if "Mood" not in head_tok["ms feats"]:
		head_tok["ms feats"]["Mood"].add("Ind")
	if "VerbForm" not in head_tok["ms feats"]:
		head_tok["ms feats"]["VerbForm"].add("Fin")
	if "Voice" not in head_tok["ms feats"]:
		head_tok["ms feats"]["Voice"].add("Act")