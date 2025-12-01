from csv_detective.formats.float import _is as is_float

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


def _is(val):
    try:
        return is_float(val) and float(val) >= -5.5 and float(val) <= 9.8
    except ValueError:
        return False
    except OverflowError:
        return False


_test_values = {
    True: ["-2.5"],
    False: ["12.8"],
}
