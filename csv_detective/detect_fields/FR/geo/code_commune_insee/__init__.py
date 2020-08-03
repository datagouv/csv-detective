from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1
f = open(join(dirname(__file__), 'code_commune_insee.txt'), 'r')
codes_insee = f.read().split('\n')
f.close()


def _is(val):
    '''Renvoie True si val peut être un code commune INSEE, False sinon'''
    # test sur la longueur
    if len(val) != 5:
        return False

    # vérification de cohérence avec prise en compte corse 2A/2B et DOM (971-976 sauf 975)
    regex = r'^([01345678][0-9]{4}|2[AB1-9][0-9]{3}|9([0-5][0-9]{3}|7[12346][0-9]{2}))$'
    if not bool(re.match(regex, val)):
        return False

    return val in codes_insee
