import logging
import collections
import conllu
from typing import List

logger = logging.getLogger(__name__)

# TODO: create_abstract_nsubj

def copy_features(node):
	if node.get("feats"):
		print(node.items())
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
	abstract_nsubj['deps'] = '-'
	abstract_nsubj['misc'] = '-'
	abstract_nsubj['head'] = head['id']
	abstract_nsubj['deprel'] = 'nsubj'
	abstract_nsubj["content"] = True
	abstract_nsubj['ms feats'] = collections.defaultdict(set)

	# if auxes: # if there are auxiliaries, take the features from the first one
	#     first_aux_id = min([child['id'] for child in auxes])
	#     feats_source = [aux for aux in auxes if aux['id'] == first_aux_id][0]
	# else: # if there are no auxiliaries, take the features from the head
	#     feats_source = head

	for attr in ['Number', 'Person', 'Gender']: # copy the features from the head or the auxiliaries
		if attr in head["ms feats"]:
			for value in head['ms feats'][attr]:
				abstract_nsubj['ms feats'][attr].add(value)

	# abstract_nsubj['ms feats'] = {k:v for k,v in abstract_nsubj['ms feats'].items() if v} #clean up nones

	# in case of some pragmatical omission of subject with no agreement on the predicate - do not create abstract node
	# if not abstract_nsubj['ms feats']:
		# return None

	return abstract_nsubj