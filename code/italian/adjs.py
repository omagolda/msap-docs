import logging

import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_adj(head_tok, children_toks):

	logger.debug("Examining head: %s", head_tok)
	head_tok["content"] = True

	# # TODO: handle sentences with copula
	# if any(tok["deprel"] == "cop" for tok in children_toks):
	# 	head_tok["ms feats"]["tmp-head"].add("VERBAL-ADJ")
	# 	for child_tok in children_toks:
	# 		child_tok["ms feats"]["tmp-child"].add("VERBAL-ADJ")

	# else:
	# TODO: copy features?
	# print("HEAD:", head_tok, head_tok["feats"])

	for child_tok in children_toks:
		logger.debug("Examining child: %s", child_tok)

		if child_tok["deprel"] == "cop":
			# print(child_tok.items())
			if "Mood" in child_tok["feats"] and "Tense" in child_tok["feats"]:
				logger.debug("Adding TAM features with values Mood: %s - Tense: %s",
							child_tok["feats"]["Mood"], child_tok["feats"]["Tense"])
				head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
				head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
			else:
				logger.warning("Copula %s has no Mood or Tense features", child_tok)

			# TODO: add Person and Number to subject

		if child_tok["deprel"] == "advmod":

			# add Degree feature
			if child_tok["lemma"] in ["più", "meno"]:
				logger.debug("Adding Degree feature with value Cmp")
				head_tok["ms feats"]["Degree"].add("Cmp")

			elif child_tok["lemma"] in ["molto"]:
				logger.debug("Adding Degree feature with value Sup")
				head_tok["ms feats"]["Degree"].add("Sup")

			# TODO: should we use all 7 possible values for degrees?

			# TODO: how to deal with "non più X"?
			# (see isst_tanl-3074, see isst_tanl-3598
			# add Negation feature
			elif child_tok["lemma"] in ["non"]:
				logger.debug("Adding Polarity feature with value Neg")
				head_tok["ms feats"]["Polarity"].add("Neg")

			else:
				# TODO: molto, poco?
				logger.debug("Switching node to content and keeping its features")
				ita_utils.copy_features(child_tok)
				child_tok["content"] = True

		elif child_tok["deprel"] == "amod":
			child_tok["ms feats"]["tmp-child"].add("amod-ADJ")
			# input()

		elif child_tok["deprel"].startswith("obl"):
			child_tok["ms feats"]["tmp-child"].add("obl-ADJ")
			# input()
