# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:54:46 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from process_text.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Repère les code csp telles que définies par l'INSEE'''
    val = _process_text(val)
    if not len(val) == 4:
        return False
    a = bool(re.match(r'^[123456][1-9]{2}[abcdefghijkl]$', val))
    b = val in ['7100', '7200', '7400', '7500', '7700', '7800', '8100', '8300', '8400', '8500', '8600']
    return a or b
