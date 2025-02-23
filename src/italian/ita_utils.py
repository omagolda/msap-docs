import logging
import collections
import conllu
from typing import List

logger = logging.getLogger(__name__)

def copy_features(node):
	if node.get("feats"):
		for feat in node["feats"]:
			node["ms feats"][feat].add(node["feats"][feat])
	else:
		logger.info("Node %s/%s has no features", node, node["upos"])


def create_abstract_nsubj(head: conllu.Token):
	'''
	When the subject is missing but agreement features appear on its head, an abstract node carrying features only is created
	'''
	abstract_nsubj = conllu.Token()
	abstract_nsubj['id'] = head['id'] + 0.1 # to make sure it's between the head and the first child
	abstract_nsubj['form'] = '-' # set all values to '-', but set the head and the deprel
	abstract_nsubj['lemma'] = '-'
	abstract_nsubj['upos'] = '-'
	abstract_nsubj['xpos'] = '-'
	abstract_nsubj['feats'] = '-'
	abstract_nsubj['head'] = head['id']
	abstract_nsubj['deprel'] = 'nsubj'
	abstract_nsubj['deps'] = '-'
	abstract_nsubj['misc'] = '-'
	abstract_nsubj['ms feats'] = collections.defaultdict(set)
	abstract_nsubj["content"] = True

	for attr in ['Number', 'Person', 'Gender']: # copy the features from the head
		if attr in head["ms feats"]:
			for value in head['ms feats'][attr]:
				abstract_nsubj['ms feats'][attr].add(value)

	abstract_nsubj["ms feats"]["Case"].add("Nom")

	return abstract_nsubj