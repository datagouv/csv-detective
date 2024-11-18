import re

PROPORTION = 1
regex = (
    r'^\d{1,2}[ \-](janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre'
    r'|octobre|novembre|decembre)[ \-]\d{4}$'
)


def _is(val):
    '''Repere les dates textuelles FR'''
    return isinstance(val, str) and bool(re.match(regex, val))
