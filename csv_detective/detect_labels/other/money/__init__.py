from csv_detective.process_text import _process_text

PROPORTION = 1

def _is(header):
    '''Returns 1 if at least one of the mentionned words is in the label, else 0
    '''

    words_list = ['budget', 'salaire', 'euro', 'euros', 'prêt', 'montant']

    return float(any([word in header for word in words_list]))

#def _is(serie):
#    '''Detects money'''
#    column_title_looks_like_money = np.ones(serie.shape[0]) * is_col_name_related_to_money(serie.name.lower())
#    return column_title_looks_like_money


