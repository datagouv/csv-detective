from os.path import dirname, join
import re

PROPORTION = 1

with open(join(dirname(__file__), 'iso_country_code_alpha2.txt'), 'r') as iofile:
    liste_pays = iofile.read().split('\n')
liste_pays = set(liste_pays)


def _is(val):
    '''Renvoie True si val peut etre un code iso pays alpha-2, False sinon'''
    if not isinstance(val, str) or not bool(re.match(r'[A-Z]{2}$', val)):
        return False
    return val in liste_pays
