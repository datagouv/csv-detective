from frformat import LongitudeL93

from csv_detective.formats.float import _is as is_float
from csv_detective.formats.float import float_casting
from csv_detective.formats.longitude_wgs import SHARED_LONGITUDE_LABELS

proportion = 1
tags = ["fr", "geo"]
mandatory_label = True
python_type = "float"
labels = SHARED_LONGITUDE_LABELS | {
    "x l93": 1,
    "longitude lb93": 1,
    "lambx": 1,
}

_longitudel93 = LongitudeL93()


def _is(val):
    try:
        if isinstance(val, str) and is_float(val):
            return _longitudel93.is_valid(float_casting(val))

        return False

    except (ValueError, OverflowError):
        return False


_test_values = {
    True: ["0", "-154", "1265783,45", "34723.4"],
    False: ["1456669.8", "-776225", "346_3214"],
}
