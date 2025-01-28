# Morphosyntax Parsing Shared Task Data Annotation Guidelines

## Table of Contents

1. [Introduction](https://github.com/omagolda/msud-docs/blob/main/README.md#introduction)
   1. [Motivation](https://github.com/omagolda/msud-docs/blob/main/README.md#motivation)
   2. [Principles](https://github.com/omagolda/msud-docs/blob/main/README.md#principles)
      1. [Independence from Word Boundaries](https://github.com/omagolda/msud-docs/blob/main/README.md#independence-from-word-boundaries)
      2. [Content-Function Divide](https://github.com/omagolda/msud-docs/blob/main/README.md#content-function-divide)
      3. [Crosslingual Parallelism](https://github.com/omagolda/msud-docs/blob/main/README.md#crosslingual-parallelism)
      4. [Minimal Deviation from CoNLL-U](https://github.com/omagolda/msud-docs/blob/main/README.md#minimal-deviation-from-conll-u)
2. [Schema Description](https://github.com/omagolda/msud-docs/blob/main/README.md#file-format)
   1. [File Format](https://github.com/omagolda/msud-docs/blob/main/README.md#morpho-syntactic-features)
   2. [Morpho-Syntactic Features](https://github.com/omagolda/msud-docs/blob/main/README.md#morpho-syntactic-features)
      1. [Feature Inventory](https://github.com/omagolda/msud-docs/blob/main/README.md#features-inventory)
   3. [Content Nodes](https://github.com/omagolda/msud-docs/blob/main/README.md#content-nodes)
      1. [Abstract Nodes](https://github.com/omagolda/msud-docs/blob/main/README.md#abstract-nodes)
      2. [Gaps](https://github.com/omagolda/msud-docs/blob/main/README.md#gaps)
3. [The Annotation Process](https://github.com/omagolda/msud-docs/blob/main/README.md#the-annotation-process)
   1. [Conversion from UD](https://github.com/omagolda/msud-docs/blob/main/README.md#conversion-from-ud)

## Introduction

In this documentation, we first explain the general principles of MSP, and then show the feature set and how to convert a regular UD treebank to MSP, with the example of English.

### Motivation

Words have long been an essential concept in the definition of treebanks in Universal Dependencies (UD), since the first stage in their construction is delimiting words in the language at hand. This is done due to the common view in theoretical linguistics of words as the dividing line between syntax, the grammatical module of word combination, and morphology, that is word construction.

We suggest defining the content-function boundary to differentiate 'morphological' from 'syntactic' elements. In our morpho-syntactic data structure, content words are represented as separate nodes on a dependency graph, even if they share a whitespace-separated word, and both function words and morphemes contribute morphology-style features to characterize the nodes.

### Principles

#### Independence from Word Boundaries

Delimiting syntactically relevant words gets exponentially more complicated the less isolating languages are. Thus, this operation, which is as simple as breaking the text on white spaces for English, is borderline impossible for polysynthetic languages, in which a single word may be composed of several lexemes that have predicate-argument relations. This reflects the fact that despite the presumed role of words in contemporary linguistics, there is no consensus on a coherent cross-lingual definition of words. We will thus avoid (most) theoretical debates on word boundaries, and solve much of the word segmentation inconsistencies that occur in UD, either across languages, e.g., Japanese is treated as isolating and Korean as agglutinative, even though they are very similar typologically, or across treebanks of the same language, e.g., the different treebanks for Hebrew segment and attribute different surface forms for clitics.

#### Content-Function Divide

The central divide in an MS graph is between content words (or morphemes) and function words (or morphemes). Content words form the nodes, while the information from function words is represented as features modifying the content nodes.

#### Crosslingual Parallelism

Morphosyntactic Annotation will bring the trees of very different languages much closer together and thus enable new typological studies. In isolating languages, the data will explicitly surface MS features that are expressed periphrastically. Morpho-syntactic data will be more inclusive towards languages that are currently treated unnaturally, most prominently noun-incorporating languages. Morpho-syntactic models will be able to parse sentences in more languages and enable better cross-lingual studies.

#### Minimal Deviation from CoNLL-U

We will add the morphosyntactic features in a new 11th column called `MS-FEATS'. The original CoNLL-U file can thus be recovered by simply dropping this column. On the other hand, the morphosyntactic tree can be built by dropping all the lemmas that do not have MS-FEATS defined for them. On the other hand, in polysynthetic languages, the addition of MS-features to content words will expose the argument structure even if it is encapsulated in a single word.

## Schema Description

### File Format

The format for morpho-syntactic parsing data is a simple extension of UD's
[CoNLL-U format](https://universaldependencies.org/format.html). It includes an addition
of a single column with morpho-syntactic features (named: MS-FEATS) for every UD node
that contains a content word. UD nodes that contain function words should have empty
(i.e. `_`) MS features. The new column should be added last, after the MISC column.

The other CoNLL-U's columns: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, and
MISC, are defined exactly the same as in UD.

### Morpho-Syntactic Features

As the key characteristics of morpho-syntactic dependency trees, morpho-syntactic
features (MS features) are modelled after the morphological features in UD and may be
viewed as a generalization of them. [Like in UD]( https://universaldependencies.org/u/overview/morphology.html),
the features are an alphabetically ordered set of name and value pairs separated by pipes, of the
structure `Name1=Value1|Name2=Value2`.[^msf0] Most feature names and values are equivalent to
those in UD, for example `Gender=Masc`, `Voice=Pass`, etc.

However, MS features also differ from morphological features in a couple
important characteristics:
* The features are only defined for content nodes (see below)._
  * Function words should not have MS features. All the information they
  convey should be expressed as features on the relevant content node.
  * Note: since the file format is a modified version of UD's CoNLL-U, function words
  may appear in the final output, their MS-feats column should be `_`. This is  in
  contrast with content words that happen to have no MS-feats that should contain an
  orphan pipe `|`.
* The features are defined not only by morphemes but by any _grammatical_ function
marker, be it a morpheme or a word. So the content node _go_ in _will go_ should bear
the feature `Tense=Fut`.
  * All applicable features should be marked on the respective content nodes, even if
  expressed by non-concatenative means (as long as they are grammatical). E.g., the node
  _go_ in _did you go?_ should be marked with `Mood=Ind;Int` even though the
  interrogative mood is expressed mostly by word order.
* Features should be applied only to their relevant node. In other words, no agreement
features are needed, and in a phrase like _he goes_ only _he_ should bear
`Number=Sing|Person=3`, and _goes_ should have only `Tense=Pres` (and other features if
relevant).
* The feature structure is not flat. In other words, features are not necessarily single
strings. They can contain:
  * a list of values separated by a semicolon, for example `Aspect=Perf;Prog` on the verb
  of the English clause _I have been walking_
  * a negation of a value, for example `Mood=not(Pot)` on the Turkish verb _yürüyemez_
  (“he can’t walk”) where the negation refers to the ability[^msf1]
  * a conjunction of values. This mechanism is to be used only in cases of explicit
  conjunction of grammatical constructions, for example `Case=and(Cnd,Temp)` is the
  manifestation of the English phrase _if and when_ when connecting two clauses (see
  below for discussion on the `Case` feature)
  * and a disjunction of values, `Tense=or(Fut,Pas)`
* If a feature includes multiple values in any kind of order or structure, they should be ordered alphabetically in accordance with the general UD guidelines.

The mapping from morpho-syntactic constructions to features does not have to be
one-to-one. In cases where several constructions have the exact some meaning (e.g.,
they differ in geographic distribution, register or personal preferences), it is
perfectly suitable to assign the same feature combination to both of them. For example,
in Spanish, both _comiera_ and _comiese_ will be assigned `Aspect=Imp|Mood=Sub|Tense=Past|VerbForm=Fin`
(remember that the agreement features should appear only on the relevant argument).

The categories of words to be "consumed" into MS features are usually: auxiliaries,
determiners, adpositions, conjunctions and subordinators, and some particles. These
categories may not neatly correspond to UD POS tags. Some clearly do, like auxiliaries
(POS tag `AUX`), while others, like `DET` may include also contentful word, like _all_
and _every_. Some POS tags like `ADV` mix many contentful words (_nicely_, _rapidly_,
_often_, etc.) with a few that serve as conjunctions (_when_, _then_, etc.), and in
rare cases the same word may be considered functional or contentful depending on the
context.[^msf2]

[^msf0]: The feature set in unordered in theory but in practice the features are ordered
alphabetically by feature name, just to make the annotations consistent.

[^msf1]: This is in contrast with the verb _yürümebilir_ (literally “he is able to not
walk”, i.e., he may not walk), where the negation pertains to the verb itself and should
be tagged as `Mood=Pot|Polarity=Neg`.

[^msf2]: Compare the word _then_ in the sentence _if you want, then I'll do it_
(functional) to the same word in _I didn't know what to do, then I understood_ (_then_
stands for "after some time" hence contentful).

#### Feature Inventory

quick link: [inventory of relation features](https://docs.google.com/spreadsheets/d/16d0B7yYwyjS-o6T15JElt37Zy6DvngjY/edit?usp=sharing&ouid=117571112446302948501&rtpof=true&sd=true)

Since the MS features are a generalization of UD's morphological features, their types
and possible values are also highly similar with that of [UD's features](https://universaldependencies.org/u/feat/index.html).
Therefore, for most features, the list in UD is sufficient in characterizing content
nodes in MS trees as well.
The most prominent exceptions to this is the expansion of the`Case` feature.

Originally, the `Case` feature characterized the relation between a predicate and
its argument, almost always a nominal, but for MS trees its role is expanded twice. First,
In line with the principle of independence from word boundaries, in MS trees this feature
corresponds to traditional case morphemes as well as adpositions (these usually have
`case` as DEPREL in UD trees) and coverbs when such exist. The inclusion of adpositions
in determining the `Case` feature entails the expansions of cases possible in almost any
language. Nominals in German, for example, now have an elative case (indicating motion
from the inside of the argument) expressed by the combination of the synthetic dative
case and the periphrastic _aus_ preposition.

The second expansion of the `Case` feature is that in MS trees this feature is also used
to characterize predicate-predicate relations, hence it is applicable also to verbal
nodes and it "consumes" also conjunctions and subordinators. So _fell_ in _I cried
until I fell asleep_ and _today_ in _It is true until today_ will both get a `Case=Ttr`
because they are both marked by the function word _until_.

In general, the same function word/morpheme combination should be mapped to the same
`Case` value, even if it serves multiple functions. For example, the Swahili preposition
_na_ should be mapped only to `Case=Conj` even when it serves a function of introducing
the agent of a passive verb.

"[inventory.md](https://docs.google.com/spreadsheets/d/16d0B7yYwyjS-o6T15JElt37Zy6DvngjY/edit?usp=sharing&ouid=117571112446302948501&rtpof=true&sd=true)"
details a set of universal values for the `Case` feature. These feature does not cover
all possible relations, and in some cases when there are adpositions or conjunctions that
do not correspond to any of the features, the value of the respective feature should be
the canonical citation form of the function word transliterated into latin letters in
quotation marks. <!-- For example, the word _books_ in the phrase _about books_ should be
assigned the MS features `Case="about"|Number=Plur`. -->

A mapping from adpositions and conjunctions to the features in "inventory.md" should be
created as part of the annotation process. Note that the mapping does not have to be
one-to-one.

### Content Nodes

Content nodes, to which morpho-syntactic features are to be defined, are all words or
morphemes from open classes (like nouns, verbs and adjectives) that do not convey a
grammatical modification of another word.[^cn1] These content words should form a
morpho-syntactic tree, and this is automatically true in most cases when converting UD
data due to the fact that UD designates content words as heads, so they directly relate
to one another (see exceptions below).

Note that copulas are not content words. In sentences with copulas refer to the nominal
as the predicate and tag it with the features expressed by the copula.

For example, in the sentence _the quick brown fox jumps over the lazy dog_ there are 6
content words (quick, brown, fox, jump, lazy, dog) and 3 function words (the, over, the).
<!--- we probably need a better example --->

In compounds or headless expressions, i.e., cases where one of the `fixed`, `flat` or
`goeswith` DEPRELs are used, all words are judged together to either be of content or of
function. Usually such cases will be contentful, but sometimes a fixed expression can be
a multi-word adposition, for example _as well as_ and _because of_.

[^cn1]: In most languages, content nodes are equivalent to words. However, in some noun
incorporating languages open class nouns can appear as morphemes concatenated to another
content node that is the verb.

#### Abstract Nodes

In addition to words from open classes, content nodes also include all arguments and
predicates in the sentence. The implications of this are twofold:
1. Pronouns should always be represented as nodes with MS features, regardless of your
theoretical position on whether pronouns are contentful or a mere bundle of features.
2. arguments that do not appear explicitly in a sentence but are expressed implicitly
(i.e., by agreement of their predicate) should also be represented by their own node.
However, this node lacks FORM or LEMMA fields and is therefore _an abstract node_.
Abstract nodes should appear after the node from which they inherit their features and
should have a special ID in the form of `X.1`, `X.2` etc.

The most common use-case of abstract nodes is when pronouns are dropped. For example, in
Basque, the UD nodes:
~~~ conllu
4	ziurtatu	ziurtatu	VERB	_	Aspect=Perf|VerbForm=Part	0	root	_	_
5	zuten	edun	AUX	_	Mood=Ind|Number[abs]=Sing|Number[erg]=Plur|Person[abs]=3|Person[erg]=3|Tense=Past|VerbForm=Fin	4	aux	_	ReconstructedLemma=Yes
~~~
should be tagged as:
~~~ conllu
4	ziurtatu	ziurtatu	VERB	_	Aspect=Perf|VerbForm=Part	0	root	_	_   Aspect=Perf|Mood=Ind|Tense=Past|VerbForm=Fin
5	zuten	edun	AUX	_	Mood=Ind|Number[abs]=Sing|Number[erg]=Plur|Person[abs]=3|Person[erg]=3|Tense=Past|VerbForm=Fin	4	aux	_	ReconstructedLemma=Yes  _
5.1 _   _   _   _   _   4   nsubj   _   _   Case=Erg|Number=Plur|Person=3
5.2 _   _   _   _   _   4   obj _   _   Case=Abs|Number=Sing|Person=3
~~~
Note that node `5` now doesn't have MS-feats (the last column) and therefore it will be
dropped from the MS tree.

This example underlines that the abstract nodes may be viewed as a replacement for
feature layering. The advantage of this mechanism is that equates the representation of
agreement morphemes, clitics and full pronouns, and removes the need to decide which is
which.

The same mechanism is used whenever an argument is missing from the clause as an
independent word, _but expressed in other means_, i.e., not when an argument was dropped
for pragmatic reasons or otherwise being not detectable from the surface forms. For
example, the annotation of the Japanese sentence _宣言したのだ_ ("(he) proclaimed") should
not contain an abstract node for the non-existent subject although one is understood.

Abstract nodes are also to be used when the argument is outside the clause.

#### Gaps

Abstract nodes are also to be used in simple gaps, when there are function words
referring to some missing argument. For example, a phrase like _books to choose from_,
should be annotated as:
~~~ conllu
4   books   book    NOUN    NN  Number=Plur 2   obj _   _   Number=Plur
5   to  to  PART    TO  _   6   mark   _   _   _
6   choose  choose  VERB    VB  VerbForm=Inf    4   acl _   _   VerbForm=Inf
7   from    from    ADP IN  _   6   obl _   _   _
7.1    _    _   _   _   _   6   obl _   _   Case=Abl
~~~
So node `7.1` is created to carry the feature of the function word _from_.

Note that this strategy is not suitable when the missing element has non-missing
arguments, for example in the phrase _Jon ate bananas and mary apples_. In these cases,
usually characterized by the `orphan` DEPREL, addition of an abstract node will require
adjustment of the HEAD column and this is beyond the current scope of this campaign in
which we only add a `MS-feats` column at the end of each line. Our suggestion is then to
not tag sentences with `orphan` DEPREL, at least not for this shared task.

<!--- TODO: other gap cases: "orphan" relation, others?
also, guidelines for "weird" rels like "fixed" --->

## The Annotation Process

### Conversion from UD

#### General

- create a new column
- decide what your content words and your function words are (by UPOS and incoming and outgoing deprels)
<!--- TODO: not necessarily only UPOS --->
- go through your function words and classify them according to UPOS, relation, and maybe lemma
- for each of these categories, figure out the morphosyntactic feature and place it on the head content word

#### English Rules

parataxis, reparandum and punct relations are left alone

fixed relation: combined to a temporary lemma to look for in the relevant map in 'eng_relations.py'.

Nominal lemmas: NOUN, PROPN, PRON, NUM, Verbal lemmas: VERB

keep existing features for all nominals. For verbs, they are not kept because the Tense may be wrong.

##### Get features from all the children

aux-children: all AUX and PART  that are not "'s"

Mood: Default Ind, or Int if an aux-child comes before a subj-child and (any child is a "?" or annotator decides), or Cnd if annotator decides

Polarity: default Pos, Neg if "not" child

VerbForm: default Fin, except if "to" as aux-child

if there is only one "do"-child, copy the tense to the verb

if there is a "be"-child
* if there is one "be"-child of a verb:
    * if the head verb is VerbForm Ger, or VerbForm Part and Tense Pres, set Aspect to Prog
    * if the head verb is VerbForm Part and Tense Past, set Voice to Pass
* if there are two "be"-children, set Aspect to Prog, and if it's a verb, set Voice to Pass
    otherwise Voice Active
    if there are no auxiliaries left, copy the remaining TAM feats from the "higher" auxiliary
    if aux are not only be and not, and the VerbForm is not inf:
        the higher be, if there were two, is the first one that does not end in -ing
        copy Tense from higher be if exists
        if the head is not a verb, copy Mood and VerbForm from higher be if exists

if there is a "get"-child, set Voice to Pass, and if aux lemmas do not contain anything other than get and not, copy Tense and VerbForm from the "get"-child

if there is a "have"-child
* if the head is not a verb or the head has VerbForm Part and Tense Past: add Perf to Aspect
* if there are no auxiliaries left, copy the remaining feats from the have

if there is a "will"-child, set Tense to Fut

if there is a "would"-child, let the annotator decide:
* Mood Conditional (conditional)
* Tense Past and add Prosp to Aspect (future in the past)

Modality
* can --> Pot
* could --> Pot, plus annotator decision between adding Cnd to Mood, or setting Tense to Past
* may or might --> Prms
* shall or should --> Des
* must --> Nec
* not --> set the previous modality to neg(modality), and delete the Polarity
concatenate all modalities

##### Get Features from Relations
relevant are all children with case, mark, or cc, or where the lemma is in case_feat_map. Remove all children that are PART, unless they're "'s"

Then case features are looked up in the feature map.

for verbs,
* copy existing features if they have not been set
* set Voice to Act if not otherwise set
* if a finite Verb has no nsubj child, create an abstract nsubj. All UD slots will be empty except for deprel and head. Take the Number and Person and Gender from somewhere
for nominals and adjectives and adverbs:
* assign features for the determiner, if any
    * a: Definite Ind
    * the: Definite Def
    * another: Definite Ind
    * no: Definite Ind and Polarity Neg
    * this: Dem Prox
    * that: Dem Dist
* for adjectives and averbs,
    * if 'more' child, set Degree to Cmp
    * if 'most' child, set Degree to Sup
