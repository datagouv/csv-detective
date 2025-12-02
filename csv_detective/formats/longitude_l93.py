from frformat import LongitudeL93

from csv_detective.formats.float import _is as is_float
from csv_detective.formats.float import float_casting

proportion = 1
tags = ["fr", "geo"]
labels = [
    "longitude",
    "lon",
    "long",
    "geocodage x gps",
    "location longitude",
    "xlongitude",
    "lng",
    "xlong",
    "x",
    "xf",
    "xd",
]

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
