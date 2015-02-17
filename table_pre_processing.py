# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 14:53:15 2015

@author: leo_cdo_intern


"""

def detect_headers(file, sep):
    ''' teste les 5 première ligne pour voir si on a une
        ligne qui ferait un bon header '''
    with open(file, 'r') as myCsvfile:
        for i in range(5):
            header = myCsvfile.readline()
            chaine = header.split(sep)
            if (chaine[-1] not in ['', '\n'] and 
                 all(mot not in ['', '\n'] for mot in chaine[1:-1])):
                return i
    return 0
