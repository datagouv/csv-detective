import pandas as pd

def test_col_val(serie, test_func, proportion=0.9, skipna=True, num_rows=50, output_mode='ALL'):
    ''' Tests values of the serie using test_func.
         - skipna : if True indicates that NaNs are not counted as False
         - proportion :  indicates the proportion of values that have to pass the test
    for the serie to be detected as a certain format
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
                    return 0.0
            return 1.0
        else:
            result = apply_test_func(serie, test_func, _range).sum() / len(serie)
            return  result if result >= proportion else 0.0

def test_col_label(label, test_func, proportion=1, output_mode='ALL') :
    ''' Tests label (from header) using test_func.
         - proportion :  indicates the minimum score to pass the test for the serie to be detected as a certain format
    '''
    if output_mode == 'ALL' :
        return test_func(label)
    else :
        result = test_func(label)
        return result if result >= proportion else False

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
        return_table.loc[key] = [test_col_label(
            col_name,
            value['func'],
            value['prop'],
            output_mode=output_mode
        ) for col_name in table.columns]
    return return_table


def prepare_output_dict(return_table, output_mode):
    return_dict_cols = return_table.to_dict('dict')
    return_dict_cols_intermediary = {}
    for column_name in return_dict_cols:
        return_dict_cols_intermediary[column_name] = []
        for detected_value_type in return_dict_cols[column_name]:
            if return_dict_cols[column_name][detected_value_type] == 0:
                continue
            dict_tmp = {}
            dict_tmp['format'] = detected_value_type
            dict_tmp['score'] = return_dict_cols[column_name][detected_value_type]
            return_dict_cols_intermediary[column_name].append(dict_tmp)

        # Clean dict using priorities
        formats_detected = {x['format'] for x in return_dict_cols_intermediary[column_name]}
        formats_to_remove = set()
        # Deprioritise float and int detection vs others
        if len(formats_detected - {'float', 'int'}) > 0:
            formats_to_remove = formats_to_remove.union({'float', 'int'})
        if 'int' in formats_detected:
            formats_to_remove.add('float')
        if 'latitude_wgs_fr_metropole' in formats_detected:
            formats_to_remove.add('latitude_l93')
            formats_to_remove.add('latitude_wgs')
        if 'longitude_wgs_fr_metropole' in formats_detected:
            formats_to_remove.add('longitude_l93')
            formats_to_remove.add('longitude_wgs')
        if 'longitude_wgs' in formats_detected:
            formats_to_remove.add('longitude_l93')
        if 'code_region' in formats_detected:
            formats_to_remove.add('code_departement')

        formats_to_keep = formats_detected - formats_to_remove

        detections = return_dict_cols_intermediary[column_name]
        detections = [x for x in detections if x['format'] in formats_to_keep]
        if output_mode == 'ALL':
            return_dict_cols_intermediary[column_name] = detections
        if output_mode == 'LIMITED':
            return_dict_cols_intermediary[column_name] = max(detections, key=lambda x: x['score']) if len(detections) > 0 else {'format': 'string', 'score': 1.0}

    return return_dict_cols_intermediary

def full_word_strictly_inside_string(word, string) :
    return (' '+word+' ' in string) or (string.startswith(word+' ')) or (string.endswith(' '+word))
