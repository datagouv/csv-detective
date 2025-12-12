from csv_detective.formats.float import _is as is_float
from csv_detective.formats.latitude_wgs import labels  # noqa

proportion = 1
tags = ["fr", "geo"]
mandatory_label = True
python_type = "float"


def _is(val):
    try:
        return is_float(val) and float(val) >= 41.3 and float(val) <= 51.3
    except Exception:
        return False


_test_values = {
    True: ["42.5"],
    False: ["22.5", "62.5"],
}
