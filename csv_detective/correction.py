# -*- coding: utf-8 -*-
"""
Created on Sun Mar 01 14:09:02 2015

@author: alexis
"""


def remove_extra_columns(file, detect_extra_columns_results):
    res = detect_extra_columns_results
    to_remove = res[0] + res[1]
    L = file.read().splitlines()
    for line in L: 
        line = line[:-to_remove]
        print line


