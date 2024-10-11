import re

PROPORTION = 0.9


def _is(val):
    '''Repere les codes SIREN'''
    if not isinstance(val, str):
        return False
    val = val.replace(' ', '')
    if not bool(re.match(r'^[0-9]{9}$', val)):
        return False
    # Vérification par clé propre aux codes siren
    cle = 0
    pair = False
    for x in val:
        y = int(x) * (1 + pair)
        cle += y // 10 + y % 10
        pair = not pair
    return cle % 10 == 0
