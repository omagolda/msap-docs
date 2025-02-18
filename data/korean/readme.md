## Correcting POS labels in Koraen GSD

Each word in the new Korean UniDive dataset is augmented with UniMorph-derived features.  
We apply deterministic rules to assign UniMorph features based on morphological patterns observed in the surface form, leveraging both UPOS (Universal POS) and XPOS (language-specific POS).  
The morphological tags are integrated directly into the Universal Dependencies (UD) format, ensuring compatibility with existing UD tools.  
To guarantee consistency and accuracy, we employ:  
1. Automatic annotation using existing tagging tools such as POS tags and NER tags on UD-annotated sentences.  
2. Manual verification by a linguistic expert, who validates the assigned POS tags.  

### POS misclassification  
One of the most frequent errors observed in GSD was the misclassification of proper nouns (NNP) as common nouns (NNG) in their XPOS labels.  Additionally, the corresponding UPOS tags were often incorrectly assigned, failing to distinguish between proper nouns (PROPN) and common nouns (NOUN) at the universal level.  

Beyond noun-related errors, verbs (VV) and adjectives (VA) were also frequently mislabeled.  In many cases, verbs were incorrectly tagged as adjectives (ADJ), particularly when descriptive verbs were involved, as Korean adjectives (VA) function similarly to stative verbs in some languages.  Likewise, verb-adjective misclassification affected UPOS, where Korean adjectives (VA) were incorrectly labeled as verbs (VERB), despite their distinct morphological and syntactic behaviors.  

To correct these errors, we systematically verify the consistency between POS tagging and Named Entity Recognition (NER) results for nouns while also applying morphosyntactic analysis for verbs and adjectives.  If a token is identified as both a proper noun (NNP) and a named entity in NER but is incorrectly labeled as a common noun (NNG), we reclassify it as a proper noun (PROPN).  Conversely, if a token is not recognized as a named entity but is incorrectly tagged as a proper noun (NNP), we adjust it to a common noun (NNG, NOUN).  

For verbs and adjectives, we analyze inflectional patterns and conjugational endings to ensure correct classification.  If a verb (VV) is incorrectly tagged as an adjective (VA), we examine morphological cues and predicate structure to determine whether the word exhibits verbal or adjectival properties.  
This approach ensures that adjectives (VA) are correctly assigned to ADJ and verbs (VV) to VERB, preserving the accuracy of the dependency structure.  

Additionally, we observed inconsistencies in the annotation of inflected verb and adjective forms, where derivational suffixes led to misclassifications between adverbs (ADV), adjectives (ADJ), and verbs (VERB).  In particular, verb-derived adjectives were frequently misclassified as adverbs (ADV) instead of adjectives (ADJ) due to their sentence context.  To address these inconsistencies, we reviewed and corrected POS information, including morphological analysis with explicit morpheme boundaries, following Sejong corpus guidelines to ensure that each word’s annotation accurately reflected its true morphological category.  However, these corrections were limited to POS tagging and morphological segmentation, without modifying the dependency structure.  

### POS assignment based on syntactic role  
A significant source of error in GSD was the misclassification of words due to an overemphasis on their syntactic role within a given sentence rather than their inherent lexical category.  This issue led to frequent misannotations, particularly in cases where temporal nouns and other category-specific words were assigned adverbial roles based on their sentence context rather than their fundamental lexical identity.  One prominent example is `가격에` (*gagyeog-e*) ("price+*e*"), which was originally labeled as ADV instead of its correct annotation as NOUN for NNG+JKB (common noun + adverbial postposition).  
This misclassification likely stemmed from the word’s function as a modifier in specific contexts, leading to an erroneous assignment of an adverbial tag. However, based on Sejong POS guidelines, such words should retain their noun classification regardless of their syntactic role in a particular sentence. To address these issues, we systematically revised the affected annotations, ensuring that UPOS labels were determined based on the lexical properties of each word rather than their contextual function within a sentence.  This correction improves consistency in POS tagging and aligns with best practices for Korean morphological annotation.  

### Misclassification of XR as a noun fragment  
XR is defined as a root, which is the core part of a word that carries the essential meaning when analyzing words.  However, in the Sejong Corpus, it is defined as a noun fragment (fragment) that lacks independence.  For example, the root `민주` (*minju*) can form a noun when combined with other affixes, such as in `민주화` (*minjuhwa*) ("democratization") or `민주주의` (*minjujuui*) ("democracy").  Only when it becomes a noun can it combine with derivational endings to be transformed into other parts of speech.  

### Complement markers in Korean grammar  
In Korean grammar, *nominals* that appear before the verbs `되다` (*doeda*) ("become") and `아니다` (*anida*) ("not be") function as complements (predicate nominatives) rather than subjects.  This is because `되다` (*doeda*) and `아니다` (*anida*) act as linking verbs (copulas) rather than action verbs. Additionally, while these complements take the subject marker (-이/가, *-i/-ga*), they function as predicate complements rather than typical subjects in the sentence structure.  Therefore, their case marker should be annotated as JKC (predicate nominative marker) instead of JKS (nominative case marker). We also revise the morphological analysis after manual verification, correcting cases where the GSD annotation and automatic annotation differ.  For example, the analysis of `중일` (*jung-il*) ("China and Japan") as `중+이+ㄹ;NNB+VCP+ETM` (bound noun + copula + adnominal ending) is corrected to `중일;PROPN;NNP`. 

By refining the UPOS and XPOS annotations, we have enhanced the reliability of GSD as a training resource for Korean syntactic parsing and morphological analysis, particularly for deriving morphosyntactic features from POS tags.  Our systematic corrections in the Korean GSD dataset effectively address major inconsistencies.  

