from csv_detective.parsing.text import _process_text

proportion = 1
tags = ["fr"]
labels = ["sexe", "sex", "civilite", "genre", "id sexe"
]


def _is(val):
    if not isinstance(val, str):
        return False
    val = _process_text(val)
    return val in {"homme", "femme", "h", "f", "m", "masculin", "feminin"}


_test_values = {
        True: ["hfemme", "H"],
        False: ["adulte"],
}
