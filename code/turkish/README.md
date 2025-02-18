# Turkish MSF Parser

This folder contains a Python script and a Makefile to process [Turkish UD IMST](https://universaldependencies.org/treebanks/tr_imst/index.html) `.conllu` files
and generate `.msf` files with morphological expansions such as null subjects and dropped possessive pronouns.

---

## Requirements

1. **Python 3.6+**
2. **[udapi](https://github.com/udapi/udapi-python)** installed (e.g., `pip install udapi`)
3. **Make** (optional, if you prefer just running the Python script by hand)

---

## Parsing Steps

Below are the major steps in the parser:

1. **Loading UD Trees**

   - `udapi.Document(...)` reads the `.conllu` file into a structured format, letting us traverse tokens (nodes) and their morphological features easily.
2. **Collecting Node Information**

   Node Types in Turkish data includes:

   - *Content Nodes:* Open class words and pronouns (UPOS Tags: `['ADJ', 'ADV', 'INTJ', 'NOUN', 'NUM', 'PRON', 'PROPN', 'VERB']`).
   - *Functional Nodes:* Closed class words and punctuations (UPOS tags: `['ADP', 'AUX', 'CCONJ', 'DET', 'PUNCT']`)
   - *Abstract Nodes:* Dropped pronouns and null subjects (UPOS tags: `['PRON']`)
3. **Morphological Feature Extraction & Merging**

   After reading source files into dependency trees, the parser operates in the following order;

   1. In each dependency tree, detects subtrees consisting solely of functional nodes.
   2. Merges functional nodes in these subtrees (most often, the subtree is a single functional node) into the parent content node based on predefined rules.
   3. Inserts abstract nodes into the trees for dropped possessive pronouns and null subjects.

      - **Dropped Possessive Pronouns**: If a token has certain `psor` features (e.g., “benim”, “senin”), we insert a new empty node if it doesn’t already exist as a child.
      - **Null Subjects**: For certain verbs and auxiliaries lacking an explicit `nsubj`, we add them (e.g., “ben”, “sen”, “o”) based on `Number=Sing/Plur` and `Person=1/2/3`.
   4. In some corner cases, dependency arcs required redefinition, and ideally, the tree should be restructured. However, alternations in the source data is out of scope.
4. **Storing the Modified Trees**

   - Each processed tree is saved back as `.conllu`. However, we do it first into an intermediate `.conllu` file (e.g., `.temp.conllu`) to preserve the normal structure before final line-based corrections.
5. **Post-Processing for Formatting**

   - Some lines need an extra `_` column in certain columns for multi-word tokens or newly inserted empty nodes.
   - The script looks for lines containing `MS_feats=` to rearrange them properly.
   - The final output with these adjustments is saved as `.msf`.
