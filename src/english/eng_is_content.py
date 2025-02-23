import os
import conllu
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
from eng_relations import case_feat_map


VERBAL = {'VERB'}
NOMINAL = {'NOUN', 'PROPN', 'PRON', 'NUM'}

case_feat_map = {
    "'s": 'Gen',
    "'til": 'Ttr',
    'about': 'The',
    'above': 'Sup',
    'according to': 'Quo',
    'across': 'Crs',
    'after': 'Tps',
    'against': 'Adv',
    'ago': '',
    'along': 'Lng',
    'alongside': 'Apu',
    'amid': 'Ces',
    'amidst': 'Ces',
    'among': 'Ces',
    'and': 'Conj',
    'around': 'Cir',
    'as': 'Ess',
    'as for': 'The',
    'as to': 'The',
    'at': 'Loc',
    'atop': 'Adt',
    'because': 'Reas',
    'because of': 'Cau',
    'before': 'Tan',
    'behind': 'Pst',
    'below': 'Sub',
    'beneath': 'Sub',
    'beside': 'Apu',
    'between': 'Int',
    'beyond': 'Pst',
    'but': 'Advs',
    'by': 'Chz',
    'circa': 'Tpx',
    'concerning': 'The',
    'considering': 'Cns',
    'depending on': 'Cnd',
    'despite': 'Ccs',
    'down': 'Dsc',
    'due to': 'Cau',
    'during': 'Dur',
    'either': 'Disj',
    'everywhere': '',
    'except': 'Exc',
    'far from': 'Dst',
    'for': 'Ben',
    'from': 'Abl',
    'from above': 'Spe',
    'from behind': 'Pse',
    'from beyond': 'Pse',
    'from below': 'Sbe',
    'from beneath': 'Sbe',
    'from past': 'Pse',
    'from under': 'Sbe',
    'from between': 'Ite',
    'given': 'Cns',
    'if': 'Cnd',
    'in': 'Ine',
    'in front of': 'Ant',
    'in order to': 'Pur',
    'including': 'Inc',
    'inside': 'Ine',
    'instead of': 'Sbs',
    'into': 'Ill',
    'like': 'Sem',
    'near': 'Prx',
    'neither': 'Nnor',
    'next to': 'Apu',
    'nor': 'Nnor',
    'notwithstanding': 'Ccs',
    'of': 'Gen',
    'off': 'Del',
    'on': 'Ade',
    'onto': 'Spl',
    'opposite': 'Opp',
    'or': 'Disj',
    'outside': 'Ext',
    'outside of': 'Ext',
    'over': 'Spx',
    'past': 'Pst',
    'per': 'Dis',
    'rather than': 'Sbs',
    'regarding': 'The',
    'regardless': 'Ign',
    'since': 'Teg',
    'so': 'Cnsq',
    'then': 'Cnsq',
    'through': 'Inx',
    'throughout': 'Tot',
    'till': 'Ttr',
    'than': 'Cmp',
    'that': 'Atr',
    'therefore': 'Cnsq',
    'though': 'Advs',
    'thus': 'Cnsq',
    'to': 'Dat',
    'under': 'Sub',
    'unless': 'Ncnd',
    'unlike': 'Dsm',
    'until': 'Ttr',
    'unto': 'Ter',
    'up': 'Asc',
    'up to': 'Ter',
    'upon': 'Tem',
    'using': 'Ins',
    'via': 'Pro',
    'when': 'Temp',
    'whenever': '',
    'where': '',
    'whereas': 'Cmt',
    'whether': 'Dbt',
    'while': 'Temp',
    'whilst': 'Temp',
    'with': 'Com',
    'within': 'Ine',
    'without': 'Abe',
    'yet': 'Advs'
}


clausal_rels = {'conj','csubj','xcomp','ccomp','advcl','acl','advcl:relcl','acl:relcl'}

modalities = {'shall':'Des', 'should':'Des', 'must':'Nec', 'may':'Prms', 'might':'Prms', 'can':'Pot', 'could':'Pot'} # words with modality features, 'will':'Fut' is treated separately

# determiners with tuples of the feature name and the feature value
determiners = {'a':('Definite', 'Ind'), 'the':('Definite', 'Def'), 'another':('Definite', 'Ind'), 'no':('Definite', 'Ind', 'Polarity', 'Neg')}  #, 'this':('Dem', 'Prox'), 'that':('Dem', 'Dist')}


forced_upos_for_closed_classes = {'the': 'DET', 'a': 'DET', 'any': 'DET'}

definitely_content = {'NOUN', 'PROPN', 'VERB', 'SYM', 'INTJ', 'ADJ'}
definitely_function = {'PUNCT', 'ADP', 'AUX', 'CCONJ', 'SCONJ', 'PART'}
skip_sentence = {'X', 'orphan'}
rules = {'DET', 'PRON', 'ADV'}
det_function_lemmas = {'a', 'the', 'no'}
adv_function_lemmas = {'then', 'so', 'therefore', 'also', 'however', 'when'}
pron_function_lemmas = {'that'}

# def is_content(index, parse_list, parse_tree):
def is_content(node, sentence):
    upos = node['upos']
    lemma = node['lemma']
    incoming_deprel = node['deprel']
    if upos in skip_sentence:
        # raise ValueError('skip sentence with upos X '+ parse_tree.metadata['text'])
        raise ValueError(f'skip sentence with upos {upos}: {sentence}')
    if incoming_deprel in skip_sentence:
        raise ValueError(f'skip sentence with deprel {incoming_deprel}: {sentence}')
    if lemma in case_feat_map:
        return False
    if lemma in forced_upos_for_closed_classes and upos != forced_upos_for_closed_classes[lemma]:
        raise ValueError(f'forced upos for {lemma} is {forced_upos_for_closed_classes[lemma]} but got {upos}, skipping sentence')
    if upos in definitely_content:
        return True
    if upos in definitely_function:
        return False

    if upos in rules:
        if upos == 'DET' and node['lemma'] not in det_function_lemmas:
            return True
        if upos == 'ADV' and node['lemma'] not in adv_function_lemmas:
            return True
        if upos == 'PRON' and node['lemma'] not in pron_function_lemmas:
            if not incoming_deprel == 'nmod:poss':
                return True
        
    return False


if __name__ == '__main__':
    filepath = 'en_ewt-ud-test.conllu'
    out_path = 'out_test.conllu'
    with open(filepath, encoding='utf8') as f:
        parse_trees = list(conllu.parse_tree_incr(f))
    with open(filepath, encoding='utf8') as f:
        parse_lists = list(conllu.parse_incr(f))

    assert len(parse_lists) == len(parse_trees)
    with open(out_path, 'w', encoding='utf8') as outfile:
        for i in range(len(parse_trees)):  # iterate over the sentences
            parse_tree = parse_trees[i]
            parse_list: conllu.TokenList = parse_lists[i]

            id2idx = {token['id']: i for i, token in enumerate(parse_list) if isinstance(token['id'], int)}
            idx2id = [token['id'] if isinstance(token['id'], int) else None for token in parse_list]

            for index, item in enumerate(parse_list):
                try:
                    content_status = is_content(index, parse_list, parse_tree)
                    if content_status and item['lemma'] in case_feat_map:
                        raise NotImplementedError(f"{item['lemma']} is classified as content but is in case_feat_map in sentence {parse_tree.metadata['text']}")

                except ValueError as e:
                    print(e)
                    break

