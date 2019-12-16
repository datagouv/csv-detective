from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.95
'''Renvoie True si val peut etre un code iso pays, False sinon'''


with open(join(dirname(__file__), 'iso_country_code.txt'), 'r') as iofile:
    LISTE_PAYS = iofile.read().split('\n')

def _is(val):
    regex = r'[A-Z]{2,3}$'
    if not bool(re.match(regex, val)):
        return False


    return val in LISTE_PAYS

'''Match avec le code des departements'''


