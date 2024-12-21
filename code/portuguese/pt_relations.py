'''
Mappings from prepositions and conjunctions to relation features.
Either arg-pred relation, i.e. case, or pred-pred relation, i.e. marker.
The final list should be updated according to the mapping done by Dan Zeman in this link: https://docs.google.com/spreadsheets/d/1--AkGor1-yQLv_BGnnXYQfekBQvMq7u7/edit?gid=1264268804#gid=1264268804
Whatever adposition or conjunction that can't be mapped to anything on the list, should appear as is as the value of the
relevant feature, transliterated to Latin letter if not already.
'''

case_feat_map = {
'de': 'TBD-de_1;TBD-de_2',
'em':'TBD-em',
'a':'TBD-a',
'para':'TBD-para',
'por':'TBD-por',
'com':'TBD-com',
'como':'TBD-como',
'entre':'TBD-entre',
'sobre':'TBD-sobre',
'até':'TBD-até',
'sem':'TBD-sem',
'segundo':'TBD-segundo',
'desde':'TBD-desde',
'após':'TBD-após',
'contra':'TBD-contra',
'durante':'TBD-durante',
'que':'TBD-que',
'sob':'TBD-sob',
'conforme':'TBD-conforme',
'ante':'TBD-ante',
'perante':'TBD-perante',
'fora':'TBD-fora',
'versus':'TBD-versus',
'menos':'TBD-menos',
'senão':'TBD-senão',
'mediante':'TBD-mediante',
'exceto':'TBD-exceto',
'via':'TBD-via',
'pró':'TBD-pró',
'dado':'TBD-dado',
'x':'TBD-x',
'visto':'TBD-visto',
'em vez de':'TBD-em vez de',
'desde que':'TBD-desde que'
}

case_feat_map = {k: v if v else k for k,v in case_feat_map.items()}
