from frformat import CodeRegion, Options

PROPORTION = 1

_code_region = CodeRegion(Options())


def _is(val):
    '''Renvoie True si val peut être un code_région, False sinon'''
    return _code_region.is_valid(val)
