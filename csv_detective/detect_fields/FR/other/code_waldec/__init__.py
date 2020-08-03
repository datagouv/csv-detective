from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.9

def _is(val):
    '''Repere le code Waldec'''
    regex = r'^\d{3}\D\d{1,10}$|^\d\D\d\D\d{10}$|^\d{3}\D{3}\d{1,10}$|^\d{3}\D\d{4}\D\d{1,10}$|^\d{3}\D\d{2}[-]\d{3}$|^\d\D\d\D\d{2}\D\d{1,8}$'
    return bool(re.match(regex, val))
