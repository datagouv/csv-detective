from csv_detective.parsing.text import header_score

from ..latlon_wgs import COMMON_COORDS_LABELS

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "lonlat wgs",
        "lonlat",
        "longlat",
        "lon lat",
    ] + COMMON_COORDS_LABELS
    return header_score(header, words_combinations_list)
