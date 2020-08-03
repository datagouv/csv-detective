from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.6

def _is(val):
    '''Repere des adresses'''
    val = _process_text(val)
    a = any([x in val for x in 'rue allee route avenue chemin boulevard bvd ilot impasse promenade montee rocade'.split()])
    return a
