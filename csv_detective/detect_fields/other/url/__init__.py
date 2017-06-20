from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Detects urls'''
    a = 'http://' in val
    b = 'www.' in val
    c = any([x in val for x in ['.fr', '.com', '.org', '.gouv', '.net']])
    d = not ('@' in val)
    return (a or b or c) and d
