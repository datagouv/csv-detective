import numpy as np
from csv_detective.process_text import _process_text
#from csv_detective.detect_labels.other.money.check_col_name import is_col_name_related_to_money

PROPORTION = 0.5

def _is(header):
    '''Returns the share of words in the (processed) header that match one of the expected words'''

    words_list = ['budget', 'salaire', 'euro', 'euros', 'prêt', 'montant']
    processed_header = _process_text(header)

    return np.mean([word in words_list for word in processed_header.split()])

#def _is(serie):
#    '''Detects money'''
#    column_title_looks_like_money = np.ones(serie.shape[0]) * is_col_name_related_to_money(serie.name.lower())
#    return column_title_looks_like_money


