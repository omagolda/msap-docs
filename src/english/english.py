
import os
import pickle
import conllu
from sympy.codegen.ast import continue_

from src import utils
from src.consts import *
from typing import List
from copy import deepcopy
from collections import defaultdict
from eng_is_content import is_content, case_feat_map

# lang = 'eng'
# bank = 'GENTLE'
# excluded_genres = ['dictionary', 'proof', 'poetry']

VERBAL = {'VERB'}
NOMINAL = {'NOUN', 'PROPN', 'PRON', 'NUM'}

clausal_rels = {'conj','csubj','xcomp','ccomp','advcl','acl','advcl:relcl','acl:relcl'}

modalities = {'shall':'Des', 'should':'Des', 'must':'Nec', 'may':'Prms', 'might':'Prms', 'can':'Pot', 'could':'Pot'} # words with modality features, 'will':'Fut' is treated separately

# determiners with tuples of the feature name and the feature value
determiners = {'a':[('Definite', 'Ind')], 'the':[('Definite', 'Def')], 'another':[('Definite', 'Ind')], 'no':[('Definite', 'Ind'), ('Polarity', 'Neg')]}  #, 'this':('Dem', 'Prox'), 'that':('Dem', 'Dist')}


def create_abstract_nsubj(head: conllu.Token, auxes: List[conllu.Token]):
    '''
    When the subject is missing but agreement features appear on its head, an abstract node carrying features only is created
    '''
    abstract_nsubj = conllu.Token()
    abstract_nsubj['id'] = head['id'] - 0.9 # to make sure it's between the head and the first child
    abstract_nsubj['form'] = '_' # set all values to '_', but set the head and the deprel
    abstract_nsubj['lemma'] = '_'
    abstract_nsubj['upos'] = '_'
    abstract_nsubj['xpos'] = '_'
    abstract_nsubj['feats'] = '_'
    abstract_nsubj['head'] = head['id']
    abstract_nsubj['deprel'] = 'nsubj'
    abstract_nsubj['deps'] = '_'
    abstract_nsubj['misc'] = '_'
    abstract_nsubj['ms feats'] = {}

    if auxes: # if there are auxiliaries, take the features from the first one
        first_aux_id = min([child['id'] for child in auxes])
        feats_source = [aux for aux in auxes if aux['id'] == first_aux_id][0]
    else: # if there are no auxiliaries, take the features from the head
        feats_source = head

    for attr in ['Number', 'Person', 'Gender']: # copy the features from the head or the auxiliaries
        abstract_nsubj['ms feats'][attr] = feats_source['feats'].get(attr, head['feats'].get(attr, None)) # if the feature is not in the auxiliaries, take it from the head
    abstract_nsubj['ms feats'] = {k:v for k,v in abstract_nsubj['ms feats'].items() if v} #clean up nones

    # in case of some pragmatical omission of subject with no agreement on the predicate - do not create abstract node
    if not abstract_nsubj['ms feats']:
        return None

    return abstract_nsubj


def get_rel_feat(word): # try to get the relation feature from the marker feature map, if not - from the case feature map, if not - return the word itself
    return case_feat_map.get(word, word)


def get_relation_feats(relation_nodes: List[conllu.Token], verb=True, clause=False) -> dict:
    '''
    Generating morpho_syntactic features for relations.
    The mapping from words (or fixed expressions) to features is in 'eng_relations.py' and should be updated there.
    '''
    feats = {}

    relation_nodes = deepcopy(relation_nodes)
    for node in relation_nodes: # if the node is a fixed node, take its fixed lemma, otherwise take its lemma
        node['lemma'] = node.get('fixed lemma', node.get('lemma'))

    feats['Case'] = ';'.join([get_rel_feat(node['lemma']) for node in relation_nodes])

    return feats


def get_agreement_feats(aux_node):
    agreement_feats = {}
    if 'Number' in aux_node['feats']:
        agreement_feats['Number'] = aux_node['feats']['Number']
    if 'Person' in aux_node['feats']:
        agreement_feats['Person'] = aux_node['feats']['Person']
    return agreement_feats


def get_nTAM_feats(aux_nodes: List[conllu.Token], head_feats: dict, verb=True, sent_num=None) -> dict:
    '''
    generating morpho-syntactic features for a head node based on its own morphological features (head_feats) and its auxiliaries (all concatenated as list in aux_nodes).
    This methods works for both verbal and nominal predicates.
    '''
    feats = defaultdict(str)
    agreement_feats = {}
    subj_ids = [child['id'] for child in children if child['deprel'] in {'nsubj', 'expl'}] # get the ids of the subjects
    if subj_ids:
        subj_id = min(subj_ids) # take the id of the first subject
        first_aux_id = min([child['id'] for child in aux_nodes]) # take the id of the first auxiliary
        if first_aux_id < subj_id: # if the first auxiliary is before the first subject (subject aux inversion)
            if any([child['form'] == '?' for child in children]): # if there is a question mark in the sentence, assume it's a question
                feats['Mood'] = 'Int'
            else:
                # subject inversion is most likely a question, but it can also signify conditionality or can be done for pragmatic reasons. The annotator decides.
                response = utils.get_response(['q', 'c', 'n'],
                                        f'Does the word "{head["form"]}" head a question in the sentence "{parse_tree.metadata["text"]}"\nq - question, c - conditional, n - NOTA',
                                              sent_num)
                if response == 'q':
                    feats['Mood'] = 'Int'
                elif response == 'c':
                    feats['Mood'] = 'Cnd'
                elif response == 'n':
                    pass

    aux_lemmas = {aux['lemma'] for aux in aux_nodes} # get the lemmas of the auxiliaries
    if verb:
        if 'to' in aux_lemmas: # if there is an infinitive marker, set the verb form to infinitive
            feats['VerbForm'] = 'Inf'
        else: # if there is no infinitive marker, set the verb form to finite
            feats['VerbForm'] = 'Fin'
    aux_lemmas.discard('to')

    # setting the polarity of the main verb, assuming that there is no modality that require internal feature structure.
    # The polarity may be deleted again later if there are modal auxiliaries.
    if 'not' in aux_lemmas: # if there is a negation marker, set the polarity to negative
        feats['Polarity'] = 'Neg'
    else: # if there is no negation marker, set the polarity to positive
        feats['Polarity'] = 'Pos'
    # aux_lemmas.discard('not')

    if 'do' in aux_lemmas:
        if not verb: 
            raise NotImplementedError('a noun with "do"?!')

        do_node = [aux for aux in aux_nodes if aux['lemma'] == 'do'] # get the node with the lemma 'do'
        assert len(do_node) == 1
        do_node = do_node[0]
        if 'Tense' in do_node['feats']:  # imperatives don't have tense
            feats['Tense'] = do_node['feats']['Tense']  # set the tense to the tense of the 'do' node
        agreement_feats = get_agreement_feats(do_node)
    aux_lemmas.discard('do')

    if 'be' in aux_lemmas:
        be_nodes = [aux for aux in aux_nodes if aux['lemma'] == 'be'] # get the nodes with the lemma 'be'

        if len(be_nodes) == 1: # if there is only one 'be' node
            if verb:
                if head_feats['VerbForm'] == 'Ger' or ('Tense' in head_feats and (head_feats['VerbForm'], head_feats['Tense']) == ('Part', 'Pres')): # if the verb form is gerund or the verb form is participle and the tense is present
                    feats['Aspect'] = 'Prog'
                elif 'Tense' in head_feats and (head_feats['VerbForm'], head_feats['Tense']) == ('Part', 'Past'): # if the verb form is participle and the tense is past
                    feats['Voice'] = 'Pass'
                else:
                    raise ValueError('untreated be-type aux')
            higher_be = be_nodes[0] # take the only 'be' node

        elif len(be_nodes) == 2:
            feats['Aspect'] = 'Prog' 
            if verb:
                feats['Voice'] = 'Pass'
            higher_be = [node for node in be_nodes if not node['form'].endswith('ing')][0] # take the 'be' node that is not a gerund

        else:
            raise NotImplementedError('too many be-nodes?')

        if 'Voice' not in feats and verb: # if the voice is not set and the head is a verb, set the voice to active
            feats['Voice'] = 'Act'

        # if there are no auxiliaries left, copy the remaining TAM feats from the "higher" auxiliary
        if not aux_lemmas-{'be', 'not'} and feats.get('VerbForm', None) != 'Inf': # if there are no auxiliaries left and the verb form is not infinitive
            if 'Tense' in higher_be['feats']: # if the 'be' node has a tense feature, copy the tense of the 'be' node
                feats['Tense'] = higher_be['feats']['Tense']
            if not verb: # if the head is not a verb, copy the mood and the verb form of the 'be' node
                if 'Mood' not in feats and 'Mood' in higher_be['feats']: # if the mood is not set and the 'be' node has a mood feature, copy it
                    feats['Mood'] = higher_be['feats']['Mood']
                if 'VerbForm' not in feats and 'VerbForm' in higher_be['feats']:  # if the verb form is not set and the 'be' node has a verb form feature, copy it
                    feats['VerbForm'] = higher_be['feats']['VerbForm']
            agreement_feats = get_agreement_feats(higher_be)
    aux_lemmas.discard('be')

    if 'get' in aux_lemmas: 
        get_node = [aux for aux in aux_nodes if aux['lemma'] == 'get'][0] # get the 'get' node
        assert 'pass' in get_node['deprel']
        feats['Voice'] = 'Pass'

        if not aux_lemmas-{'get', 'not'}: # if there are no auxiliaries left except for get and not
            feats['Tense'] = get_node['feats'].get('Tense') # copy the tense of the 'get' node
            feats['VerbForm'] = get_node['feats'].get('VerbForm') # copy the verb form of the 'get' node
            agreement_feats = get_agreement_feats(get_node)
    aux_lemmas.discard('get')

    if 'have' in aux_lemmas:
        if not verb or (head_feats['VerbForm'], head_feats['Tense']) == ('Part', 'Past') or (higher_be['feats']['VerbForm'], higher_be['feats']['Tense']) == ('Part', 'Past'): # if the head is not a verb or the verb form is participle and the tense is past
            feats['Aspect'] += ';Perf'
        else:
            raise NotImplementedError('untreated have-type aux')

        # if there are no auxiliaries left, copy the remaining TAM feats from the "higher" auxiliary
        if not aux_lemmas-{'have', 'not'} and feats.get('VerbForm', None) != 'Inf': # if there are no auxiliaries left and the verb form is not infinitive
            have_node = [aux for aux in aux_nodes if aux['lemma'] == 'have']
            assert len(have_node) == 1
            have_node = have_node[0]
            if 'Tense' in have_node['feats']:
                feats['Tense'] = have_node['feats']['Tense'] # copy the tense of the 'have' node
            if 'VerbForm' in have_node['feats']:
                feats['VerbForm'] = have_node['feats']['VerbForm']
            agreement_feats = get_agreement_feats(have_node)
    aux_lemmas.discard('have')

    if 'will' in aux_lemmas:
        feats['Tense'] = 'Fut'
    aux_lemmas.discard('will')

    if 'would' in aux_lemmas:
        # Would stands for both conditional and FITP. Let the annotator decide.
        response = utils.get_response(['c', 'f'],
                                f'what does the "would" stand for in this sentence:\n"{parse_tree.metadata["text"]}"\nhead:"{head["form"]}"\nchildren:"{" ".join([child["form"] for child in children])}"\nc - conditional, f - future in the past',
                                      sent_num)
        if response == 'c':
            feats['Mood'] += ';Cnd'
        else:
            feats['Tense'] = 'Past'
            feats['Aspect'] += ';Prosp'
    aux_lemmas.discard('would')

    # treatment of modality
    if aux_lemmas&{'can','could','may','shall','should','must','might'}:

        if 'could' in aux_lemmas:
            response = utils.get_response(['c', 'p'],
                                    f'what does the "could" stand for in this sentence:\n"{parse_tree.metadata["text"]}"\nhead:"{head["form"]}"\nchildren:"{" ".join([child["form"] for child in children])}"\nc - conditional, p - past',
                                          sent_num)
            if response == 'c':
                feats['Mood'] += ';Cnd'
            else:
                feats['Tense'] = 'Pst'

        for lemma in aux_lemmas&{'can','could','may','shall','should','must','might'}: # look up in modalities
            modality = modalities[lemma]
            aux_lemmas.discard(lemma)

        if 'not' in aux_lemmas: # if there is a negation marker, set the modality to negative and remove the Polarity feature
            modality = f'neg({modality})'
            del feats['Polarity']
        aux_lemmas.discard('not')

        feats['Mood'] += ';' + modality  # add the modality to the mood
        feats['Mood'] = feats['Mood'].strip(';')  # clean up the mood

    else:
        aux_lemmas.discard('not')

    if aux_lemmas:
        raise NotImplementedError(f'untreated auxiliaries. their lemmas: {aux_lemmas}')

    feats = {k: v.strip(';') for k, v in feats.items() if v}

    return feats, agreement_feats


def copy_feats(ms_feats, morpho_feats, values):
    '''
    copies features from morpho_feats to ms_feats only is they do not exist in morpho_feats.
    '''
    for value in values:
        ms_feats[value] = ms_feats.get(value, morpho_feats.get(value, None))
    return ms_feats


def set_nodes(nodes):
    '''
    conllu.Token is not hashable so sets consist of ids
    '''
    return {node['id'] for node in nodes}


def combine_fixed_nodes(head, fixed_children):
    '''
    In cases where several function words are combined to one meaning (e.g., because of, more then) they are tagged with
     a 'fixed' deprel and are combined to one temporary lemma to look for in the relevant map in 'eng_relations.py'.
    '''
    if not fixed_children:
        return head['lemma']

    l = [head] + fixed_children
    l.sort(key=lambda node: node['id'])
    return ' '.join([node['lemma'] for node in l])


def apply_grammar(head: conllu.Token, children: List[conllu.Token], sent_num):
    '''
    The main method combining functional children to create the morpho-syntactic features of head.
    '''

    children = [child for child in children if not child['deprel'] in {'parataxis', 'reparandum', 'punct'}] # remove punctuation and parataxis and reparandum

    fixed_children = [child for child in children if child['deprel'] == 'fixed']
    head['fixed lemma'] = combine_fixed_nodes(head, fixed_children) # combine the fixed nodes to one lemma for further processing
    children = [child for child in children if child['deprel'] != 'fixed'] # remove the fixed nodes from the children

    added_nodes = []

    verb = head['upos'] in VERBAL
    noun = head['upos'] in NOMINAL

    if verb: # only if the head is not a verb, copy the existing features to ms_feats
        head['ms feats'] = {}
    else:
        head['ms feats'] = deepcopy(head['feats'])

    # if there are auxiliaries "consume" them to change head's feats
    TAM_nodes = [child for child in children if child['upos'] in {'AUX', 'PART'} and child['lemma'] != "'s"] # consider all aux and part nodes, except for "'s"
    if TAM_nodes:
        ms_feats, agreement_feats = get_nTAM_feats(TAM_nodes, head['feats'], verb=verb, sent_num=sent_num)
        if head[('ms feats')] is None and ms_feats:
            head['ms feats'] = {}
        head['ms feats'].update(ms_feats) # update the head's features with the features of the auxiliaries

        if not head['ms feats'].get('Mood', None): head['ms feats']['Mood'] = 'Ind' #set Mood to Ind by default
        if not head['ms feats'].get('Polarity', None): head['ms feats']['Polarity'] = 'Pos' #set Polarity to Pos by default
        if not head['ms feats'].get('VerbForm', None): head['ms feats']['VerbForm'] = 'Fin' #set VerbForm to Fin by default

    # if there are cases or conjunctures "consume" them as well
    # the last condition is complicated to exclude infinitive "to" while allowing case "'s"
    relation_nodes = [child for child in children if
                      (child['deprel'] in {'case', 'mark', 'cc'}
                      or child['lemma'] in case_feat_map)
                      and (child['upos'] != 'PART' or child['lemma'] == "'s")
                      and 'subj' not in child['deprel']]
    if relation_nodes:
        to_update = get_relation_feats(relation_nodes, verb=verb, clause=head['deprel'] in clausal_rels)
        if to_update and not head['ms feats']:
            head['ms feats'] = to_update
        else:
            head['ms feats'].update(to_update)

    # make sure we did not use the same node twice
    assert not set_nodes(TAM_nodes) & set_nodes(relation_nodes)
    children = [node for node in children if node not in relation_nodes + TAM_nodes] # remove the auxiliaries and the relations from the children

    if verb:
        # copy values from the morphological feats if they were not set by now
        head['ms feats'] = copy_feats(head['ms feats'], head['feats'], ['Mood','Tense','Aspect','Voice','VerbForm','Polarity'])

        # set default values for feats underspecified in UD
        if not head['ms feats'].get('Voice', None): head['ms feats']['Voice'] = 'Act'
        if not head['ms feats'].get('Polarity', None): head['ms feats']['Polarity'] = 'Pos'

        # not sure it's needed. eng is not pro-drop so there always should be an nsubj.
        if head['ms feats']['VerbForm'] == 'Fin' and 'nsubj' not in ''.join([child['deprel'] for child in children]):
            abstract_nsubj = create_abstract_nsubj(head, TAM_nodes) # create an abstract subject node if there is no subject
            if abstract_nsubj:
                added_nodes.append(abstract_nsubj)
        rel_subj = [child for child in children if child['upos']=='PRON' and child['deprel']=='nsubj' and child['feats'].get('PronType', None)=='Rel']
        if rel_subj:
            rel_subj = rel_subj[0]
            rel_subj['ms feats'] = deepcopy(rel_subj['feats'])
            try:
                feats = agreement_feats
            except NameError:
                feats = head['feats']
            if 'Number' in feats:
                rel_subj['ms feats']['Number'] = feats['Number']
            if 'Person' in feats:
                rel_subj['ms feats']['Person'] = feats['Person']

    elif noun or head['upos'] in {'ADV', 'ADJ'}:
        # treat determiners
        det_nodes = [child for child in children if child['deprel'] == 'det']
        if det_nodes:
            assert len(det_nodes) == 1 # there should only be one determiner
            det_node = det_nodes[0]
            children = [node for node in children if node != det_node]
            try:
                det_features = dict(determiners[det_node['lemma']])
                for feature, value in det_features.items():
                    head['ms feats'][feature] = value
                    if det_node['lemma'] == 'another':
                        children = [det_node] + children
            except KeyError:
                # print(f'a non treated determiner: "{det_node["lemma"]}"')  # overlooked determiners
                children = [det_node] + children

        if head['upos'] in {'ADV', 'ADJ'} and children:
            child_lemmas = [child['lemma'] for child in children]
            if 'no' in child_lemmas:
                if not head['ms feats']:
                    head['ms feats'] = {}
                head['ms feats']['Polarity'] = 'Neg'
            if 'more' in child_lemmas: # if there is a 'more' node, set the degree to comparative
                if not head['ms feats']:
                    head['ms feats'] = {}
                head['ms feats']['Degree'] = 'Cmp'
            elif 'most' in child_lemmas: # if there is a 'most' node, set the degree to superlative
                if not head['ms feats']:
                    head['ms feats'] = {}
                head['ms feats']['Degree'] = 'Sup'
            children = [node for node in children if node['lemma'] not in {'more', 'most'}] # remove the 'more' and 'most' nodes from the children

    if head['ms feats']: # clean up the ms_feats by removing None values
        head['ms feats'] = {k: v for k, v in head['ms feats'].items() if v}

    for child in children:
        if is_content(child, sentence=parse_tree.metadata['text']) and not child.get('ms feats', None): # if the child is a content node and the ms_feats are not set
            ms_feats = deepcopy(child['feats']) # copy the features from the child's feats
            if ms_feats is None: # if the child has no feats, set the feats to an separator
                ms_feats = '|'
            child['ms feats'] = ms_feats

    # del head['fixed lemma']
    if not is_content(head, sentence=parse_tree.metadata['text']) and not all([child['upos']=='PUNCT' for child in children]):
        print(f'seems like there is a function node with children.\ncheck lemma "{head["lemma"]}" in sentence:')
        print(parse_tree.metadata['text'])
        del head['ms feats']

    return added_nodes


def get_where_to_add(added_nodes, id2idx): # get where to add the abstract nsubj, right now before the verb, might change to after
    res = []
    for node in added_nodes:
        idx = int(node['id'])
        if idx == 0:
            res.append(-1)
        else:
            res.append(id2idx[idx])
    return res

def order_alphabetically(feats):
    if isinstance(feats, str):
        assert feats == '|'
        return feats
    elif isinstance(feats, dict):
        feats = [f'{key}={value}' for key, value in feats.items()]
        feats = sorted(feats)
        return '|'.join(feats)
    else:
        assert feats is None
        return feats


def remove_fixed_function_nodes(parse_list):
    for node in parse_list:
        if node['deprel'] == 'fixed':
            head = [n for n in parse_list if n['id'] == node['head']][0]
            if head['deprel'] == 'fixed':
                head = [n for n in parse_list if n['id'] == head['head']][0]
            if head['ms feats'] is None:
                node['ms feats'] = None


decisions = []  # this is outside of the main loop to be accessible to methods in utils
if os.path.isfile(r'C:\Users\omer\Documents\university\compsci\phd\research\msud-docs\src\english\responses.pkl'):
    with open(r'C:\Users\omer\Documents\university\compsci\phd\research\msud-docs\src\english\responses.pkl', 'rb') as f:
        decisions = pickle.load(f)
new_decisions = []
if __name__ == '__main__':
    split = 'train'
    # filepath = os.path.join(ud_dir, lang, bank, splits[bank]['test'])
    # out_path = os.path.join('UD+', lang, bank, 'test.conllu')
    filepath = fr'C:\Users\omer\Documents\university\compsci\phd\research\morpho-syntax\UD\eng\EWT\en_ewt-ud-{split}.conllu'
    out_path = fr'C:\Users\omer\Documents\university\compsci\phd\research\msud-docs\data\english\en_ewt-msp-{split}.conllu'
    with open(filepath, encoding='utf8') as f:
        parse_trees = list(conllu.parse_tree_incr(f))
        # parse_trees = [sent for sent in parse_trees if sent.metadata['sent_id'].split('_')[1] not in excluded_genres]
    with open(filepath, encoding='utf8') as f:
        parse_lists = list(conllu.parse_incr(f))
        # parse_lists = [sent for sent in parse_lists if sent.metadata['sent_id'].split('_')[1] not in excluded_genres]

    assert len(parse_lists) == len(parse_trees)
    with open(out_path, 'w', encoding='utf8') as outfile:
        w = 0
        for i in range(len(parse_trees)): # iterate over the sentences
            if i == 10000:
                break
            parse_tree = parse_trees[i]
            assert parse_tree.metadata.get('text', None) is not None
            parse_list: conllu.TokenList = parse_lists[i]

            if any([node['misc'] and 'Promoted' in node['misc'] for node in parse_list]):
                print(f'sentence {i} has a promoted function word. skipping.')
                continue
            if any([':outer' in node['deprel'] for node in parse_list]):
                print(f'sentence {i} has a has an outer subject. skipping.')
                continue

            id2idx = {token['id']:i for i, token in enumerate(parse_list) if isinstance(token['id'], int)}
            idx2id = [token['id'] if isinstance(token['id'], int) else None for token in parse_list]

            heads = utils.span(parse_tree)
            assert utils.verify_span(heads)
            to_add = []
            try:
                for head, children in heads[::-1]:
                    head: conllu.Token = parse_list[id2idx[head]]
                    if head['lemma']=='ago' and head['upos']=='ADV':
                        raise ValueError(f'skipping sentence {i} due to "ago" issue.')
                    children = [parse_list[id2idx[child]] for child in children]

                    try:
                        assert is_content(head, parse_tree.metadata['text']), f"a function node with children occurred in {parse_tree.metadata['sent_id']}: {head['id']}, {head['form']}, {head['upos']}"
                    except AssertionError:
                        # print('assertion failed.')
                        print(f"a function node with children occurred in {parse_tree.metadata['sent_id']}: {head['id']}, {head['form']}, {head['upos']}")

                    added_nodes = apply_grammar(head, children, i)
                    if added_nodes:
                        added_idxs = get_where_to_add(added_nodes, id2idx)
                        to_add += list(zip(added_nodes, added_idxs))
            except ValueError as e:
                print(e)
                continue
            except NotImplementedError as e:
                print('skipping a sentence that failed to apply grammar.')
                print(f'sentence {i} got an error: {e}.')
                print(f'the sentence: {parse_tree.metadata["text"]}')
                continue

            for added_node in to_add[::-1]:
                node, idx = added_node
                parse_list.insert(idx + 1, node)

            try:
                for node in parse_list:
                    if not is_content(node, parse_tree.metadata['text']):
                        node['ms feats'] = None
                    else:
                        # setting ms-feats for content nodes that were not dealt with earlier
                        if not node.get('ms feats', None):
                            ms_feats = deepcopy(node['feats'])
                            if ms_feats is None:
                                ms_feats = '|'
                            node['ms feats'] = ms_feats
                        # function nodes end up with empty ms-feats
                        # else:
                        #     # node['ms feats'] = node.get('ms feats', None)
                        #     assert node['ms feats']

                        # sort alphabetically the MS features of all nodes
                        node['ms feats'] = order_alphabetically(node['ms feats'])
                    if 'fixed lemma' in node:
                        del node['fixed lemma']
            except ValueError as e:
                print(e)
                continue

            remove_fixed_function_nodes(parse_list)
            is_ok = utils.verify_treeness(parse_list)
            if not is_ok:
                utils.get_response(['y','n'],
                                   f'The following sentence is probably off. Should we just skip it? (y/n)\n{parse_list.metadata["text"]}',
                                   i)

            to_write = parse_list.serialize()
            outfile.write(to_write + '\n')
            w += 1
