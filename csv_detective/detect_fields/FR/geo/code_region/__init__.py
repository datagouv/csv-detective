
PROPORTION = 1
liste_regions = {
    '01',
    '02',
    '03',
    '04',
    '06',
    '11',
    '24',
    '27',
    '28',
    '32',
    '44',
    '52',
    '53',
    '75',
    '76',
    '84',
    '93',
    '94'
}


def _is(val):
    '''Renvoie True si val peut être un code_région, False sinon'''
    return val in liste_regions
