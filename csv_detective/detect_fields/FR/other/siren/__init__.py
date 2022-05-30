from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.9


def _is(val):
    '''Repere les codes SIREN'''
    val = val.replace(' ', '')
    regex = r'^[0-9]{9}$'
    if not bool(re.match(regex, val)):
        return False
    # Vérification par clé propre aux codes siren
    cle = 0
    pair = False
    for x in val:
        y = int(x) * (1 + pair)
        cle += y // 10 + y % 10
        pair = not pair
    return cle % 10 == 0
