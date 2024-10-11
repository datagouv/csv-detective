from os.path import dirname, join
import re

PROPORTION = 1

with open(join(dirname(__file__), 'iso_country_code_numeric.txt'), 'r') as iofile:
    liste_pays = iofile.read().split('\n')
liste_pays = set(liste_pays)


def _is(val):
    '''Renvoie True si val peut etre un code iso pays numerique, False sinon'''
    if not isinstance(val, str) or not bool(re.match(r'[0-9]{3}$', val)):
        return False
    return val in liste_pays
