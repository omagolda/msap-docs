import logging

import code.italian.lemma_based_decisions as lbd

logger = logging.getLogger(__name__)

# TODO: create_abstract_nsubj

def copy_features(node):
	if node.get("feats"):
		for feat in node["feats"]:
			node["ms feats"][feat].add(node["feats"][feat])
	else:
		logger.warning("Node %s has no features", node)




def process_noun(head_tok, children_toks):

	logger.debug("Examining head: %s", head_tok)

	# TODO: sentences with copula?

	# keep existing features for all nominals
	copy_features(head_tok)

	for child_tok in children_toks:
		logger.debug("Examining child: %s", child_tok)

		# determiners
		if child_tok["deprel"] == "det":
			# add definiteness
			if "Definite" in child_tok["feats"]:
				logger.debug("Adding Definite feature with value %s", child_tok["feats"]["Definite"])
				head_tok["ms feats"]["Definite"].add(child_tok["feats"]["Definite"])
			else:
				logger.warning("DET %s with features %s", child_tok, child_tok["feats"])

			# if Degree was set to Cmp earlier, now change it to Sup
			if "Degree" in head_tok["ms feats"] and "Cmp" in head_tok["ms feats"]["Degree"]:
				logger.debug("Changing Degree feature to Sup")
				head_tok["ms feats"]["Degree"].remove("Cmp").add("Sup")


		# case relations
		elif child_tok["deprel"] in ["case", "mark"]:
			logger.debug("Adding Case feature with value %s", lbd.switch_case(child_tok, head_tok))
			head_tok["ms feats"]["Case"].add(lbd.switch_case(child_tok, head_tok))

		elif child_tok["upos"] in ["NOUN", "PROPN"]:
			logger.debug("Switching node to content and keeping its features")
			copy_features(child_tok)
			child_tok["content"] = True

		else:
			logger.warning("Node %s/%s needs new rules", child_tok, child_tok["upos"])
			child_tok["ms feats"]["tmp-child"].add("NOUN")


def process_adj(head_tok, children_toks):

	logger.debug("Examining head: %s", head_tok)

	# TODO: handle sentences with copula
	if any(tok["deprel"] == "cop" for tok in children_toks):
		head_tok["ms feats"]["tmp-head"].add("VERBAL-ADJ")
		for child_tok in children_toks:
			child_tok["ms feats"]["tmp-child"].add("VERBAL-ADJ")

	else:
		# TODO: copy features?
		# print("HEAD:", head_tok, head_tok["feats"])

		for child_tok in children_toks:
			logger.debug("Examining child: %s", child_tok)

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
					copy_features(child_tok)
					child_tok["content"] = True

			elif child_tok["deprel"] == "amod":
				child_tok["ms feats"]["tmp-child"].add("amod-ADJ")
				# input()

			elif child_tok["deprel"].startswith("obl"):
				child_tok["ms feats"]["tmp-child"].add("obl-ADJ")
				# input()



def process_adv(head_tok, children_toks):

	logging.info("Here")

	head_tok["ms feats"]["tmp-head"].add("ADV")

	for child_tok in children_toks:
		child_tok["ms feats"]["tmp-child"].add("ADV")
