import conllu
import random

def sample(input_file, n, output_file, seed):
	random.seed(seed)

	ret = []
	N = 0

	with open(input_file, encoding='utf8') as fin:
		parse_trees = list(conllu.parse_incr(fin))
		for sent in parse_trees:
			# print(sent)
			# print(sent)
			# n_orphans = len(sent.filter(deprel="orphan").filter(deprel="parataxis"))
			n_exclusion = len(sent.filter(deprel="parataxis")) + \
						len(sent.filter(deprel="orphan"))
			# print(n_exclusion)
			if n_exclusion == 0: #TODO change with extended list of conditions
				N += 1
				if len(ret) < n:
					ret.append(sent)
				else:
					i = int(random.random() * N)
					if i < n:
						ret[i] = sent
			# else:
			# 	input()

	with open(output_file, "w", encoding="utf-8") as fout:
		for sent in ret:
			print(sent.serialize(), file=fout)



if __name__ == "__main__":
	import sys
	import pathlib
	def _select_sentences(sentences_number, ud_directory, output_dir, seed):
		train_split = int(sentences_number*0.8)
		dev_split = int(sentences_number*0.1)
		test_split = int(sentences_number*0.1)

		train_filename = ud_directory.glob("*train.conllu").__next__()
		dev_filename = ud_directory.glob("*dev.conllu").__next__()
		test_filename = ud_directory.glob("*test.conllu").__next__()

		output_dir.mkdir(parents=True, exist_ok=True)

		sample(train_filename, train_split, output_dir.joinpath("train.conllu"), seed)
		sample(dev_filename, dev_split, output_dir.joinpath("dev.conllu"), seed)
		sample(test_filename, test_split, output_dir.joinpath("test.conllu"), seed)


	sentences_number = 10000
	ud_directory = pathlib.Path(sys.argv[1])
	output_dir = pathlib.Path("data/italian/")
	seed = 563

	_select_sentences(sentences_number, ud_directory, output_dir, seed)