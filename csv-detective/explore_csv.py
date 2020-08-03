"""
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le
contenu possible des champs
"""

from pkg_resources import resource_string

import pandas as pd

from csv_detective import detect_fields

from .detection import (
    detect_ints_as_floats,
    detect_separator,
    detect_encoding,
    detect_headers,
    detect_heading_columns,
    detect_trailing_columns,
    parse_table,
    detetect_categorical_variable, detect_continuous_variable)

#############################################################################
############### ROUTINE DE TEST CI DESSOUS ##################################


def test_col(serie, test_func, proportion=0.9, skipna=True, num_rows=50, output_mode='ALL'):
    ''' Tests values of the serie using test_func.
         - skipna : if True indicates that NaNs are not counted as False
         - proportion :  indicates the proportion of values that have to pass the test
    for the serie to be detected as a certain type
    '''
    serie = serie[serie.notnull()]
    ser_len = len(serie)
    if ser_len == 0:
        return False
    if(output_mode == 'ALL'):
        return serie.apply(test_func).sum() / num_rows
    else:
        if proportion == 1:  # Then try first 1 value, then 5, then all
            for _range in [
                range(0, min(1, ser_len)),
                range(min(1, ser_len), min(5, ser_len)),
                range(min(5, ser_len), min(num_rows, ser_len))
            ]:  # Pour ne pas faire d'opérations inutiles, on commence par 1,
                # puis 5 puis num_rows valeurs
                if all(serie.iloc[_range].apply(test_func)):
                    pass
                else:
                    return False
            return True
        else:
            return serie.apply(test_func).sum() > proportion * len(serie)



def return_all_tests(user_input_tests):
    all_packages = resource_string(__name__, 'all_packages.txt')
    all_packages = all_packages.decode().split('\n')
    all_packages.remove('')
    all_packages.remove('csv_detective')
    all_packages = [x.replace('csv_detective.', '') for x in all_packages]

    if user_input_tests is None:
        return []

    if isinstance(user_input_tests, str):
        assert user_input_tests[0] != '-'
        if user_input_tests == 'ALL':
            tests_to_do = ['detect_fields']
        else:
            tests_to_do = ['detect_fields' + '.' + user_input_tests]
        tests_to_not_do = []
    elif isinstance(user_input_tests, list):
        if 'ALL' in user_input_tests:
            tests_to_do = ['detect_fields']
        else:
            tests_to_do = ['detect_fields' + '.' + x for x in user_input_tests if x[0] != '-']
        tests_to_not_do = ['detect_fields' + '.' + x[1:] for x in user_input_tests if x[0] == '-']

    all_fields = [x for x in all_packages if any([y == x[:len(y)] for y in tests_to_do]) and all([y != x[:len(y)] for y in tests_to_not_do])]
    all_tests = [eval(field) for field in all_fields]
    all_tests = [test for test in all_tests if '_is' in dir(test)] # TODO : Fix this shit
    return all_tests


def routine(file_path, num_rows=50, user_input_tests='ALL',output_mode='LIMITED'):
    '''Returns a dict with information about the csv table and possible
    column contents
    '''
    # print('This is tests_to_do', user_input_tests)
    binary_file = open(file_path, mode='rb')
    encoding = detect_encoding(binary_file)['encoding']

    with open(file_path, 'r', encoding=encoding) as str_file:
        sep = detect_separator(str_file)
        header_row_idx, header = detect_headers(str_file, sep)
        if header is None:
            return_dict = {'error': True}
            return return_dict
        elif isinstance(header, list):
            if any([x is None for x in header]):
                return_dict = {'error': True}
                return return_dict
        heading_columns = detect_heading_columns(str_file, sep)
        trailing_columns = detect_trailing_columns(str_file, sep, heading_columns)
        table, total_lines = parse_table(str_file, encoding, sep, num_rows)

    # Detects columns that are ints but written as floats
    res_ints_as_floats = list(detect_ints_as_floats(table))

    # Detects columns that are categorical
    res_categorical, categorical_mask = detetect_categorical_variable(table)
    res_categorical = list(res_categorical)
    # Detect columns that are continuous (we already know the categorical)
    res_continuous = list(detect_continuous_variable(table.iloc[:, ~categorical_mask.values]))

    # Creating return dictionary
    return_dict = dict()
    return_dict['encoding'] = encoding
    return_dict['separator'] = sep
    return_dict['header_row_idx'] = header_row_idx
    return_dict['header'] = header
    return_dict['total_lines'] = total_lines

    return_dict['heading_columns'] = heading_columns
    return_dict['trailing_columns'] = trailing_columns
    return_dict['ints_as_floats'] = res_ints_as_floats

    return_dict['continuous'] = res_continuous
    return_dict['categorical'] = res_categorical

    all_tests = return_all_tests(user_input_tests)

    if not all_tests:
        return return_dict

    # Initialising dict for tests
    test_funcs = dict()
    for test in all_tests:
        name = test.__name__.split('.')[-1]

        test_funcs[name] = {
            'func': test._is,
            'prop': test.PROPORTION
        }

    return_table = pd.DataFrame(columns=table.columns)
    for key, value in test_funcs.items():
        return_table.loc[key] = table.apply(lambda serie: test_col(
            serie,
            value['func'],
            value['prop'],
            output_mode=output_mode
        ))

    # Filling the columns attributes of return dictionnary
    return_dict_cols = dict()
    
    if(output_mode == 'LIMITED'):
        for colnum in range(0,len(return_table.columns)):
            col=return_table.columns[colnum]
            possible_values = list(return_table[return_table[col]].index)
            if possible_values != []:
                #print('  >>  La colonne', col, 'est peut-être :',)
                #print(possible_values)
                return_dict_cols[header[colnum]] = possible_values
        return_dict['columns'] = return_dict_cols
        
    if(output_mode  == 'ALL'):
        return_dict_cols = return_table.to_dict('index')
        return_dict_cols_intermediary = {}
        for key in return_dict_cols:
            return_dict_cols_intermediary[key] = []
            for subkey in return_dict_cols[key]:
                dict_tmp = {}
                dict_tmp['colonne'] = subkey
                dict_tmp['score_rb'] = return_dict_cols[key][subkey]
                return_dict_cols_intermediary[key].append(dict_tmp)
        return_dict['columns'] = return_dict_cols_intermediary

    return return_dict
