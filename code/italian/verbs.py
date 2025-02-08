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

	# * default voice to Act
	logging.debug("Setting Voice as Act")
	head_tok["ms feats"]["Voice"].add("Act")

	# * default aspect to Imp if Mood = Ind
	logging.debug("Setting Aspct as Imp")
	if "Mood" in head_tok["feats"] and head_tok["feats"]["Mood"] == "Ind":
		if head_tok["feats"]["Tense"] in ["Pres", "Imp"]:
			head_tok["ms feats"]["Aspect"].add("Imp")
		elif head_tok["feats"]["Tense"] in ["Past", "Fut"]:
			head_tok["ms feats"]["Aspect"].add("Perf")

	# * default mood
	if "Mood" in head_tok["feats"]:
		head_tok["ms feats"]["Mood"].add(head_tok["feats"]["Mood"])

	# * default tense
	if "Tense" in head_tok["feats"]:
		head_tok["ms feats"]["VerbForm"].add(head_tok["feats"]["VerbForm"])

	# * default verbform
	head_tok["ms feats"]["VerbForm"].add(head_tok["feats"]["VerbForm"])

	# # * default person
	# if "Person" in head_tok["feats"]:
	# 	head_tok["ms feats"]["Person"].add(head_tok["feats"]["Person"])

	for child_tok in children_toks:
		logger.info("Examining child: %s", child_tok.values())

		# * Auxiliaries and copulas
		if child_tok["deprel"] in ["aux","cop"]:

			# if "Person" in child_tok["feats"]:
			# 	head_tok["ms feats"]["Person"].add(child_tok["feats"]["Person"])

			del head_tok["ms feats"]["VerbForm"]
			head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])

			# Aspect
			if head_tok["feats"]["VerbForm"] == "Ger":

				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
				if child_tok["lemma"] == "stare":
					logger.debug("Adding Aspect feature with value Prog")
					# del head_tok["ms feats"]["Aspect"]
					head_tok["ms feats"]["Aspect"].add("Prog")

				elif child_tok["lemma"] in ["andare", "venire"]:
					logger.debug("Adding Aspect feature with value Imp")
					# del head_tok["ms feats"]["Aspect"]
					head_tok["ms feats"]["Aspect"].add("Imp")
				else:
					logger.warning("Head '%s' is 'Ger' but Aux/cop '%s' has incompatible lemma",
									head_tok, child_tok)

			elif head_tok["feats"]["VerbForm"] == "Part":

				# logger.debug("Adding VerbForm feature with value %s", child_tok["feats"]["VerbForm"])
				# head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])
				# if head_tok["feats"]["Tense"] in ["Past"]:
				# 	logger.debug("Adding Aspect feature with value Perf")
				# 	del head_tok["ms feats"]["Aspect"]
				# 	head_tok["ms feats"]["Aspect"].add("Perf")

				# Indicativo perfetto composto > sono andata
				# Congiuntivo perfetto > sia andata
				# Condizionale composto > sarei andata

				if child_tok["feats"]["Tense"] == "Pres":
					if child_tok["feats"]["Mood"] == "Ind":
						head_tok["ms feats"]["Aspect"].add("Perf")
					head_tok["ms feats"]["Tense"].add("Past")
					head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
					# del head_tok["ms feats"]["VerbForm"]
					# head_tok["ms feats"]["VerbForm"].add("Fin")

				# Indicativo piùcheperfetto > ero andata
				# Congiuntivo piucheperfetto > fossi andata

				if child_tok["feats"]["Tense"] == "Imp":
					if child_tok["feats"]["Mood"] == "Ind":
						head_tok["ms feats"]["Aspect"].add("Perf")
					head_tok["ms feats"]["Tense"].add("Past")
					head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
					# del head_tok["ms feats"]["VerbForm"]
					# head_tok["ms feats"]["VerbForm"].add("Fin")

				# Indicativo trapassato > fui andata
				# Indicativo futuro composto > sarò andata

				if child_tok["feats"]["Tense"] in ["Past", "Fut"]:
					head_tok["ms feats"]["Aspect"].add("Perf")
					head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
					head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
					# del head_tok["ms feats"]["VerbForm"]
					# head_tok["ms feats"]["VerbForm"].add("Fin")

			else:
				logger.warning("Head '%s' is neither 'Ger' not 'Part'",
									head_tok)

			# Modality
			modality = lbd.switch_verb_modality(child_tok)
			if modality:
				logger.debug("Adding Modality feature with value %s", modality)
				head_tok["ms feats"]["Modality"].add(modality)
				if "Mood" in child_tok["feats"]:
					head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
				if "Tense" in child_tok["feats"]:
					head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])


		elif child_tok["deprel"] == "aux:pass":
			logger.debug("Adding Voice feature with value 'Pass'")
			del head_tok["ms feats"]["Voice"]
			head_tok["ms feats"]["Voice"].add("Pass")

			del head_tok["ms feats"]["VerbForm"]
			head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])

			# if "Person" in child_tok["feats"]:
			# 	head_tok["ms feats"]["Person"].add(child_tok["feats"]["Person"])

			if child_tok["feats"]["VerbForm"] == "Fin":

				# Indicativo presente > è mandata
				# Indicativo imperfetto > era mandata
				# Congiuntivo presente > sia mandata
				# Congiuntivo imperfetto > fosse mandata
				# Condizionale presente > sarebbe mandata
				if child_tok["feats"]["Tense"] in ["Pres", "Imp"]:
					if child_tok["feats"]["Mood"] == "Ind":
						head_tok["ms feats"]["Aspect"].add("Imp")
					head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
					head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

				# Indicativo passato
				# Indicativo futuro
				if child_tok["feats"]["Tense"] in ["Pres", "Imp"]:
					if child_tok["feats"]["Mood"] == "Ind":
						head_tok["ms feats"]["Aspect"].add("Perf")
					head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
					head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

			else:
				head_tok["ms feats"]["Tense"].add("Pres")



		elif child_tok["deprel"] in ["case", "mark"]:
			logger.debug("Adding Case feature with value %s", lbd.switch_case(child_tok, head_tok))

			if child_tok["lemma"] == "che":
				if head_tok["deprel"] == "csubj":
					head_tok["ms feats"]["Case"].add("Nom")
				elif head_tok["deprel"] == "ccomp":
					head_tok["ms feats"]["Case"].add("Acc")
				else:
					head_tok["ms feats"]["Case"].add(lbd.switch_case(child_tok, head_tok))
			else:
				head_tok["ms feats"]["Case"].add(lbd.switch_case(child_tok, head_tok))


		# TODO: Indexing (person, number)
		# * evaluate determiners (cases like "Il perdurare...")
		# ? From the 'det' we get Gender and Number, but then we remove it in italian.py
		elif child_tok["deprel"] in ["det", "det:poss", "det:predet"]:

			# if child_tok.get("feats") and "Gender" in child_tok["feats"]:
			# 	head_tok["ms feats"]["Gender"].add(child_tok["feats"]["Gender"])
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
			else:
				logging.debug("No Definite features in %s - %s", child_tok, child_tok["feats"])

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

	# if head_tok.get("feats"):
	# 	for feat in head_tok.get("feats"):
	# 		if not feat in head_tok["ms feats"]:
	# 			head_tok["ms feats"][feat].add(head_tok["feats"][feat])

	# #Default features: indicative mood, finite verb forms and active voice
	# # TODO: add default tense Pres?
	# if "Mood" not in head_tok["ms feats"]:
	# 	head_tok["ms feats"]["Mood"].add("Ind")
	# if "VerbForm" not in head_tok["ms feats"]:
	# 	head_tok["ms feats"]["VerbForm"].add("Fin")
	# if "Voice" not in head_tok["ms feats"]:
	# 	head_tok["ms feats"]["Voice"].add("Act")