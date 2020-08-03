# -*- coding: utf-8 -*-
"""
Détection codes UAI (éducation nationale)

@author: cquest
"""

from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Repere les codes UAI de l'éducation nationale'''

    # test sur la longueur
    if len(val) != 8:
        return False

    regex = r'^(0[0-8][0-9]|09[0-5]|9[78][0-9]|[67]20)[0-9]{4}[A-Z]$'
    if not bool(re.match(regex, val)):
        return False
    return True
