from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut etre un code iso pays, False sinon'''
    regex = r'[A-Z]{2}'
    if not bool(re.match(regex, val)):
        return False

    f = open(join(dirname(__file__), 'iso_country_code.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    return val in liste


