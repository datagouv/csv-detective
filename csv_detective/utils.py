def test_col(serie, test_func, proportion=0.9, skipna=True, num_rows=50, output_mode='ALL'):
    ''' Tests values of the serie using test_func.
         - skipna : if True indicates that NaNs are not counted as False
         - proportion :  indicates the proportion of values that have to pass the test
    for the serie to be detected as a certain type
    '''
    def apply_test_func(serie, test_func, _range):
        try:
            return serie.iloc[_range].apply(test_func)
        except AttributeError:
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