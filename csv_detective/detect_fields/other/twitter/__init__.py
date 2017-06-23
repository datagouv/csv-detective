from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Detects twitter accounts'''
    regex = r'^@[A-Za-z0-9_]+$'
    return bool(re.match(regex, val))
