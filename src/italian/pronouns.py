import logging

import src.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_pron(head_tok, children_toks):

	logger.info("Examining head: '%s'", head_tok)

	if head_tok["deprel"] in ["root", "nsubj", "obj", "iobj"]:

		# print(head_tok.items())
		# print(children_toks)

		logging.debug("Switching node to content and keeping its features")
		head_tok["content"] = True
		ita_utils.copy_features(head_tok)

		for child_tok in children_toks:
			logger.info("Examining child: '%s/%s'", child_tok, child_tok["upos"])

			if child_tok["deprel"] in ["cop"]:
				if "Mood" in child_tok["feats"]:
					logging.debug("Adding TAM features with values Mood: %s - Tense: %s",
								child_tok["feats"]["Mood"], child_tok["feats"]["Tense"])
					head_tok["ms feats"]["Mood"].add(child_tok["feats"]["Mood"])
				else:
					logging.warning("No Mood feature in %s - %s", child_tok, child_tok["feats"])

				if "Tense" in child_tok["feats"]:
					head_tok["ms feats"]["Tense"].add(child_tok["feats"]["Tense"])
				else:
					logging.warning("No Tense feature in %s - %s", child_tok, child_tok["feats"])

				if "VerbForm" in child_tok["feats"]:
					logging.debug("Adding VerbForm feature with value: %s",
								child_tok["feats"]["VerbForm"])
					head_tok["ms feats"]["VerbForm"].add(child_tok["feats"]["VerbForm"])
				else:
					logging.warning("No VerbForm feature in %s - %s", child_tok, child_tok["feats"])

			else:
				logging.warning("Node %s/%s needs new rules", child_tok, child_tok["upos"])
				child_tok["ms feats"]["tmp-child"].add("PRON")
