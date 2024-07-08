from frformat import Pays, Options

PROPORTION = 0.6

def _is(val):
    '''Match avec le nom des pays'''
    options = Options(
        ignore_case=True,
        ignore_non_alphanumeric=True,
        ignore_extra_white_space=True,
        ignore_accents=True
    )
    return Pays.is_valid(val, options)
