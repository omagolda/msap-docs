import os
import conllu
import utils
from typing import List
from copy import deepcopy
from collections import defaultdict
from pt_relations import case_feat_map

VERBAL = {'VERB'}
NOMINAL = {'NOUN', 'PROPN', 'PRON', 'NUM'}
clausal_rels = {'conj','csubj','xcomp','ccomp','advcl','acl','advcl:relcl','acl:relcl','ccomp:speech','csubj:outer','csubj:pass'}
determiners = {'ambos':('Definite','Ind'), 'aquele':('Dem','Dist'), 'cada':('Definite','Ind'), 'certo':('Definite','Ind'), 'demais':('Definite','Ind'), 'esse':('Dem','Prox'), 'este':('Dem','Prox'), 'mais':('Definite','Ind'), 'menos':('Definite','Ind'), 'o':('Definite','Def'), 'outro':('Definite','Ind'), 'qualquer':('Definite','Ind'), 'quanto':('Definite','Ind'), 'tanto':('Definite','Ind'), 'um':('Definite','Ind'), 'vários':('Definite','Ind')}
modalities = {'dever':'Nec','precisar':'Nec','necessitar':'Nec','ter':'Nec','haver':'Nec','poder':'Pot'}
negation_markers = {'não', 'nunca', 'jamais', 'sem','nem'}

def combine_fixed_nodes(head, fixed_children):
    '''
    In cases where several function words are combined to one meaning (e.g., because of, more then) they are tagged with
     a 'fixed' deprel and are combined to one temporary lemma to look for in the relevant map in 'eng_relations.py'.
    '''
    if not fixed_children:
        return head['lemma']

    l = [head] + fixed_children
    l.sort(key=lambda node: node['id'])
    #print(' '.join([node['lemma'] for node in l]))
    return ' '.join([node['lemma'] for node in l])

def apply_grammar(head: conllu.Token, children: List[conllu.Token]):
    '''
    The main method combining functional children to create the morpho-syntactic features of head.
    '''

    children = [child for child in children if not child['deprel'] in {'parataxis', 'reparandum'}] # remove punctuation and parataxis and reparandum

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
    #TAM_nodes = [child for child in children if child['upos'] in {'AUX', 'PART'} and child['lemma'] != "'s"] # consider all aux and part nodes, except for "'s"


    #Treat questions
    if any([child['form'] == '?' for child in children]): # if there is a question mark in the sentence, assume it's a question
        if head.get('ms feats') is None:  # Ensure ms_feats is initialized
            head['ms feats'] = {}
        head['ms feats']['Mood'] = 'Int'

    TAM_nodes = [child for child in children if child['upos'] in {'AUX'}]  # consider all aux nodes
    negation_nodes = [child for child in children if child['upos'] == 'ADV' and child['lemma'] in negation_markers]

    if TAM_nodes or negation_nodes:  # Check for TAM or negation nodes

        if head.get('ms feats') is None:
            head['ms feats'] = {}

        # Safely update ms_feats without causing errors
        new_feats = get_nTAM_feats(TAM_nodes, head['feats'], verb=verb)

        if new_feats:
            head['ms feats'].update(new_feats)  # update the head's features with the features of the auxiliaries

        if negation_nodes:
            head['ms feats']['Polarity'] = 'Neg'  # Set Polarity to 'Neg' if a negation marker is found

        # Set defaults if necessary
        if not head['ms feats'].get('Mood', None):
            head['ms feats']['Mood'] = 'Ind'  # set Mood to Ind by default
        if not head['ms feats'].get('Polarity', None):
            head['ms feats']['Polarity'] = 'Pos'  # set Polarity to Pos by default
        if not head['ms feats'].get('VerbForm', None):
            head['ms feats']['VerbForm'] = 'Fin'  # set VerbForm to Fin by default


    # if there are cases or conjunctures "consume" them as well
    # the last condition is complicated to exclude infinitive "to" while allowing case "'s"
    relation_nodes = [child for child in children if
                      (child['deprel'] in {'case', 'mark', 'cc'})
                      or (child['lemma'] in case_feat_map and child['deprel'] not in ['nsubj','nsubj:pass'])]
    if relation_nodes:
        to_update = get_relation_feats(relation_nodes, verb=verb, clause=head['deprel'] in clausal_rels)
        if to_update and not head['ms feats']:
            head['ms feats'] = to_update
        else:
            head['ms feats'].update(to_update)

    handle_modal_verbs(head, children, head['ms feats'], modalities, clausal_rels, negation_markers)

    # make sure we did not use the same node twice
    assert not set_nodes(TAM_nodes) & set_nodes(relation_nodes)
    children = [node for node in children if node not in relation_nodes + TAM_nodes] # remove the auxiliaries and the relations from the children

    #for child in children:
    #    print(child)
    #    print(child['deprel'])

    if verb:
        # copy values from the morphological feats if they were not set by now
        head['ms feats'] = copy_feats(head['ms feats'], head['feats'], ['Mood','Tense','Aspect','Voice','VerbForm','Polarity'])

        # set default values for feats underspecified in UD
        if not head['ms feats'].get('Voice', None): head['ms feats']['Voice'] = 'Act'

        # not sure it's needed. eng is not pro-drop so there always should be an nsubj.
        verbform = ['Fin','Inf','Part','Ger']
        if head['ms feats']['VerbForm'] in verbform and 'nsubj' not in [child['deprel'] for child in children] and 'nsubj:pass' not in [child['deprel'] for child in children]:
            abstract_nsubj = create_abstract_nsubj(head, TAM_nodes) # create an abstract subject node if there is no subject
            if abstract_nsubj:
                added_nodes.append(abstract_nsubj)

    elif noun or head['upos'] in {'ADV', 'ADJ'}:
        # treat determiners

        det_nodes = [child for child in children if child['deprel'] == 'det']        

        if det_nodes:
            # Extract Gender and Number from all determiners
            genders = {det_node['feats'].get('Gender') for det_node in det_nodes if 'feats' in det_node}
            numbers = {det_node['feats'].get('Number') for det_node in det_nodes if 'feats' in det_node}

            # Check agreement in Gender and Number
            if len(genders) > 1:
                print(f"Conflict in Gender among determiners: {genders}")
            if len(numbers) > 1:
                print(f"Conflict in Number among determiners: {numbers}")

            # Ensure ms_feats is initialized
            if head['ms feats'] is None:
                head['ms feats'] = {}

            # If they agree, use the features
            if len(genders) == 1 and len(numbers) == 1:
                head_gender = genders.pop()
                head_number = numbers.pop()

                if head_gender:
                    head['ms feats']['Gender'] = head_gender
                if head_number:
                    head['ms feats']['Number'] = head_number

                # Copy other features from determiners to the head
                for det_node in det_nodes:
                    det_feats = det_node.get('feats', {})
                    for key, value in det_feats.items():
                        if key not in {'Gender', 'Number'}:  # Exclude Gender and Number
                            head['ms feats'][key] = value

            else:
                # Handle disagreement case
                print(f"Disagreement in determiners for head: {head}")

            # Remove determiner nodes from children
            children = [node for node in children if node not in det_nodes]

        #if head['upos'] in {'ADV', 'ADJ'} and children:
        #    child_lemmas = [child['lemma'] for child in children]
        #    if 'more' in child_lemmas: # if there is a 'more' node, set the degree to comparative
        #        head['ms feats']['Degree'] = 'Cmp'
        #    elif 'most' in child_lemmas: # if there is a 'most' node, set the degree to superlative
        #        head['ms feats']['Degree'] = 'Sup'
        #    children = [node for node in children if node['lemma'] not in {'more', 'most'}] # remove the 'more' and 'most' nodes from the children

        # if head['upos'] in {'ADV', 'ADJ'} and children:
        #     child_lemmas = [child['lemma'] for child in children]
        #     print(child_lemmas)
        #     child_det = [child for child in children if child['lemma'] == 'o' and child['deprel'] == 'det']

        #     if head.get('ms feats') is None:
        #         head['ms feats'] = {}  # Ensure ms_feats is a dictionary

        #     # Handle "mais" and "menos" cases
        #     if 'mais' in child_lemmas or 'menos' in child_lemmas:
        #         if child_det:  # If "o" is present as a determiner
        #             head['ms feats']['Degree'] = 'Sup'
        #         else:  # If "o" is not present
        #             head['ms feats']['Degree'] = 'Cmp'
        #         # Remove "mais" and "menos" nodes from children
        #         children = [node for node in children if node['lemma'] not in {'mais', 'menos'}]

        #     # Handle "maior", "menor", "melhor", "pior" cases
        #     elif head['lemma'] in {'maior', 'menor', 'melhor', 'pior'}:
        #         if child_det:  # If "o" is present as a determiner
        #             head['ms feats']['Degree'] = 'Sup'
        #         else:  # If "o" is not present
        #             head['ms feats']['Degree'] = 'Cmp'

    if head['ms feats']: # clean up the ms_feats by removing None values
        head['ms feats'] = {k: v for k, v in head['ms feats'].items() if v}

    for child in children:
        if child['upos'] in {'ADV', 'ADJ', 'INTJ', 'DET'} | VERBAL | NOMINAL and not child.get('ms feats', None): # if the child is a content node and the ms_feats are not set
            ms_feats = deepcopy(child['feats']) # copy the features from the child's feats
            if ms_feats is None: # if the child has no feats, set the feats to an separator
                ms_feats = '|'
            child['ms feats'] = ms_feats

    del head['fixed lemma']

    return added_nodes

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

def get_rel_feat(word): # try to get the relation feature from the marker feature map, if not - from the case feature map, if not - return the word itself
    return case_feat_map.get(word, word)

def set_nodes(nodes):
    '''
    conllu.Token is not hashable so sets consist of ids
    '''
    return {node['id'] for node in nodes}

def get_nTAM_feats(aux_nodes: List[conllu.Token], head_feats: dict, verb=True) -> dict:
    '''
    generating morpho-syntactic features for a head node based on its own morphological features (head_feats) and its auxiliaries (all concatenated as list in aux_nodes).
    This methods works for both verbal and nominal predicates.
    '''
    feats = defaultdict(str)

    subj_ids = [child['id'] for child in children if child['deprel'] in {'nsubj', 'expl'}] # get the ids of the subjects

    aux_lemmas = {aux['lemma'] for aux in aux_nodes} # get the lemmas of the auxiliaries

    if head_feats is None:
        head_feats = {}


    # Handle auxiliary "ter" or "haver"
    if 'ter' in aux_lemmas or 'haver' in aux_lemmas:
        # Find the auxiliary nodes for "ter" or "haver"
        relevant_aux_nodes = [aux for aux in aux_nodes if aux['lemma'] in {'ter', 'haver'}]

        # Check if there is at least one "ter" or "haver" auxiliary
        for aux_node in relevant_aux_nodes:
            # If the auxiliary verb has a "Tense" feature, transfer it to the head verb's tense
            if 'Tense' in aux_node['feats']:
                feats['Tense'] = aux_node['feats']['Tense']
            if 'Mood' in aux_node['feats']:
                feats['Mood'] = aux_node['feats']['Mood']

            # Add Aspect based on the Tense of "ter" or "haver"
            if head_feats.get('VerbForm') == 'Part' and len(aux_lemmas - {'ter','haver'}) == 0:  # If the head verb is a participle
                if aux_node['feats'].get('Tense') == 'Pres':  # Present tense -> Progressive aspect
                    feats['Aspect'] = 'Prog'
                elif aux_node['feats'].get('Tense') == 'Imp':  # Imperfect tense -> Perfect aspect
                    feats['Aspect'] = 'Perf'
            elif aux_node['feats'].get('Tense') == 'Imp' and len(aux_lemmas - {'ter','haver'}) > 0:
                feats['Aspect'] = 'Perf'


    if 'ser' in aux_lemmas:
        # Get the "ser" nodes
        ser_nodes = [aux for aux in aux_nodes if aux['lemma'] == 'ser']

        if len(ser_nodes) == 1:  # If there is only one "ser" auxiliary
            ser_node = ser_nodes[0]
            if head_feats is None:
                head_feats = {}

            # Check if it's the only auxiliary
            if len(aux_lemmas) == 1:  # "ser" is the only auxiliary
                # Transfer Mood and Tense from the head verb if not already set
                if 'Mood' not in feats and 'Mood' in head_feats:
                    feats['Mood'] = head_feats['Mood']
                if 'Tense' not in feats and 'Tense' in head_feats:
                    feats['Tense'] = head_feats['Tense']

            # Always add 'Voice' as 'Pass' because if head is a participle
            if head_feats.get('VerbForm') == 'Part':
                feats['Voice'] = 'Pass'

        # If there are higher auxiliaries, do not transfer Mood/Tense but still add 'Voice' as 'Pass'
        if len(ser_nodes) > 0 and len(aux_lemmas - {'ser'}) > 0:  # There are other auxiliaries
            if head_feats.get('VerbForm') == 'Part':
                feats['Voice'] = 'Pass'

        # Remove "ser" from aux_lemmas to avoid further processing
        aux_lemmas.discard('ser')


    if 'estar' in aux_lemmas:
        # Get the "estar" nodes
        estar_nodes = [aux for aux in aux_nodes if aux['lemma'] == 'estar']

        if head_feats is None:
            head_feats = {}

        if len(estar_nodes) == 1:  # If there is only one "estar" auxiliary
            estar_node = estar_nodes[0]

            # Check if "estar" is the highest auxiliary (i.e., no other auxiliaries are higher)
            if len(aux_lemmas) == 1:  # "estar" is the only auxiliary
                # Transfer Mood and Tense from the head verb if not already set
                if 'Mood' not in feats and 'Mood' in head_feats:
                    feats['Mood'] = head_feats['Mood']
                if 'Tense' not in feats and 'Tense' in head_feats:
                    feats['Tense'] = head_feats['Tense']

            # Always add 'Aspect' as 'Prog' when head has feat 'Ger'
            if head_feats.get('VerbForm') == 'Ger':
                feats['Aspect'] = 'Prog'

        elif len(estar_nodes) > 1:  # If there are multiple "estar" auxiliaries
            raise NotImplementedError('Too many "estar" auxiliaries detected')

        # If "estar" is not the only auxiliary but is still present, ensure 'Aspect' is 'Prog'
        if len(estar_nodes) > 0 and len(aux_lemmas - {'estar'}) > 0:  # There are other auxiliaries
            if head_feats.get('VerbForm') == 'Ger':
                feats['Aspect'] = 'Prog'

        # Remove "estar" from aux_lemmas to avoid further processing
        aux_lemmas.discard('estar')

    # For the verb 'ir'
    if 'ir' in aux_lemmas:
        ir_nodes = [aux for aux in aux_nodes if aux['lemma'] == 'ir']

        if len(ir_nodes) == 1:  # If there is only one "ir" auxiliary
            ir_node = ir_nodes[0]

            # If "ir" has Tense = Pres and the head has VerbForm = Inf, add Mood = Ind and Tense = Fut
            if ir_node['feats'].get('Tense') == 'Pres' and head_feats.get('VerbForm') == 'Inf':
                feats['Mood'] = 'Ind'  # Set Mood to Indicative
                feats['Tense'] = 'Fut'  # Set Tense to Future

        # If the head has VerbForm = Ger, add Aspect = Prog (Progressive)
            elif head_feats.get('VerbForm') == 'Ger':
                feats['Aspect'] = 'Prog'  # Set Aspect to Progressive

        # If "ir" has Tense = Cnd and the head has VerbForm = Inf, add Mood = Cnd
            if ir_node['feats'].get('Tense') == 'Pres' and head_feats.get('VerbForm') == 'Inf':
                feats['Mood'] = 'Cnd'  # Set Mood to Indicative


        aux_lemmas.discard('ir')  # Remove "ir" from aux_lemmas to avoid further processing

    # For the verb 'vir'
    if 'vir' in aux_lemmas:
        vir_nodes = [aux for aux in aux_nodes if aux['lemma'] == 'vir']

        if len(vir_nodes) == 1:  # If there is only one "vir" auxiliary
            vir_node = vir_nodes[0]

            # If the head has VerbForm = Ger, add Aspect = Prog
            if head_feats.get('VerbForm') == 'Ger':
                feats['Aspect'] = 'Prog'  # Set Aspect to Progressive

        aux_lemmas.discard('vir')  # Remove "vir" from aux_lemmas to avoid further processing


    #if aux_lemmas:
    #    raise ValueError(f'untreated auxiliaries. their lemmas: {aux_lemmas}')

    feats = {k: v.strip(';') for k, v in feats.items() if v}

    return feats

def handle_modal_verbs(head: conllu.Token, children: List[conllu.Token], feats: dict, modalities: dict, clausal_rels: set, negation_markers: set):
    """
    Function to handle Portuguese modal verbs in sentences based on specific clausal relations
    and the modality feature. It checks for negation markers and adds modality to the head's features.
    """
    # Check if the head lemma is in the modalities dictionary and if the head has an appropriate clausal relation
    if head['lemma'] in modalities and any(child['deprel'] in clausal_rels for child in children):
        # Get the corresponding modality from the dictionary
        modality = modalities[head['lemma']]

        # Add the modality to the head's features (Mood)
        if 'Mood' not in feats:
            feats['Mood'] = modality
        else:
            feats['Mood'] += f";{modality}"

        # Check for negation markers in the children
        if any(child['form'] in negation_markers for child in children):
            feats['Mood'] = f"neg({feats['Mood']})"
            if 'Polarity' in feats:
                del feats['Polarity']  # Remove Polarity if negation is present

        # No need to process negation_markers directly in aux_lemmas anymore, as it's handled within the children.

def copy_feats(ms_feats, morpho_feats, values):
    '''
    copies features from morpho_feats to ms_feats only is they do not exist in morpho_feats.
    '''
    for value in values:
        ms_feats[value] = ms_feats.get(value, morpho_feats.get(value, None))
    return ms_feats

def create_abstract_nsubj(head: conllu.Token, auxes: List[conllu.Token]):
    '''
    When the subject is missing but agreement features appear on its head, an abstract node carrying features only is created
    '''
    abstract_nsubj = conllu.Token()
    abstract_nsubj['id'] = head['id'] - 0.9 # to make sure it's between the head and the first child
    abstract_nsubj['form'] = '-' # set all values to '-', but set the head and the deprel
    abstract_nsubj['lemma'] = '-'
    abstract_nsubj['upos'] = '-'
    abstract_nsubj['xpos'] = '-'
    abstract_nsubj['deps'] = '-'
    abstract_nsubj['misc'] = '-'
    abstract_nsubj['head'] = head['id']
    abstract_nsubj['deprel'] = 'nsubj'
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

#Problema: frases como "Choveu ontem."

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
    # Check if feats is None or not a dictionary or string
    if feats is None:
        return ""  # Return an empty string or handle as you prefer

    if isinstance(feats, dict):  # If feats is a dictionary, sort its keys
        # Sort the dictionary keys alphabetically and join them with '|'
        feats = '|'.join(f"{k}={v}" for k, v in sorted(feats.items()))
    elif isinstance(feats, str):  # If feats is a string, split, sort and join
        feats = feats.split('|')
        feats = sorted(feats)
        feats = '|'.join(feats)
    else:
        return ""  # In case feats is neither a dict nor a string

    return feats

if __name__ == '__main__':
    #filepath = os.path.join(ud_dir, lang, bank, splits[bank]['test'])
    filepath = './input/pt_porttinari-ud-train-preprocessed.conllu'
    #out_path = os.path.join('UD+', lang, bank, 'test.conllu')
    out_path = './input/pt_porttinari-ud-train-morph.conllu'
    with open(filepath, encoding='utf8') as f:
        parse_trees = list(conllu.parse_tree_incr(f))
        #parse_trees = [sent for sent in parse_trees if sent.metadata['sent_id'].split('_')[1] not in excluded_genres]
        parse_trees = [sent for sent in parse_trees]
    with open(filepath, encoding='utf8') as f:
        parse_lists = list(conllu.parse_incr(f))
        #parse_lists = [sent for sent in parse_lists if sent.metadata['sent_id'].split('_')[1] not in excluded_genres]
        parse_lists = [sent for sent in parse_lists]

    assert len(parse_lists) == len(parse_trees)
    with open(out_path, 'w', encoding='utf8') as outfile:
        for i in range(len(parse_trees)): # iterate over the sentences
            parse_tree = parse_trees[i]
            parse_list: conllu.TokenList = parse_lists[i]

            id2idx = {token['id']:i for i, token in enumerate(parse_list) if isinstance(token['id'], int)}
            idx2id = [token['id'] if isinstance(token['id'], int) else None for token in parse_list]

            heads = utils.span(parse_tree)
            assert utils.verify_span(heads)
            to_add = []
            for head, children in heads[::-1]:
                head: conllu.Token = parse_list[id2idx[head]]
                children = [parse_list[id2idx[child]] for child in children]
                #skip_lemmas = {'meu', 'teu', 'seu', 'nosso', 'vosso'}
                #children = [
                #    child for child in children 
                #        if not (child['deprel'] == 'det' and child['lemma'] in skip_lemmas)
                #        ]
                added_nodes = apply_grammar(head, children)
                if added_nodes:
                    added_idxs = get_where_to_add(added_nodes, id2idx)
                    to_add += list(zip(added_nodes, added_idxs))

            for added_node in to_add[::-1]:
                node, idx = added_node
                parse_list.insert(idx + 1, node)

            for node in parse_list:
                # setting ms-feats for content nodes that were not dealt with earlier
                if node['upos'] in {'ADJ', 'INTJ'} | VERBAL | NOMINAL and not node.get('ms feats', None): # if the node is a content node and the ms_feats are not set
                    ms_feats = deepcopy(node['feats'])
                    if ms_feats is None:
                        ms_feats = '|'
                    node['ms feats'] = ms_feats
                # function nodes end up with empty ms-feats
                else:
                    node['ms feats'] = node.get('ms feats', None)


                # sort alphabetically the MS features of all nodes
                node['ms feats'] = order_alphabetically(node['ms feats'])
            #assert utils.verify_treeness(parse_list)

            to_write = parse_list.serialize()
            outfile.write(to_write + '\n')