from csv_detective.formats.latitude_wgs import _is as is_lat
from csv_detective.formats.latlon_wgs import SHARED_COORDS_LABELS
from csv_detective.formats.longitude_wgs import _is as is_lon

proportion = 1
tags = ["geo"]

specific = [
    "lonlat",
    "lon lat",
    "y x",
    "yx",
]

# we aim wide to catch exact matches if possible for the highest possible score
words = (
    SHARED_COORDS_LABELS
    + specific
    + [w + sep + suf for suf in specific for w in SHARED_COORDS_LABELS for sep in ["", " "]]
)


def _is(val):
    if not isinstance(val, str) or val.count(",") != 1:
        return False
    lon, lat = val.split(",")
    # handling [lon,lat]
    if lon.startswith("[") and lat.endswith("]"):
        lon, lat = lon[1:], lat[:-1]
    return is_lon(lon) and is_lat(lat.replace(" ", ""))


_test_values = {
    True: ["-22.6,43.2", "140,-10.7", "10.8, -40.7", "[-0.28,12]"],
    False: ["192,0.1", "92, -102", "[4.1,23.02", "4.1,23.02]", "-27,160.1"],
}
