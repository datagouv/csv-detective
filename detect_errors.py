# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 19:33:04 2015

@author: alexis
"""

def ints_as_floats(table):
    '''Détecte les colonnes contenant des entiers possibles écrits sous forme de float'''
    regex = r'^[0-9]+\.0+$'
    res = table.apply(lambda serie: serie.str.match(regex).all() and any(serie.notnull()))
    return res.index[res]

def detect_headers(file, sep):
    ''' Tests 10 first rows for possible header (header not in 1st line)'''
    file.seek(0)
    for i in range(10):
        header = file.readline()
        chaine = header.split(sep)
        if (chaine[-1] not in ['', '\n'] and 
             all([mot not in ['', '\n'] for mot in chaine[1:-1]])):
            return i
    return 0

def detect_heading_columns(file, sep):
    ''' Tests first 10 lines to see if there are empty heading columns'''
    file.seek(0)
    return_int = inf
    for i in range(10):
        line = file.readline()
        return_int = min(return_int, len(line) - len(line.strip(sep)))
        if return_int == 0:
            return 0
    return return_int

def detect_trailing_columns(file, sep, heading_columns):
    ''' Tests first 10 lines to see if there are empty trailing columns'''
    file.seek(0)
    return_int = inf
    for i in range(10):
        line = file.readline()
        return_int = min(return_int, len(line.replace('\n', '')) - len(line.replace('\n', '').strip(sep)) - heading_columns)
        if return_int == 0:
            return 0
    return return_int