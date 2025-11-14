from csv_detective.parsing.text import header_score

PROPORTION = 0.5

COMMON_COORDS_LABELS = [
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
words = (
    COMMON_COORDS_LABELS
    + specific
    + [w + sep + suf for suf in specific for w in COMMON_COORDS_LABELS for sep in ["", " "]]
)


def _is(header: str) -> float:
    return header_score(header, words)
