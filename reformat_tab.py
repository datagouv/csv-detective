# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 10:57:20 2015

@author: debian
"""

from os.path import join
from detect_from_cells import routine
import pandas as pd

path = '/home/debian/Documents/data/test_csv_detector'

file = open(join(path, 'annuaire_cph.csv'))
return_dict = routine(file)

file.seek(0)
table = pd.read_csv(file, sep = return_dict['separator'], 
                                skiprows = return_dict['headers_row'],
                                dtype = 'unicode',
                                encoding = return_dict['encoding']                 
                                )
file.close()
