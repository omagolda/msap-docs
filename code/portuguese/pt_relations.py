'''
Mappings from prepositions and conjunctions to relation features.
Either arg-pred relation, i.e. case, or pred-pred relation, i.e. marker.
The final list should be updated according to the mapping done by Dan Zeman in this link: https://docs.google.com/spreadsheets/d/1--AkGor1-yQLv_BGnnXYQfekBQvMq7u7/edit?gid=1264268804#gid=1264268804
Whatever adposition or conjunction that can't be mapped to anything on the list, should appear as is as the value of the
relevant feature, transliterated to Latin letter if not already.
'''

case_feat_map = {
'de': 'Gen',
'em':'Ine',
'a':'Lat',
'para':'Lat',
'por':'Pro',
'com':'Com',
'como':'Sem',
'entre':'Int',
'sobre':'Sup',
'até':'Ttr',
'sem':'Abe',
'segundo':'Quo',
'desde':'Teg',
'após':'Pst',
'contra':'Adv',
'durante':'Dur',
#'que':'TBD-que',
'sob':'Sub',
'conforme':'Quo',
'ante':'Ant',
'perante':'Ant',
'fora':'Ext',
'versus':'Adv',
'menos':'Exc',
'senão':'Exc',
'mediante':'Ins',
'exceto':'Exc',
'via':'Pro',
'pró':'Ben',
'dado':'Cns',
'x':'Dis',
'visto':'Reas',
'em vez de':'Sbs',
'desde que':'Cnd',
'se':'Cnd',
'quando':'Temp',
'ou':'Disj',
'e':'Conj',
'porém':'Advs',
'porque':'Cau',
'enquanto':'Cmt'
}


case_feat_map = {k: v if v else k for k,v in case_feat_map.items()}
