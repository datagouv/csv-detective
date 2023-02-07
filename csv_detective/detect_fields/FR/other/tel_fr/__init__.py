import re

PROPORTION = 0.7


def _is(val):
    '''Repère les numeros de telephone francais'''

    if len(val) < 10:
        return False

    val = val.replace('.', '').replace('-', '').replace(' ', '')

    regex = r'^(0|\+33|0033)?[0-9]{9}$'
    match_1 = bool(re.match(regex, val))
    return match_1
