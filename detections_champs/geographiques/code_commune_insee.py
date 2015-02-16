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

def _code_commune_insee(val):
    '''Renvoie True si val peut être un code commune INSEE, False sinon'''
        # TODO : ajouter une regex pour : 'que des chiffres ou bien commence par 2A, 2B puis 3 chiffres'
    if not len(val) in [4,5]:
        return False
    val = val.zfill(5)
    f = open(join(path,'codes_commune_insee.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    return val in liste

