import re

from csv_detective.parsing.text import _process_text

proportion = 1
tags = ["fr", "temp"]
labels = ["date"]

pattern = (
    r"^(0?[1-9]|[12][0-9]|3[01])[ \-/](janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre"
    r"|octobre|novembre|decembre)[ \-/]\d{4}$"
)


def _is(val):
    return isinstance(val, str) and bool(re.match(pattern, _process_text(val)))


_test_values = {
    True: ["13 février 1996", "15 decembre 2024"],
    False: ["44 march 2025"],
}
