from datetime import datetime
from typing import Optional

from dateparser import parse as date_parser
from dateutil.parser import parse as dateutil_parser, ParserError

PROPORTION = 1
# /!\ this is only for dates, not datetimes which are handled by other utils


def date_casting(val: str) -> Optional[datetime]:
    """For performance reasons, we try first with dateutil and fallback on dateparser"""
    try:
        return dateutil_parser(val)
    except ParserError:
        return date_parser(val)
    except OverflowError:
        return None


threshold = 0.3


def _is(val):
    '''Renvoie True si val peut être une date, False sinon'''
    # early stops, to cut processing time
    if not isinstance(val, str) or len(val) > 20 or len(val) < 8:
        return False
    if sum([char.isdigit() for char in val]) / len(val) < threshold:
        return False
    res = date_casting(val)
    if not res or res.hour or res.minute or res.second:
        return False
    return True
