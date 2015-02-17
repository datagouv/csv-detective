# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 09:47:26 2015

@author: leo_cdo_intern

###############################################################################
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le
contenu possible des champs


ACTUELLEMENT EN DEVELOPPEMENT : Indactions comment tester tout en bas
"""

import pandas as pd
import chardet
from os.path import join

import detect_fields


from detect_erreur import ints_as_floats

#############################################################################
############### ROUTINE DE TEST CI DESSOUS ##################################

# TODO : Mettre un pourcentage de valeurs justes (au lieu de nécessiter que toutes les valeurs soient justes)

def detect_separator(file):
    '''Detects csv separator'''
    # TODO: add a robust detection:
    # si on a un point virgule comme texte et \t comme séparateur, on renvoit
    # pour l'instant un point virgule
    file.seek(0)
    header = file.readline()
    possible_separators = [";", ",", "|", "\t"]
    sep_count = dict()
    for sep in possible_separators:
        sep_count[sep] = header.count(sep)
    return max(sep_count, key = sep_count.get)

def detect_headers(file, sep):
    ''' Tests 10 first rows for possible header'''
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
        header = file.readline()
        return_int = min(return_int, len(header) - len(header.strip(sep)))
        if return_int == 0:
            return 0
    return return_int

#def detect_trailing_columns(file, sep):
#    ''' Tests first 10 lines to see if there are empty trailing columns'''
#    file.seek(0)
#    return_int = inf
#    for i in range(10):
#        header = file.readline()
#        return_int = min(return_int, len(header) - len(header.strip(sep)))
#        if return_int == 0:
#            return 0
#    return return_int
   
def detect_encoding(file):
    '''Detects file encoding using chardet based on N first lines
    '''
    file.seek(0)
    head = ''
    count = 0
    for line in file:
        if count == 100:
            break
        else:
            count += 1
            head += line
    chardet_res = chardet.detect(head)
    return chardet_res
    

    
        


def test_col(serie, test_func, proportion = 0.9, skipna = True):
    ''' Tests values of the serie using test_func.
    skipna = True indicates that NaNs are not counted as False
    proportion indicates the proportion of values that have to pass the test
    for the serie to be detected as a certain type
    '''
    serie = serie[serie.notnull()]
    ser_len = len(serie)
    if ser_len == 0:
        return False
    if proportion == 1:
        for range_ in [range(0,min(1, ser_len)), range(min(1, ser_len),min(5, ser_len)), range(min(5, ser_len),min(50, ser_len))]: # Pour ne pas faire d'opérations inutiles, on commence par 1, puis 5 puis 50 valeurs
            if all(serie.iloc[range_].apply(test_func)):
                pass
            else:
                return False
        return True
    else:
        try:
            return serie.apply(test_func).sum() > proportion * len(serie)
        except:
            import pdb
            pdb.set_trace()

def routine(file):
    '''Returns a dict with information about the csv table and possible
    column contents    
    '''

    sep = detect_separator(file)
    headers_row = detect_headers(file, sep)
    empty_cols = detect_heading_columns(file, sep)
    print headers_row, empty_cols
    chardet_res = detect_encoding(file)
    
    print chardet_res
    
    for encoding in [chardet_res['encoding'], 'ISO-8859-1', 'utf-8']:
        # TODO : modification systematique 
        if 'ISO-8859' in encoding:
            encoding = 'ISO-8859-1'
        try:
            file.seek(0)
            table = pd.read_csv(file, sep = sep, 
                                skiprows = headers_row,
                                nrows = 50, dtype = 'unicode',
                                encoding = encoding                 
                                )
            break
        except:
            pass
    else:
        return False
     

    # Creating return dictionnary
    return_dict = dict()
    return_dict['encoding'] = encoding
    return_dict['separator'] = sep
    return_dict['headers_row'] = headers_row
    return_dict['empty_cols'] = empty_cols       
                        
    # List of test values
    all_tests = [detect_fields.code_postal,
                 detect_fields.code_commune_insee,
                 #detect_fields.code_departement, 
                 detect_fields.iso_country_code,
                 detect_fields.pays,
                 detect_fields.region,
                 detect_fields.departement,
                 detect_fields.commune,
                 detect_fields.adresse,
                 
                 detect_fields.jour_de_la_semaine,
                 detect_fields.year,
                 detect_fields.date,
                 
                 detect_fields.code_csp_insee,
                 detect_fields.csp_insee,
                 detect_fields.sexe,
                 detect_fields.url,
                 detect_fields.email,
                 detect_fields.tel_fr,
                 detect_fields.siren
                 ]
    
    # Initialising dict for tests    
    test_funcs = dict()
    for test in all_tests:
        name = test.__name__.split('.')[-1]
        test_funcs[name] = {'func' : test._is,
                            'prop' : test.PROPORTION
                            }
    
    
    return_table = pd.DataFrame(columns = table.columns)
    for key, value in test_funcs.iteritems():
        try:
            return_table.loc[key] = table.apply(lambda serie: test_col(serie, value['func'], value['prop']))
        except Exception, e:
            import pdb
            print str(e)
            pdb.set_trace()
            
    # Détection des colonnes d'entiers écrits avec virgules
    table.apply(ints_as_floats, axis=1)
    
    
    # Filling the columns attributes of return dictionnary
    return_dict_cols = dict()
    for col in return_table.columns:
        possible_values = list(return_table[return_table[col]].index)
        if possible_values != []:
            print '  >>  La colonne', col, 'est peut-être :',
            print possible_values
            return_dict_cols[col] = possible_values
    return_dict['columns'] = return_dict_cols
    return return_dict






if __name__ == '__main__':

    from os import listdir
    from os.path import isfile, join
    import json
    
    ### CONSIGNES : Mettre toutes les data a tester dans le dossier indiqué par path
    # et lancer le script. Il doit afficherc pour chaque fichier dans ce dossier (ne doit contenir que des csv)
    # les colonnes pour lesquelles un match a été trouvé
    
    path = '/home/debian/Documents/data/test_csv_detector' # 'data'
    json_path = '/home/debian/Documents/data/test_csv_detector/jsons'
    
    
    all_files = listdir(path)
    counter = 0
    for file_name in all_files:
        print '*****************************************'
        print file_name
        if any([extension in file_name for extension in ['.csv', '.tsv']]):
            file = open(join(path, file_name), 'r')
            a = routine(file)
            file.close()
        if a:
            counter += len(a)
            with open(join(json_path, file_name.replace('.csv', '.json')), 'wb') as fp:
                json.dump(a, fp, indent=4, separators=(',', ': '))
        print '\n'
    print 'on a trouvé des matchs éventuels pour ', counter, 'valeurs'



