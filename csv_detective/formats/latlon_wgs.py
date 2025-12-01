from csv_detective.formats.latitude_wgs import _is as is_lat
from csv_detective.formats.longitude_wgs import _is as is_lon

proportion = 1
tags = ["geo"]

SHARED_COORDS_LABELS = [
    "ban",
    "coordinates",
    "coordonnees",
    "coordonnees insee",
    "geo",
    "geopoint",
    "geoloc",
    "geolocalisation",
    "geom",
    "geometry",
    "gps",
    "localisation",
    "point",
    "position",
    "wgs84",
]

specific = [
    "latlon",
    "lat lon",
    "x y",
    "xy",
]

# we aim wide to catch exact matches if possible for the highest possible score
labels = (
    SHARED_COORDS_LABELS
    + specific
    + [w + sep + suf for suf in specific for w in SHARED_COORDS_LABELS for sep in ["", " "]]
)


def _is(val):
    if not isinstance(val, str) or val.count(",") != 1:
        return False
    lat, lon = val.split(",")
    # handling [lat,lon]
    if lat.startswith("[") and lon.endswith("]"):
        lat, lon = lat[1:], lon[:-1]
    return is_lat(lat) and is_lon(lon.replace(" ", ""))


_test_values = {
    True: ["43.2,-22.6", "-10.7,140", "-40.7, 10.8", "[12,-0.28]"],
    False: ["0.1,192", "-102, 92", "[23.02,4.1", "23.02,4.1]", "160.1,-27"],
}
