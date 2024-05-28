from frformat import LatitudeL93
from csv_detective.detect_fields.other.float import _is as is_float
from csv_detective.detect_fields.other.float import float_casting


PROPORTION = 0.9


def _is(val):
    try:
        if type(val) is float or type(val) is int:
            return LatitudeL93.is_valid(val)

        elif type(val) is str and is_float(val):
                return LatitudeL93.is_valid(float_casting(val))

        return False

    except ValueError:
        return False
    except OverflowError:
        return False
