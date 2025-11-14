from csv_detective.parsing.text import header_score

from ..latlon_wgs import COMMON_COORDS_LABELS

PROPORTION = 0.5

specific = [
    "lonlat",
    "lon lat",
    "y x",
    "yx",
]

# we aim wide to catch exact matches if possible for the highest possible score
words = (
    COMMON_COORDS_LABELS
    + specific
    + [w + sep + suf for suf in specific for w in COMMON_COORDS_LABELS for sep in ["", " "]]
)


def _is(header: str) -> float:
    return header_score(header, words)
