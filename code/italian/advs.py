import logging

import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_adv(head_tok, children_toks):

	logger.info("Examining head: '%s'", head_tok)

	# head_tok["ms feats"]["tmp-head"].add("ADV")

	for child_tok in children_toks:
		logger.info("Examining child: '%s/%s'", child_tok, child_tok["upos"])
		# child_tok["ms feats"]["tmp-child"].add("ADV")
