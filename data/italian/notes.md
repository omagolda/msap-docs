---
Project:
  - "[[Bologna]]"
Date: 2023-01-08
tags:
  - "#UD"
Status: ongoing
Summary: Notes on verbs.py shared task
---
# Verbs

## General remarks

* Not clear why we add features and then in italian.py we remove those features. We add Person, Mood, Tense from aux/cop and then in italian.py (line 164) we remove Person; then from the 'det' we get Gender and Number, but then we remove it again.
* Why do we transfer VerbForm of aux/cop onto the head? In an example as 'non sarebbero mai potuti arrivare' > head arrivare is VerbForm = Inf, Part and Fin?



Aspect 					Hab 	Imp 	Iter 	Perf 						Prog 			Prosp
Tense
Pres (tempi semplici)	-		def		-		-							-				-
Pres (tempi composti)	-		-		-		-							stare(Pres)+Ger	-
Past (tempi semplici)	-		-		-		def							-				-
Past (tempi composti)	-		-		-		ess/avere(Pres/Past)+Part	-				-
Fut	 (tempi semplici)	-		def?	-
Fut	 (tempi composti)	-		-		-		ess/avere(Fut)+Part			stare(Fut)+Ger	-
Imp						-		def?	-		-							-				-
Imp (tempi composti)	-		-		-		ess/avere(Imp)+Part			stare(Imp)+Ger	-


## Aux/cop

transfer Person feature
transfer Mood feature
Tense ???

* Gerunds
if VerbForm is Ger, and child is lemma 'stare' > add Prog (aspect) (ok)
	lemmi != 'stare': andare, essere (problematico)
	https://universal.grew.fr/?custom=677daebbafd5e

* Participles
if VerbForm Part, transfer VerbForm (ok)
if Tense = Past, add aspect = Perf (ok)
and when Tense is not Past? https://universal.grew.fr/?custom=677db3544ffed

* TODO: handle Props: cominciare a, finire di, stare per + VERB (ok)
* volere, potere, dovere
* Cau con 'fare': vogliamo ancora farlo? No.

## Passive voice
* venire
* deprel aux:pass > Voice = Pass (ok)

## Case, mark
* deprel case, mark > see lemma-based decisions

Markers that needs to be discussed

| Request              | mark.req | case             | to discuss |     |
| -------------------- | -------- | ---------------- | ---------- | --- |
| Request              | mark.req | case             | discuss    |     |
| così da/così come    | 2        | così da/Rpl      | discuss    |     |
| che                  | 1138     | che              | discuss    |     |
| di                   | 1166     | di	             | discuss    |     |
| come                 | 192      | Rpl              | discuss    |     |
| da/da quando/da dove | 203      | da/Teg/da dove   | discuss    |     |
| dove                 | 6        | dove             | discuss    |     |
| tanto/tanto che      | 3        | Ccs/tanto che  	 | discuss    |     |
| ecco che             | 2        | ecco che         | discuss    |     |
| più che              | 1        | più che          | discuss    |     |
| Quando               | 1        |                  | titolo     |     |
| a/a che/a meno che   | 991      | Pur/a che/Abe    | discuss    |     |

  deprel = case on VERB (clustered by lemma of ADP & VerbForm of VERB): https://universal.grew.fr/?custom=677db8e0e9bd9 (sono tutti verbi che svolgono funzione nominale)

## Verbi con funzione nominale
* TODO: Indexing (person, number)? Is the same as above? TODO? From the guidelines: features should be applied only to their relevant node. In other words, no agreement features are needed, and in a phrase like he goes only he should bear Number=Sing|Person=3, and goes should have only Tense=Pres (and other features if relevant).

* frasi con deprel = det, det:poss, det:predet
	* feats Gender, Number (ok) -> then we remove them in italian.py
	* feats Definite; https://universal.grew.fr/?custom=677dbcac51cea != Definite

	frasi con:
	* nessuno - no results
	* alcuno - no results
	* qualche - no results
	* questo - no results
	* quello - 1 occ
	* di - no results
	* nessuno - no results
	* alcuno - no results
	frasi con:
	* questo e quello, PronType Dem (ok)

* frasi con deprel advmod
	* frasi con la negazione (non) che ha advmod (ok)
	* frasi AUX-non-VERB (ok) e non-AUX-non-VERB (ok)

---
# References


### Resources
* 📦 [Repo](https://github.com/omagolda/msap-docs)
* [Repo ita (Old)](https://github.com/ellepannitto/msap-docs-ita/tree/dev-ita)