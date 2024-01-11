from os.path import dirname, join
import re

PROPORTION = 0.75
f = open(join(dirname(__file__), 'code_commune_insee.txt'), 'r')
codes_insee = f.read().split('\n')
# removing empty str due to additionnal line in file
del codes_insee[-1]
codes_insee = set(codes_insee)
f.close()
# vérification de cohérence avec prise en compte corse 2A/2B et DOM (971-976 sauf 975)
regex = r'^([01345678][0-9]{4}|2[AB1-9][0-9]{3}|9([0-5][0-9]{3}|7[12346][0-9]{2}))$'


def _is(val):
    '''Renvoie True si val peut être un code commune INSEE, False sinon'''
    # test sur la longueur
    if len(val) != 5:
        return False

    if not bool(re.match(regex, val)):
        return False

    return val in codes_insee
