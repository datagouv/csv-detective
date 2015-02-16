# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:51:29 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from process_text.process_text import _process_text
import re

rel_path = '../../fichiers_de_reference/geographiques'
path = join(dirname(__file__), rel_path)

def _departement(val):
    '''Match avec le nom des departements'''
    f = open(join(path,'departements.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste
