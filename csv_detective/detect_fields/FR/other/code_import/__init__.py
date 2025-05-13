import re

PROPORTION = 0.9
regex = r"^(\d{3}[SP]\d{4,10}(.\w{1,3}\d{0,5})?|\d[A-Z0-9]\d[SP]\w(\w-?\w{0,2}\d{0,6})?)$"


def _is(val):
    """Repere le code Import (ancien RNA)"""
    return isinstance(val, str) and bool(re.match(regex, val))
