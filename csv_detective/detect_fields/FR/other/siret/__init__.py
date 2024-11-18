import re

PROPORTION = 0.8


def _is(val):
    '''Détection des identifiants SIRET (SIRENE)'''
    if not isinstance(val, str):
        return False
    val = val.replace(' ', '')
    if not bool(re.match(r'^[0-9]{14}$', val)):
        return False

    # Vérification par clé de luhn du SIREN
    cle = 0
    pair = False
    for x in val[:9]:
        y = int(x) * (1 + pair)
        cle += y // 10 + y % 10
        pair = not pair
    if cle % 10 != 0:
        return cle % 10 == 0

    # Vérification par clé de luhn du SIRET
    cle = 0
    pair = len(val) % 2 == 0
    for x in val:
        y = int(x) * (1 + pair)
        cle += y // 10 + y % 10
        pair = not pair
    return cle % 10 == 0
