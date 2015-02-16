# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:53:48 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from process_text.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si les cahmps peuvent être des jours de la semaine'''
    try:
        val = int(val)
    except:
        return False
    if (1900 <= val) and (val <= 2100):
        return True
    else:
        return False
