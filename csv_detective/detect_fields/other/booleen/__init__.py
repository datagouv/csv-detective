PROPORTION = 1
liste_bool = {
    '0',
    '1',
    'vrai',
    'faux',
    'true',
    'false',
    'oui',
    'non',
    'yes',
    'no',
    'y',
    'n',
    'o'
}


def _is(val):
    '''Détection les booléens'''
    return isinstance(val, str) and val.lower() in liste_bool
