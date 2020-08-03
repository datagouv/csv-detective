from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1
f = open(join(dirname(__file__), 'code_fantoir.txt'), 'r')
codes_fantoir = f.read().split('\n')
f.close()


def _is(val):
    '''Renvoie True si val peut être un code FANTOIR/RIVOLI, False sinon'''

    regex = r'^[0-9A-Z][0-9]{3}[ABCDEFGHJKLMNPRSTUVWXYZ]$'
    if not bool(re.match(regex, val)):
        return False

    return val[:4] in codes_fantoir
