from csv_detective.formats.float import _is as is_float

proportion = 1
tags = ["geo"]
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


def _is(val):
    try:
        return is_float(val) and float(val) >= -180 and float(val) <= 180
    except ValueError:
        return False
    except OverflowError:
        return False


_test_values = {
    True: ["120", "-20.2"],
    False: ["-200"],
}
