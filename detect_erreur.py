# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 19:33:04 2015

@author: alexis
"""

def entier_a_virgule(serie):
    if all(serie.str.contains('.')):
        avant_virg = serie.str.split('.').str.get(0)
        apres_virg = serie.str.split('.').str.get(1)
        if len(set(apres_virg.values)) == 1:
            print apres_virg.iloc[0]
            print str(serie.name) + " a une seule valeur après la virgule, on la supprime"
    