# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:51:29 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from process_text.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut être un code postal, False sinon'''
    if isinstance(val, str) or isinstance(val, unicode): # Si val est un string, on essaye de le convertir en nombre
        if val.isdigit():
            val = int(val)
        else:
            return False
    else:
        return False
    if not (val > 1000) and (val < 100000):
        return False
    f = open(join('/home/debian/Documents/projects/csv_detective/detect_fields/geographiques/code_postal', 'code_postal.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    return str(val).zfill(5) in liste



