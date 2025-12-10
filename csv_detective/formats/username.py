import re

proportion = 1
labels = {"account": 1, "username": 1, "user": 0.75}


def _is(val):
    return isinstance(val, str) and bool(re.match(r"^@[A-Za-z0-9_]+$", val))


_test_values = {
    True: ["@accueil1"],
    False: ["adresse@mail"],
}
