from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1


def _is(val):
    '''Repere les dates textuelles FR'''
    regex = r'^\d{1,2}[ \-](janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)[ \-]\d{4}$'
    return bool(re.match(regex, val))
