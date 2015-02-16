# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:54:46 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from process_text.process_text import _process_text
import re

rel_path = '../../fichiers_de_reference/autres'
path = join(dirname(__file__), rel_path)

def _url(val):
    '''Repère les url'''
    a = 'http://' in val
    b = 'www.' in val
    c = any([x in val for x in ['.fr', '.com', '.org', '.gouv', '.net']])
    d = not ('@' in val)
    return (a or b or c) and d
