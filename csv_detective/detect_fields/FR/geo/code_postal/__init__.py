from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.9
f = open(join(dirname(__file__), 'code_postal.txt'), 'r')
codes_postal = f.read().split('\n')
f.close()


def _is(val):
    '''Renvoie True si val peut être un code postal, False sinon'''

    regex = r'^[0-9]{5}$'
    if not bool(re.match(regex, val)):
        return False

    return val in codes_postal
