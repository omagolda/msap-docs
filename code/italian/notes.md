# Notes and decisions

- [Notes and decisions](#notes-and-decisions)
	- [Preliminar steps](#preliminar-steps)
	- [Content Heads](#content-heads)
		- [NOUNs, PROPNs](#nouns-propns)
		- [VERBs](#verbs)
			- [modals?](#modals)
		- [ADJs](#adjs)
		- [ADVs](#advs)
	- [Other](#other)
		- [INTJs](#intjs)
		- [ADP](#adp)
		- [AUX](#aux)
		- [CCONJ](#cconj)
		- [DET](#det)
		- [NUM](#num)
		- [PART](#part)
		- [PRON](#pron)
		- [SCONJ](#sconj)
		- [PUNCT](#punct)
		- [SYM](#sym)
		- [X](#x)
	- [Decision based on relations](#decision-based-on-relations)
		- [`fixed`](#fixed)


## Preliminar steps

1. Excluded sentences
   1. [x] any sentence containing `orphan` relation has been filtered out
2. Excluded tokens
   1. [x] any token whose `id` is not `int`
   2. [x] any token whose `deprel` is `punct`
3. [ ] content words with no MSFEATS -> `|`


## Content Heads

### NOUNs, PROPNs

- [x] all features copied
- [ ] dependents with `det` relation:
  - [x] `Definite` feature copied on HEAD
  - [ ] TODO: `ogni`, `alcuni`...?
- [ ] dependents with `case` relation:
  - [ ] at the moment, provisional attribute has been set

### VERBs

#### modals?

### ADJs

- [ ] copy all features? (`no agreement features are needed`)

### ADVs

- [ ] copy all features?

## Other

### INTJs

### ADP

### AUX

### CCONJ

### DET

### NUM

### PART

### PRON

### SCONJ

### PUNCT

- [x] Ignored. They get filtered out by removing `punct` relations

### SYM

1. SYM is the dependent: `pattern { e: X -> Y; Y[upos=SYM]}`:
   1. - [ ] has no features, we can ignore it

2. SYM is the head: `pattern { e: X -> Y; X[upos=SYM]}`

289 occurrences in isdt

```
# sent_id = tut-2172
# text = Qui non si trova più un seguace del Partito democratico che pure a Valona aveva vinto le ultime elezioni con l'88% dei consensi.
1    Qui    qui    ADV    B    _    4    advmod    _    _
2    non    non    ADV    BN    PronType=Neg    4    advmod    _    _
3    si    si    PRON    PC    Clitic=Yes|Person=3|PronType=Prs    4    expl:impers    _    _
4    trova    trovare    VERB    V    Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin    0    root    _    _
5    più    più    ADV    B    _    4    advmod    _    _
6    un    uno    DET    RI    Definite=Ind|Gender=Masc|Number=Sing|PronType=Art    7    det    _    _
7    seguace    seguace    NOUN    S    Number=Sing    4    obj    _    _
8-9    del    _    _    _    _    _    _    _    _
8    di    di    ADP    E    _    10    case    _    _
9    il    il    DET    RD    Definite=Def|Gender=Masc|Number=Sing|PronType=Art    10    det    _    _
10    Partito    partito    NOUN    S    Gender=Masc|Number=Sing    7    nmod    _    _
11    democratico    democratico    ADJ    A    Gender=Masc|Number=Sing    10    amod    _    _
12    che    che    PRON    PR    PronType=Rel    17    nsubj    _    _
13    pure    pure    ADV    B    _    17    advmod    _    _
14    a    a    ADP    E    _    15    case    _    _
15    Valona    Valona    PROPN    SP    _    17    obl    _    _
16    aveva    avere    AUX    VA    Mood=Ind|Number=Sing|Person=3|Tense=Imp|VerbForm=Fin    17    aux    _    _
17    vinto    vincere    VERB    V    Gender=Masc|Number=Sing|Tense=Past|VerbForm=Part    10    acl:relcl    _    _
18    le    il    DET    RD    Definite=Def|Gender=Fem|Number=Plur|PronType=Art    20    det    _    _
19    ultime    ultimo    ADJ    NO    Gender=Fem|Number=Plur|NumType=Ord    20    amod    _    _
20    elezioni    elezione    NOUN    S    Gender=Fem|Number=Plur    17    obj    _    _
21    con    con    ADP    E    _    24    case    _    _
22    l'    il    DET    RD    Definite=Def|Number=Sing|PronType=Art    24    det    _    SpaceAfter=No
23    88    88    NUM    N    NumType=Card    24    nummod    _    SpaceAfter=No
24    %    %    SYM    SYM    _    17    obl    _    _
25-26    dei    _    _    _    _    _    _    _    _
25    di    di    ADP    E    _    27    case    _    _
26    i    il    DET    RD    Definite=Def|Gender=Masc|Number=Plur|PronType=Art    27    det    _    _
27    consensi    consenso    NOUN    S    Gender=Masc|Number=Plur    24    nmod    _    SpaceAfter=No
28    .    .    PUNCT    FS    _    4    punct    _    _

```

### X

1. X is the dependent: `pattern { e: X -> Y; Y[upos=X]}`

2. X is the head: `pattern { e: X -> Y; X[upos=X]}`


## Decision based on relations

### `fixed`
- [x] Ignored and lemma collapsed on head
- [ ] when does the lemma need to be copied in ms feats?