# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 13:50:13 2015

@author: leo_cdo_intern
"""

#### PROCESSING DU TEXTE
def _process_text(val):
    '''Met le string val sous sous sa forme normee'''
    val = val.lower()
    val = val.replace('-', ' ')
    val = val.replace("'", ' ')
    val = val.replace(',', ' ')
    val = val.replace('  ', ' ')
    val = val.replace('\xc3\xa8', 'e')
    val = val.replace('\xc3\xa9', 'e')
    val = val.replace('\xc3\xaa', 'e')
    val = val.replace('\xc3\x8e', 'i')    
    val = val.replace('\xc3\xb4', 'o')
    val = val.replace('\xc3\xa7', 'c')
    val = val.replace('\xc3\xa0', 'a')
    val = val.replace('\xc3\xa2', 'a')
    val = val.replace('\xc3\xae', 'i')
    return val