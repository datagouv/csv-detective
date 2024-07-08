from frformat import Canton, Options

PROPORTION = 0.9

def _is(val):
    '''Match avec le nom des cantons'''
    options = Options(
        ignore_case=True,
        ignore_non_alphanumeric=True,
        ignore_extra_white_space=True,
        ignore_accents=True
    )
    return Canton.is_valid(val, options)
