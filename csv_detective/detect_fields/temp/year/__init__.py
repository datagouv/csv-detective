from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Returns True if val can be a year'''
    try:
        val = int(val)
    except:
        return False
    if (1900 <= val) and (val <= 2100):
        return True
    else:
        return False
