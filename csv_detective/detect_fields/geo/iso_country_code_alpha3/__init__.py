from os.path import dirname, join
import re

PROPORTION = 1

with open(join(dirname(__file__), 'iso_country_code_alpha3.txt'), 'r') as iofile:
    liste_pays = iofile.read().split('\n')


def _is(val):
    '''Renvoie True si val peut etre un code iso pays alpha-3, False sinon'''
    regex = r'[A-Z]{3}$'
    if not bool(re.match(regex, val)):
        return False
    return val in set(liste_pays)
