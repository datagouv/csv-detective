from frformat import LongitudeL93
from csv_detective.detect_fields.other.float import _is as is_float

from csv_detective.detect_fields.other.float import float_casting


PROPORTION = 0.9

_longitudel93 = LongitudeL93()


def _is(val):
    try:
        if isinstance(val, str) and is_float(val):
            return _longitudel93.is_valid(float_casting(val))

        return False

    except (ValueError, OverflowError):
        return False
