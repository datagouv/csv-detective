import pandas as pd

def test_col_val(serie, test_func, proportion=0.9, skipna=True, num_rows=50, output_mode='ALL'):
    ''' Tests values of the serie using test_func.
         - skipna : if True indicates that NaNs are not counted as False
         - proportion :  indicates the proportion of values that have to pass the test
    for the serie to be detected as a certain type
    '''
    def apply_test_func(serie, test_func, _range): #TODO : change for a cleaner method and only test columns in modules labels
        try:
            return serie.iloc[_range].apply(test_func)
        except AttributeError: # .name n'est pas trouvé
            return test_func(serie.iloc[_range])


    serie = serie[serie.notnull()]
    ser_len = len(serie)
    num_rows = min(ser_len, num_rows)
    _range = range(0, ser_len)
    if ser_len == 0:
        return False
    if(output_mode == 'ALL'):
        return apply_test_func(serie, test_func, _range).sum() / num_rows
    else:
        if proportion == 1:  # Then try first 1 value, then 5, then all
            for _range in [
                range(0, min(1, ser_len)),
                range(min(1, ser_len), min(5, ser_len)),
                range(min(5, ser_len), min(num_rows, ser_len))
            ]:  # Pour ne pas faire d'opérations inutiles, on commence par 1,
                # puis 5 puis num_rows valeurs
                if all(apply_test_func(serie, test_func, _range)):
                    pass
                else:
                    return False
            return True
        else:
            return apply_test_func(serie, test_func, _range).sum() > proportion * len(serie)

def test_col_label(serie, test_func, proportion=1, output_mode='ALL') :
    ''' Tests label (from header) using test_func.
         - proportion :  indicates the minimum score to pass the test for the serie to be detected as a certain type
    '''
    label = serie.name

    if output_mode == 'ALL' :
        return test_func(label)
    else :
        return test_func(label) >= proportion

def test_col(table, all_tests, num_rows, output_mode):
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
        return_table.loc[key] = table.apply(lambda serie: test_col_val(
            serie,
            value['func'],
            value['prop'],
            num_rows = num_rows,
            output_mode=output_mode
        ))
    return return_table

def test_label(table, all_tests, output_mode) :
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
        return_table.loc[key] = table.apply(lambda serie: test_col_label(
            serie,
            value['func'],
            value['prop'],
            output_mode=output_mode
        ))
    return return_table


def prepare_output_dict(return_table, output_mode):
    """
    if (output_mode == 'LIMITED'):
        for colnum in range(0, len(return_table.columns)):
            col = return_table.columns[colnum]
            possible_values = list(return_table[return_table[col]].index)
            if possible_values != []:
                # print('  >>  La colonne', col, 'est peut-être :',)
                # print(possible_values)
                return_dict_cols[header[colnum]] = possible_values
        return return_dict_cols"""

    return_dict_cols = return_table.to_dict('index')
    return_dict_cols_intermediary = {}
    for detected_value_type in return_dict_cols:
        return_dict_cols_intermediary[detected_value_type] = []
        for column_name in return_dict_cols[detected_value_type]:
            if output_mode == 'LIMITED':
                if return_dict_cols[detected_value_type][column_name]:
                    return_dict_cols_intermediary[detected_value_type].append(column_name)
            if (output_mode == 'ALL'):
                dict_tmp = {}
                dict_tmp['colonne'] = column_name
                dict_tmp['score_rb'] = return_dict_cols[detected_value_type][column_name]
                return_dict_cols_intermediary[detected_value_type].append(dict_tmp)

    return return_dict_cols_intermediary

def full_word_strictly_inside_string(word, string) :
    return (' '+word+' ' in string) or (string.startswith(word+' ')) or (string.endswith(' '+word))
