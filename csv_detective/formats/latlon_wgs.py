from csv_detective.formats.latitude_wgs import _is as is_lat
from csv_detective.formats.longitude_wgs import _is as is_lon

proportion = 1
tags = ["geo"]
mandatory_label = True

SHARED_COORDS_LABELS = {
    "ban": 1,
    "coordinates": 1,
    "coordonnees": 1,
    "coordonnees insee": 1,
    "coord": 1,
    "geo": 0.5,
    "geopoint": 1,
    "geoloc": 1,
    "geolocalisation": 1,
    "geom": 0.75,
    "geometry": 1,
    "gps": 1,
    "localisation": 1,
    "point": 1,
    "position": 1,
    "wgs84": 1,
}

specific = {
    "latlon": 1,
    "lat lon": 1,
    "x y": 0.75,
    "xy": 0.75,
}

# we aim wide to catch exact matches if possible for the highest possible score
labels = (
    SHARED_COORDS_LABELS
    | specific
    | {w + sep + suf: 1 for suf in specific for w in SHARED_COORDS_LABELS for sep in ["", " "]}
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
    True: ["43.2,-22.6", "-10.71,140.0", "-40.791, 10.81", "[12.01,-0.28]"],
    False: ["0.1,192", "-102, 92", "[23.02,4.1", "23.02,4.1]", "160.1,-27", "1,2", "43, -23"],
}
