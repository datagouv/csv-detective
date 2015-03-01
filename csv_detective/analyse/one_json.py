# -*- coding: utf-8 -*-
"""
Created on Sun Mar 01 11:19:41 2015

@author: alexis
"""

import json
from os import listdir
from os.path import isfile, join
import pandas as pd

main_path = 'C:/git/csv_detective/'    
path = main_path + 'data' # 
json_path = main_path + 'data/test_csv_detector/jsons'

num_lines = 50 # nombre de lignes à analyser

# rassemble tous dans une base de donnes
def one_table():
    all_files = listdir(json_path)
    all = dict()
    for file_name in all_files:
        print '*****************************************'
        print file_name

        file = open(join(json_path, file_name), 'r')
        data = json.load(file)
        file.close()
        all[file_name[:-5]] = data
    return pd.DataFrame(all)


# detect headers
tab = one_table()
head = tab.loc['headers'] 
cond = (head == u'not_found')
list_not_found = tab.loc[:,cond].columns


from csv_detective.detect_errors import (ints_as_floats, detect_headers, 
                           detect_heading_columns, detect_trailing_columns)

from csv_detective.explore_csv import detect_separator


file_name = list_not_found[0]
try: 
    file = open(join(main_path, 'data', 'test_csv_detector', file_name + '.csv'), 'r')
except:
    file = open(join(main_path, 'data', 'test_csv_detector', file_name + '.tsv'), 'r')


sep = detect_separator(file)
remove_extra_columns(file, sep)
detect_headers(file, sep)
file.seek(0)
for i in range(10):
    header = file.readline()
    chaine = header.split(sep)
    print chaine
#    if (chaine[-1] not in ['', '\n'] and 
#         all([mot not in ['', '\n'] for mot in chaine[1:-1]])):
#        return i, header.replace(sep, ';')