from typing import List, Union
from copy import deepcopy
from src.english.english import decisions, new_decisions
import pickle

def span(parse_tree):
    '''
    creates a list of all node ids that have children (i.e. that are heads) along with their children's ids.
    :return: a list of 2-tuples, each of form (head, list_of_children).
             [(head_id, [child_id, child_id, ...]), (head_id, [child_id, child_id, ...]), ...]
    '''
    res = []
    waiting_list = [parse_tree]
    while waiting_list:
        curr = waiting_list[0]
        if curr.children:
            res.append([curr.token['id'], [child.token['id'] for child in curr.children]])
            waiting_list += curr.children
        waiting_list = waiting_list[1:]
    return res


def verify_span(heads: List[List[Union[List[int], int]]]):
    '''
    verifies that for a given list of heads and children, all heads appear in ascending id order
    :param heads: output of utils.span()
    :return: bool
    '''
    first_head = {}
    first_child = {}
    for i, (head, children) in enumerate(heads):
        first_head[head] = i
        for child in children:
            first_child[child] = i
    for head in first_head:
        if head in first_child and first_head[head] < first_child[head]:
            return False
    return True

def verify_treeness(parse_list):
    '''
    After assignment of ms_feats, making sure that the content nodes still make a tree.
    '''
    parse_list = deepcopy(parse_list)
    new_list = []
    new_ids = {0}
    for node in parse_list:
        node['feats'] = node['ms feats']
        if node['feats']:
            new_list.append(node)
            new_ids.add(node['id'])
    for node in new_list:
        if node['head'] not in new_ids:
            return False
    return True


def get_response(possible_responses, prompt, sent_num):
    '''
    When one construction may serve several features, let the annotator decide which it is.
    '''
    global decisions
    global new_decisions

    if not decisions:
        possible_responses.append('s')  # save and exit
        response = None
        while response not in possible_responses:
            if response:
                print(f'invalid response. options are {possible_responses}.')
            print('##### USER INPUT NEEDED #####')
            response = input(prompt)
            if response == 's':
                response = input('are you sure you want to save and exit? (y/n)')
                if response == 'y':
                    with open(r'C:\Users\omer\Documents\university\compsci\phd\research\msud-docs\src\english\responses.pkl', 'rb') as f:
                        prev_decisions = pickle.load(f)
                    prev_decisions += new_decisions
                    with open(r'C:\Users\omer\Documents\university\compsci\phd\research\msud-docs\src\english\responses.pkl', 'wb') as f:
                        pickle.dump(prev_decisions, f)
                    exit()

        new_decisions.append(response)

    else:
        print(prompt)
        response = decisions.pop(0)
        print(f'going with saved decision. it is *{response}*')
        assert response in possible_responses

    return response
