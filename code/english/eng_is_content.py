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
    'to': 'Lat',
    'with': 'Com',
    'of': 'Gen',
    "'s": 'Gen',
    'from': 'Abl',
    'for': 'Ben',
    'on': 'Ade',
    'above': 'Sup',
    'atop': 'Adt',
    'at': 'Loc',
    'in': 'Ine',
    'into': 'Ill',
    'onto': 'Spl',
    'through': 'Inx',
    'by': 'Chz',
    'and': 'Conj',
    'or': 'Disj',
    'nor': 'Nnor',
    'under': 'Sub',
    'near': 'Prx',
    'around': 'Cir',
    'against': 'Adv',
    'without': 'Abe',  # may also be 'neg(Com)'
    'like': 'Sem',
    'as': 'Ess',
    'along': 'Lng',
    'during': 'Dur',
    'across': 'Crs',
    'inside': 'Ine',
    'outside': 'Ext',
    'after': 'Tps',  # may also be 'TempPost
    'ago': '',
    'before': 'Tan',
    'behind': 'Pst',
    'amid': 'Ces',
    'amidst': 'Ces',
    'among': 'Ces',
    'upon': 'Tem',
    'unto': 'Ter',
    'about': '',
    'throughout': 'Tot',
    'beyond': 'Pst',
    'when': 'Temp',
    'whenever': '',
    'where': '',
    'if': 'Cnd',
    'so': 'Cnsq',
    'but': 'Advs',
    'because': 'Reas',
    'since': 'Teg',
    'while': 'Temp',
    'until': 'Ttr',
    'till': 'Ttr',
    'everywhere': '',
    'then': 'Cnsq'
}


clausal_rels = {'conj','csubj','xcomp','ccomp','advcl','acl','advcl:relcl','acl:relcl'}

modalities = {'shall':'Des', 'should':'Des', 'must':'Nec', 'may':'Prms', 'might':'Prms', 'can':'Pot', 'could':'Pot'} # words with modality features, 'will':'Fut' is treated separately

# determiners with tuples of the feature name and the feature value
determiners = {'a':('Definite', 'Ind'), 'the':('Definite', 'Def'), 'another':('Definite', 'Ind'), 'no':('Definite', 'Ind', 'Polarity', 'Neg'), 'this':('Dem', 'Prox'), 'that':('Dem', 'Dist')}

def is_content(index, parse_list, parse_tree):
    forced_upos_for_closed_classes = {'the':'DET', 'a':'DET', 'any':'DET'}

    definitely_content = {'NOUN', 'PROPN', 'VERB', 'SYM', 'INTJ', 'ADJ'}
    definitely_function = {'PUNCT', 'ADP', 'AUX', 'CCONJ', 'SCONJ','PART'}
    skip_sentence = {'X'}
    rules = {'DET', 'PRON', 'ADV'} 
    det_function_lemmas = {'a', 'the', 'no'}
    adv_function_lemmas = {'then', 'so', 'therefore', 'also', 'however'}
    pron_function_lemmas = {'that'}
    node = parse_list[index]
    upos = node['upos']
    lemma = node['lemma']
    incoming_deprel = node['deprel']
    if upos in skip_sentence:
        raise ValueError('skip sentence with upos X '+ parse_tree.metadata['text'])
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

filepath = 'en_ewt-ud-test.conllu'
out_path = 'out_test.conllu'
with open(filepath, encoding='utf8') as f:
    parse_trees = list(conllu.parse_tree_incr(f))
with open(filepath, encoding='utf8') as f:
    parse_lists = list(conllu.parse_incr(f))
    
assert len(parse_lists) == len(parse_trees)
with open(out_path, 'w', encoding='utf8') as outfile:
    for i in range(len(parse_trees)): # iterate over the sentences
        parse_tree = parse_trees[i]
        parse_list: conllu.TokenList = parse_lists[i]

        id2idx = {token['id']:i for i, token in enumerate(parse_list) if isinstance(token['id'], int)}
        idx2id = [token['id'] if isinstance(token['id'], int) else None for token in parse_list]
        
        for index, item in enumerate(parse_list):
            try:
                content_status = is_content(index, parse_list, parse_tree)
                if content_status == True and item['lemma'] in case_feat_map:
                    raise NotImplementedError(f'{item['lemma']} is classified as content but is in case_feat_map in sentence {parse_tree.metadata['text']}')
                    
            except ValueError as e:
                print(e)
                break

