from csv_detective.process_text import _process_text

PROPORTION = 1


def _is(val):
    '''Repère le sexe'''
    val = _process_text(val)
    return val in {'homme', 'femme', 'h', 'f', 'm', 'masculin', 'feminin'}
