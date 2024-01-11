from os.path import dirname, join
import re

PROPORTION = 0.9
f = open(join(dirname(__file__), 'code_postal.txt'), 'r')
codes_postaux = f.read().split('\n')
# removing empty str due to additionnal line in file
del codes_postaux[-1]
codes_postaux = set(codes_postaux)
f.close()


def _is(val):
    '''Renvoie True si val peut être un code postal, False sinon'''

    if not bool(re.match(r'^[0-9]{5}$', val)):
        return False

    return val in codes_postaux
