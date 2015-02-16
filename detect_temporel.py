# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:53:48 2015

@author: leo_cdo_intern
"""

from os.path import join
from process_text.process_text import _process_text
import re

path = 'fichiers_de_reference/temporel'



#### DATES
def _jour_de_la_semaine(val):
    '''Renvoie True si les cahmps peuvent être des jours de la semaine'''
    val = val.lower()
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    return val in jours

def _annee(val):
    '''Renvoie True si les cahmps peuvent être des jours de la semaine'''
    try:
        val = int(val)
    except:
        return False
    if (1900 <= val) and (val <= 2100):
        return True
    else:
        return False

def _date(val):
    '''Renvoie True si val peut être une date, False sinon'''
    a = bool(re.match(r'^(19|20)\d\d[ -/_](0[1-9]|1[012])[ -/_](0[1-9]|[12][0-9]|3[01])', val)) # matches 1993-12/02
    b = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])[ -/_](0[1-9]|1[012])[ -/_]([0-9]{2}|(19|20)[0-9]{2}$)', val)) # matches 02/12 03 and 02_12 2003
    c = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])([0-9]{2}|(19|20){2}$)', val)) # matches 02_05_2003
    d = bool(re.match(r'^(19|20)\d\d(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])', val)) # matches 19931202
    return a or b or c or d