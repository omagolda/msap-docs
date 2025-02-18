
'''
Mappings from prepositions and conjunctions to relation features.
Either arg-pred relation, i.e. case, or pred-pred relation, i.e. marker.
The final list should be updated according to the mapping done by Dan Zeman in this link: https://docs.google.com/spreadsheets/d/1--AkGor1-yQLv_BGnnXYQfekBQvMq7u7/edit?gid=1264268804#gid=1264268804
Whatever adposition or conjunction that can't be mapped to anything on the list, should appear as is as the value of the
relevant feature, transliterated to Latin letter if not already.
'''

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
case_feat_map = {k: v if v else k for k,v in case_feat_map.items()}
