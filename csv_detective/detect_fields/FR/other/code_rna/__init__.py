from os.path import dirname, join
from process_text import _process_text
import re

PROPORTION = 0.9
def _is(val):
    '''Repere le code RNA'''
    regex = r'^[wW]\d{9}$'
    return bool(re.match(regex, val))
