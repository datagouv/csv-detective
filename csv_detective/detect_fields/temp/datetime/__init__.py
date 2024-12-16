from typing import Any, Optional

from csv_detective.detect_fields.temp.date import date_casting

PROPORTION = 1


def _is(val: Optional[Any]) -> bool:
    '''Renvoie True si val peut être un datetime, False sinon'''
    # early stops, to cut processing time
    if not isinstance(val, str) or len(val) > 30 or len(val) < 15:
        return False
    threshold = 0.7
    if sum([char.isdigit() for char in val]) / len(val) < threshold:
        return False
    res = date_casting(val)
    if res and (res.hour or res.minute or res.second):
        return True
    return False
