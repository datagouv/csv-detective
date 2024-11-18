from frformat import CodeRegion, Millesime

PROPORTION = 1

_code_region = CodeRegion(Millesime.LATEST)


def _is(val):
    '''Renvoie True si val peut être un code_région, False sinon'''
    return isinstance(val, str) and _code_region.is_valid(val)
