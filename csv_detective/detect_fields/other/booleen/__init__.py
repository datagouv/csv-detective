PROPORTION = 1


def _is(val):
    '''Détection les booléens'''
    liste_bool = [
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
    ]
    return val.lower() in liste_bool
