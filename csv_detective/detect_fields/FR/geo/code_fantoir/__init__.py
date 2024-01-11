from os.path import dirname, join
import re

PROPORTION = 1
f = open(join(dirname(__file__), 'code_fantoir.txt'), 'r')
codes_fantoir = f.read().split('\n')
f.close()


def _is(val):
    '''Renvoie True si val peut être un code FANTOIR/RIVOLI, False sinon'''
    if not bool(re.match(r'^[0-9A-Z][0-9]{3}[ABCDEFGHJKLMNPRSTUVWXYZ]$', val)):
        return False

    return val[:4] in codes_fantoir
