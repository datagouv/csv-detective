PROPORTION = 0.5


def _is(header):
    '''
    Returns 1 if at least one of the mentionned words is in the label, else 0
    '''

    words_list = ['budget', 'salaire', 'euro', 'euros', 'prêt', 'montant']

    return float(any([word in header.lower() for word in words_list]))
