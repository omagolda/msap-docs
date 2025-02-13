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

	pos_non = []
	pos_mod = []

	pos_aux = []

	children_toks_dict = {}

	for child_tok in children_toks:
		children_toks_dict[child_tok["id"]] = child_tok
		logger.info("Examining child: %s", child_tok.values())

		# * Auxiliaries and copulas
		if child_tok["deprel"] in ["aux","cop"]:

			pos_aux.append(child_tok["id"])

			if child_tok["feats"]["VerbForm"] == "Fin":
				del head_tok["ms feats"]["VerbForm"]
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

			# Modality
			modality = lbd.switch_verb_modality(child_tok)
			if modality:
				pos_mod.append(child_tok["id"])
				logger.debug("Adding Modality feature with value %s", modality)
				head_tok["ms feats"]["Modality"].add(modality)


		elif child_tok["deprel"] == "aux:pass":

			pos_aux.append(child_tok["id"])

			logger.debug("Adding Voice feature with value 'Pass'")
			del head_tok["ms feats"]["Voice"]
			head_tok["ms feats"]["Voice"].add("Pass")

			if child_tok["feats"]["VerbForm"] == "Fin":
				del head_tok["ms feats"]["VerbForm"]
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

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

			if child_tok.get("feats") and "PronType" in child_tok["feats"] and child_tok["feats"]["PronType"] == "Dem":
				dem = lbd.switch_det_dem(child_tok)
				if dem:
					logging.debug("Adding Dem feature with value %s", dem)
					head_tok["ms feats"]["Dem"].add(dem)
				else:
					logging.debug("No Dem features in %s - %s", child_tok, child_tok["feats"])

		elif child_tok["deprel"] in ["advmod"]:

			if child_tok["lemma"] in ["non"]:
				pos_non.append(child_tok["id"])

		else:
			logging.warning("Node %s/%s with deprel '%s' needs new rules",
							child_tok, child_tok["upos"], child_tok["deprel"])


	if len(pos_non)>0 and len(pos_mod)>0:
		assert(len(pos_mod)==1)

		pos_mod_id = pos_mod[0]
		for i in pos_non:
			if i < pos_mod_id:
				modality_value = head_tok["ms feats"]["Modality"].pop()
				del head_tok["ms feats"]["Modality"]
				head_tok["ms feats"]["Modality"].add(f"not({modality_value})")
			else:
				del head_tok["ms feats"]["Polarity"]
				head_tok["ms feats"]["Polarity"].add("Neg")

	elif len(pos_non)>0:
		del head_tok["ms feats"]["Polarity"]
		head_tok["ms feats"]["Polarity"].add("Neg")


	verbforms = [children_toks_dict[x]["feats"]["VerbForm"] for x in pos_aux]
	if "Inf" in verbforms:
		del head_tok["ms feats"]["VerbForm"]
		head_tok["ms feats"]["VerbForm"].add("Inf")
	elif "Ger" in verbforms:
		del head_tok["ms feats"]["VerbForm"]
		head_tok["ms feats"]["VerbForm"].add("Ger")


	if len(pos_mod)>0:
		pos_mod = pos_mod[0]
		pos_mod_child = children_toks_dict[pos_mod]
		modality_aux = [x for x in pos_aux if x < pos_mod]
		head_aux = [x for x in pos_aux if x > pos_mod]

		tense_modality_aux = None
		mood_modality_aux = None
		aspect_modality_aux = None
		verbform_modality_aux = None


		if len(modality_aux) == 0:
			if "Tense" in children_toks_dict[pos_mod]["feats"] and "Mood" in children_toks_dict[pos_mod]["feats"]:
				tense_modality_aux = children_toks_dict[pos_mod]["feats"]["Tense"]
				mood_modality_aux = children_toks_dict[pos_mod]["feats"]["Mood"]
				verbform_modality_aux = children_toks_dict[pos_mod]["feats"]["VerbForm"]
		else:

			assert(len(modality_aux)==1)
			modality_aux_child = children_toks_dict[modality_aux[0]]
			verbform_modality_aux = modality_aux_child["feats"]["VerbForm"]

			# if modality_aux_child["lemma"] == "stare":
			# 	aspect_modality_aux = "Prog"

			# we're supposing 'andare' and 'venire' do not bear auxiliaries themselves
			if modality_aux_child["lemma"] in ["andare", "venire"]:
				aspect_modality_aux = "Imp"

			if pos_mod_child["feats"]["VerbForm"] == "Ger":
				tense_modality_aux = modality_aux_child["feats"]["Tense"]
				mood_modality_aux = modality_aux_child["feats"]["Mood"]


			elif pos_mod_child["feats"]["VerbForm"] == "Part":

				# Indicativo perfetto composto > ho potuto
				# Congiuntivo perfetto > abbia potuto
				# Condizionale composto > avrei potuto
				if modality_aux_child["feats"]["Tense"] == "Pres":
					# if modality_aux_child["feats"]["Mood"] == "Ind":
					# 	aspect_modality_aux = "Perf"
					tense_modality_aux = "Past"
					mood_modality_aux = modality_aux_child["feats"]["Mood"]

				# Indicativo piùcheperfetto > avevo potuto
				# Congiuntivo piucheperfetto > avessi potuto
				elif modality_aux_child["feats"]["Tense"] == "Imp":
					# if modality_aux_child["feats"]["Mood"] == "Ind":
					# 	aspect_modality_aux = "Perf"
					tense_modality_aux = "Past"
					mood_modality_aux = modality_aux_child["feats"]["Mood"]

				# Indicativo trapassato > ebbi potuto
				# Indicativo futuro composto > avrò potuto
				elif modality_aux_child["feats"]["Tense"] in ["Past", "Fut"]:
					tense_modality_aux = modality_aux_child["feats"]["Tense"]
					mood_modality_aux = modality_aux_child["feats"]["Mood"]
					# if modality_aux_child["feats"]["Tense"] == "Past":
					# 	aspect_modality_aux = "Perf"

		if mood_modality_aux:
			head_tok["ms feats"]["Mood"].add(mood_modality_aux)
		if aspect_modality_aux:
			head_tok["ms feats"]["Aspect"].add(aspect_modality_aux)
		if verbform_modality_aux:
			del head_tok["ms feats"]["VerbForm"]
			head_tok["ms feats"]["VerbForm"].add(verbform_modality_aux)

		if len(head_aux) == 0:
			if tense_modality_aux:
				head_tok["ms feats"]["Tense"].add(tense_modality_aux)
		else:

			if any(children_toks_dict[x]["lemma"] == "stare" for x in head_aux):
				head_tok["ms feats"]["Aspect"].add("Prog")

			# we're supposing 'andare' and 'venire' do not bear auxiliaries themselves
			if any(children_toks_dict[x]["lemma"] in ["andare", "venire"] for x in head_aux):
				head_tok["ms feats"]["Aspect"].add("Imp")

			if tense_modality_aux in ["Fut", "Past"]:
				head_tok["ms feats"]["Tense"].add(tense_modality_aux)
			else:
				if any(children_toks_dict[x]["deprel"] == "aux" for x in head_aux):
					head_tok["ms feats"]["Tense"].add("Past")
				else:
					head_tok["ms feats"]["Tense"].add("Pres")

	else:
		head_aux = pos_aux

		for aux in head_aux:
			child_tok = children_toks_dict[aux]

			if child_tok["deprel"] in ["aux", "cop"]:

				if child_tok["feats"]["VerbForm"] in ["Inf", "Ger"]:
					head_tok["ms feats"]["Tense"].add("Past")

				if child_tok["lemma"] == "stare":
					if child_tok["feats"]["Mood"] == "Ind":
						logger.debug("Adding Aspect feature with value Prog")
						head_tok["ms feats"]["Aspect"].add("Prog")

				elif child_tok["lemma"] in ["andare", "venire"]:
					if child_tok["feats"]["Mood"] == "Ind":
						logger.debug("Adding Aspect feature with value Imp")
						head_tok["ms feats"]["Aspect"].add("Imp")

				if "feats" in child_tok:
					logger.debug(f"child_tok['feats']: {child_tok['feats']}")
					if child_tok["feats"].get("Tense") == "Fut":
						head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
						if child_tok["feats"]["Mood"] == "Ind":
							head_tok["ms feats"]["Aspect"].add("Perf")

					elif child_tok["feats"].get("Tense") in ["Pres", "Past", "Imp"]:
						head_tok["ms feats"]["Tense"].add("Past")
						if child_tok["feats"]["Mood"] == "Ind":
							head_tok["ms feats"]["Aspect"].add("Perf")

			elif child_tok["deprel"] == "aux:pass" and child_tok["feats"]["VerbForm"] == "Fin" :

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
					elif child_tok["feats"]["Tense"] in ["Past"]:
						if child_tok["feats"]["Mood"] == "Ind":
							head_tok["ms feats"]["Aspect"].add("Perf")
						head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
						head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

					elif child_tok["feats"]["Tense"] in ["Fut"]:
						head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
						head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
