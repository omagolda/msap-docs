"""
usage (launch from msap-docs directory):
python -m code.italian.italian SOURCE_TREEBANK.conllu OUTPUT_FILEPATH

e.g.

python -m code.italian.italian data/italian/dev.conllu data/italian/dev.out.conllu
"""
import logging
import collections
import tqdm
import code.utils as utils
import code.italian.verbs as verbs
import code.italian.nouns as nouns
import code.italian.adjs as adjs
import code.italian.advs as advs
import code.italian.ita_utils as ita_utils
import conllu


def DFS(root_tree):

	if root_tree.children:
		children = root_tree.children
		for child in children:
			# print(child)
			yield from DFS(child)
		yield(root_tree.token, [child.token for child in children])
	else:
		yield(root_tree.token, [])

	# else:
	# 	return
		# return root_tree.token, [tok.token for tok in root_tree.children]
		# process_vertex(root_tree)
	# else:
	# 	pass

if __name__ == '__main__':
	import sys
	import pathlib

	filepath = pathlib.Path(sys.argv[1])
	out_path = pathlib.Path(sys.argv[2])

	logger = logging.getLogger(__name__)
	logging.basicConfig(format='[%(module)s:%(lineno)d] %(levelname)s:%(message)s',
					filename=f"logs/italian/{filepath.stem}.log",
					filemode='w', encoding='utf-8',
					level=logging.DEBUG)

	logging.info("Processing %s into %s", filepath, out_path)

	with open(filepath, encoding='utf8') as f:
		parse_trees = list(conllu.parse_tree_incr(f))

	with open(filepath, encoding='utf8') as f:
		parse_lists = list(conllu.parse_incr(f))

	with open(out_path, "w", encoding="utf-8") as fout:

		for tree, tokenlist in tqdm.tqdm(zip(parse_trees, parse_lists)):
			logging.info("Processing sentence id: %s", tokenlist.metadata["sent_id"])
			logging.info("Sentence content: %s", tokenlist.metadata["text"])

			for node in tokenlist:
				# * initialize empty ms-feats and set all nodes to false at the beginning
				node["ms feats"] = collections.defaultdict(set)
				node["content"] = False

			id2idx = {token['id']:i for i, token in enumerate(tokenlist)}
			idx2id = {y:x for x, y in id2idx.items()}

			# * filter out useless nodes (punct, reparandum)
			filtered_tokenlist = tokenlist \
								.filter(id=lambda x: isinstance(x, int)) \
								.filter(upos=lambda x: x!="PUNCT") \
								.filter(deprel=lambda x: x != "punct") \
								.filter(deprel=lambda x: x != "reparandum")
			logging.debug("Removed punctuation: %s", " ".join([str(x) for x in filtered_tokenlist]))

			# * combine fixed expressions and remove nodes with 'fixed' relation
			fixed_nodes = filtered_tokenlist.filter(deprel="fixed")
			filtered_tokenlist = filtered_tokenlist.filter(deprel=lambda x: x!= "fixed")

			if len(fixed_nodes):
				fixed_nodes_sorted = sorted(fixed_nodes, key=lambda x: x['id'])
				for node in fixed_nodes_sorted:
					node_head = tokenlist[id2idx[node['head']]]
					node_head["lemma"] += f" {node['lemma']}"
					node_head["form"] += f" {node['form']}"

				logging.debug("Removed fixed deprels: %s", " | ".join([str(x) for x in filtered_tokenlist]))

			tree = filtered_tokenlist.to_tree()

			# * visit tree in depth-first fashion
			for head_tok, children_toks in DFS(tree):

				# * only select non-content children: information will be gathered only from those
				children_toks = [tok for tok in children_toks if not tok["content"]]

				logging.info("Processing head '%s/%s' with children '%s'",
							head_tok, head_tok["upos"],
							" | ".join(str(x) for x in children_toks))

				# TODO: placeholder for agentive in passive clauses

				# * Assigning 'Nom', 'Acc' and 'Dat' Case based on syntactic function
				if head_tok["deprel"] == "nsubj":
					head_tok["ms feats"]["Case"].add("Nom")
					logging.debug("Assigned 'Nom' case to head '%s' because its deprel is '%s'",
								head_tok, head_tok["deprel"])

				if head_tok["deprel"] == "nsubj:pass" or head_tok["deprel"] == "obj":
					head_tok["ms feats"]["Case"].add("Acc")
					logging.debug("Assigned 'Acc' case to head '%s' because its deprel is '%s'",
								head_tok, head_tok["deprel"])

				if head_tok["deprel"] == "iobj":
					head_tok["ms feats"]["Case"].add("Dat")
					logging.debug("Assigned 'Dat' case to head '%s' because its deprel is '%s'",
								head_tok, head_tok["deprel"])


				# Open class words 	Closed class words 	Other
				# ADJ 				ADP 				PUNCT
				# ADV 				AUX 				SYM
				# INTJ 				CCONJ			 	X
				# NOUN 				DET
				# PROPN 			NUM
				# VERB 				PART
				# 					PRON
				# 					SCONJ

				# * Check that interjection has no deps and set to content word
				if head_tok["upos"] in ["INTJ"]:
					if len(children_toks) > 0:
						logging.error("Found INTJ '%s' with children '%s'. Consider removing sentence %s",
									head_tok, ", ".join(str(x) for x in children_toks),
									tokenlist.metadata["sent_id"])
					head_tok["content"] = True

				# * OPEN CLASS WORDS SECTION
				elif head_tok["upos"] in ["VERB"]:
					verbs.process_verb(head_tok, children_toks)
				elif head_tok["upos"] in ["NOUN", "PROPN", "NUM", "SYM"]:
					nouns.process_noun(head_tok, children_toks)
				elif head_tok["upos"] in ["ADJ"]:
					adjs.process_adj(head_tok, children_toks)
				elif head_tok["upos"] in ["ADV"]:
					advs.process_adv(head_tok, children_toks)

				# * CLOSED CLASS WORDS SECTION
				elif head_tok["upos"] in ["CCONJ", "SCONJ"]:
					if len(children_toks) > 0:
						logging.error("Found CONJ '%s' with children '%s'. Consider removing sentence %s",
									head_tok, ", ".join(str(x) for x in children_toks),
									tokenlist.metadata["sent_id"])

						# TODO: advmod case (non appena, anche se...)
						# TODO: cc

						# print(head_tok.items())
						# print(children_toks)
						# input()

				elif head_tok["upos"] in ["PART"]:
					if len(children_toks) > 0:
						logging.error("Found PART '%s' with children '%s'. Consider removing sentence %s",
									head_tok, ", ".join(str(x) for x in children_toks),
									tokenlist.metadata["sent_id"])
						print(head_tok.items())
						print(children_toks)
						input()
				elif head_tok["upos"] in ["DET", "AUX"]:
					# TODO: handle case with dependencies
					pass
				elif head_tok["upos"] in ["ADP"]:
					# TODO everything here
					pass
				else:
					logging.warning("Not treated head '%s/%s', children '%s'",
									head_tok, head_tok["upos"],
									" | ".join(str(x) for x in children_toks))
					#TODO: PRON?

			for node in tokenlist:
				# TODO: at the end function words should have "_" and content words with no ms-feat should have "|"

				# restore original lemma
				node['lemma'] = node['lemma'].split(" ")[0]
				node['form'] = node['form'].split(" ")[0]

				if node["content"]:
					if node.get("feats"):
						node_feats = node['feats']
						node_msfeats = node["ms feats"]

						# TODO: copy default values
						# for feat, value in node["feats"].items():
						# 	if feat in node["ms feats"]:
						# 		print(node.items())
						# 		input()
						# 		assert any(x==node["feats"][feat] for x in node["ms feats"][feat])
						# 	else:
						# 		node["ms feats"][feat].add(node["feats"][feat])

					sorted_msfeats = sorted(node["ms feats"].items())
					# * if multiple values are present, they are conjoined by semi-colon
					# TODO: handle negation -> es. not(Pot)
					# TODO: handle conjunction of values -> es. "if and when" and(Cnd,Tmp)
					# TODO: handle disjunction of values -> es. Tense=or(Past,Fut)
					sorted_msfeats = [f"{x}={';'.join(y)}" for x, y in sorted_msfeats]
					node['ms feats'] = "|".join(sorted_msfeats)

				elif node.get("ms feats"):
					logging.error("Node %s should be empty bus has features %s", node, node["ms feats"])
					node["ms feats"] = None

			to_write = tokenlist.serialize()
			print(to_write, file=fout)