import re

PROPORTION = 0.9
regex = r"^W\d[\dA-Z]\d{7}$"


def _is(val):
    """Repere le code Waldec"""
    return isinstance(val, str) and bool(re.match(regex, val))
