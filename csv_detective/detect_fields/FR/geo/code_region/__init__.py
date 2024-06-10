from frformat import CodeRegion

PROPORTION = 1


def _is(val):
    '''Renvoie True si val peut être un code_région, False sinon'''
    return CodeRegion.is_valid(val)
