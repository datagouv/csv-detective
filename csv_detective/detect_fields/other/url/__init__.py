import re

PROPORTION = 1
url_pattern = re.compile(
    r"^((https?|ftp)://|www\.)(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})"
    r"(/[A-Za-z0-9._~:/?#[@!$&'()*+,;=%-]*)?$"
)


def _is(val):
    """Detects urls"""
    if not isinstance(val, str):
        return False
    return bool(url_pattern.match(val))
