import numpy as np

from csv_detective.detect_labels.other.money.check_col_name import is_col_name_related_to_money

PROPORTION = 1

def _is(serie):
    '''Detects money'''
    column_title_looks_like_money = np.ones(serie.shape[0]) * is_col_name_related_to_money(serie.name.lower())
    return column_title_looks_like_money


