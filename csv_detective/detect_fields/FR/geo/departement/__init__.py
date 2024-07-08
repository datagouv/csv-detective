from frformat import Departement, Options

PROPORTION = 0.9

def _is(val):
    '''Match avec le nom des departements'''
    options = Options(
        ignore_case=True,
        ignore_non_alphanumeric=True,
        ignore_extra_white_space=True,
        ignore_accents=True
    )
    return Departement.is_valid(val, options)
