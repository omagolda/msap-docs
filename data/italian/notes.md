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


Da Salvi/Vanelli:
Aspetto:
* perfettivo:
	* aoristico
	* compiuto -> compatibile con *da x tempo*

* imperfettivo:
	* progressivo
	* abituale
	* continuo

Incompatibile con *in x tempo, per x tempo, fino a x, da x a y, tra x e y*. 
Compatibile con *da x tempo*

Noi facciamo distinzione solo tra perf, imp e prog

Tense & Aspect

Voice Act

* Indic Pres: default Imp, ma casi di Perf che verranno disambiguati a mano (verbi performativi e usato al posto del futuro)
* Indic Imp: default Imp, ma casi di Perf che verranno disambiguati a mano (evento appena concluso, *arrivava in quel momento* e quando viene usato al posto del condizionale composto *ho aspettato per vedere se venivi* = *se saresti venuto*, e narrativo ha valore aoristico).
* Indic Past: aspetto perfettivo
* Indic Past composto: aspetto perfettivo 
* Fut: no aspetto.
* Fut composto: default Perf.  

Tutto ciò vale solo per l'indic, eliminiamo aspetto su Sub, Cnd, Imp

Perifrasi aspettuali:

stare + Ger -> Aspect = Prog 
andare, venire -> Aspect = Imp

Tense & Aspect
Voice Pass

Indic Pres Pass è mangiata


### Verbi Nominali
abbiamo deciso coscientemente che gli infiniti con funzione nominale non hanno Genere e Numero. Nota: nel gold eventualmente aggiungeremo il numero a mano.

### And/or(value, value)
a mano

### Aspect on Mod verbs
non abbiamo messo aspetto su verbi modali

volere e dovere hanno sempre l'aspetto?
potere ha l'aspetto quando è equivalente a be able to, ma non quando è un irrealis e indica l'azione come nel mondo della possibilità. -> disambiguare a mano. 

luigi mangia
luigi può mangiare -> se è inf, copia tense child // gerundio

la mela sta venendo mangiata da luigi
la mela stava venendo mangiata da luigi

luigi ha mangiato
lui
luigi può mangiare

dovrà aver fatto -> tense: fut (dal aux potere, dovere, volere);
dovrà essere fatto -> tense: fut

deve fare > tense: dal modale; mood: dal modale; aspect: dal modale
deve aver fatto > tense: past; 
deve essere fatto > tense: pres
deve essere stato fatto > tense: past

sta dovendo mangiare
se hai progressivizzato il modale, allora dai il progr a tutto e non puoi avere qualcosa come sta dovendo aver mangiato.

Perifrasi aspettuale stare, andare, venire + gerundio (cit. Salvi Vanelli): 
lemmi = stare, andare, venire

* lemma = stare
	* asp: progr.
	* restrizioni:
		* tempi composti (pass prossimo, piùcheperfetto, trap. prossimo), no perfetto semplice (passato remoto). No Tense Past.
		* no Mood = imperativo
		* no Voice = Pass

* lemmi = andare, venire > asp. Imp


---
# References


### Resources
* 📦 [Repo](https://github.com/omagolda/msap-docs)
* [Repo ita (Old)](https://github.com/ellepannitto/msap-docs-ita/tree/dev-ita)