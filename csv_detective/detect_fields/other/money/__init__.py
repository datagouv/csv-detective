import numpy as np

from csv_detective.detect_fields.other.money.check_col_name import is_col_name_related_to_money
from csv_detective.utils import test_col
from csv_detective.detect_fields.other import float_field as ff

PROPORTION = 1

def _is(serie):
    '''Detects money'''
    serie_looks_like_money = test_col(serie, ff._is, 1)
    column_title_looks_like_money = np.ones(serie.shape[0]) * is_col_name_related_to_money(serie.name.lower())
    return serie_looks_like_money * column_title_looks_like_money


if __name__ == '__main__':
    import pandas as pd
    serie = pd.Series(name='montant total', data=['4.0', '1.0', '1.0'])
    print(_is(serie))