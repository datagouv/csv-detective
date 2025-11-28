import re

proportion = 1
tags = ["fr", "temp"]
labels = ["date"
]

pattern = (
    r"^\d{1,2}[ \-](janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre"
    r"|octobre|novembre|decembre)[ \-]\d{4}$"
)


def _is(val):
    return isinstance(val, str) and bool(re.match(pattern, val))


_test_values = {
        True: ["13 février 1996"],
        False: ["44 march 2025"],
}
