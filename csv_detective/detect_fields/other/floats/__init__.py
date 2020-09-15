import re

PROPORTION = 1

def _is(val):
    '''Detects floats'''
    regex = r'[-+]?[ ]?([0-9]*\.[0-9]+|[0-9]+)'
    return bool(re.match(regex, val))

if __name__ == '__main__':
    print(_is('500,0'))

    print(_is('500'))

    print(_is('500.0'))

    print(_is('500b0')) # TODO fix this as this is not good

    print(_is('b 500.0'))