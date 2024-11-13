import re

PROPORTION = 0.7


def _is(val):
    '''Repère les numeros de telephone francais'''
    if not isinstance(val, str):
        return False

    if len(val) < 10:
        return False

    val = val.replace('.', '').replace('-', '').replace(' ', '')

    match_1 = bool(re.match(r'^(0|\+33|0033)?[0-9]{9}$', val))
    return match_1
