import logging
import conllu.serializer as conllu

import code.italian.lemma_based_decisions as lbd
import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_adj(head_tok, children_toks):

	logging.debug("Setting %s/%s to content and copying its features", head_tok, head_tok["upos"])
	head_tok["content"] = True
	ita_utils.copy_features(head_tok)


	pos_non = []
	pos_mod = []

	pos_aux = []
	cop = False

	children_toks_dict = {}
	for child_tok in children_toks:
		children_toks_dict[child_tok["id"]] = child_tok

		logger.debug("Examining child: %s", child_tok.values())

		if child_tok["deprel"] in ["cop"]:
			cop = True

			# * default aspect to Imp if Mood = Ind
			logging.debug("Setting Aspct")
			if "Mood" in child_tok["feats"] and child_tok["feats"]["Mood"] == "Ind":
				if child_tok["feats"]["Tense"] in ["Pres", "Imp"]:
					head_tok["ms feats"]["Aspect"].add("Imp")
				elif child_tok["feats"]["Tense"] in ["Past"]:
					head_tok["ms feats"]["Aspect"].add("Perf")

			# * default mood
			if "Mood" in child_tok["feats"]:
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

			# * default tense
			if "Tense" in child_tok["feats"]:
				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])

			# * default verbform
			if "VerbForm" in child_tok["feats"]:
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])

		# * evaluate copulas
		elif child_tok["deprel"] in ["aux"]:
			pos_aux.append(child_tok["id"])

			modality = lbd.switch_verb_modality(child_tok)
			if modality:
				pos_mod.append(child_tok["id"])
				logger.debug("Adding Modality feature with value %s", modality)
				head_tok["ms feats"]["Modality"].add(modality)

			if child_tok["feats"]["VerbForm"] == "Fin":
				if "VerbForm" in head_tok:
					del head_tok["ms feats"]["VerbForm"]
				head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])

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
			if child_tok["lemma"] == "non":
				if "Degree" in head_tok["ms feats"] and head_tok["ms feats"]["Degree"] == "Cmp":
					logging.error("What should we do here??")

				pos_non.append(child_tok["id"])

			# * add Degree feature
			elif child_tok["lemma"] in ["più", "meno"]:
				logging.debug("Adding Degree feature with value Cmp")
				head_tok["ms feats"]["Degree"].add("Cmp")

				if "Definite" in child_tok["ms feats"]:
					for x in child_tok["ms feats"]["Definite"]:
						head_tok["ms feats"]["Definite"].add(x)
					del child_tok["ms feats"]["Definite"]

				if "Gender" in child_tok["ms feats"]:
					for x in child_tok["ms feats"]["Gender"]:
						head_tok["ms feats"]["Gender"].add(x)
					del child_tok["ms feats"]["Gender"]

				if "Number" in child_tok["ms feats"]:
					for x in child_tok["ms feats"]["Number"]:
						head_tok["ms feats"]["Number"].add(x)
					del child_tok["ms feats"]["Number"]

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

	if cop:
		if len(pos_non)>0 and len(pos_mod)>0:
			assert(len(pos_mod)==1)

			pos_mod_id = pos_mod[0]
			for i in pos_non:
				if i < pos_mod_id:
					modality_value = head_tok["ms feats"]["Modality"].pop()
					del head_tok["ms feats"]["Modality"]
					head_tok["ms feats"]["Modality"].add(f"not({modality_value})")
				else:
					head_tok["ms feats"]["Polarity"].add("Neg")



		elif len(pos_non)>0:
			head_tok["ms feats"]["Polarity"].add("Neg")

		verbforms = [children_toks_dict[x]["feats"]["VerbForm"] for x in pos_aux]
		if "Inf" in verbforms:
			del head_tok["ms feats"]["VerbForm"]
			head_tok["ms feats"]["VerbForm"].add("Inf")
		elif "Ger" in verbforms:
			del head_tok["ms feats"]["VerbForm"]
			head_tok["ms feats"]["VerbForm"].add("Ger")
		else:
			del head_tok["ms feats"]["VerbForm"]
			head_tok["ms feats"]["VerbForm"].add("Fin")

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
						tense_modality_aux = "Past"
						mood_modality_aux = modality_aux_child["feats"]["Mood"]

					# Indicativo piùcheperfetto > avevo potuto
					# Congiuntivo piucheperfetto > avessi potuto
					elif modality_aux_child["feats"]["Tense"] == "Imp":
						tense_modality_aux = "Past"
						mood_modality_aux = modality_aux_child["feats"]["Mood"]

					# Indicativo trapassato > ebbi potuto
					# Indicativo futuro composto > avrò potuto
					elif modality_aux_child["feats"]["Tense"] in ["Past", "Fut"]:
						tense_modality_aux = modality_aux_child["feats"]["Tense"]
						mood_modality_aux = modality_aux_child["feats"]["Mood"]

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

				if child_tok["feats"]["VerbForm"] in ["Inf", "Ger"]:
					head_tok["ms feats"]["Tense"].add("Past")

				if child_tok["lemma"] == "stare":
					if "Mood" in child_tok["feats"]:
						if child_tok["feats"]["Mood"] == "Ind":
							logger.debug("Adding Aspect feature with value Prog")
							head_tok["ms feats"]["Aspect"].add("Prog")
					else:
						logger.warning("Node %s has no Mood: %s", child_tok, child_tok["feats"])

				elif child_tok["lemma"] in ["andare", "venire"]:
					if "Mood" in child_tok["feats"]:
						if child_tok["feats"]["Mood"] == "Ind":
							logger.debug("Adding Aspect feature with value Imp")
							head_tok["ms feats"]["Aspect"].add("Imp")
					else:
						logger.warning("Node %s has no Mood: %s", child_tok, child_tok["feats"])

				if "feats" in child_tok:
					logger.debug(f"child_tok['feats']: {child_tok['feats']}")
					if child_tok["feats"].get("Tense") == "Fut":
						head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
						if "Mood" in child_tok["feats"]:
							if child_tok["feats"]["Mood"] == "Ind":
								head_tok["ms feats"]["Aspect"].add("Perf")
						else:
							logger.warning("Node %s has no Mood: %s", child_tok, child_tok["feats"])

					elif child_tok["feats"].get("Tense") in ["Pres", "Past", "Imp"]:
						head_tok["ms feats"]["Tense"].add("Past")
						if "Mood" in child_tok["feats"]:
							if child_tok["feats"]["Mood"] == "Ind":
								head_tok["ms feats"]["Aspect"].add("Perf")
						else:
							logger.warning("Node %s has no Mood: %s", child_tok, child_tok["feats"])

	if len(head_tok["ms feats"]["Polarity"]) == 0:
		head_tok["ms feats"]["Polarity"].add("Pos")