import re

PROPORTION = 0.9


def _is(val):
    """Detects e-mails"""
    return isinstance(val, str) and bool(
        re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", val, re.IGNORECASE)
    )
