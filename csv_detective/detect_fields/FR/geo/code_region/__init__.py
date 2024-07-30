from frformat import CodeRegion

PROPORTION = 1

_code_region = CodeRegion()


def _is(val):
    '''Renvoie True si val peut être un code_région, False sinon'''
    return _code_region.is_valid(val)
