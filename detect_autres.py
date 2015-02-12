# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:54:46 2015

@author: leo_cdo_inter

##############################################################################
Contient : _sexe, _code_csp_insee, _csp_insee, _url


"""

from os.path import join
from process_text import _process_text
import re
path = '/home/debian/Documents/projects/csv_detective/fichiers_de_reference/autres'



#### AUTRES INFOS
def _sexe(val):
    '''Repère le sexe'''
    if not (isinstance(val, str) or isinstance(val, unicode)):
        return False
    val =_process_text(val)
    return val in ['homme', 'femme', 'h', 'f', 'm', 'masculin', 'feminine']

def _code_csp_insee(val):
    '''Repère les csp telles que définies par l'INSEE'''
    val = str(val)
    val = _process_text(val)
    if not len(val) == 4:
        return False
    a = bool(re.match(r'^[123456][1-9]{2}[abcdefghijkl]$', val))
    b = val in ['7100', '7200', '7400', '7500', '7700', '7800', '8100', '8300', '8400', '8500', '8600']
    return a or b

def _csp_insee(val):
    '''Repère les csp telles que définies par l'INSEE'''
    if not (isinstance(val, str) or isinstance(val, unicode)):
        return False
    val = _process_text(val)
    f = open(join(path,'csp_insee.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    return val in liste
    
def _url(val):
    '''Repère les url'''
    val = str(val)
    a = 'http://' in val
    b = 'www.' in val
    c = any([x in val for x in ['.fr', '.com', '.org', '.gouv', '.net']])
    return a or b or c
    
