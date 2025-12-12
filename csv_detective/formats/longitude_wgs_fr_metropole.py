from csv_detective.formats.float import _is as is_float
from csv_detective.formats.longitude_wgs import labels  # noqa

proportion = 1
tags = ["fr", "geo"]
mandatory_label = True
python_type = "float"


def _is(val):
    try:
        return is_float(val) and float(val) >= -5.5 and float(val) <= 9.8
    except Exception:
        return False


_test_values = {
    True: ["-2.5"],
    False: ["12.8"],
}
