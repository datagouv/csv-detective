from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.8


def _is(val):
    '''Détection des identifiants SIRET (SIRENE)'''
    val = val.replace(' ', '')
    regex = r'^[0-9]{14}$'
    if not bool(re.match(regex, val)):
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
